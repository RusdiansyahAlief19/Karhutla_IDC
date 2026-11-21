from __future__ import annotations

import pandas as pd

from src.model.features import build_features, build_oni_monthly
from src.model.train import _rolling_origin_folds


def test_oni_ndj_maps_to_december_of_its_year(tmp_path) -> None:
    source = tmp_path / "oni.txt"
    source.write_text(
        " SEAS  YR   TOTAL   ANOM\n  NDJ 2015  27.54   2.30\n",
        encoding="utf-8",
    )

    monthly = build_oni_monthly(source)

    assert monthly.to_dict("records") == [{"year": 2015, "month": 12, "oni_anom": 2.3}]


def test_features_include_completed_origin_month_and_keep_future_row() -> None:
    counties = [f"C{i}" for i in range(6)]
    months = pd.date_range("2025-01-01", periods=4, freq="MS")
    panel = pd.DataFrame(
        [
            {
                "month": month.strftime("%Y-%m-%d"),
                "kab_id": kab_id,
                "kab_name": kab_id,
                "prov_name": "RIAU",
                "hotspot_count": month_index * 10 + county_index,
            }
            for county_index, kab_id in enumerate(counties)
            for month_index, month in enumerate(months)
        ]
    )
    dim = pd.DataFrame(
        {
            "kab_id": counties,
            "centroid_lat": [0.0] * 6,
            "centroid_lon": [float(i) for i in range(6)],
            "area_km2": [100.0] * 6,
        }
    )
    oni = pd.DataFrame(
        {
            "year": [2025] * 4,
            "month": [1, 2, 3, 4],
            "oni_anom": [-0.2, 0.1, 0.3, 0.4],
        }
    )

    observed = build_features(panel, oni, dim, h=1)
    march_origin = observed[
        (observed["kab_id"] == "C0")
        & (observed["origin_month"] == pd.Timestamp("2025-03-01"))
    ].iloc[0]
    assert march_origin["hs_lag1"] == 20
    assert march_origin["hs_lag2"] == 10
    assert march_origin["target_count"] == 30

    with_future = build_features(panel, oni, dim, h=1, keep_unobserved_targets=True)
    april_origin = with_future[
        (with_future["kab_id"] == "C0")
        & (with_future["origin_month"] == pd.Timestamp("2025-04-01"))
    ].iloc[0]
    assert april_origin["hs_lag1"] == 30
    assert april_origin["target_month"] == pd.Timestamp("2025-05-01")
    assert pd.isna(april_origin["target_count"])


def test_rolling_folds_only_use_labels_available_at_validation_origin() -> None:
    months = pd.Series(pd.date_range("2015-01-01", "2022-12-01", freq="MS"))
    for horizon in (1, 2, 3):
        folds = _rolling_origin_folds(
            months,
            pd.Timestamp("2022-12-01"),
            horizon=horizon,
        )
        assert len(folds) >= 3
        for train_start, train_end, val_start in folds:
            assert train_start == months.min()
            assert train_end + pd.DateOffset(months=horizon) == val_start
            assert len(months[(months >= train_start) & (months <= train_end)]) >= 24
