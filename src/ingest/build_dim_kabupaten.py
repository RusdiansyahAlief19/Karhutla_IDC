"""Build Sumatra county geometry dimensions from boundaries and final crosswalk.

Areas and centroids are computed in WGS84 / Equal Area Cylindrical (EPSG:6933).
Peatland area share remains missing because no county peatland-cover raster has
been ingested. Burned-peat share is a different annual outcome and is not used
as a substitute.
"""

from __future__ import annotations

import json
import math
import pathlib
import sys
from typing import Sequence

import pandas as pd

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

GEOJSON_PATH = REPO_ROOT / "data/raw/boundaries/idn_adm2.geojson"
CROSSWALK_PATH = REPO_ROOT / "data/interim/trase_crosswalk_final.csv"
OUTPUT_PATH = REPO_ROOT / "data/interim/dim_kabupaten_interim.csv"

# EPSG:6933 is the WGS84 ellipsoidal Lambert cylindrical equal-area projection
# with a 30 degree latitude of true scale and central meridian 0 degrees.
_WGS84_A_M = 6_378_137.0
_WGS84_F = 1 / 298.257223563
_WGS84_E2 = _WGS84_F * (2 - _WGS84_F)
_LAT_TS = math.radians(30.0)
_CEA_K0 = math.cos(_LAT_TS) / math.sqrt(1 - _WGS84_E2 * math.sin(_LAT_TS) ** 2)


def _authalic_q(sin_lat: float) -> float:
    """Return the ellipsoidal authalic latitude function used by EPSG:6933."""
    eccentricity = math.sqrt(_WGS84_E2)
    denominator = 1 - _WGS84_E2 * sin_lat**2
    logarithm = math.log((1 - eccentricity * sin_lat) / (1 + eccentricity * sin_lat))
    return (1 - _WGS84_E2) * (
        sin_lat / denominator - logarithm / (2 * eccentricity)
    )


def _project_equal_area(lon: float, lat: float) -> tuple[float, float]:
    """Project WGS84 longitude/latitude to EPSG:6933 easting/northing meters."""
    lon_rad = math.radians(lon)
    lat_rad = math.radians(lat)
    x = _WGS84_A_M * _CEA_K0 * lon_rad
    y = _WGS84_A_M * _authalic_q(math.sin(lat_rad)) / (2 * _CEA_K0)
    return x, y


def _inverse_equal_area(x: float, y: float) -> tuple[float, float]:
    """Return longitude/latitude degrees from EPSG:6933 coordinates."""
    q_target = 2 * _CEA_K0 * y / _WGS84_A_M
    q_pole = _authalic_q(1.0)
    q_target = min(q_pole, max(-q_pole, q_target))
    low, high = -math.pi / 2, math.pi / 2
    for _ in range(80):
        middle = (low + high) / 2
        if _authalic_q(math.sin(middle)) < q_target:
            low = middle
        else:
            high = middle
    lon = math.degrees(x / (_WGS84_A_M * _CEA_K0))
    lat = math.degrees((low + high) / 2)
    return lon, lat


def _ring_area_and_centroid(
    ring: Sequence[Sequence[float]],
) -> tuple[float, float, float]:
    """Return absolute area and centroid for a ring in projected meters."""
    if len(ring) < 4:
        raise ValueError("Polygon rings must contain at least four coordinates")
    signed_twice_area = 0.0
    cx_sum = 0.0
    cy_sum = 0.0
    for i, (x0, y0) in enumerate(ring):
        x1, y1 = ring[(i + 1) % len(ring)]
        cross = x0 * y1 - x1 * y0
        signed_twice_area += cross
        cx_sum += (x0 + x1) * cross
        cy_sum += (y0 + y1) * cross

    signed_area = signed_twice_area / 2
    if math.isclose(signed_area, 0.0, abs_tol=1e-8):
        raise ValueError("Polygon ring has zero area")
    centroid_x = cx_sum / (6 * signed_area)
    centroid_y = cy_sum / (6 * signed_area)
    return abs(signed_area), centroid_x, centroid_y


