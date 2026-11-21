"""Build leakage-safe monthly features for direct hotspot forecasts.

Origin month t is complete, so hotspot features include y_t and earlier
months. Targets are counts at t+h, for horizons one through three. CPC ONI is
a centered three-month index; center t-1 is the latest safe index at origin t.
"""
from __future__ import annotations

import pathlib
import sys
from typing import Optional

import warnings

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

warnings.filterwarnings(
    "ignore",
    message="DataFrameGroupBy.apply operated on the grouping columns",
    category=FutureWarning,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# ONI parsing
# ---------------------------------------------------------------------------

# Maps CPC overlapping seasons to their center month: DJF=Jan, ..., NDJ=Dec.
_SEAS_TO_MONTH = {
    "DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
    "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12,
}


def build_oni_monthly(oni_path: pathlib.Path | str) -> pd.DataFrame:
    """Parse ONI ascii file into monthly DataFrame.

    The NOAA CPC file has rows like: DJF 1950 25.01 -1.32. Each season/year
    pair maps to the season's center month in that year; NDJ Y maps to Dec Y.

    Returns DataFrame with columns: year (int), month (int 1-12), oni_anom (float).
    """
    rows = []
    with open(oni_path, "r") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) != 4:
                continue
            seas, yr, _, anom = parts
            seas = seas.strip()
            if seas not in _SEAS_TO_MONTH:
                continue
            try:
                year = int(yr)
                anom_val = float(anom)
            except ValueError:
                continue
            center_month = _SEAS_TO_MONTH[seas]
            rows.append({"year": year, "month": center_month, "oni_anom": anom_val})

    df = pd.DataFrame(rows)
    if df.duplicated(["year", "month"]).any():
        raise ValueError("NOAA ONI seasons produced duplicate center months")
    df = df.sort_values(["year", "month"]).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# ENSO phase helpers
# ---------------------------------------------------------------------------

def _enso_phase(oni: float) -> str:
    """Classify ONI anomaly into ENSO phase."""
    if pd.isna(oni):
        return "unknown"
    if oni >= 0.5:
        return "el_nino"
    elif oni <= -0.5:
        return "la_nina"
    else:
        return "netral"


# ---------------------------------------------------------------------------
# Main feature builder
# ---------------------------------------------------------------------------

