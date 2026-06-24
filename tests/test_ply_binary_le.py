"""Tests for output algorithm module ``ply_binary_le``."""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

from luthier.models import Point3D, PointCloud
from luthier.output.ply_binary_le import BYTES_PER_VERTEX, name, write

_VERTEX_STRUCT = struct.Struct("<fffBBB")


def test_ply_binary_le_name() -> None:
    assert name == "ply_binary_le"


def test_ply_binary_le_write_produces_binary_ply(tmp_path: Path) -> None:
    cloud = PointCloud(
        points=(
            Point3D(0.0, 0.0, 0.0, r=10, g=20, b=30),
            Point3D(1.0, 2.0, 3.0, r=40, g=50, b=60),
        )
    )
    output_path = tmp_path / "out.ply"
    write(cloud, output_path)

    data = output_path.read_bytes()
    header_end = data.index(b"end_header\n") + len(b"end_header\n")
    header = data[:header_end].decode("ascii")
    body = data[header_end:]

    assert "format binary_little_endian 1.0" in header
    assert "element vertex 2" in header
    assert len(body) == BYTES_PER_VERTEX * 2

    x, y, z, r, g, b = _VERTEX_STRUCT.unpack(body[:BYTES_PER_VERTEX])
    assert (x, y, z) == (0.0, 0.0, 0.0)
    assert (r, g, b) == (10, 20, 30)


def test_ply_binary_le_write_resolves_tilde_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    cloud = PointCloud(points=(Point3D(1.0, 0.0, 0.0),))
    output_path = Path("~/resolved.ply")
    write(cloud, output_path)
    assert (tmp_path / "resolved.ply").is_file()
