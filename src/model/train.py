"""src/model/train.py — Train Karhutla risk models (S5).

Architecture: DIRECT multi-horizon (h=1,2,3 separate models).
Models: Persistence baseline, Seasonal-Climatology (Laplace-smoothed),
        ENSO-conditioned Climatology, PoissonGLM, HGB (HistGradientBoosting).
Validation: Rolling-origin folds (temporal, min 3 folds) on 2015-2022 train.

Outputs
-------
  data/interim/model_artifacts/  — pickled models per horizon
  data/interim/thresholds.json   — risk_class cutoffs
  model metrics are printed but not exported until their column contract is
  approved in HANDOVER_CURSOR_karhutla.md section 6

Usage
-----
  python -m src.model.train
"""
from __future__ import annotations

import json
import os
import pathlib
import pickle
import sys
import warnings

# Keep OpenMP deterministic and avoid oversized thread pools on Windows.
os.environ.setdefault("OMP_NUM_THREADS", "1")

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import PoissonRegressor
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.model.features import (
    ALL_NUMERIC_FEATURES,
    ENSO_PHASE_COL,
    build_features,
    build_oni_monthly,
)
from src.model.evaluate import compute_metrics, poisson_deviance

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TRAIN_END = pd.Timestamp("2022-12-01")
VAL_END = pd.Timestamp("2024-12-01")
TEST_END = pd.Timestamp("2026-10-01")
HORIZONS = [1, 2, 3]
EPSILON = 1e-3
ROLLING_FOLD_STEP_MONTHS = 6  # advance the target-month boundary by 6 months
MIN_TRAIN_MONTHS = 24          # minimum months in each fold's train window

ONI_PATH = REPO_ROOT / "data/raw/oni/oni.ascii.txt"
PANEL_PATH = REPO_ROOT / "data/interim/fact_kab_month_interim.csv"
DIM_PATH = REPO_ROOT / "data/interim/dim_kabupaten_interim.csv"
ARTIFACTS_DIR = REPO_ROOT / "data/interim/model_artifacts"
THRESHOLDS_PATH = REPO_ROOT / "data/interim/thresholds.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _enso_phase_to_int(phase: str) -> float:
    return {"la_nina": -1, "netral": 0, "el_nino": 1}.get(phase, np.nan)


