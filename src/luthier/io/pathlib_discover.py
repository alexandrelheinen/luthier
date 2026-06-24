"""Pathlib-based image discovery (IO layer).

Stack slot: ``io.discover`` → ``algorithm: pathlib_discover``
Implements :class:`~luthier.protocols.io.ImageDiscoverer`.
"""

from __future__ import annotations

from pathlib import Path

from luthier.exceptions import InvalidInputError

SUPPORTED_IMAGE_SUFFIXES: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
)

name = "pathlib_discover"


def discover(image_dir: Path) -> tuple[Path, ...]:
    """Return sorted image paths found directly inside ``image_dir``."""
    images = tuple(
        sorted(
            path
            for path in image_dir.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES
        )
    )
    if not images:
        msg = (
            f"No supported image files found in {image_dir}. "
            f"Supported suffixes: {', '.join(sorted(SUPPORTED_IMAGE_SUFFIXES))}"
        )
        raise InvalidInputError(msg)
    return images


def discover_images(image_dir: Path) -> tuple[Path, ...]:
    """Backward-compatible alias used by the public API and tests."""
    return discover(image_dir)
