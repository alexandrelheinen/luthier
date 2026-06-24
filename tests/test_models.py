"""Tests for domain models."""

from __future__ import annotations

from pathlib import Path

import pytest

from luthier.models import LocalImageInput, Point3D, PointCloud


def test_point3d_defaults_to_neutral_gray() -> None:
    point = Point3D(x=1.0, y=2.0, z=3.0)
    assert point.r == 128
    assert point.g == 128
    assert point.b == 128


def test_point3d_rejects_invalid_color_channel() -> None:
    with pytest.raises(ValueError, match="Color channel"):
        Point3D(x=0.0, y=0.0, z=0.0, r=256)


def test_point_cloud_count() -> None:
    cloud = PointCloud(
        points=(
            Point3D(0.0, 0.0, 0.0),
            Point3D(1.0, 0.0, 0.0),
        )
    )
    assert cloud.count == 2


def test_local_image_input_requires_existing_directory(tmp_path: Path) -> None:
    image_dir = tmp_path / "photos"
    image_dir.mkdir()
    source = LocalImageInput(image_dir=image_dir)
    assert source.image_dir == image_dir


def test_local_image_input_rejects_missing_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        LocalImageInput(image_dir=tmp_path / "missing")


def test_local_image_input_rejects_file(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="not a directory"):
        LocalImageInput(image_dir=file_path)
