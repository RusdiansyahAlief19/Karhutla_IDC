"""Download the NOAA CPC Oceanic Niño Index text file. One URL, no fallback."""

from __future__ import annotations

import sys

from src.ingest.errors import SourceUnavailable
from src.ingest.rawstore import download_bytes, sha256_file, write_raw

ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
ONI_RELATIVE = "oni/oni.ascii.txt"


def ingest_oni() -> str:
    content = download_bytes(ONI_URL)
    if not content.strip():
        raise SourceUnavailable(ONI_URL, "berkas kosong")
    path = write_raw(ONI_RELATIVE, content)
    digest = sha256_file(path)
    print(f"ONI tersimpan: {path}")
    print(f"SHA-256: {digest}")
    return digest


def main() -> None:
    try:
        ingest_oni()
    except SourceUnavailable as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
