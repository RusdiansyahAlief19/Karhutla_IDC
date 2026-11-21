"""src/model/forecast.py — 3-scenario × 3-horizon ENSO conditional projections.

Outputs: data/processed/ml_risk_forecast.csv (1,386 rows, Pandera validated)

Usage
-----
  python -m src.model.forecast

Requires that src/model/train.py has already been run (artifacts in
data/interim/model_artifacts/).
"""
from __future__ import annotations

import json
import os
import pathlib
import pickle
import sys
import warnings

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.model.features import (
    ALL_NUMERIC_FEATURES,
    ENSO_PHASE_COL,
    build_features,
    build_oni_monthly,
    _enso_phase,
)
from src.model.train import (
    HORIZONS,
    _enso_phase_to_int,
    _hgb_predict,
    _glm_predict,
    _climatology_predict,
)
from src.export.schemas import validate_export, SCENARIOS, RISK_CLASSES

ONI_PATH = REPO_ROOT / "data/raw/oni/oni.ascii.txt"
PANEL_PATH = REPO_ROOT / "data/interim/fact_kab_month_interim.csv"
DIM_PATH = REPO_ROOT / "data/interim/dim_kabupaten_interim.csv"
ARTIFACTS_DIR = REPO_ROOT / "data/interim/model_artifacts"
THRESHOLDS_PATH = REPO_ROOT / "data/interim/thresholds.json"
OUTPUT_PATH = REPO_ROOT / "data/processed/ml_risk_forecast.csv"

# Scenario ONI values
SCENARIO_ONI: dict[str, float] = {
    "netral": 0.0,
    "el_nino": 1.5,
    "la_nina": -1.0,
}

# Horizon → target window label (forecast origin = Oct 2026 = last data month)
FORECAST_ORIGIN = pd.Timestamp("2026-10-01")


def _target_window_label(h: int) -> str:
    target = FORECAST_ORIGIN + pd.DateOffset(months=h)
    return target.strftime("%Y-%m")


# ---------------------------------------------------------------------------
# Feature driver labelling
# ---------------------------------------------------------------------------

DRIVER_GROUPS: dict[str, list[str]] = {
    "Riwayat Hotspot Tinggi": [
        "hs_lag1", "hs_lag2", "hs_lag3",
        "hs_roll_mean3", "hs_roll_max3",
        "hs_lag12", "hs_cum6", "hs_cum12",
        "months_since_last",
    ],
    "Anomali Pemanasan ENSO": ["oni_now", "oni_prev", "delta_oni", "enso_int"],
    "Puncak Kemarau Musiman": ["month_sin", "month_cos"],
    "Tekanan Wilayah Tetangga": ["knn_lag_rate", "prov_loo_rate"],
    "Lokasi Geografis": ["centroid_lat", "centroid_lon"],
}


def _get_top_drivers(
    coef_df: pd.DataFrame,
    feature_means: dict[str, float],
    feature_scales: dict[str, float],
    feature_medians: dict[str, float],
    X_row: pd.Series,
    n: int = 2,
) -> list[str]:
    """Return top-n driver labels for one kabupaten row.

    Driver contribution is computed in the standardized GLM feature space.
    Features are grouped; the group with highest abs contribution wins.
    """
    contributions: dict[str, float] = {}
    for group_label, group_features in DRIVER_GROUPS.items():
        total = 0.0
        for feat in group_features:
            if feat not in coef_df["feature"].values:
                continue
            beta = float(coef_df.loc[coef_df["feature"] == feat, "coef"].iloc[0])
            x_val = float(X_row.get(feat, feature_medians.get(feat, 0.0)))
            if np.isnan(x_val):
                x_val = feature_medians.get(feat, 0.0)
            mu = feature_means.get(feat, 0.0)
            if np.isnan(mu):
                mu = 0.0
            scale = feature_scales.get(feat, 1.0)
            total += beta * (x_val - mu) / max(scale, 1e-12)
        contributions[group_label] = total

    if not any(abs(value) > 1e-12 for value in contributions.values()):
        return [None] * n

    # Sort by absolute contribution descending
    sorted_groups = sorted(contributions.items(), key=lambda kv: abs(kv[1]), reverse=True)
    result = [g for g, _ in sorted_groups[:n]]
    # Pad with None if fewer than n
    while len(result) < n:
        result.append(None)  # type: ignore[arg-type]
    return result


