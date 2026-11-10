"""Write-once storage for data/raw, with a SHA-256 manifest."""

from __future__ import annotations

import hashlib
import urllib.error
import urllib.request
from pathlib import Path

from src.ingest.errors import RawConflict, SourceUnavailable

USER_AGENT = "karhutla-idc/0.1 (student competition; IDC Dateraquest 2.0)"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_bytes(url: str, timeout: float = 120) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            if status != 200:
                raise SourceUnavailable(url, f"HTTP {status}")
            return response.read()
    except SourceUnavailable:
        raise
    except urllib.error.HTTPError as exc:
        raise SourceUnavailable(url, f"HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise SourceUnavailable(url, str(exc.reason)) from exc
    except TimeoutError as exc:
        raise SourceUnavailable(url, "timeout") from exc


def manifest_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / "data" / "raw" / "SHA256SUMS"


def write_raw(relative: str, content: bytes, root: Path | None = None) -> Path:
    """Store bytes under data/raw. Identical re-downloads are a no-op. Conflicts stop."""
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"Path mentah tidak valid: {relative}")
    base = (root or repo_root()) / "data" / "raw"
    path = base / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = sha256_bytes(content)
    if path.exists():
        if sha256_file(path) != digest:
            raise RawConflict(rel.as_posix())
        return path
    path.write_bytes(content)
    _record_checksum(base / "SHA256SUMS", rel.as_posix(), digest)
    return path


def _record_checksum(manifest: Path, relative: str, digest: str) -> None:
    line = f"{digest}  {relative}\n"
    existing = manifest.read_text(encoding="utf-8") if manifest.exists() else ""
    kept = [row for row in existing.splitlines() if row.strip() and not row.endswith(f"  {relative}")]
    kept.append(line.rstrip("\n"))
    manifest.write_text("\n".join(kept) + "\n", encoding="utf-8")
