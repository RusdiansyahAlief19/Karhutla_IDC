"""src/model/evaluate.py — Metric computation for Karhutla risk model (S5).

All metrics treat hotspot COUNT as the prediction unit.
Hotspot count ≠ burned area (ha): never equated or summed with burned area.

Main entry point
----------------
compute_metrics(y_true, y_pred, y_pred_clim=None, *, epsilon=1e-3,
                df_month=None, month_col="target_month")
    -> dict of metric name to value

Also exports: poisson_deviance, skill_score, top_k_capture_rate
"""
from __future__ import annotations

import warnings
from typing import Optional

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

EPSILON_DEFAULT = 1e-3


# ---------------------------------------------------------------------------
# Core metrics
# ---------------------------------------------------------------------------

def poisson_deviance(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    epsilon: float = EPSILON_DEFAULT,
) -> float:
    """Mean Poisson deviance with epsilon clipping on predictions.

    Both y_true and y_pred are clipped to >= epsilon to avoid log(0).
    y_true is NOT clipped (observed zeros are valid; we clip only preds).
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.clip(np.asarray(y_pred, dtype=float), epsilon, None)
    # Clip true as well for the ratio term only
    y_true_clipped = np.clip(y_true, epsilon, None)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        dev = 2.0 * (
            y_true_clipped * np.log(y_true_clipped / y_pred) - (y_true_clipped - y_pred)
        )
    # Rows where y_true == 0: dev = 2 * (0 - (0 - y_pred)) = 2 * y_pred
    zero_mask = y_true == 0.0
    dev[zero_mask] = 2.0 * y_pred[zero_mask]
    return float(np.mean(dev))


def skill_score(
    dev_model: float,
    dev_clim: float,
) -> float:
    """Skill score = 1 - dev_model / dev_clim.  Range: (-inf, 1].
    Positive = model better than climatology; 0 = same; negative = worse.
    """
    if dev_clim == 0.0 or np.isnan(dev_clim):
        return float("nan")
    return 1.0 - dev_model / dev_clim


def top_k_capture_rate(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    k: int = 10,
) -> float:
    """Fraction of total hotspots captured by the top-k ranked kabupaten.

    y_true and y_pred must be 1-D arrays of the same kabupaten in the
    same month (or aggregated over all months in the eval set).
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if len(y_true) == 0:
        return float("nan")
    k = min(k, len(y_true))
    top_indices = np.argsort(y_pred)[::-1][:k]
    return float(y_true[top_indices].sum() / max(y_true.sum(), 1.0))


def mean_spearman_per_month(
    df: pd.DataFrame,
    y_true_col: str = "y_true",
    y_pred_col: str = "y_pred",
    month_col: str = "target_month",
) -> float:
    """Average Spearman ρ across months (must have >= 3 kabupaten per month)."""
    rhos = []
    for _, grp in df.groupby(month_col):
        if len(grp) < 3:
            continue
        rho, _ = spearmanr(grp[y_true_col], grp[y_pred_col])
        if not np.isnan(rho):
            rhos.append(rho)
    return float(np.mean(rhos)) if rhos else float("nan")


# ---------------------------------------------------------------------------
# Bootstrap significance test
# ---------------------------------------------------------------------------

def bootstrap_deviance_diff(
    y_true: np.ndarray,
    y_pred_model: np.ndarray,
    y_pred_clim: np.ndarray,
    n_bootstrap: int = 1000,
    block_size: int = 3,
    epsilon: float = EPSILON_DEFAULT,
    rng_seed: int = 42,
) -> dict:
    """Block-bootstrap significance test: model vs climatology deviance diff.

    Returns dict with keys: observed_diff, p_value, ci_lower, ci_upper.
    p_value: fraction of bootstrap samples where clim beats model (diff >= 0).
    """
    rng = np.random.default_rng(rng_seed)
    y_true = np.asarray(y_true, dtype=float)
    y_pred_model = np.asarray(y_pred_model, dtype=float)
    y_pred_clim = np.asarray(y_pred_clim, dtype=float)

    n = len(y_true)
    obs_dev_m = poisson_deviance(y_true, y_pred_model, epsilon)
    obs_dev_c = poisson_deviance(y_true, y_pred_clim, epsilon)
    observed_diff = obs_dev_m - obs_dev_c  # negative = model better

    # Block bootstrap on temporal axis
    n_blocks = int(np.ceil(n / block_size))
    boot_diffs = []
    for _ in range(n_bootstrap):
        idx = []
        for _ in range(n_blocks):
            start = rng.integers(0, max(1, n - block_size + 1))
            idx.extend(range(start, min(start + block_size, n)))
        idx = np.array(idx[:n])
        bd_m = poisson_deviance(y_true[idx], y_pred_model[idx], epsilon)
        bd_c = poisson_deviance(y_true[idx], y_pred_clim[idx], epsilon)
        boot_diffs.append(bd_m - bd_c)

    boot_diffs = np.array(boot_diffs)
    p_value = float(np.mean(boot_diffs >= 0.0))  # H0: model not better
    ci_lower = float(np.percentile(boot_diffs, 2.5))
    ci_upper = float(np.percentile(boot_diffs, 97.5))

    return {
        "observed_diff": float(observed_diff),
        "p_value": p_value,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "model_wins": observed_diff < 0.0,
    }


# ---------------------------------------------------------------------------
# Full metric bundle
# ---------------------------------------------------------------------------

def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_pred_clim: Optional[np.ndarray] = None,
    *,
    epsilon: float = EPSILON_DEFAULT,
    df_month: Optional[pd.DataFrame] = None,  # for spearman; must have month col
    month_col: str = "target_month",
    k_values: tuple[int, ...] = (10, 20),
) -> dict:
    """Compute full metric bundle for one (model, horizon, split) combination.

    Parameters
    ----------
    y_true  : observed hotspot counts (1-D array)
    y_pred  : predicted hotspot counts (1-D array)
    y_pred_clim : climatology predictions (for skill score); may be None
    epsilon : clipping for Poisson deviance
    df_month: DataFrame with y_true, y_pred, and target_month columns
              (used for per-month Spearman; skip if None)
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    dev = poisson_deviance(y_true, y_pred, epsilon)
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

    metrics: dict = {
        "poisson_deviance": dev,
        "mae": mae,
        "rmse": rmse,
        "n_samples": int(len(y_true)),
        "sum_true": float(y_true.sum()),
        "sum_pred": float(y_pred.sum()),
        "calibration_ratio": float(y_pred.sum() / max(y_true.sum(), 1.0)),
    }

    if y_pred_clim is not None:
        y_pred_clim = np.asarray(y_pred_clim, dtype=float)
        dev_clim = poisson_deviance(y_true, y_pred_clim, epsilon)
        metrics["dev_climatology"] = dev_clim
        metrics["skill_score"] = skill_score(dev, dev_clim)

    for k in k_values:
        metrics[f"top{k}_capture"] = top_k_capture_rate(y_true, y_pred, k)

    if df_month is not None and month_col in df_month.columns:
        df_m = df_month.copy()
        df_m["y_true"] = y_true
        df_m["y_pred"] = y_pred
        metrics["spearman_mean"] = mean_spearman_per_month(
            df_m, month_col=month_col
        )

    return metrics


# ---------------------------------------------------------------------------
# Epsilon sensitivity check
# ---------------------------------------------------------------------------

def epsilon_sensitivity(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    epsilons: tuple[float, ...] = (1e-4, 1e-3, 1e-2),
) -> dict[float, float]:
    """Return deviance for each epsilon value."""
    return {eps: poisson_deviance(y_true, y_pred, eps) for eps in epsilons}
