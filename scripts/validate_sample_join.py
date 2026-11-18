"""Reproducible one-month linkage check for FIRMS and annual Trase data."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterator

SUMATRA_PROVINCES = frozenset(
    {
        "ACEH",
        "BENGKULU",
        "JAMBI",
        "KEPULAUAN BANGKA BELITUNG",
        "KEPULAUAN RIAU",
        "LAMPUNG",
        "RIAU",
        "SUMATERA BARAT",
        "SUMATERA SELATAN",
        "SUMATERA UTARA",
    }
)


@dataclass(frozen=True)
class CountyBoundary:
    shape_id: str
    region_id: str
    region_name: str
    province: str
    bounds: tuple[float, float, float, float]
    polygons: list[list[list[list[float]]]]


def iter_positions(value: Any) -> Iterator[list[float]]:
    if (
        isinstance(value, list)
        and len(value) >= 2
        and isinstance(value[0], (int, float))
        and isinstance(value[1], (int, float))
    ):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_positions(item)


def point_in_ring(longitude: float, latitude: float, ring: list[list[float]]) -> tuple[bool, bool]:
    inside = False
    for index, first in enumerate(ring):
        second = ring[(index + 1) % len(ring)]
        x1, y1 = first[0], first[1]
        x2, y2 = second[0], second[1]
        cross = (longitude - x1) * (y2 - y1) - (latitude - y1) * (x2 - x1)
        if (
            abs(cross) <= 1e-10
            and min(x1, x2) - 1e-10 <= longitude <= max(x1, x2) + 1e-10
            and min(y1, y2) - 1e-10 <= latitude <= max(y1, y2) + 1e-10
        ):
            return True, True
        if (y1 > latitude) != (y2 > latitude):
            crossing_x = x1 + (latitude - y1) * (x2 - x1) / (y2 - y1)
            if longitude < crossing_x:
                inside = not inside
    return inside, False


def point_in_polygon(longitude: float, latitude: float, polygon: list[list[list[float]]]) -> bool:
    outer_inside, outer_boundary = point_in_ring(longitude, latitude, polygon[0])
    if outer_boundary:
        return True
    if not outer_inside:
        return False
    for hole in polygon[1:]:
        hole_inside, hole_boundary = point_in_ring(longitude, latitude, hole)
        if hole_boundary:
            return True
        if hole_inside:
            return False
    return True


def read_crosswalk(path: Path, features: dict[str, dict[str, Any]]) -> list[CountyBoundary]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    boundaries: list[CountyBoundary] = []
    seen_region_ids: set[str] = set()
    seen_shape_ids: set[str] = set()
    for row in rows:
        region_id = row["region_trase_id"].strip()
        shape_id = row.get("boundary_shape_id", "").strip()
        if not shape_id:
            match = re.search(r"shapeID\s+([A-Za-z0-9]+)", row.get("review_decision", ""))
            shape_id = match.group(1) if match else ""
        if region_id in seen_region_ids or shape_id in seen_shape_ids:
            raise ValueError(f"Duplicate crosswalk ID: {region_id} / {shape_id}")
        if not shape_id or shape_id not in features:
            raise ValueError(f"No valid geoBoundaries shapeID for {region_id}: {shape_id}")
        if row["parent_region"] not in SUMATRA_PROVINCES:
            raise ValueError(f"Crosswalk row outside Sumatra: {row['parent_region']}")
        feature = features[shape_id]
        geometry = feature["geometry"]
        coordinates = geometry["coordinates"]
        polygons = coordinates if geometry["type"] == "MultiPolygon" else [coordinates]
        positions = list(iter_positions(coordinates))
        bounds = (
            min(position[0] for position in positions),
            min(position[1] for position in positions),
            max(position[0] for position in positions),
            max(position[1] for position in positions),
        )
        boundaries.append(
            CountyBoundary(
                shape_id=shape_id,
                region_id=region_id,
                region_name=row["trase_region"],
                province=row["parent_region"],
                bounds=bounds,
                polygons=polygons,
            )
        )
        seen_region_ids.add(region_id)
        seen_shape_ids.add(shape_id)
    provinces = {boundary.province for boundary in boundaries}
    if provinces != SUMATRA_PROVINCES:
        raise ValueError(f"Expected 10 Sumatra provinces, found {sorted(provinces)}")
    return boundaries


def find_county(longitude: float, latitude: float, boundaries: list[CountyBoundary]) -> list[CountyBoundary]:
    matches: list[CountyBoundary] = []
    for boundary in boundaries:
        west, south, east, north = boundary.bounds
        if west - 1e-10 <= longitude <= east + 1e-10 and south - 1e-10 <= latitude <= north + 1e-10:
            if any(point_in_polygon(longitude, latitude, polygon) for polygon in boundary.polygons):
                matches.append(boundary)
    return matches


def read_year_metrics(path: Path, year: str, region_ids: set[str], value_column: str) -> dict[str, tuple[str, str, float]]:
    values: dict[str, tuple[str, str, float]] = {}
    with path.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            if row["year"] != year or row["region_trase_id"] not in region_ids:
                continue
            region_id = row["region_trase_id"]
            if region_id in values:
                raise ValueError(f"Duplicate Trase row for {year} / {region_id}")
            values[region_id] = (row["region"], row["parent_region"], float(row[value_column]))
    if values.keys() != region_ids:
        raise ValueError(f"Trase {year} coverage differs from reviewed crosswalk")
    return values


def run_sample(root: Path, month: str) -> dict[str, Any]:
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        raise ValueError("Month must use YYYY-MM format")
    year = month[:4]
    raw = root / "data" / "raw"
    boundary_path = raw / "boundaries" / "idn_adm2.geojson"
    review_path = root / "data" / "interim" / "trase_crosswalk_review_farid_2026-11-14.csv"
    geojson = json.loads(boundary_path.read_text(encoding="utf-8"))
    features = {feature["properties"]["shapeID"]: feature for feature in geojson["features"]}
    boundaries = read_crosswalk(review_path, features)
    region_ids = {boundary.region_id for boundary in boundaries}
    area = read_year_metrics(
        raw / "trase" / "burned_area_kabupaten_20261104.csv",
        year,
        region_ids,
        "burned_area_hectares",
    )
    peat = read_year_metrics(
        raw / "trase" / "burned_peat_kabupaten_20261104.csv",
        year,
        region_ids,
        "burned_peatlands_hectares",
    )
    fires: Counter[str] = Counter()
    counts = Counter()
    firms_path = raw / "DL_FIRE_SV-C2_842268" / "fire_archive_SV-C2_842268.csv"
    with firms_path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if "type" not in (reader.fieldnames or []):
            raise ValueError("Archive is missing the FIRMS type field")
        for row in reader:
            if not row["acq_date"].startswith(month):
                continue
            counts["archive_rows_in_month"] += 1
            if row["satellite"] != "SNPP":
                counts["excluded_other_satellite"] += 1
                continue
            counts["snpp_viirs_rows"] += 1
            if row["confidence"].lower() not in {"n", "h"}:
                counts["excluded_low_or_unknown_confidence"] += 1
                continue
            counts["confidence_nominal_or_high"] += 1
            if row["type"] != "0":
                counts["excluded_non_vegetation_type"] += 1
                continue
            counts["presumed_vegetation_fire_rows"] += 1
            try:
                latitude = float(row["latitude"])
                longitude = float(row["longitude"])
            except (TypeError, ValueError):
                counts["dropped_invalid_coordinates"] += 1
                continue
            matches = find_county(longitude, latitude, boundaries)
            if len(matches) == 1:
                fires[matches[0].region_id] += 1
                counts["joined_to_one_sumatra_county"] += 1
            elif not matches:
                counts["dropped_no_sumatra_polygon"] += 1
            else:
                counts["dropped_ambiguous_multiple_polygons"] += 1
    candidates: list[dict[str, Any]] = []
    for boundary in boundaries:
        hotspot_count = fires[boundary.region_id]
        burned_area = area[boundary.region_id][2]
        burned_peat = peat[boundary.region_id][2]
        if hotspot_count > 0 and burned_area > 0 and burned_peat > 0:
            candidates.append(
                {
                    "region_trase_id": boundary.region_id,
                    "region": boundary.region_name,
                    "province": boundary.province,
                    "geoBoundaries_shape_id": boundary.shape_id,
                    "hotspot_detections_in_month": hotspot_count,
                    "trase_burned_area_hectares_yearly": burned_area,
                    "trase_burned_peatlands_hectares_yearly": burned_peat,
                }
            )
    candidates.sort(key=lambda item: (-item["hotspot_detections_in_month"], item["region_trase_id"]))
    return {
        "validation_run_date": date.today().isoformat(),
        "sample_month": month,
        "firms_file": "DL_FIRE_SV-C2_842268/fire_archive_SV-C2_842268.csv",
        "firms_filter": "VIIRS S-NPP; confidence nominal/high (n/h); type 0 presumed vegetation fire",
        "trase_year": year,
        "trase_granularity_note": "Trase burned area and burned peatlands are annual measures; they are not monthly values.",
        "crosswalk_counties": len(boundaries),
        "crosswalk_sumatra_provinces": len(SUMATRA_PROVINCES),
        "counts": dict(counts),
        "counties_with_hotspots_and_both_trase_metrics_positive": len(candidates),
        "example_county": candidates[0] if candidates else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", default="2024-10", help="Month to validate (YYYY-MM); must overlap Trase coverage")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root")
    args = parser.parse_args()
    report = run_sample(args.root, args.month)
    output = args.root / "data" / "interim" / f"spatial_join_validation_{args.month}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Report saved: {output}")


if __name__ == "__main__":
    main()