def _prepare_X_y(
    feat_df: pd.DataFrame,
    target_start: pd.Timestamp,
    target_end: pd.Timestamp,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Slice rows by target month so all horizons share date boundaries."""
    mask = (feat_df["target_month"] >= target_start) & (
        feat_df["target_month"] <= target_end
    )
    sub = feat_df[mask & feat_df["target_count"].notna()].copy()
    sub = sub.sort_values(["target_month", "kab_id"]).reset_index(drop=True)
    sub["enso_int"] = sub[ENSO_PHASE_COL].apply(_enso_phase_to_int)
    num_cols = ALL_NUMERIC_FEATURES + ["enso_int"]
    X = sub[num_cols].copy()
    y = sub["target_count"].values.astype(float)
    w = sub["area_km2"].values.astype(float)
    return X, y, w


def _rolling_origin_folds(
    all_months: pd.Series,
    train_end_month: pd.Timestamp,
    horizon: int = 1,
    step: int = ROLLING_FOLD_STEP_MONTHS,
    min_train: int = MIN_TRAIN_MONTHS,
) -> list[tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]]:
    """Generate expanding training ends for non-overlapping six-month folds.

    Each tuple is (training start, training label cutoff, validation start).
    Validation starts ``horizon`` months after the cutoff, so the first target
    is forecast using only labels available at its origin month.
    """
    all_m = sorted(all_months.unique())
    start = all_m[0]
    # Keep at least min_train target months before each validation origin.
    first_val_idx = min_train + horizon - 1
    folds = []
    idx = first_val_idx
    while idx < len(all_m) and all_m[idx] <= train_end_month:
        folds.append((start, all_m[idx - horizon], all_m[idx]))
        idx += step
    return folds


# ---------------------------------------------------------------------------
# Baseline models
# ---------------------------------------------------------------------------

def _persistence_predict(
    feat_df: pd.DataFrame,
    target_start: pd.Timestamp,
    target_end: pd.Timestamp,
) -> np.ndarray:
    """Use the completed origin-month count as the persistence prediction."""
    mask = (feat_df["target_month"] >= target_start) & (
        feat_df["target_month"] <= target_end
    )
    sub = feat_df[mask & feat_df["target_count"].notna()].copy()
    sub = sub.sort_values(["target_month", "kab_id"])
    return sub["hotspot_count"].values.astype(float)


def _climatology_predict(
    feat_df: pd.DataFrame,
    train_start: pd.Timestamp,
    train_end: pd.Timestamp,
    predict_start: pd.Timestamp,
    predict_end: pd.Timestamp,
    enso_conditioned: bool = False,
    shrinkage_alpha: float = 0.3,
) -> tuple[np.ndarray, np.ndarray]:
    """Predict using Laplace-smoothed seasonal climatology.

    Returns (y_pred, y_pred_enso_cond) for the predict window.
    Both are count predictions (rate × area_km2).
    """
    train_mask = (feat_df["target_month"] >= train_start) & (
        feat_df["target_month"] <= train_end
    )
    pred_mask = (feat_df["target_month"] >= predict_start) & (
        feat_df["target_month"] <= predict_end
    )
    train = feat_df[train_mask].copy()
    pred = feat_df[pred_mask].copy().sort_values(
        ["target_month", "kab_id"]
    ).reset_index(drop=True)
    train = train[train["target_count"].notna()].copy()

    # Compute target_month's calendar month for climatology grouping
    train["target_cal_month"] = train["target_month"].dt.month
    pred["target_cal_month"] = pred["target_month"].dt.month

    # --- County-specific seasonal mean count with a weak county prior ---
    clim = (
        train.groupby(["kab_id", "target_cal_month"])
        .agg(
            sum_count=("target_count", "sum"),
            n=("target_count", "count"),
        )
        .reset_index()
    )
    county_prior = train.groupby("kab_id")["target_count"].mean().to_dict()
    clim["county_prior"] = clim["kab_id"].map(county_prior)
    clim["mean_count"] = (
        clim["sum_count"] + shrinkage_alpha * clim["county_prior"]
    ) / (clim["n"] + shrinkage_alpha)
    clim_lookup = clim.set_index(["kab_id", "target_cal_month"])["mean_count"].to_dict()

    def _clim_pred(row: pd.Series) -> float:
        return float(clim_lookup.get((row["kab_id"], row["target_cal_month"]),
                                     county_prior.get(row["kab_id"], 0.0)))

    y_pred_clim = pred.apply(_clim_pred, axis=1).values.astype(float)

    if not enso_conditioned:
        return y_pred_clim, y_pred_clim

    # --- ENSO-conditioned with shrinkage ---
    train["enso_p"] = train[ENSO_PHASE_COL]
    enso_clim = (
        train.groupby(["kab_id", "target_cal_month", "enso_p"])
        .agg(sum_count=("target_count", "sum"), n=("target_count", "count"))
        .reset_index()
    )
    enso_clim["mean_count"] = (
        enso_clim["sum_count"] + shrinkage_alpha * enso_clim["kab_id"].map(county_prior)
    ) / (enso_clim["n"] + shrinkage_alpha)
    enso_lookup = enso_clim.set_index(
        ["kab_id", "target_cal_month", "enso_p"]
    )["mean_count"].to_dict()

    pred2 = pred.copy()
    pred2["enso_p"] = pred2[ENSO_PHASE_COL]

    def _enso_clim_pred(row: pd.Series) -> float:
        enso_count = enso_lookup.get(
            (row["kab_id"], row["target_cal_month"], row["enso_p"]), None
        )
        base_count = clim_lookup.get(
            (row["kab_id"], row["target_cal_month"]),
            county_prior.get(row["kab_id"], 0.0),
        )
        if enso_count is None:
            # No ENSO conditioning available → shrink fully to overall clim
            final_count = base_count
        else:
            final_count = shrinkage_alpha * base_count + (1 - shrinkage_alpha) * enso_count
        return float(final_count)

    y_pred_enso = pred2.apply(_enso_clim_pred, axis=1).values.astype(float)
    return y_pred_clim, y_pred_enso


# ---------------------------------------------------------------------------
# HGB + GLM training
# ---------------------------------------------------------------------------

def _train_hgb(X_train: pd.DataFrame, y_train: np.ndarray,
               w_train: np.ndarray) -> HistGradientBoostingRegressor:
    model = HistGradientBoostingRegressor(
        loss="poisson",
        max_iter=500,
        learning_rate=0.05,
        max_depth=4,
        min_samples_leaf=20,
        random_state=42,
        early_stopping=False,  # no val split needed in CV; refit on full train+val
    )
    exposure = np.maximum(np.asarray(w_train, dtype=float), 1e-9)
    rate = np.asarray(y_train, dtype=float) / exposure
    model.fit(X_train, rate, sample_weight=exposure)
    return model


def _train_glm(X_train: pd.DataFrame, y_train: np.ndarray,
               w_train: np.ndarray) -> tuple[PoissonRegressor, StandardScaler, dict[str, float]]:
    exposure = np.maximum(np.asarray(w_train, dtype=float), 1e-9)
    rate = np.asarray(y_train, dtype=float) / exposure
    medians = X_train.median(axis=0).fillna(0.0).to_dict()
    X_imputed = X_train.fillna(pd.Series(medians))
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)
    glm = PoissonRegressor(alpha=0.1, max_iter=500)
    glm.fit(X_scaled, np.clip(rate, 0, None), sample_weight=exposure)
    return glm, scaler, {str(k): float(v) for k, v in medians.items()}


def _hgb_predict(model: HistGradientBoostingRegressor,
                 X: pd.DataFrame,
                 area_km2: np.ndarray) -> np.ndarray:
    rate = model.predict(X)
    return np.clip(rate, 0, None) * np.asarray(area_km2, dtype=float)


def _glm_predict(glm: PoissonRegressor, scaler: StandardScaler,
                 X: pd.DataFrame,
                 area_km2: np.ndarray,
                 feature_medians: dict[str, float]) -> np.ndarray:
    X_imputed = X.fillna(pd.Series(feature_medians))
    X_scaled = scaler.transform(X_imputed)
    rate = glm.predict(X_scaled)
    return np.clip(rate, 0, None) * np.asarray(area_km2, dtype=float)


# ---------------------------------------------------------------------------
# Ablation feature groups
# ---------------------------------------------------------------------------

from src.model.features import (
    AUTOREGRESSIVE_COLS,
    ONI_COLS,
    SPATIAL_COLS,
    STATIC_COLS,
    CALENDAR_COLS,
)

ABLATION_GROUPS = {
    "no_oni": ONI_COLS + ["enso_int"],
    "no_lag": AUTOREGRESSIVE_COLS,
    "no_knn": SPATIAL_COLS,
}


def _ablation_X(X: pd.DataFrame, drop_group: str) -> pd.DataFrame:
    drop_cols = [c for c in ABLATION_GROUPS[drop_group] if c in X.columns]
    return X.drop(columns=drop_cols)


# ---------------------------------------------------------------------------
# ENSO regime detection
# ---------------------------------------------------------------------------

def _enso_regime(oni_series: np.ndarray) -> np.ndarray:
    """Return boolean mask: True where El Niño (ONI >= 0.5)."""
    return oni_series >= 0.5


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------

def run_training() -> None:
    print("=" * 60)
    print("S5 Karhutla Risk Model Training")
    print("=" * 60)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    pathlib.Path(REPO_ROOT / "data/processed").mkdir(parents=True, exist_ok=True)

    # Load inputs
    print("\nLoading data...")
    panel = pd.read_csv(PANEL_PATH)
    oni = build_oni_monthly(ONI_PATH)
    dim = pd.read_csv(DIM_PATH)
    print(f"  Panel: {len(panel)} rows | ONI: {len(oni)} rows | Dim: {len(dim)} rows")

    all_metrics_rows: list[dict] = []
    artifacts: dict[int, dict[str, Any]] = {}

    for h in HORIZONS:
        print(f"\n{'-'*50}")
        print(f"Horizon h={h}")
        print(f"{'-'*50}")

        # Build feature matrix for this horizon
        print("  Building feature matrix...")
        feat = build_features(panel, oni, dim, h)
        feat["origin_month"] = pd.to_datetime(feat["origin_month"])
        feat["target_month"] = pd.to_datetime(feat["target_month"])

        # Split by target month, not origin, so no horizon can place a target
        # from a later split into an earlier split's training labels.
        train_targets = feat[feat["target_month"] <= TRAIN_END]["target_month"]
        val_targets = feat[
            (feat["target_month"] > TRAIN_END) & (feat["target_month"] <= VAL_END)
        ]["target_month"]
        test_targets = feat[
            (feat["target_month"] > VAL_END) & (feat["target_month"] <= TEST_END)
        ]["target_month"]

        print(f"  Train targets: {train_targets.min()} to {train_targets.max()} ({train_targets.nunique()} months)")
        print(f"  Val targets:   {val_targets.min()} to {val_targets.max()} ({val_targets.nunique()} months)")
        print(f"  Test targets:  {test_targets.min()} to {test_targets.max()} ({test_targets.nunique()} months)")

        # Rolling-origin folds
        folds = _rolling_origin_folds(train_targets, TRAIN_END, horizon=h)
        print(f"  Rolling-origin folds: {len(folds)}")

        fold_results: list[dict] = []

        for fold_i, (fold_start, fold_train_end, val_start) in enumerate(folds):
            # Non-overlapping validation window: six target months.
            val_end_fold = val_start + pd.DateOffset(months=ROLLING_FOLD_STEP_MONTHS - 1)
            # Clamp to overall train end (rolling-origin: test within train period)
            val_end_fold = min(val_end_fold, TRAIN_END)

            X_tr, y_tr, w_tr = _prepare_X_y(feat, fold_start, fold_train_end)
            X_va, y_va, w_va = _prepare_X_y(feat, val_start, val_end_fold)

            if len(X_tr) == 0 or len(X_va) == 0:
                continue

            # --- Baselines ---
            # Persistence
            pers_va = _persistence_predict(feat, val_start, val_end_fold)

            # Climatology (overall + ENSO-conditioned)
            clim_va, enso_clim_va = _climatology_predict(
                feat, fold_start, fold_train_end, val_start, val_end_fold,
                enso_conditioned=True,
            )

            # --- HGB ---
            hgb = _train_hgb(X_tr, y_tr, w_tr)
            hgb_va = _hgb_predict(hgb, X_va, w_va)

            # --- GLM ---
            glm, scaler, medians = _train_glm(X_tr, y_tr, w_tr)
            glm_va = _glm_predict(glm, scaler, X_va, w_va, medians)

            # --- Metrics ---
            dev_clim = poisson_deviance(y_va, clim_va, EPSILON)

            for model_name, y_pred_va in [
                ("persistence", pers_va),
                ("climatology", clim_va),
                ("enso_climatology", enso_clim_va),
                ("hgb", hgb_va),
                ("glm", glm_va),
            ]:
                m = compute_metrics(y_va, y_pred_va,
                                    y_pred_clim=clim_va, epsilon=EPSILON)
                m.update({
                    "model": model_name,
                    "horizon": h,
                    "fold": fold_i,
                    "split": "val_fold",
                    "fold_train_end": str(fold_train_end.date()),
                    "fold_val_start": str(val_start.date()),
                    "fold_val_end": str(val_end_fold.date()),
                    "regime": "all",
                    "province": "all",
                })
                all_metrics_rows.append(m)

            fold_results.append({
                "fold": fold_i,
                "hgb_dev": poisson_deviance(y_va, hgb_va, EPSILON),
                "clim_dev": dev_clim,
            })

        # --- Ablation study on full validation targets (2023-2024) ---
        val_start = TRAIN_END + pd.DateOffset(months=1)
        val_train_end = val_start - pd.DateOffset(months=h)
        X_full_tr, y_full_tr, w_full_tr = _prepare_X_y(
            feat,
            feat["target_month"].min(),
            val_train_end,
        )
        X_va_full, y_va_full, w_va_full = _prepare_X_y(
            feat,
            val_start,
            VAL_END,
        )

        for ablation_name, _ in ABLATION_GROUPS.items():
            X_tr_ab = _ablation_X(X_full_tr, ablation_name)
            X_va_ab = _ablation_X(X_va_full, ablation_name)
            if len(X_tr_ab) == 0 or len(X_va_ab) == 0:
                continue
            hgb_ab = _train_hgb(X_tr_ab, y_full_tr, w_full_tr)
            hgb_va_ab = _hgb_predict(hgb_ab, X_va_ab, w_va_full)
            _, clim_va_full = _climatology_predict(
                feat,
                feat["target_month"].min(), val_train_end,
                val_start, VAL_END,
                enso_conditioned=False,
            )
            m_ab = compute_metrics(y_va_full, hgb_va_ab,
                                   y_pred_clim=clim_va_full, epsilon=EPSILON)
            m_ab.update({
                "model": f"hgb_ablation_{ablation_name}",
                "horizon": h,
                "fold": -1,
                "split": "val",
                "regime": "all",
                "province": "all",
            })
            all_metrics_rows.append(m_ab)

        # Fit each candidate at the first validation origin and score the full
        # 2023-2024 window. This selection window remains separate from test.
        hgb_val_model = _train_hgb(X_full_tr, y_full_tr, w_full_tr)
        glm_val_model, glm_val_scaler, glm_val_medians = _train_glm(
            X_full_tr, y_full_tr, w_full_tr
        )
        hgb_val = _hgb_predict(hgb_val_model, X_va_full, w_va_full)
        glm_val = _glm_predict(
            glm_val_model, glm_val_scaler, X_va_full, w_va_full, glm_val_medians
        )
        _, clim_val = _climatology_predict(
            feat, feat["target_month"].min(), val_train_end,
            val_start, VAL_END, enso_conditioned=False,
        )
        _, enso_clim_val = _climatology_predict(
            feat, feat["target_month"].min(), val_train_end,
            val_start, VAL_END, enso_conditioned=True,
        )
        pers_val = _persistence_predict(feat, val_start, VAL_END)
        val_predictions = {
            "persistence": pers_val,
            "climatology": clim_val,
            "enso_climatology": enso_clim_val,
            "hgb": hgb_val,
            "glm": glm_val,
        }
        val_devs = {
            name: poisson_deviance(y_va_full, prediction, EPSILON)
            for name, prediction in val_predictions.items()
        }
        for model_name, y_pred_val in val_predictions.items():
            m_val = compute_metrics(
                y_va_full, y_pred_val, y_pred_clim=clim_val, epsilon=EPSILON
            )
            m_val.update({
                "model": model_name,
                "horizon": h,
                "fold": -1,
                "split": "val",
                "regime": "all",
                "province": "all",
            })
            all_metrics_rows.append(m_val)

        # --- Fit at the first test origin, then evaluate the test window ---
        test_start = VAL_END + pd.DateOffset(months=1)
        test_train_end = test_start - pd.DateOffset(months=h)
        print(f"\n  Test-window training labels end at {test_train_end.date()}...")
        X_trainval, y_trainval, w_trainval = _prepare_X_y(
            feat, feat["target_month"].min(), test_train_end
        )
        X_test, y_test, w_test = _prepare_X_y(
            feat,
            test_start,
            TEST_END,
        )

        if len(X_trainval) == 0 or len(X_test) == 0:
            print(f"  WARNING: empty train+val or test for h={h}; skipping test eval.")
            continue

        hgb_final = _train_hgb(X_trainval, y_trainval, w_trainval)
        glm_final, scaler_final, glm_medians = _train_glm(X_trainval, y_trainval, w_trainval)
        hgb_test = _hgb_predict(hgb_final, X_test, w_test)
        glm_test = _glm_predict(glm_final, scaler_final, X_test, w_test, glm_medians)

        _, clim_test = _climatology_predict(
            feat,
            feat["target_month"].min(), test_train_end,
            test_start, TEST_END,
            enso_conditioned=False,
        )
        _, enso_clim_test = _climatology_predict(
            feat,
            feat["target_month"].min(), test_train_end,
            test_start, TEST_END,
            enso_conditioned=True,
        )
        pers_test = _persistence_predict(feat, test_start, TEST_END)

        # Check test regime (ENSO episodes in test period)
        test_feat = feat[
            (feat["target_month"] > VAL_END) & (feat["target_month"] <= TEST_END)
        ].copy().sort_values(["target_month", "kab_id"]).reset_index(drop=True)
        # Count El Niño rows in test period for regime check
        enso_in_test_mask = test_feat["enso_phase"] == "el_nino"
        enso_in_test_count = int(enso_in_test_mask.sum())
        total_test_rows = len(test_feat)
        enso_note = (
            f"El Niño rows in test: {enso_in_test_count}/{total_test_rows}"
            + (" - ENSO claim partially testable" if enso_in_test_count > 0
               else " - ENSO claim CANNOT be tested on this test period")
        )
        print(f"  TEST REGIME CHECK: {enso_note}")

        # Regime-split metrics on test
        test_feat["y_pred_hgb"] = hgb_test
        test_feat["y_pred_clim"] = clim_test
        test_feat["y_true"] = y_test

        for regime_label, regime_mask in [
            ("all", np.ones(len(y_test), dtype=bool)),
            ("el_nino", test_feat["enso_phase"].values == "el_nino"),
            ("non_el_nino", test_feat["enso_phase"].values != "el_nino"),
        ]:
            if regime_mask.sum() < 5:
                continue
            df_m = test_feat.reset_index(drop=True)
            for model_name, y_pred_t in [
                ("persistence", pers_test),
                ("climatology", clim_test),
                ("enso_climatology", enso_clim_test),
                ("hgb", hgb_test),
                ("glm", glm_test),
            ]:
                m_t = compute_metrics(
                    y_test[regime_mask],
                    y_pred_t[regime_mask],
                    y_pred_clim=clim_test[regime_mask],
                    epsilon=EPSILON,
                    df_month=df_m[regime_mask],
                    month_col="target_month",
                )
                m_t.update({
                    "model": model_name,
                    "horizon": h,
                    "fold": -1,
                    "split": "test",
                    "regime": regime_label,
                    "province": "all",
                })
                all_metrics_rows.append(m_t)

        # Per-province breakdown (test, HGB only)
        for prov, grp in test_feat.groupby("prov_name"):
            if len(grp) < 10:
                continue
            prov_mask = test_feat["prov_name"] == prov
            m_prov = compute_metrics(
                y_test[prov_mask],
                hgb_test[prov_mask],
                y_pred_clim=clim_test[prov_mask],
                epsilon=EPSILON,
            )
            m_prov.update({
                "model": "hgb",
                "horizon": h,
                "fold": -1,
                "split": "test",
                "regime": "all",
                "province": prov,
            })
            all_metrics_rows.append(m_prov)

        # Select candidates only when they beat both required baselines on the
        # rolling folds and the 2023-2024 validation window. Test stays held out.
        cv_frame = pd.DataFrame(all_metrics_rows)
        cv_frame = cv_frame[
            (cv_frame["horizon"] == h)
            & (cv_frame["split"] == "val_fold")
            & cv_frame["model"].isin(
                ["persistence", "climatology", "enso_climatology", "hgb", "glm"]
            )
        ]
        cv_devs = cv_frame.groupby("model")["poisson_deviance"].mean().to_dict()
        test_devs = {
            "persistence": poisson_deviance(y_test, pers_test, EPSILON),
            "climatology": poisson_deviance(y_test, clim_test, EPSILON),
            "enso_climatology": poisson_deviance(y_test, enso_clim_test, EPSILON),
            "hgb": poisson_deviance(y_test, hgb_test, EPSILON),
            "glm": poisson_deviance(y_test, glm_test, EPSILON),
        }
        required_baselines = ("persistence", "climatology")
        cv_qualified = [
            name for name in ("hgb", "glm")
            if all(name in cv_devs and base in cv_devs
                   and cv_devs[name] < cv_devs[base] for base in required_baselines)
        ]
        val_qualified = [
            name for name in ("hgb", "glm")
            if all(val_devs[name] < val_devs[base] for base in required_baselines)
        ]
        qualified = [name for name in cv_qualified if name in val_qualified]
        baseline_names = ("persistence", "climatology", "enso_climatology")
        best_baseline = min(baseline_names, key=lambda name: val_devs[name])
        winner = min(qualified, key=lambda name: val_devs[name]) if qualified else best_baseline
        model_wins = winner in {"hgb", "glm"} and all(
            test_devs[winner] < test_devs[base] for base in required_baselines
        )
        test_comparisons = {
            base: bool(test_devs[winner] < test_devs[base])
            for base in baseline_names
        }
        print(f"  Rolling-origin mean deviance: {cv_devs}")
        print(f"  2023-2024 validation deviance: {val_devs}")
        print(f"  2025-2026 test deviance: {test_devs}")
        print(f"  Forecast family selected by rolling-origin CV + validation: {winner}")
        print(f"  Selected family beats persistence and seasonal climatology on test: {model_wins}")
        if winner in {"hgb", "glm"} and not test_comparisons["enso_climatology"]:
            print("  Note: ENSO-conditioned climatology has lower test deviance than the selected model.")

        # Refit candidates on every observed label through October 2026 for
        # projections beyond the observed period.
        X_all, y_all, w_all = _prepare_X_y(
            feat, feat["target_month"].min(), TEST_END
        )
        hgb_final = _train_hgb(X_all, y_all, w_all)
        glm_final, scaler_final, glm_medians = _train_glm(X_all, y_all, w_all)
        feature_names = X_all.columns.tolist()
        coef_df = pd.DataFrame({"feature": feature_names, "coef": glm_final.coef_})
        feature_means = dict(zip(feature_names, scaler_final.mean_.astype(float)))
        feature_scales = dict(zip(feature_names, scaler_final.scale_.astype(float)))

        artifacts[h] = {
            "hgb": hgb_final,
            "glm": glm_final,
            "scaler": scaler_final,
            "feature_medians": glm_medians,
            "feature_names": feature_names,
            "coef_df": coef_df,
            "feature_means": feature_means,
            "feature_scales": feature_scales,
            "winner": winner,
            "model_wins_test_baselines": model_wins,
            "cv_mean_deviance": cv_devs,
            "validation_deviance": val_devs,
            "test_deviance": test_devs,
            "test_comparisons": test_comparisons,
            "enso_note": enso_note,
        }

        artifact_path = ARTIFACTS_DIR / f"model_h{h}.pkl"
        with open(artifact_path, "wb") as f:
            pickle.dump(artifacts[h], f)
        print(f"  Saved artifact: {artifact_path}")

    # model_metrics.csv remains unwritten until its required column contract is
    # agreed. Test and rolling-origin metrics are printed per horizon above.
    print("\nComputing risk class thresholds from observed 2015-2022 rates...")
    thresholds = _compute_thresholds(panel, dim)
    with open(THRESHOLDS_PATH, "w") as f:
        json.dump(thresholds, f, indent=2)
    print(f"Thresholds saved: {THRESHOLDS_PATH}")
    print(thresholds)

    print("\nTraining complete.")


# ---------------------------------------------------------------------------
# Risk class threshold computation
# ---------------------------------------------------------------------------

def _compute_thresholds(
    panel: pd.DataFrame,
    dim: pd.DataFrame,
) -> dict:
    """Compute fixed risk cutoffs from positive observed training rates."""
    train = panel[pd.to_datetime(panel["month"]) <= TRAIN_END].merge(
        dim[["kab_id", "area_km2"]],
        on="kab_id",
        how="left",
        validate="many_to_one",
    )
    if train["area_km2"].isna().any() or (train["area_km2"] <= 0).any():
        raise ValueError("Cannot compute training thresholds with missing county area")
    counts = train["hotspot_count"].to_numpy(dtype=float)
    areas = train["area_km2"].to_numpy(dtype=float)
    log_rate = np.log1p(counts / areas * 100)
    positive = log_rate[log_rate > 0]
    if len(positive) == 0:
        raise ValueError("No positive training hotspot rates for risk thresholds")
    p50, p75, p90 = (float(np.percentile(positive, q)) for q in (50, 75, 90))
    return {
        "log_rate_thresholds_raw": [0.0, p50, p75, p90],
        "risk_classes": ["rendah", "sedang", "tinggi", "sangat_tinggi"],
        "log_rate_max_train": float(log_rate.max()),
        "threshold_data": "observed hotspot counts per 100 km2, 2015-2022",
        "note": (
            "Risk cutoffs use positive observed hotspot rates, not burned area. "
            "They are the 50th, 75th, and 90th percentiles and are fixed from "
            "the training period before validation/test evaluation."
        ),
    }


if __name__ == "__main__":
    run_training()
