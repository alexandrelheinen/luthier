"""Tests for the reconstruction pipeline."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from luthier.exceptions import InvalidInputError
from luthier.pipeline import reconstruct_from_directory


def _write_overlapping_images(image_dir: Path, count: int) -> None:
    rng = np.random.default_rng(42)
    base = rng.integers(0, 256, (400, 600, 3), dtype=np.uint8)
    for index in range(count):
        shift = index * 20
        canvas = np.zeros_like(base)
        width = base.shape[1] - shift
        canvas[:, shift : shift + width] = base[:, :width]
        image_path = image_dir / f"img{index:02d}.png"
        bgr = cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)
        assert cv2.imwrite(str(image_path), bgr)


def test_reconstruct_requires_at_least_two_images(tmp_path: Path) -> None:
    """AC-REC-02."""
    image_dir = tmp_path / "photos"
    image_dir.mkdir()
    _write_overlapping_images(image_dir, count=1)
    with pytest.raises(InvalidInputError, match="At least 2 images"):
        reconstruct_from_directory(
            image_dir,
            output_path=tmp_path / "out.ply",
        )


def test_reconstruct_from_directory_writes_ply(tmp_path: Path) -> None:
    """Integration: discover → decode → SfM → PLY on synthetic overlapping views."""
    image_dir = tmp_path / "photos"
    image_dir.mkdir()
    _write_overlapping_images(image_dir, count=5)
    output_path = tmp_path / "scene.ply"

    result = reconstruct_from_directory(image_dir, output_path=output_path)

    assert result.output_path == output_path.resolve()
    assert result.output_path.is_file()
    assert result.point_cloud.count >= 1
    assert b"format binary_little_endian 1.0" in output_path.read_bytes()
