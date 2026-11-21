"""Pytest suite validating spatial join, panel creation, and totals reconciliation."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

import pytest

from src.ingest.rawstore import repo_root
from src.transform.build_panel import END_MONTH, START_MONTH, months_between


@pytest.fixture(scope="session")
def root_dir() -> Path:
    return repo_root()


@pytest.fixture(scope="session")
def spatial_log(root_dir: Path) -> dict:
    log_path = root_dir / "data" / "interim" / "spatial_join_log.json"
    assert log_path.exists(), f"Log file missing: {log_path}"
    return json.loads(log_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def joined_rows(root_dir: Path) -> list[dict[str, str]]:
    joined_path = root_dir / "data" / "interim" / "hotspot_kab_month_joined.csv"
    assert joined_path.exists(), f"Joined file missing: {joined_path}"
    with joined_path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@pytest.fixture(scope="session")
def monthly_panel_rows(root_dir: Path) -> list[dict[str, str]]:
    panel_path = root_dir / "data" / "interim" / "fact_kab_month_interim.csv"
    assert panel_path.exists(), f"Monthly panel file missing: {panel_path}"
    with panel_path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@pytest.fixture(scope="session")
def annual_panel_rows(root_dir: Path) -> list[dict[str, str]]:
    panel_path = root_dir / "data" / "interim" / "fact_kab_year_interim.csv"
    assert panel_path.exists(), f"Annual panel file missing: {panel_path}"
    with panel_path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@pytest.fixture(scope="session")
def crosswalk_rows(root_dir: Path) -> list[dict[str, str]]:
    cw_path = root_dir / "data" / "interim" / "trase_crosswalk_final.csv"
    assert cw_path.exists(), f"Crosswalk missing: {cw_path}"
    with cw_path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_crosswalk_covers_154_sumatra_counties_across_10_provinces(
    crosswalk_rows: list[dict[str, str]],
) -> None:
    assert len(crosswalk_rows) == 154
    kab_ids = {r["region_trase_id"] for r in crosswalk_rows}
    assert len(kab_ids) == 154
    shape_ids = {r["boundary_shape_id"] for r in crosswalk_rows}
    assert len(shape_ids) == 154
    provinces = {r["parent_region"] for r in crosswalk_rows}
    assert len(provinces) == 10


def test_no_duplicate_month_kab_id_in_joined_and_panel(
    joined_rows: list[dict[str, str]],
    monthly_panel_rows: list[dict[str, str]],
) -> None:
    joined_keys = [(r["month"], r["kab_id"]) for r in joined_rows]
    assert len(joined_keys) == len(set(joined_keys)), "Duplicate (month, kab_id) in joined aggregates"

    panel_keys = [(r["month"], r["kab_id"]) for r in monthly_panel_rows]
    assert len(panel_keys) == len(set(panel_keys)), "Duplicate (month, kab_id) in monthly panel"


def test_full_month_coverage_in_monthly_panel(
    monthly_panel_rows: list[dict[str, str]],
    crosswalk_rows: list[dict[str, str]],
) -> None:
    expected_months = months_between(START_MONTH, END_MONTH)
    assert len(expected_months) == 142  # 2015-01 through 2026-10

    expected_kab_ids = {r["region_trase_id"] for r in crosswalk_rows}
    assert len(expected_kab_ids) == 154

    expected_total_rows = len(expected_months) * len(expected_kab_ids)
    assert len(monthly_panel_rows) == expected_total_rows

    months_in_panel = {r["month"] for r in monthly_panel_rows}
    assert months_in_panel == set(expected_months)

    kab_in_panel = {r["kab_id"] for r in monthly_panel_rows}
    assert kab_in_panel == expected_kab_ids

    # Every month has exactly 154 counties
    month_counts = Counter(r["month"] for r in monthly_panel_rows)
    for month, count in month_counts.items():
        assert count == 154, f"Month {month} has {count} rows instead of 154"


def test_spatial_join_totals_reconcile_with_raw_and_log(
    spatial_log: dict,
    joined_rows: list[dict[str, str]],
    monthly_panel_rows: list[dict[str, str]],
) -> None:
    counts = spatial_log["counts"]
    qualified = counts["qualifying_before_spatial_join"]
    joined = counts["joined_to_one_sumatra_county"]
    dropped = counts["dropped_no_sumatra_polygon"]
    multi = counts.get("dropped_ambiguous_multiple_polygons", 0)

    # Qualified points partition into joined, dropped outside polygon, and ambiguous
    assert qualified == joined + dropped + multi
    assert multi == 0

    # Total hotspots in joined CSV equals joined count in log
    sum_joined_hotspots = sum(int(r["hotspot_count"]) for r in joined_rows)
    assert sum_joined_hotspots == joined

    # Total hotspots in full monthly panel equals joined count
    sum_panel_hotspots = sum(int(r["hotspot_count"]) for r in monthly_panel_rows)
    assert sum_panel_hotspots == joined


def test_monthly_panel_matches_joined_raw_aggregates_by_county_month(
    joined_rows: list[dict[str, str]],
    monthly_panel_rows: list[dict[str, str]],
) -> None:
    joined = {
        (row["month"], row["kab_id"]): int(row["hotspot_count"])
        for row in joined_rows
    }
    panel = {
        (row["month"], row["kab_id"]): int(row["hotspot_count"])
        for row in monthly_panel_rows
    }
    assert set(joined).issubset(panel)
    assert all(panel[key] == count for key, count in joined.items())
    assert sum(panel.values()) == sum(joined.values())


def test_annual_panel_matches_sumatra_trase_raw_aggregates(
    root_dir: Path,
    annual_panel_rows: list[dict[str, str]],
    crosswalk_rows: list[dict[str, str]],
) -> None:
    import pandas as pd

    sumatra_ids = {row["region_trase_id"] for row in crosswalk_rows}
    panel = {
        (int(row["year"]), row["kab_id"]): row
        for row in annual_panel_rows
    }
    for filename, raw_column, panel_column in (
        ("burned_area_kabupaten_20261104.csv", "burned_area_hectares", "burned_ha_total"),
        ("burned_peat_kabupaten_20261104.csv", "burned_peatlands_hectares", "burned_ha_peat"),
    ):
        raw_path = root_dir / "data" / "raw" / "trase" / filename
        raw = pd.read_csv(raw_path)
        raw = raw[raw["region_trase_id"].isin(sumatra_ids)]
        aggregate = raw.groupby(["year", "region_trase_id"])[raw_column].sum()
        assert len(aggregate) == len(panel)
        for (year, kab_id), hectares in aggregate.items():
            assert abs(float(panel[(int(year), kab_id)][panel_column]) - float(hectares)) < 1e-5


def test_annual_panel_reconciles_with_monthly_panel_and_trase(
    annual_panel_rows: list[dict[str, str]],
    monthly_panel_rows: list[dict[str, str]],
) -> None:
    # Trase years 2015-2024 (10 years) x 154 counties = 1540 rows
    assert len(annual_panel_rows) == 1540

    annual_keys = [(r["year"], r["kab_id"]) for r in annual_panel_rows]
    assert len(annual_keys) == len(set(annual_keys)), "Duplicate (year, kab_id) in annual panel"

    # Compare annual hotspot sum with monthly hotspot sum for 2015-2024
    monthly_hotspots_by_year: Counter[str] = Counter()
    for r in monthly_panel_rows:
        year = r["month"][:4]
        if "2015" <= year <= "2024":
            monthly_hotspots_by_year[year] += int(r["hotspot_count"])

    annual_hotspots_by_year: Counter[str] = Counter()
    for r in annual_panel_rows:
        annual_hotspots_by_year[r["year"]] += int(r["hotspot_count_year"])

    for year in map(str, range(2015, 2025)):
        assert annual_hotspots_by_year[year] == monthly_hotspots_by_year[year], (
            f"Year {year} hotspot mismatch: annual={annual_hotspots_by_year[year]} vs monthly={monthly_hotspots_by_year[year]}"
        )

    # Validate burned area peat <= total and peat share pct
    for r in annual_panel_rows:
        total = float(r["burned_ha_total"])
        peat = float(r["burned_ha_peat"])
        mineral = float(r["burned_ha_mineral"])
        share = float(r["peat_burn_share_pct"])

        assert peat <= total + 1e-5, f"Peat burned > total for {r['year']}/{r['kab_id']}"
        assert abs((total - peat) - mineral) < 1e-5
        if total > 0:
            assert abs((100 * peat / total) - share) < 1e-4
        else:
            assert share == 0.0
