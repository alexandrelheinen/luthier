"""Tests for OpenCV image decode and ImageSet preparation."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from luthier.exceptions import InvalidInputError
from luthier.io.opencv_decode import decode
from luthier.io.prepare import prepare_image_set
from luthier.models import ImageSet


def _write_rgb_png(
    path: Path, width: int, height: int, rgb: tuple[int, int, int]
) -> None:
    array = np.zeros((height, width, 3), dtype=np.uint8)
    array[:, :] = rgb
    bgr = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
    assert cv2.imwrite(str(path), bgr)


def test_decode_returns_rgb_uint8_array(tmp_path: Path) -> None:
    image_path = tmp_path / "red.png"
    _write_rgb_png(image_path, width=3, height=2, rgb=(10, 20, 30))

    pixels = decode(image_path)

    assert pixels.shape == (2, 3, 3)
    assert pixels.dtype == np.uint8
    assert tuple(pixels[0, 0]) == (10, 20, 30)


def test_decode_raises_for_unreadable_file(tmp_path: Path) -> None:
    bad_path = tmp_path / "not-an-image.txt"
    bad_path.write_text("hello", encoding="utf-8")
    with pytest.raises(InvalidInputError, match="Could not decode"):
        decode(bad_path)


def test_prepare_image_set_builds_sorted_images(tmp_path: Path) -> None:
    _write_rgb_png(tmp_path / "b.png", width=4, height=3, rgb=(1, 2, 3))
    _write_rgb_png(tmp_path / "a.png", width=5, height=2, rgb=(4, 5, 6))

    image_set = prepare_image_set(tmp_path)

    assert isinstance(image_set, ImageSet)
    assert image_set.count == 2
    assert image_set.source_dir == tmp_path.resolve()
    assert [image.path.name for image in image_set.images] == ["a.png", "b.png"]
    assert image_set.images[0].id == 0
    assert image_set.images[1].id == 1
    assert image_set.images[0].width == 5
    assert image_set.images[0].height == 2
    assert image_set.images[0].pixels.shape == (2, 5, 3)


def test_prepare_image_set_raises_when_directory_empty(tmp_path: Path) -> None:
    with pytest.raises(InvalidInputError, match="No supported image files"):
        prepare_image_set(tmp_path)
