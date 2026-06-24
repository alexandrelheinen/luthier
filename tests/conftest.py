"""Shared pytest fixtures and constants."""

from __future__ import annotations

from pathlib import Path

import pytest

GOLDEN_IMAGES_DIR = Path(__file__).parent / "data" / "golden" / "images"


def golden_images_available() -> bool:
    """Return True when the golden acceptance image set is present."""
    if not GOLDEN_IMAGES_DIR.is_dir():
        return False
    return any(GOLDEN_IMAGES_DIR.iterdir())


requires_golden_images = pytest.mark.skipif(
    not golden_images_available(),
    reason="Golden images not found at tests/data/golden/images/",
)
