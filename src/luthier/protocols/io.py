"""IO layer protocols."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class ImageDiscoverer(Protocol):
    """Discover image paths from a source directory."""

    name: str

    def discover(self, image_dir: Path) -> tuple[Path, ...]:
        """Return absolute paths to supported images."""


@runtime_checkable
class ImageDecoder(Protocol):
    """Decode a raster file into an array usable by downstream stages."""

    name: str

    def decode(self, path: Path) -> object:
        """Return decoded image (array type defined when ImageSet lands)."""
