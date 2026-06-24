"""Image discovery and validation for local directory input."""

from __future__ import annotations

from pathlib import Path

from luthier.exceptions import InvalidInputError

SUPPORTED_IMAGE_SUFFIXES: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
)


def discover_images(image_dir: Path) -> tuple[Path, ...]:
    """Return sorted image paths found directly inside ``image_dir``.

    Only files with supported suffixes are included. Subdirectories are ignored.

    Raises:
        InvalidInputError: If the directory contains no supported images.
    """
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
