"""Build a conservative Trase-to-geoBoundaries name review list."""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

from src.ingest.rawstore import repo_root

SUMATRA_PROVINCE_IDS = {
    "ID-11",  # Aceh
    "ID-12",  # Sumatera Utara
    "ID-13",  # Sumatera Barat
    "ID-14",  # Riau
    "ID-15",  # Jambi
    "ID-16",  # Sumatera Selatan
    "ID-17",  # Bengkulu
    "ID-18",  # Lampung
    "ID-19",  # Kepulauan Bangka Belitung
    "ID-21",  # Kepulauan Riau
}

TRASE_CSV = Path("data/raw/trase/burned_area_kabupaten_20261104.csv")
BOUNDARIES_GEOJSON = Path("data/raw/boundaries/idn_adm2.geojson")
OUTPUT_CSV = Path("data/interim/trase_crosswalk_review.csv")


def normalize_name(name: str) -> str:
    """Normalize case, Unicode composition, and repeated whitespace only."""
    normalized = unicodedata.normalize("NFKC", name).strip().casefold()
    return re.sub(r"\s+", " ", normalized)


def build_review_rows(root: Path | None = None) -> list[dict[str, str]]:
    """Return exact name matches and explicitly unresolved Sumatra names."""
    base = root or repo_root()
    with (base / BOUNDARIES_GEOJSON).open(encoding="utf-8") as handle:
        geojson = json.load(handle)
    boundary_by_name = {
        normalize_name(feature["properties"]["shapeName"]): feature["properties"]
        for feature in geojson["features"]
    }

    trase_path = base / TRASE_CSV
    with trase_path.open(encoding="utf-8-sig", newline="") as handle:
        records = list(csv.DictReader(handle))

    unique_regions = {
        (
            record["region_trase_id"],
            record["region"],
            record["parent_region_trase_id"],
            record["parent_region"],
        )
        for record in records
        if record["parent_region_trase_id"] in SUMATRA_PROVINCE_IDS
    }

    rows: list[dict[str, str]] = []
    for region_id, region, province_id, province in sorted(unique_regions):
        props = boundary_by_name.get(normalize_name(region))
        rows.append(
            {
                "region_trase_id": region_id,
                "trase_region": region,
                "parent_region_trase_id": province_id,
                "parent_region": province,
                "boundary_shape_name": str(props.get("shapeName", "")) if props else "",
                "boundary_shape_id": str(props.get("shapeID", "")) if props else "",
                "review_status": "exact_name_match" if props else "needs_manual_review",
                "review_decision": "",
            }
        )
    return rows


def write_review_csv(root: Path | None = None) -> Path:
    """Write the reproducible crosswalk review CSV under data/interim."""
    base = root or repo_root()
    rows = build_review_rows(base)
    output_path = base / OUTPUT_CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "region_trase_id",
        "trase_region",
        "parent_region_trase_id",
        "parent_region",
        "boundary_shape_name",
        "boundary_shape_id",
        "review_status",
        "review_decision",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    unresolved = sum(row["review_status"] == "needs_manual_review" for row in rows)
    print(f"Crosswalk awal: {len(rows)} kabupaten Sumatera")
    print(f"Perlu tinjauan manual: {unresolved}")
    print(f"Daftar tersimpan: {output_path}")
    return output_path


def main() -> None:
    write_review_csv()


if __name__ == "__main__":
    main()