def build_features(
    panel_df: pd.DataFrame,
    oni_df: pd.DataFrame,
    dim_df: pd.DataFrame,
    h: int,
    *,
    knn_k: int = 5,
    keep_unobserved_targets: bool = False,
) -> pd.DataFrame:
    """Build feature matrix for horizon h.

    Parameters
    ----------
    panel_df : monthly panel (fact_kab_month_interim.csv)
               must have columns: month (YYYY-MM-DD str), kab_id, kab_name,
               prov_name, hotspot_count
    oni_df   : output of build_oni_monthly()
    dim_df   : dim_kabupaten_interim.csv with centroid_lat, centroid_lon,
               area_km2
    h        : horizon 1, 2, or 3
    knn_k    : number of spatial neighbours (default 5)
    keep_unobserved_targets : retain forecast rows whose future targets are
               not available yet; only the projection step should set this

    Returns
    -------
    DataFrame indexed by (kab_id, target_month).  Every row contains:
      - All feature columns (prefixed accordingly)
      - 'target_count'  : hotspot_count at target month (t+h)
      - 'target_month'  : pd.Timestamp of target month
      - 'origin_month'  : pd.Timestamp of origin month (target_month - h months)
      - 'area_km2'      : from dim_df (for sample_weight)
      - 'rate'          : target_count / area_km2
      - 'log_rate'      : log1p(rate * 100)   [per 100 km²]
      - metadata columns: kab_name, prov_name, centroid_lat, centroid_lon
    """
    if h not in {1, 2, 3}:
        raise ValueError("Forecast horizon must be 1, 2, or 3 months")

    # ---- 0. Copy and parse dates ----
    df = panel_df.copy()
    df["month"] = pd.to_datetime(df["month"])
    df = df.sort_values(["kab_id", "month"]).reset_index(drop=True)

    # Merge dim
    dim_cols = ["kab_id", "centroid_lat", "centroid_lon", "area_km2"]
    df = df.merge(dim_df[dim_cols], on="kab_id", how="left")

    # ---- 1. Autoregressive features through the completed origin month t ----

    def _per_kab(g: pd.DataFrame) -> pd.DataFrame:
        g = g.sort_values("month").copy()
        hc = g["hotspot_count"].astype(float)

        # Lag names are relative to the target at h=1: lag1 is y_t.
        g["hs_lag1"] = hc
        g["hs_lag2"] = hc.shift(1)
        g["hs_lag3"] = hc.shift(2)

        g["hs_roll_mean3"] = hc.rolling(3, min_periods=1).mean()
        g["hs_roll_max3"] = hc.rolling(3, min_periods=1).max()

        # Seasonal memory
        g["hs_lag12"] = hc.shift(12)

        # Cumulative
        g["hs_cum6"] = hc.rolling(6, min_periods=1).sum()
        g["hs_cum12"] = hc.rolling(12, min_periods=1).sum()

        # Months since last hotspot (from shifted series)
        def _months_since(s: pd.Series) -> pd.Series:
            result = []
            last = np.nan
            for i, val in enumerate(s):
                if np.isnan(val) or val == 0:
                    if np.isnan(last):
                        result.append(np.nan)
                    else:
                        result.append(i - last)
                else:
                    last = i
                    result.append(0.0)
            return pd.Series(result, index=s.index)

        g["months_since_last"] = _months_since(hc)

        return g

    df = df.groupby("kab_id", group_keys=False).apply(_per_kab)

    # ---- 2. ONI features (lagged ≥1 from ORIGIN = lagged ≥h+1 from target) ----
    # oni_now  = ONI at t-1  (origin relative)
    # oni_prev = ONI at t-2
    # We merge ONI at the ORIGIN month level, then lag by 1 extra (oni at t-1)
    oni_m = oni_df[["year", "month", "oni_anom"]].copy()
    # Create a month timestamp for joining
    oni_m["month_ts"] = pd.to_datetime(
        oni_m["year"].astype(str) + "-" + oni_m["month"].astype(str).str.zfill(2) + "-01"
    )

    # Build a month→oni lookup
    oni_lookup = oni_m.set_index("month_ts")["oni_anom"].to_dict()

    def _get_oni(ts: pd.Timestamp, lag: int) -> float:
        target_ts = ts - pd.DateOffset(months=lag)
        # round to 1st of month
        key = pd.Timestamp(target_ts.year, target_ts.month, 1)
        return oni_lookup.get(key, np.nan)

    # Center t-1 is the latest safe CPC value because ONI is a centered
    # three-month running mean; its window ends at origin month t.
    df["oni_now"] = df["month"].apply(lambda ts: _get_oni(ts, 1))
    df["oni_prev"] = df["month"].apply(lambda ts: _get_oni(ts, 2))
    df["delta_oni"] = df["oni_now"] - df["oni_prev"]
    df["enso_phase"] = df["oni_now"].apply(_enso_phase)

    # ---- 3. Calendar features of TARGET month ----
    # target month = origin + h months (kalender bulan, tidak bocor)
    df["target_month_ts"] = df["month"] + pd.DateOffset(months=h)
    df["target_month_num"] = df["target_month_ts"].dt.month
    df["month_sin"] = np.sin(2 * np.pi * df["target_month_num"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["target_month_num"] / 12)

    # ---- 4. KNN spatial lag ----
    # Fit NearestNeighbors on (lat, lon) of all 154 kabupaten
    kab_coords = (
        dim_df[["kab_id", "centroid_lat", "centroid_lon"]]
        .drop_duplicates("kab_id")
        .set_index("kab_id")
    )
    coord_arr = kab_coords[["centroid_lat", "centroid_lon"]].values
    kab_ids_ordered = kab_coords.index.tolist()

    nbrs = NearestNeighbors(n_neighbors=knn_k + 1, algorithm="ball_tree",
                            metric="haversine")
    coord_rad = np.radians(coord_arr)
    nbrs.fit(coord_rad)
    _, indices = nbrs.kneighbors(coord_rad)
    # indices[i, 0] = self; indices[i, 1..k] = k nearest others
    neighbor_ids: dict[str, list[str]] = {}
    for i, kab_id in enumerate(kab_ids_ordered):
        neighbor_ids[kab_id] = [kab_ids_ordered[j] for j in indices[i, 1:knn_k + 1]]

    # For each origin month, compute the mean rate of neighboring counties.
    def _add_rate_lag(g: pd.DataFrame) -> pd.DataFrame:
        g = g.sort_values("month").copy()
        g["_rate_self"] = g["hotspot_count"] / g["area_km2"]
        return g

    df = df.groupby("kab_id", group_keys=False).apply(_add_rate_lag)

    # Build month → {kab_id: rate} lookup
    rate_pivot = df.pivot_table(
        index="month", columns="kab_id", values="_rate_self", aggfunc="first"
    )

    def _knn_lag(row: pd.Series) -> float:
        neighbors = neighbor_ids.get(row["kab_id"], [])
        if not neighbors:
            return np.nan
        vals = []
        for nb in neighbors:
            if nb in rate_pivot.columns:
                v = rate_pivot.at[row["month"], nb] if row["month"] in rate_pivot.index else np.nan
                if not np.isnan(v):
                    vals.append(v)
        return float(np.mean(vals)) if vals else np.nan

    df["knn_lag_rate"] = df.apply(_knn_lag, axis=1)

    # ---- 5. Province leave-one-county-out rate at the origin ----
    prov_totals = (
        df.groupby(["prov_name", "month"], as_index=False)
        .agg(prov_total=("hotspot_count", "sum"), prov_area=("area_km2", "sum"))
    )
    df = df.merge(prov_totals, on=["prov_name", "month"], how="left")
    df["prov_loo_count"] = df["prov_total"] - df["hotspot_count"]
    df["prov_loo_area"] = df["prov_area"] - df["area_km2"]
    df["prov_loo_rate"] = df["prov_loo_count"] / df["prov_loo_area"]
    df = df.drop(columns=["prov_total", "prov_loo_count", "prov_area", "prov_loo_area"])

    # ---- 6. Build target ----
    # target_count = hotspot_count at target_month_ts
    # We build a lookup: (kab_id, month) → hotspot_count
    hc_lookup = (
        panel_df.assign(month=pd.to_datetime(panel_df["month"]))
        .set_index(["kab_id", "month"])["hotspot_count"]
        .to_dict()
    )

    df["target_count"] = df.apply(
        lambda r: hc_lookup.get((r["kab_id"], r["target_month_ts"]), np.nan),
        axis=1,
    )
    df["rate"] = df["target_count"] / df["area_km2"]
    df["log_rate"] = np.log1p(df["rate"] * 100)

    # ---- 7. Rename and clean ----
    df = df.rename(columns={"month": "origin_month", "target_month_ts": "target_month"})

    # Drop internal helpers
    _drop_cols = ["_rate_self", "prov_total", "prov_loo_count", "prov_area", "prov_loo_area",
                  "hotspot_high_conf", "frp_sum", "burn_days", "data_quality",
                  "target_month_num"]
    df = df.drop(columns=[c for c in _drop_cols if c in df.columns])

    df = df.sort_values(["target_month", "kab_id"]).reset_index(drop=True)
    if not keep_unobserved_targets:
        df = df.dropna(subset=["target_count"]).reset_index(drop=True)

    return df


# ---------------------------------------------------------------------------
# Feature column lists
# ---------------------------------------------------------------------------

AUTOREGRESSIVE_COLS = [
    "hs_lag1", "hs_lag2", "hs_lag3",
    "hs_roll_mean3", "hs_roll_max3",
    "hs_lag12",
    "hs_cum6", "hs_cum12",
    "months_since_last",
]

ONI_COLS = ["oni_now", "oni_prev", "delta_oni"]

CALENDAR_COLS = ["month_sin", "month_cos"]

SPATIAL_COLS = ["knn_lag_rate", "prov_loo_rate"]

STATIC_COLS = ["centroid_lat", "centroid_lon"]

# enso_phase is categorical — handled separately in train.py.
ALL_NUMERIC_FEATURES = (
    AUTOREGRESSIVE_COLS
    + ["oni_now", "oni_prev", "delta_oni"]
    + CALENDAR_COLS
    + SPATIAL_COLS
    + STATIC_COLS
)

ENSO_PHASE_COL = "enso_phase"


if __name__ == "__main__":
    import pathlib

    ONI_PATH = REPO_ROOT / "data/raw/oni/oni.ascii.txt"
    PANEL_PATH = REPO_ROOT / "data/interim/fact_kab_month_interim.csv"
    DIM_PATH = REPO_ROOT / "data/interim/dim_kabupaten_interim.csv"

    panel = pd.read_csv(PANEL_PATH)
    oni = build_oni_monthly(ONI_PATH)
    dim = pd.read_csv(DIM_PATH)

    print(f"ONI shape: {oni.shape}, range {oni['year'].min()}–{oni['year'].max()}")
    print("Building features h=1 …")
    feat = build_features(panel, oni, dim, h=1)
    print(f"Feature matrix shape: {feat.shape}")
    print("Columns:", feat.columns.tolist())
    print(feat[["kab_id", "origin_month", "target_month", "target_count",
                "hs_lag1", "oni_now"]].head(10))
