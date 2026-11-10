"""Download geoBoundaries Indonesia ADM2 via its official API metadata.

The geometry URL is taken only from the API field ``gjDownloadURL``.
If that field is missing, or either request fails, the script stops.
"""

from __future__ import annotations

import json
import sys

from src.ingest.errors import SourceUnavailable
from src.ingest.rawstore import download_bytes, sha256_file, write_raw

GEOBOUNDARIES_ADM2_API = "https://www.geoboundaries.org/api/current/gbOpen/IDN/ADM2/"
API_RELATIVE = "boundaries/gbOpen_IDN_ADM2.json"
GEOJSON_RELATIVE = "boundaries/idn_adm2.geojson"


def ingest_boundaries() -> str:
    payload = download_bytes(GEOBOUNDARIES_ADM2_API)
    try:
        meta = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SourceUnavailable(GEOBOUNDARIES_ADM2_API, "respons bukan JSON") from exc
    if not isinstance(meta, dict):
        raise SourceUnavailable(GEOBOUNDARIES_ADM2_API, "respons JSON bukan objek")
    geometry_url = meta.get("gjDownloadURL")
    if not isinstance(geometry_url, str) or not geometry_url.startswith("http"):
        keys = ", ".join(sorted(str(key) for key in meta))
        raise SourceUnavailable(
            GEOBOUNDARIES_ADM2_API,
            f"field gjDownloadURL tidak ada atau bukan URL. Field yang ada: {keys}",
        )
    write_raw(API_RELATIVE, payload)
    geometry = download_bytes(geometry_url, timeout=180)
    if not geometry.strip():
        raise SourceUnavailable(geometry_url, "berkas geometri kosong")
    path = write_raw(GEOJSON_RELATIVE, geometry)
    digest = sha256_file(path)
    print(f"Batas wilayah tersimpan: {path}")
    print(f"URL geometri dari API: {geometry_url}")
    print(f"SHA-256: {digest}")
    return digest


def main() -> None:
    try:
        ingest_boundaries()
    except SourceUnavailable as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
