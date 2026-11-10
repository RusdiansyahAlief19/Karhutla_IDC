"""Pandera schemas for the Looker CSV contract in HANDOVER section 6.

``model_metrics`` and ``feature_importance`` are named in that section but their
columns are not listed. Those two schemas are intentionally absent.
"""

from __future__ import annotations

import pandas as pd
import pandera.pandas as pa

SUMATRA_ISO = [
    "ID-AC",
    "ID-SU",
    "ID-SB",
    "ID-RI",
    "ID-KR",
    "ID-JA",
    "ID-SS",
    "ID-BE",
    "ID-LA",
    "ID-BB",
]
SCENARIOS = ["netral", "el_nino", "la_nina"]
RISK_CLASSES = ["rendah", "sedang", "tinggi", "sangat_tinggi"]
DATA_QUALITY = ["SP", "NRT"]
LATLON = r"^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?$"
MONTH_START = r"^\d{4}-\d{2}-01$"

UNSPECIFIED_SCHEMAS = {
    "model_metrics": "Bagian 6 menyebut file ini tanpa daftar kolom.",
    "feature_importance": "Bagian 6 menyebut file ini tanpa daftar kolom.",
}


def _non_negative_int() -> pa.Column:
    return pa.Column(int, checks=pa.Check.ge(0), nullable=False)


def _share() -> pa.Column:
    return pa.Column(float, checks=pa.Check.in_range(0, 100), nullable=True)


dim_kabupaten = pa.DataFrameSchema(
    {
        "kab_id": pa.Column(str, nullable=False),
        "kab_name": pa.Column(str, nullable=False),
        "prov_id": pa.Column(str, nullable=False),
        "prov_name": pa.Column(str, nullable=False),
        "iso_3166_2": pa.Column(str, checks=pa.Check.isin(SUMATRA_ISO), nullable=False),
        "centroid_lat": pa.Column(float, checks=pa.Check.in_range(-90, 90), nullable=False),
        "centroid_lon": pa.Column(float, checks=pa.Check.in_range(-180, 180), nullable=False),
        "latlon": pa.Column(str, checks=pa.Check.str_matches(LATLON), nullable=False),
        "area_km2": pa.Column(float, checks=pa.Check.gt(0), nullable=False),
        "peat_share_pct": _share(),
        "population_latest": pa.Column(float, checks=pa.Check.ge(0), nullable=True),
        "population_year": pa.Column("Int64", nullable=True),
    },
    strict=True,
    coerce=True,
    unique=["kab_id"],
    name="dim_kabupaten",
)

fact_kab_month = pa.DataFrameSchema(
    {
        "month": pa.Column(str, checks=pa.Check.str_matches(MONTH_START), nullable=False),
        "kab_id": pa.Column(str, nullable=False),
        "hotspot_count": _non_negative_int(),
        "hotspot_high_conf": _non_negative_int(),
        "hotspot_per_100km2": pa.Column(float, checks=pa.Check.ge(0), nullable=False),
        "frp_sum": pa.Column(float, checks=pa.Check.ge(0), nullable=True),
        "burn_days": _non_negative_int(),
        "rain_mm": pa.Column(float, nullable=True),
        "rain_anom_mm": pa.Column(float, nullable=True),
        "rain_anom_pct": pa.Column(float, nullable=True),
        "oni": pa.Column(float, nullable=True),
        "enso_phase": pa.Column(str, nullable=True),
        "data_quality": pa.Column(str, checks=pa.Check.isin(DATA_QUALITY), nullable=False),
        "prov_name": pa.Column(str, nullable=False),
        "kab_name": pa.Column(str, nullable=False),
        "latlon": pa.Column(str, checks=pa.Check.str_matches(LATLON), nullable=False),
        "peat_share_pct": _share(),
    },
    strict=True,
    coerce=True,
    unique=["month", "kab_id"],
    name="fact_kab_month",
)

fact_kab_year = pa.DataFrameSchema(
    {
        "year": pa.Column(int, checks=pa.Check.in_range(2015, 2026), nullable=False),
        "kab_id": pa.Column(str, nullable=False),
        "burned_ha_total": pa.Column(float, checks=pa.Check.ge(0), nullable=True),
        "burned_ha_peat": pa.Column(float, checks=pa.Check.ge(0), nullable=True),
        "burned_ha_mineral": pa.Column(float, checks=pa.Check.ge(0), nullable=True),
        "peat_burn_share_pct": _share(),
        "hotspot_count_year": _non_negative_int(),
        "source": pa.Column(str, nullable=True),
        "notes": pa.Column(str, nullable=True),
        "prov_name": pa.Column(str, nullable=False),
        "kab_name": pa.Column(str, nullable=False),
        "latlon": pa.Column(str, checks=pa.Check.str_matches(LATLON), nullable=False),
        "peat_share_pct": _share(),
    },
    strict=True,
    coerce=True,
    unique=["year", "kab_id"],
    name="fact_kab_year",
)

prov_summary_year = pa.DataFrameSchema(
    {
        "year": pa.Column(int, checks=pa.Check.in_range(2015, 2026), nullable=False),
        "prov_name": pa.Column(str, nullable=False),
        "iso_3166_2": pa.Column(str, checks=pa.Check.isin(SUMATRA_ISO), nullable=False),
        "hotspot_count": _non_negative_int(),
        "burned_ha_total": pa.Column(float, checks=pa.Check.ge(0), nullable=True),
        "burned_ha_peat": pa.Column(float, checks=pa.Check.ge(0), nullable=True),
        "share_of_sumatra_hotspot_pct": _share(),
        "concentration_index": pa.Column(float, nullable=True),
    },
    strict=True,
    coerce=True,
    unique=["year", "prov_name"],
    name="prov_summary_year",
)

ml_risk_forecast = pa.DataFrameSchema(
    {
        "kab_id": pa.Column(str, nullable=False),
        "kab_name": pa.Column(str, nullable=False),
        "prov_name": pa.Column(str, nullable=False),
        "target_window": pa.Column(str, nullable=False),
        "scenario": pa.Column(str, checks=pa.Check.isin(SCENARIOS), nullable=False),
        "risk_score": pa.Column(float, checks=pa.Check.in_range(0, 1), nullable=False),
        "risk_rank": pa.Column(int, checks=pa.Check.ge(1), nullable=False),
        "risk_class": pa.Column(str, checks=pa.Check.isin(RISK_CLASSES), nullable=False),
        "top_driver_1": pa.Column(str, nullable=True),
        "top_driver_2": pa.Column(str, nullable=True),
        "latlon": pa.Column(str, checks=pa.Check.str_matches(LATLON), nullable=False),
    },
    strict=True,
    coerce=True,
    unique=["kab_id", "target_window", "scenario"],
    name="ml_risk_forecast",
)

SCHEMAS: dict[str, pa.DataFrameSchema] = {
    "dim_kabupaten": dim_kabupaten,
    "fact_kab_month": fact_kab_month,
    "fact_kab_year": fact_kab_year,
    "prov_summary_year": prov_summary_year,
    "ml_risk_forecast": ml_risk_forecast,
}


class SchemaNotSpecified(RuntimeError):
    """Raised when a named export has no column contract yet."""


def validate_export(name: str, frame: pd.DataFrame) -> pd.DataFrame:
    if name in UNSPECIFIED_SCHEMAS:
        raise SchemaNotSpecified(f"{name}: {UNSPECIFIED_SCHEMAS[name]}")
    schema = SCHEMAS[name]
    return schema.validate(frame)