# ---------------------------------------------------------------------------
# Risk score + class computation
# ---------------------------------------------------------------------------

def _apply_risk_class(score_normalized: float, thresholds: list[float]) -> str:
    """Map normalized score [0,1] to risk class.

    thresholds: [0, p50_norm, p75_norm, p90_norm]
    rendah: [0, p50_norm)
    sedang: [p50_norm, p75_norm)
    tinggi: [p75_norm, p90_norm)
    sangat_tinggi: [p90_norm, 1]
    """
    if score_normalized < thresholds[1]:
        return "rendah"
    elif score_normalized < thresholds[2]:
        return "sedang"
    elif score_normalized < thresholds[3]:
        return "tinggi"
    else:
        return "sangat_tinggi"


# ---------------------------------------------------------------------------
# Main forecast function
# ---------------------------------------------------------------------------

def run_forecast() -> None:
    print("=" * 60)
    print("S5 Karhutla Risk Forecast")
    print("=" * 60)

    pathlib.Path(REPO_ROOT / "data/processed").mkdir(parents=True, exist_ok=True)

    # Load inputs
    print("\nLoading data...")
    panel = pd.read_csv(PANEL_PATH)
    oni = build_oni_monthly(ONI_PATH)
    dim = pd.read_csv(DIM_PATH)

    # Load thresholds
    with open(THRESHOLDS_PATH) as f:
        threshold_config = json.load(f)
    log_rate_max_train = float(threshold_config["log_rate_max_train"])
    if log_rate_max_train <= 0:
        raise ValueError("Training log-rate maximum must be positive")
    log_rate_thresholds_raw = threshold_config["log_rate_thresholds_raw"]

    # Collect predictions; scores use a fixed training-period scale.
    all_pred_rows: list[dict] = []

    for h in HORIZONS:
        artifact_path = ARTIFACTS_DIR / f"model_h{h}.pkl"
        if not artifact_path.exists():
            raise FileNotFoundError(
                f"Artifact not found: {artifact_path}. Run src.model.train first."
            )
        with open(artifact_path, "rb") as f:
            art = pickle.load(f)

        hgb = art["hgb"]
        glm = art["glm"]
        scaler = art["scaler"]
        feature_medians = art["feature_medians"]
        feature_names = art["feature_names"]
        coef_df = art["coef_df"]
        feature_means = art["feature_means"]
        feature_scales = art["feature_scales"]
        winner = art["winner"]

        print(f"\n  h={h}: winner model = {winner}")

        # Keep the Oct 2026 origin even though its future target is unobserved.
        feat = build_features(panel, oni, dim, h, keep_unobserved_targets=True)
        feat["origin_month"] = pd.to_datetime(feat["origin_month"])
        feat["target_month"] = pd.to_datetime(feat["target_month"])

        # The forecast row: origin = FORECAST_ORIGIN (Oct 2026)
        forecast_rows = feat[feat["origin_month"] == FORECAST_ORIGIN].copy()

        if len(forecast_rows) != 154:
            raise ValueError(f"Expected 154 forecast counties for h={h}, got {len(forecast_rows)}")

        for scenario, oni_val in SCENARIO_ONI.items():
            sc_rows = forecast_rows.copy()

            # Override ONI features for scenario
            sc_rows["oni_now"] = oni_val
            sc_rows["oni_prev"] = oni_val  # persistence assumption
            sc_rows["delta_oni"] = 0.0
            sc_rows["enso_phase"] = _enso_phase(oni_val)
            sc_rows["enso_int"] = _enso_phase_to_int(_enso_phase(oni_val))

            areas = sc_rows["area_km2"].to_numpy(dtype=float)
            if (areas <= 0).any():
                raise ValueError("Forecast has a county with non-positive area")

            if winner in {"hgb", "glm"}:
                X_sc = sc_rows[feature_names].copy()
                if winner == "hgb":
                    pred_count = _hgb_predict(hgb, X_sc, areas)
                else:
                    pred_count = _glm_predict(glm, scaler, X_sc, areas, feature_medians)
                drivers_by_row = [
                    _get_top_drivers(
                        coef_df,
                        feature_means,
                        feature_scales,
                        feature_medians,
                        X_sc.iloc[i],
                        n=2,
                    ) if winner == "glm" else [None, None]
                    for i in range(len(sc_rows))
                ]
            else:
                if winner == "persistence":
                    pred_count = sc_rows["hotspot_count"].to_numpy(dtype=float)
                else:
                    scenario_feat = feat.copy()
                    scenario_mask = scenario_feat["origin_month"] == FORECAST_ORIGIN
                    scenario_feat.loc[scenario_mask, "enso_phase"] = _enso_phase(oni_val)
                    forecast_target = FORECAST_ORIGIN + pd.DateOffset(months=h)
                    clim_count, enso_clim_count = _climatology_predict(
                        scenario_feat,
                        scenario_feat["target_month"].min(),
                        FORECAST_ORIGIN,
                        forecast_target,
                        forecast_target,
                        enso_conditioned=True,
                    )
                    pred_count = (
                        enso_clim_count if winner == "enso_climatology" else clim_count
                    )
                drivers_by_row = [[None, None] for _ in range(len(sc_rows))]

            # Compute log_rate_per_100km2 for each kabupaten
            pred_rate_per100 = pred_count / areas * 100
            log_rate = np.log1p(pred_rate_per100)

            target_window = _target_window_label(h)

            for i, (_, row) in enumerate(sc_rows.iterrows()):
                drivers = drivers_by_row[i]
                all_pred_rows.append({
                    "kab_id": row["kab_id"],
                    "kab_name": row["kab_name"],
                    "prov_name": row["prov_name"],
                    "target_window": target_window,
                    "scenario": scenario,
                    "log_rate": float(log_rate[i]),
                    "pred_count": float(pred_count[i]),
                    "area_km2": float(row["area_km2"]),
                    "centroid_lat": float(row["centroid_lat"]),
                    "centroid_lon": float(row["centroid_lon"]),
                    "top_driver_1": drivers[0],
                    "top_driver_2": drivers[1],
                })

    # Use the same fixed 2015–2022 scale for every horizon and scenario.
    for r in all_pred_rows:
        r["risk_score"] = float(
            np.clip(r["log_rate"] / log_rate_max_train, 0.0, 1.0)
        )

    # --- Risk rank per (target_window, scenario) ---
    df_all = pd.DataFrame(all_pred_rows)
    df_all["risk_rank"] = (
        df_all.groupby(["target_window", "scenario"])["risk_score"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    # --- Risk class ---
    # Normalize raw historical thresholds using the same fixed training scale.
    norm_thresholds = [
        np.clip(t / log_rate_max_train, 0.0, 1.0)
        for t in log_rate_thresholds_raw
    ]
    df_all["risk_class"] = df_all["risk_score"].apply(
        lambda s: _apply_risk_class(s, norm_thresholds)
    )

    # --- Build latlon column ---
    df_all["latlon"] = (
        df_all["centroid_lat"].map("{:.6f}".format)
        + ","
        + df_all["centroid_lon"].map("{:.6f}".format)
    )

    # --- Select schema columns ---
    output_cols = [
        "kab_id", "kab_name", "prov_name",
        "target_window", "scenario",
        "risk_score", "risk_rank", "risk_class",
        "top_driver_1", "top_driver_2",
        "latlon",
    ]
    df_out = df_all[output_cols].copy()

    # --- Type coercion ---
    df_out["risk_score"] = df_out["risk_score"].astype(float)
    df_out["risk_rank"] = df_out["risk_rank"].astype(int)
    df_out["risk_class"] = df_out["risk_class"].astype(str)

    print(f"\nForecast shape: {df_out.shape}")
    print(df_out.head(5).to_string())
    print(f"\nRisk class distribution:\n{df_out['risk_class'].value_counts()}")
    print(f"\nScenario distribution:\n{df_out['scenario'].value_counts()}")
    print(f"\nTarget window distribution:\n{df_out['target_window'].value_counts()}")

    # --- Pandera validation ---
    print("\nValidating against schema...")
    try:
        validate_export("ml_risk_forecast", df_out)
        print("  Pandera validation passed.")
    except Exception as e:
        print(f"  Pandera validation FAILED: {e}")
        raise

    # --- Write output ---
    df_out.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved: {OUTPUT_PATH} ({len(df_out)} rows)")
    print("Forecast complete.")


if __name__ == "__main__":
    run_forecast()
