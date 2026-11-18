"""Spatially assign filtered FIRMS detections to Sumatra ADM2 polygons."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

# Ensure matplotlib does not warn about non-writable home dir in sandbox
os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())
import matplotlib.path as mpath
import numpy as np

from src.ingest.rawstore import repo_root

CUTOFF = date(2026, 10, 31)
CONFIDENCE = {"n", "h"}


@dataclass(frozen=True)
class CountyPolygon:
    region_id: str
    region_name: str
    prov_name: str
    shape_id: str
    bbox: tuple[float, float, float, float]
    poly_paths: list[tuple[mpath.Path, list[mpath.Path]]]


@dataclass
class MonthlyHotspot:
    month: str
    kab_id: str
    kab_name: str
    prov_name: str
    hotspot_count: int = 0
    hotspot_high_conf: int = 0
    frp_sum: float = 0.0
    burn_days: set[str] | None = None

    def add(self, confidence: str, frp: float, acq_date: str) -> None:
        self.hotspot_count += 1
        if confidence.lower() == "h":
            self.hotspot_high_conf += 1
        self.frp_sum += frp
        if self.burn_days is None:
            self.burn_days = set()
        self.burn_days.add(acq_date)


def inside_cutoff(acq_date: str) -> bool:
    try:
        return date.fromisoformat(acq_date) <= CUTOFF
    except ValueError:
        return False


def source_files(raw: Path) -> list[tuple[Path, str]]:
    return [
        (raw / "DL_FIRE_SV-C2_842268" / "fire_archive_SV-C2_842268.csv", "SP"),
        (raw / "DL_FIRE_SV-C2_842268" / "fire_nrt_SV-C2_842268.csv", "NRT"),
    ]


def load_county_polygons(geojson_path: Path, crosswalk_path: Path) -> list[CountyPolygon]:
    """Parse GeoJSON features for Sumatra counties listed in the crosswalk."""
    geojson = json.loads(geojson_path.read_text(encoding="utf-8"))
    features = {feat["properties"]["shapeID"]: feat for feat in geojson["features"]}

    with crosswalk_path.open(encoding="utf-8-sig", newline="") as source:
        crosswalk_rows = list(csv.DictReader(source))

    counties: list[CountyPolygon] = []
    for row in crosswalk_rows:
        shape_id = row["boundary_shape_id"].strip()
        feat = features[shape_id]
        geom = feat["geometry"]
        polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]

        poly_paths: list[tuple[mpath.Path, list[mpath.Path]]] = []
        all_coords: list[list[float]] = []
        for p in polys:
            outer = mpath.Path(p[0])
            holes = [mpath.Path(h) for h in p[1:]]
            poly_paths.append((outer, holes))
            for ring in p:
                all_coords.extend(ring)

        coords_arr = np.array(all_coords)
        west, south = coords_arr.min(axis=0)
        east, north = coords_arr.max(axis=0)

        counties.append(
            CountyPolygon(
                region_id=row["region_trase_id"].strip(),
                region_name=row["trase_region"].strip(),
                prov_name=row["parent_region"].strip(),
                shape_id=shape_id,
                bbox=(float(west), float(south), float(east), float(north)),
                poly_paths=poly_paths,
            )
        )
    return counties


def match_points_to_counties(
    coords: np.ndarray, counties: list[CountyPolygon]
) -> tuple[np.ndarray, np.ndarray]:
    """Perform vectorized spatial join of coordinates to county polygons.

    Returns:
        (match_counts, matched_county_indices)
        where match_counts is the number of polygons containing each point,
        and matched_county_indices points to the county index when match_counts == 1.
    """
    n_points = len(coords)
    match_counts = np.zeros(n_points, dtype=np.int32)
    matched_county = np.full(n_points, -1, dtype=np.int32)

    lons = coords[:, 0]
    lats = coords[:, 1]

    for c_idx, county in enumerate(counties):
        west, south, east, north = county.bbox
        cand_mask = (
            (lons >= west - 1e-10)
            & (lons <= east + 1e-10)
            & (lats >= south - 1e-10)
            & (lats <= north + 1e-10)
        )
        cand_indices = np.where(cand_mask)[0]
        if len(cand_indices) == 0:
            continue

        cand_pts = coords[cand_indices]
        in_county = np.zeros(len(cand_indices), dtype=bool)

        for outer, holes in county.poly_paths:
            in_poly = outer.contains_points(cand_pts)
            if holes:
                for hole in holes:
                    in_poly = in_poly & (~hole.contains_points(cand_pts))
            in_county = in_county | in_poly

        matched = cand_indices[in_county]
        match_counts[matched] += 1
        matched_county[matched] = c_idx

    return match_counts, matched_county


def run_spatial_join(root: Path | None = None) -> tuple[Path, Path]:
    """Aggregate qualifying detections by month/county and write audit counts."""
    base = root or repo_root()
    raw = base / "data" / "raw"
    boundaries_path = raw / "boundaries" / "idn_adm2.geojson"
    crosswalk_path = base / "data" / "interim" / "trase_crosswalk_final.csv"

    counties = load_county_polygons(boundaries_path, crosswalk_path)

    aggregates: dict[tuple[str, str], MonthlyHotspot] = {}
    qualities_by_month: dict[str, set[str]] = defaultdict(set)
    counts: Counter[str] = Counter()
    counts_by_source: dict[str, Counter[str]] = defaultdict(Counter)

    for path, quality in source_files(raw):
        if not path.exists():
            raise FileNotFoundError(f"FIRMS source missing: {path}")

        batch_rows: list[dict[str, str]] = []
        batch_coords: list[tuple[float, float]] = []

        with path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            fields = set(reader.fieldnames or [])
            required = {"latitude", "longitude", "acq_date", "satellite", "confidence", "frp"}
            missing = sorted(required - fields)
            if missing:
                raise ValueError(f"Missing FIRMS columns in {path.name}: {missing}")

            has_type = "type" in fields

            for row in reader:
                acq_date = row.get("acq_date", "")
                if not inside_cutoff(acq_date):
                    if acq_date[:7] == "2026-11":
                        counts["excluded_after_cutoff"] += 1
                        counts_by_source[quality]["excluded_after_cutoff"] += 1
                    continue

                counts["rows_in_period"] += 1
                counts_by_source[quality]["rows_in_period"] += 1

                if row["satellite"] != "SNPP":
                    counts["excluded_other_satellite"] += 1
                    counts_by_source[quality]["excluded_other_satellite"] += 1
                    continue

                if row["confidence"].lower() not in CONFIDENCE:
                    counts["excluded_low_or_unknown_confidence"] += 1
                    counts_by_source[quality]["excluded_low_or_unknown_confidence"] += 1
                    continue

                if has_type and row["type"] != "0":
                    counts["excluded_non_vegetation_type"] += 1
                    counts_by_source[quality]["excluded_non_vegetation_type"] += 1
                    continue

                counts["qualifying_before_spatial_join"] += 1
                counts_by_source[quality]["qualifying_before_spatial_join"] += 1

                try:
                    lat, lon = float(row["latitude"]), float(row["longitude"])
                    frp = float(row["frp"])
                    if not (-90 <= lat <= 90 and -180 <= lon <= 180 and frp >= 0):
                        raise ValueError
                except (TypeError, ValueError):
                    counts["dropped_invalid_coordinates_or_frp"] += 1
                    counts_by_source[quality]["dropped_invalid_coordinates_or_frp"] += 1
                    continue

                batch_rows.append(row)
                batch_coords.append((lon, lat))

        if not batch_coords:
            continue

        coords_array = np.array(batch_coords, dtype=np.float64)
        match_counts, matched_county = match_points_to_counties(coords_array, counties)

        for i, row in enumerate(batch_rows):
            n_match = match_counts[i]
            month = row["acq_date"][:7] + "-01"

            if n_match == 1:
                county = counties[matched_county[i]]
                key = (month, county.region_id)
                record = aggregates.get(key)
                if record is None:
                    record = MonthlyHotspot(
                        month=month,
                        kab_id=county.region_id,
                        kab_name=county.region_name,
                        prov_name=county.prov_name,
                    )
                    aggregates[key] = record

                record.add(
                    confidence=row["confidence"],
                    frp=float(row["frp"]),
                    acq_date=row["acq_date"],
                )
                qualities_by_month[month].add(quality)
                counts["joined_to_one_sumatra_county"] += 1
                counts_by_source[quality]["joined_to_one_sumatra_county"] += 1

            elif n_match == 0:
                counts["dropped_no_sumatra_polygon"] += 1
                counts_by_source[quality]["dropped_no_sumatra_polygon"] += 1

            else:
                counts["dropped_ambiguous_multiple_polygons"] += 1
                counts_by_source[quality]["dropped_ambiguous_multiple_polygons"] += 1

    output_dir = base / "data" / "interim"
    output_dir.mkdir(parents=True, exist_ok=True)
    panel_path = output_dir / "hotspot_kab_month_joined.csv"
    fields = [
        "month",
        "kab_id",
        "kab_name",
        "prov_name",
        "hotspot_count",
        "hotspot_high_conf",
        "frp_sum",
        "burn_days",
        "data_quality",
    ]

    with panel_path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        for key in sorted(aggregates):
            item = aggregates[key]
            writer.writerow(
                {
                    "month": item.month,
                    "kab_id": item.kab_id,
                    "kab_name": item.kab_name,
                    "prov_name": item.prov_name,
                    "hotspot_count": item.hotspot_count,
                    "hotspot_high_conf": item.hotspot_high_conf,
                    "frp_sum": f"{item.frp_sum:.4f}",
                    "burn_days": len(item.burn_days or set()),
                    "data_quality": "NRT" if "NRT" in qualities_by_month[item.month] else "SP",
                }
            )

    log_path = output_dir / "spatial_join_log.json"
    log = {
        "cutoff_inclusive": CUTOFF.isoformat(),
        "sensor": "VIIRS S-NPP 375 m",
        "confidence_filter": "n or h",
        "type_filter": "type=0 when present; NRT source lacks type",
        "crosswalk_counties": len(counties),
        "counts": dict(counts),
        "counts_by_source": {k: dict(v) for k, v in counts_by_source.items()},
        "monthly_aggregate_rows": len(aggregates),
        "sources": [p.name for p, _ in source_files(raw)],
    }
    log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    joined = counts["joined_to_one_sumatra_county"]
    dropped = counts["dropped_no_sumatra_polygon"] + counts["dropped_ambiguous_multiple_polygons"]
    print(f"Monthly county aggregates: {len(aggregates)} rows -> {panel_path}")
    print(f"Qualified={counts['qualifying_before_spatial_join']}; joined={joined}; dropped={dropped}")
    print(f"Audit log -> {log_path}")

    return panel_path, log_path


def main() -> None:
    run_spatial_join()


if __name__ == "__main__":
    main()
