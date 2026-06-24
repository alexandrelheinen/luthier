"""Shared pytest fixtures and golden dataset helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from luthier.exceptions import InvalidInputError
from luthier.io.images import discover_images

GOLDEN_IMAGES_DIR = Path(__file__).parent / "data" / "golden" / "images"
MIN_GOLDEN_IMAGES = 10


def golden_image_paths() -> tuple[Path, ...]:
    """Return discovered golden images, or an empty tuple if unavailable."""
    if not GOLDEN_IMAGES_DIR.is_dir():
        return ()
    try:
        return discover_images(GOLDEN_IMAGES_DIR)
    except InvalidInputError:
        return ()


def golden_images_available() -> bool:
    """True when at least ``MIN_GOLDEN_IMAGES`` supported images are present."""
    return len(golden_image_paths()) >= MIN_GOLDEN_IMAGES


requires_golden_images = pytest.mark.skipif(
    not golden_images_available(),
    reason=(
        "Golden images not found: need >= 10 supported images in "
        "tests/data/golden/images/ (run ./scripts/fetch_golden_colmap.sh)"
    ),
)
