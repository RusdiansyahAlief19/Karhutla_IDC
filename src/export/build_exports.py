"""Build and validate the specified Looker-ready CSV exports."""

from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.export.schemas import validate_export
from src.model.features import build_oni_monthly

DIM_PATH = REPO_ROOT / "data/interim/dim_kabupaten_interim.csv"
MONTH_PATH = REPO_ROOT / "data/interim/fact_kab_month_interim.csv"
YEAR_PATH = REPO_ROOT / "data/interim/fact_kab_year_interim.csv"
ONI_PATH = REPO_ROOT / "data/raw/oni/oni.ascii.txt"
OUTPUT_DIR = REPO_ROOT / "data/processed"

PROVINCE_ISO: dict[str, str] = {
    "ACEH": "ID-AC",
    "SUMATERA UTARA": "ID-SU",
    "SUMATERA BARAT": "ID-SB",
    "RIAU": "ID-RI",
    "KEPULAUAN RIAU": "ID-KR",
    "JAMBI": "ID-JA",
    "SUMATERA SELATAN": "ID-SS",
    "BENGKULU": "ID-BE",
    "LAMPUNG": "ID-LA",
    "KEPULAUAN BANGKA BELITUNG": "ID-BB",
}


def _latlon(lat: pd.Series, lon: pd.Series) -> pd.Series:
    return lat.map("{:.6f}".format) + "," + lon.map("{:.6f}".format)


def _load_dimension() -> pd.DataFrame:
    dim = pd.read_csv(DIM_PATH)
    dim["iso_3166_2"] = dim["prov_name"].str.upper().map(PROVINCE_ISO)
    if dim["iso_3166_2"].isna().any():
        missing = sorted(dim.loc[dim["iso_3166_2"].isna(), "prov_name"].unique())
        raise ValueError(f"Province ISO mapping is missing: {missing}")
    dim["latlon"] = _latlon(dim["centroid_lat"], dim["centroid_lon"])
    dim["population_latest"] = np.nan
    dim["population_year"] = pd.Series(pd.NA, index=dim.index, dtype="Int64")
    columns = [
        "kab_id", "kab_name", "prov_id", "prov_name", "iso_3166_2",
        "centroid_lat", "centroid_lon", "latlon", "area_km2", "peat_share_pct",
        "population_latest", "population_year",
    ]
    return dim[columns]


def _build_fact_month(dim: pd.DataFrame, oni_path: pathlib.Path = ONI_PATH) -> pd.DataFrame:
    panel = pd.read_csv(MONTH_PATH)
    month = panel.drop(columns=["kab_name", "prov_name"]).merge(
        dim[["kab_id", "kab_name", "prov_name", "latlon", "peat_share_pct", "area_km2"]],
        on="kab_id",
        how="left",
        validate="many_to_one",
    )
    oni = build_oni_monthly(oni_path)
    oni["month"] = (
        oni["year"].astype(str) + "-" + oni["month"].astype(str).str.zfill(2) + "-01"
    )
    oni = oni[["month", "oni_anom"]].rename(columns={"oni_anom": "oni"})
    month = month.merge(oni, on="month", how="left", validate="many_to_one")
    month["hotspot_per_100km2"] = month["hotspot_count"] / month["area_km2"] * 100
    month["rain_mm"] = np.nan
    month["rain_anom_mm"] = np.nan
    month["rain_anom_pct"] = np.nan
    phase = np.select(
        [month["oni"].ge(0.5), month["oni"].le(-0.5)],
        ["el_nino", "la_nina"],
        default="netral",
    ).astype(object)
    phase[pd.isna(month["oni"]).to_numpy()] = None
    month["enso_phase"] = phase
    return month[
        [
            "month", "kab_id", "hotspot_count", "hotspot_high_conf",
            "hotspot_per_100km2", "frp_sum", "burn_days", "rain_mm",
            "rain_anom_mm", "rain_anom_pct", "oni", "enso_phase",
            "data_quality", "prov_name", "kab_name", "latlon", "peat_share_pct",
        ]
    ]


def _build_fact_year(dim: pd.DataFrame) -> pd.DataFrame:
    annual = pd.read_csv(YEAR_PATH)
    annual = annual.drop(columns=["kab_name", "prov_name"]).merge(
        dim[["kab_id", "kab_name", "prov_name", "latlon", "peat_share_pct"]],
        on="kab_id",
        how="left",
        validate="many_to_one",
    )
    annual["year"] = annual["year"].astype(int)
    return annual[
        [
            "year", "kab_id", "burned_ha_total", "burned_ha_peat",
            "burned_ha_mineral", "peat_burn_share_pct", "hotspot_count_year",
            "source", "notes", "prov_name", "kab_name", "latlon", "peat_share_pct",
        ]
    ]


def _build_province_summary(month: pd.DataFrame, annual: pd.DataFrame, dim: pd.DataFrame) -> pd.DataFrame:
    # Keep the annual summary within Trase's verified 2015–2024 coverage.
    monthly = month[month["month"].str[:4].between("2015", "2024")].copy()
    monthly["year"] = monthly["month"].str[:4].astype(int)
    hot = monthly.groupby(["year", "prov_name"], as_index=False)["hotspot_count"].sum()
    burned = annual.groupby(["year", "prov_name"], as_index=False).agg(
        burned_ha_total=("burned_ha_total", "sum"),
        burned_ha_peat=("burned_ha_peat", "sum"),
    )
    summary = hot.merge(burned, on=["year", "prov_name"], how="left", validate="one_to_one")
    sumatra_totals = summary.groupby("year")["hotspot_count"].transform("sum")
    summary["share_of_sumatra_hotspot_pct"] = summary["hotspot_count"] / sumatra_totals * 100
    summary["concentration_index"] = np.nan  # definition remains open in the data dictionary
    province_iso = dim[["prov_name", "iso_3166_2"]].drop_duplicates()
    summary = summary.merge(province_iso, on="prov_name", how="left", validate="many_to_one")
    return summary[
        [
            "year", "prov_name", "iso_3166_2", "hotspot_count", "burned_ha_total",
            "burned_ha_peat", "share_of_sumatra_hotspot_pct", "concentration_index",
        ]
    ]


def build_export_frames() -> dict[str, pd.DataFrame]:
    """Build each schema-defined export without writing files."""
    dim = _load_dimension()
    month = _build_fact_month(dim)
    annual = _build_fact_year(dim)
    province = _build_province_summary(month, annual, dim)
    return {
        "dim_kabupaten": dim,
        "fact_kab_month": month,
        "fact_kab_year": annual,
        "prov_summary_year": province,
    }


def write_exports() -> list[pathlib.Path]:
    """Validate every frame before writing any final CSV."""
    frames = build_export_frames()
    validated = {name: validate_export(name, frame) for name, frame in frames.items()}
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[pathlib.Path] = []
    for name, frame in validated.items():
        path = OUTPUT_DIR / f"{name}.csv"
        frame.to_csv(path, index=False)
        paths.append(path)
    return paths


def main() -> None:
    for path in write_exports():
        print(f"Validated and saved {path}")
    print("rain_mm/anomalies, peat_share_pct, and population are NaN: sources are not ingested")
    print("prov_summary_year.concentration_index is NaN: its formula is not approved")


if __name__ == "__main__":
    main()
