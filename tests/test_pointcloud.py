"""Tests for point cloud serialization (AC-OUT-01, AC-OUT-02)."""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

from luthier.io.pointcloud import (
    DEFAULT_POINT_CLOUD_FORMAT,
    POINT_CLOUD_FORMAT_PLY,
    write_point_cloud,
)
from luthier.models import Point3D, PointCloud
from luthier.output.ply_binary_le import BYTES_PER_VERTEX

_VERTEX_STRUCT = struct.Struct("<fffBBB")


def _split_ply(data: bytes) -> tuple[str, bytes]:
    marker = b"end_header\n"
    index = data.index(marker)
    header_end = index + len(marker)
    return data[:header_end].decode("ascii"), data[header_end:]


def test_default_format_is_ply() -> None:
    assert DEFAULT_POINT_CLOUD_FORMAT == POINT_CLOUD_FORMAT_PLY


def test_write_point_cloud_rejects_unknown_format(tmp_path: Path) -> None:
    """AC-OUT-02."""
    cloud = PointCloud(points=(Point3D(0.0, 0.0, 0.0),))
    with pytest.raises(ValueError, match="Unsupported point cloud format"):
        write_point_cloud(cloud, tmp_path / "out.laz", file_format="laz")


def test_write_point_cloud_binary_ply_header(tmp_path: Path) -> None:
    """AC-OUT-01 — header encodes binary little-endian PLY 1.0 layout."""
    cloud = PointCloud(
        points=(
            Point3D(0.0, 0.0, 0.0, r=10, g=20, b=30),
            Point3D(1.0, 0.0, 0.0, r=40, g=50, b=60),
        )
    )
    output_path = write_point_cloud(cloud, tmp_path / "out.ply")
    assert output_path == (tmp_path / "out.ply").resolve()

    header, body = _split_ply(output_path.read_bytes())
    assert header.startswith("ply\n")
    assert "format binary_little_endian 1.0" in header
    assert "element vertex 2" in header
    for prop in (
        "property float x",
        "property float y",
        "property float z",
        "property uchar red",
        "property uchar green",
        "property uchar blue",
    ):
        assert prop in header
    assert header.endswith("end_header\n")
    assert len(body) == BYTES_PER_VERTEX * cloud.count


def test_write_point_cloud_binary_ply_vertex_bytes(tmp_path: Path) -> None:
    """AC-OUT-01 — body stores x,y,z as float32 and RGB as uchar."""
    cloud = PointCloud(
        points=(
            Point3D(1.5, -2.25, 3.75, r=1, g=2, b=3),
            Point3D(0.0, 0.0, 0.0, r=255, g=128, b=64),
        )
    )
    output_path = write_point_cloud(cloud, tmp_path / "scene.ply")
    _, body = _split_ply(output_path.read_bytes())

    decoded = [
        _VERTEX_STRUCT.unpack(body[offset : offset + BYTES_PER_VERTEX])
        for offset in range(0, len(body), BYTES_PER_VERTEX)
    ]
    x0, y0, z0, r0, g0, b0 = decoded[0]
    assert (x0, y0, z0) == pytest.approx((1.5, -2.25, 3.75), rel=0, abs=1e-6)
    assert (r0, g0, b0) == (1, 2, 3)

    x1, y1, z1, r1, g1, b1 = decoded[1]
    assert (x1, y1, z1) == pytest.approx((0.0, 0.0, 0.0), rel=0, abs=1e-6)
    assert (r1, g1, b1) == (255, 128, 64)


def test_write_point_cloud_uses_default_rgb(tmp_path: Path) -> None:
    cloud = PointCloud(points=(Point3D(0.0, 0.0, 0.0),))
    output_path = write_point_cloud(cloud, tmp_path / "defaults.ply")
    _, body = _split_ply(output_path.read_bytes())
    _, _, _, r, g, b = _VERTEX_STRUCT.unpack(body)
    assert (r, g, b) == (128, 128, 128)


def test_write_point_cloud_empty_cloud(tmp_path: Path) -> None:
    cloud = PointCloud()
    output_path = write_point_cloud(cloud, tmp_path / "empty.ply")
    header, body = _split_ply(output_path.read_bytes())
    assert "element vertex 0" in header
    assert body == b""


def test_write_point_cloud_creates_parent_directories(tmp_path: Path) -> None:
    cloud = PointCloud(points=(Point3D(0.0, 0.0, 0.0),))
    nested = tmp_path / "nested" / "dir" / "cloud.ply"
    write_point_cloud(cloud, nested)
    assert nested.is_file()
