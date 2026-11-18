"""Download the official Trase Indonesia burned-area kabupaten CSVs."""

from __future__ import annotations

import sys

from src.ingest.errors import SourceUnavailable
from src.ingest.rawstore import download_bytes, sha256_file, write_raw

TRASE_DOWNLOADS = {
    "burned_area_kabupaten_20261104.csv": (
        "https://resources.trase.earth/20261104/data/spatial-metrics/"
        "spatial-metrics-indonesia-burned_area_kabupaten.csv"
    ),
    "burned_peat_kabupaten_20261104.csv": (
        "https://resources.trase.earth/20261104/data/spatial-metrics/"
        "spatial-metrics-indonesia-burned_peat_kabupaten.csv"
    ),
}


def ingest_trase() -> list[tuple[str, str]]:
    """Store the two source CSVs without modifying their bytes."""
    results: list[tuple[str, str]] = []
    for filename, url in TRASE_DOWNLOADS.items():
        payload = download_bytes(url)
        if not payload:
            raise SourceUnavailable(url, "berkas kosong")
        path = write_raw(f"trase/{filename}", payload)
        digest = sha256_file(path)
        print(f"Trase tersimpan: {path} ({len(payload)} bytes)")
        print(f"SHA-256: {digest}")
        results.append((str(path), digest))
    return results


def main() -> None:
    try:
        ingest_trase()
    except SourceUnavailable as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
