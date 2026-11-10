from __future__ import annotations

import pandas as pd
import pytest

from src.export.schemas import SCHEMAS, UNSPECIFIED_SCHEMAS, SchemaNotSpecified, validate_export
from src.ingest.boundaries import GEOBOUNDARIES_ADM2_API
from src.ingest.oni import ONI_URL


def test_official_urls_are_the_handover_urls() -> None:
    assert ONI_URL == "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
    assert GEOBOUNDARIES_ADM2_API == "https://www.geoboundaries.org/api/current/gbOpen/IDN/ADM2/"


def test_named_exports_are_either_specified_or_explicitly_open() -> None:
    assert set(SCHEMAS) == {
        "dim_kabupaten",
        "fact_kab_month",
        "fact_kab_year",
        "prov_summary_year",
        "ml_risk_forecast",
    }
    assert set(UNSPECIFIED_SCHEMAS) == {"model_metrics", "feature_importance"}


def test_unspecified_schema_is_not_invented() -> None:
    with pytest.raises(SchemaNotSpecified):
        validate_export("model_metrics", pd.DataFrame({"mae": [1.0]}))


def test_fact_month_rejects_duplicate_keys() -> None:
    frame = pd.DataFrame(
        [
            _month_row("2019-08-01", "1401"),
            _month_row("2019-08-01", "1401"),
        ]
    )
    with pytest.raises(Exception):
        SCHEMAS["fact_kab_month"].validate(frame)


def test_fact_month_accepts_one_row_per_key() -> None:
    frame = pd.DataFrame([_month_row("2019-08-01", "1401")])
    validated = SCHEMAS["fact_kab_month"].validate(frame)
    assert len(validated) == 1


def _month_row(month: str, kab_id: str) -> dict[str, object]:
    return {
        "month": month,
        "kab_id": kab_id,
        "hotspot_count": 3,
        "hotspot_high_conf": 1,
        "hotspot_per_100km2": 0.4,
        "frp_sum": 12.5,
        "burn_days": 2,
        "rain_mm": 80.0,
        "rain_anom_mm": -20.0,
        "rain_anom_pct": -20.0,
        "oni": 0.5,
        "enso_phase": None,
        "data_quality": "SP",
        "prov_name": "Riau",
        "kab_name": "Contoh",
        "latlon": "0.50,101.45",
        "peat_share_pct": 40.0,
    }
