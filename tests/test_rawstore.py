from __future__ import annotations

from pathlib import Path

import pytest

from src.ingest.errors import RawConflict, SourceUnavailable
from src.ingest.rawstore import download_bytes, sha256_bytes, write_raw


def test_write_raw_records_checksum_and_refuses_overwrite(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    first = write_raw("oni/oni.ascii.txt", b"SEAS YEAR TOTAL\n", root=tmp_path)
    assert first.read_bytes() == b"SEAS YEAR TOTAL\n"
    manifest = (raw / "SHA256SUMS").read_text(encoding="utf-8")
    assert sha256_bytes(b"SEAS YEAR TOTAL\n") in manifest
    again = write_raw("oni/oni.ascii.txt", b"SEAS YEAR TOTAL\n", root=tmp_path)
    assert again == first
    with pytest.raises(RawConflict):
        write_raw("oni/oni.ascii.txt", b"different\n", root=tmp_path)
    assert first.read_bytes() == b"SEAS YEAR TOTAL\n"


def test_write_raw_rejects_parent_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        write_raw("../secrets.txt", b"nope", root=tmp_path)


def test_download_bytes_reports_the_requested_url(monkeypatch: pytest.MonkeyPatch) -> None:
    import urllib.error

    def explode(request, timeout=0):  # noqa: ANN001
        raise urllib.error.URLError("blocked")

    monkeypatch.setattr("src.ingest.rawstore.urllib.request.urlopen", explode)
    with pytest.raises(SourceUnavailable) as caught:
        download_bytes("https://example.test/oni.ascii.txt")
    assert caught.value.url == "https://example.test/oni.ascii.txt"
    assert "blocked" in caught.value.reason
