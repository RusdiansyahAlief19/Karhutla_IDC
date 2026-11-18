"""Build complete monthly hotspot and annual burned-area interim panels."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path

from src.ingest.rawstore import repo_root

START_MONTH = date(2015, 1, 1)
END_MONTH = date(2026, 10, 1)
MONTH_COLUMNS = ["month", "kab_id", "kab_name", "prov_name", "hotspot_count", "hotspot_high_conf", "frp_sum", "burn_days", "data_quality"]
YEAR_COLUMNS = ["year", "kab_id", "kab_name", "prov_name", "burned_ha_total", "burned_ha_peat", "burned_ha_mineral", "peat_burn_share_pct", "hotspot_count_year", "source", "notes"]


def months_between(start: date, end: date) -> list[str]:
    months: list[str] = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        months.append(f"{year:04d}-{month:02d}-01")
        month += 1
        if month == 13:
            month, year = 1, year + 1
    return months


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_panels(root: Path | None = None) -> tuple[Path, Path]:
    """Fill absent hotspot months with zero and keep annual Trase metrics annual."""
    base = root or repo_root()
    interim = base / "data" / "interim"
    hot_rows = _read_rows(interim / "hotspot_kab_month_joined.csv")
    crosswalk = _read_rows(interim / "trase_crosswalk_final.csv")
    county = {row["region_trase_id"]: row for row in crosswalk}
    if len(county) != 154 or len({r["boundary_shape_id"] for r in crosswalk}) != 154:
        raise ValueError("Final crosswalk must contain 154 unique Sumatra counties and shape IDs")

    observed: dict[tuple[str, str], dict[str, str]] = {}
    source_by_month: dict[str, str] = {}
    for row in hot_rows:
        key = (row["month"], row["kab_id"])
        if key in observed:
            raise ValueError(f"Duplicate month/county aggregate: {key}")
        if row["kab_id"] not in county:
            raise ValueError(f"Hotspot county absent from final crosswalk: {row['kab_id']}")
        observed[key] = row
        source_by_month[row["month"]] = row["data_quality"]

    all_months = months_between(START_MONTH, END_MONTH)
    month_path = interim / "fact_kab_month_interim.csv"
    with month_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MONTH_COLUMNS)
        writer.writeheader()
        for month in all_months:
            for kab_id, cross in sorted(county.items()):
                source = observed.get((month, kab_id))
                writer.writerow({
                    "month": month, "kab_id": kab_id, "kab_name": cross["trase_region"],
                    "prov_name": cross["parent_region"],
                    "hotspot_count": source["hotspot_count"] if source else 0,
                    "hotspot_high_conf": source["hotspot_high_conf"] if source else 0,
                    "frp_sum": source["frp_sum"] if source else "0.0000",
                    "burn_days": source["burn_days"] if source else 0,
                    "data_quality": source["data_quality"] if source else source_by_month.get(month, "NRT" if month >= "2026-08-01" else "SP"),
                })

    area_rows = _read_rows(base / "data/raw/trase/burned_area_kabupaten_20261104.csv")
    peat_rows = _read_rows(base / "data/raw/trase/burned_peat_kabupaten_20261104.csv")
    area = {(r["year"], r["region_trase_id"]): r for r in area_rows if r["region_trase_id"] in county}
    peat = {(r["year"], r["region_trase_id"]): r for r in peat_rows if r["region_trase_id"] in county}
    annual_keys = sorted(area)
    if set(annual_keys) != set(peat):
        raise ValueError("Trase burned-area and burned-peat keys do not reconcile")

    annual_hotspots: Counter[tuple[str, str]] = Counter()
    for row in hot_rows:
        year = row["month"][:4]
        annual_hotspots[(year, row["kab_id"])] += int(row["hotspot_count"])
    year_path = interim / "fact_kab_year_interim.csv"
    with year_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=YEAR_COLUMNS)
        writer.writeheader()
        for year, kab_id in annual_keys:
            a = float(area[(year, kab_id)]["burned_area_hectares"])
            p = float(peat[(year, kab_id)]["burned_peatlands_hectares"])
            if p > a + max(1e-6, a * 1e-9):
                raise ValueError(f"Burned peat exceeds total burned area for {year}/{kab_id}: {p}>{a}")
            cross = county[kab_id]
            writer.writerow({"year": year, "kab_id": kab_id, "kab_name": cross["trase_region"],
                "prov_name": cross["parent_region"], "burned_ha_total": f"{a:.8f}",
                "burned_ha_peat": f"{p:.8f}", "burned_ha_mineral": f"{max(0.0, a-p):.8f}",
                "peat_burn_share_pct": f"{(100*p/a) if a else 0.0:.8f}",
                "hotspot_count_year": annual_hotspots[(year, kab_id)],
                "source": "Trase/MapBiomas Fire Collection 2", "notes": "Trase metrics annual; available 2015-2024"})

    print(f"Monthly panel: {len(all_months)} months x {len(county)} counties -> {month_path}")
    print(f"Annual panel: {len(annual_keys)} county-years -> {year_path}")
    return month_path, year_path


def main() -> None:
    build_panels()


if __name__ == "__main__":
    main()
