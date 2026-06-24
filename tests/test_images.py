"""Tests for image discovery (AC-IN-01, AC-IN-02)."""

from __future__ import annotations

from pathlib import Path

import pytest

from luthier.exceptions import InvalidInputError
from luthier.io.images import SUPPORTED_IMAGE_SUFFIXES, discover_images


def test_supported_suffixes_include_common_formats() -> None:
    assert ".jpg" in SUPPORTED_IMAGE_SUFFIXES
    assert ".png" in SUPPORTED_IMAGE_SUFFIXES


def test_discover_images_returns_sorted_paths(tmp_path: Path) -> None:
    """AC-IN-01."""
    (tmp_path / "b.jpg").write_bytes(b"\xff\xd8\xff")
    (tmp_path / "a.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (tmp_path / "ignore.txt").write_text("x", encoding="utf-8")
    subdir = tmp_path / "nested"
    subdir.mkdir()
    (subdir / "c.jpg").write_bytes(b"\xff\xd8\xff")

    images = discover_images(tmp_path)
    assert images == (
        tmp_path / "a.png",
        tmp_path / "b.jpg",
    )


def test_discover_images_is_case_insensitive(tmp_path: Path) -> None:
    """AC-IN-01."""
    (tmp_path / "Photo.JPG").write_bytes(b"\xff\xd8\xff")
    images = discover_images(tmp_path)
    assert len(images) == 1


def test_discover_images_raises_when_empty(tmp_path: Path) -> None:
    """AC-IN-02."""
    with pytest.raises(InvalidInputError, match="No supported image files"):
        discover_images(tmp_path)
