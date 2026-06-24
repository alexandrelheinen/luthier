"""Tests for point cloud serialization (AC-OUT-01, AC-OUT-02)."""

from __future__ import annotations

from pathlib import Path

import pytest

from luthier.exceptions import NotImplementedPipelineError
from luthier.io.pointcloud import (
    DEFAULT_POINT_CLOUD_FORMAT,
    POINT_CLOUD_FORMAT_PLY,
    write_point_cloud,
)
from luthier.models import Point3D, PointCloud


def test_default_format_is_ply() -> None:
    assert DEFAULT_POINT_CLOUD_FORMAT == POINT_CLOUD_FORMAT_PLY


def test_write_point_cloud_rejects_unknown_format(tmp_path: Path) -> None:
    """AC-OUT-02."""
    cloud = PointCloud(points=(Point3D(0.0, 0.0, 0.0),))
    with pytest.raises(ValueError, match="Unsupported point cloud format"):
        write_point_cloud(cloud, tmp_path / "out.laz", file_format="laz")


@pytest.mark.not_implemented
def test_write_point_cloud_binary_ply_not_implemented(tmp_path: Path) -> None:
    """AC-OUT-01 — red phase until serialization is implemented."""
    cloud = PointCloud(
        points=(
            Point3D(0.0, 0.0, 0.0, r=10, g=20, b=30),
            Point3D(1.0, 0.0, 0.0, r=40, g=50, b=60),
        )
    )
    with pytest.raises(NotImplementedPipelineError):
        write_point_cloud(cloud, tmp_path / "out.ply")
