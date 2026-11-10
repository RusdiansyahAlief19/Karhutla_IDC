"""Shared exceptions for source downloads."""


class SourceUnavailable(RuntimeError):
    """The configured primary URL could not be read. Do not swap in another source."""

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(
            f"Sumber tidak bisa diunduh dan tidak diganti dengan URL lain.\nURL: {url}\nAlasan: {reason}"
        )


class RawConflict(RuntimeError):
    """A file already in data/raw has different bytes. Never overwrite raw."""

    def __init__(self, relative: str) -> None:
        self.relative = relative
        super().__init__(
            f"data/raw/{relative} sudah ada dengan checksum berbeda. Berkas mentah tidak ditimpa."
        )