def geometry_stats(geom: dict) -> tuple[float, float, float]:
    """Return equal-area km² and geographic area centroid for a polygon."""
    geom_type = geom["type"]
    if geom_type == "Polygon":
        polygons = [geom["coordinates"]]
    elif geom_type == "MultiPolygon":
        polygons = geom["coordinates"]
    else:
        raise ValueError(f"Unsupported geometry type: {geom_type}")

    total_area_m2 = 0.0
    weighted_x = 0.0
    weighted_y = 0.0
    for polygon in polygons:
        if not polygon:
            continue
        exterior = [[*_project_equal_area(lon, lat)] for lon, lat, *_ in polygon[0]]
        outer_area, outer_x, outer_y = _ring_area_and_centroid(exterior)
        net_area = outer_area
        net_x = outer_area * outer_x
        net_y = outer_area * outer_y
        for hole in polygon[1:]:
            projected_hole = [[*_project_equal_area(lon, lat)] for lon, lat, *_ in hole]
            hole_area, hole_x, hole_y = _ring_area_and_centroid(projected_hole)
            net_area -= hole_area
            net_x -= hole_area * hole_x
            net_y -= hole_area * hole_y
        if net_area <= 0:
            raise ValueError("Polygon has no positive area after subtracting holes")
        total_area_m2 += net_area
        weighted_x += net_x
        weighted_y += net_y

    if total_area_m2 <= 0:
        raise ValueError("Geometry has no positive area")
    centroid_lon, centroid_lat = _inverse_equal_area(
        weighted_x / total_area_m2,
        weighted_y / total_area_m2,
    )
    return total_area_m2 / 1_000_000, centroid_lon, centroid_lat


def build_dim_kabupaten() -> pd.DataFrame:
    """Build one geometry dimension row per validated Sumatra crosswalk entry."""
    feature_collection = json.loads(GEOJSON_PATH.read_text(encoding="utf-8"))
    geometries = {
        feature["properties"]["shapeID"]: feature["geometry"]
        for feature in feature_collection["features"]
    }
    crosswalk = pd.read_csv(CROSSWALK_PATH, dtype=str)
    required = {
        "region_trase_id",
        "trase_region",
        "parent_region_trase_id",
        "parent_region",
        "boundary_shape_id",
    }
    missing = required - set(crosswalk.columns)
    if missing:
        raise ValueError(f"Final crosswalk lacks columns: {sorted(missing)}")
    if len(crosswalk) != 154 or crosswalk["region_trase_id"].nunique() != 154:
        raise ValueError("Final Sumatra crosswalk must contain 154 unique county IDs")
    if crosswalk["boundary_shape_id"].nunique() != 154:
        raise ValueError("Final Sumatra crosswalk must contain 154 unique shape IDs")

    rows: list[dict[str, object]] = []
    for row in crosswalk.itertuples(index=False):
        geom = geometries.get(row.boundary_shape_id)
        if geom is None:
            raise ValueError(f"No boundary geometry for {row.region_trase_id}")
        area_km2, centroid_lon, centroid_lat = geometry_stats(geom)
        rows.append(
            {
                "kab_id": row.region_trase_id,
                "kab_name": row.trase_region,
                "prov_id": row.parent_region_trase_id,
                "prov_name": row.parent_region,
                "centroid_lat": centroid_lat,
                "centroid_lon": centroid_lon,
                "area_km2": area_km2,
                "peat_share_pct": float("nan"),
            }
        )

    dim = pd.DataFrame(rows).sort_values("kab_id").reset_index(drop=True)
    if dim["area_km2"].isna().any() or (dim["area_km2"] <= 0).any():
        raise ValueError("County geometry is missing or has non-positive area")
    return dim


def main() -> None:
    dim = build_dim_kabupaten()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dim.to_csv(OUTPUT_PATH, index=False)
    print(f"Built {len(dim)} county dimensions -> {OUTPUT_PATH}")
    print("peat_share_pct is NaN: no county peatland-cover dataset is ingested")


if __name__ == "__main__":
    main()
