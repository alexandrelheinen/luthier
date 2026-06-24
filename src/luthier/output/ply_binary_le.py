"""Binary little-endian PLY serializer.

Stack slot: ``output.serializer`` → ``algorithm: ply_binary_le``
Implements :class:`~luthier.protocols.output.PointCloudSerializer`.
"""

from __future__ import annotations

import struct
from pathlib import Path

from luthier.models import PointCloud

name = "ply_binary_le"

_VERTEX_STRUCT = struct.Struct("<fffBBB")
BYTES_PER_VERTEX = _VERTEX_STRUCT.size

_PLY_HEADER_LINES = (
    "ply",
    "format binary_little_endian 1.0",
    "element vertex {count}",
    "property float x",
    "property float y",
    "property float z",
    "property uchar red",
    "property uchar green",
    "property uchar blue",
    "end_header",
)


def _build_header(vertex_count: int) -> bytes:
    lines = [
        line.format(count=vertex_count) if "{count}" in line else line
        for line in _PLY_HEADER_LINES
    ]
    return ("\n".join(lines) + "\n").encode("ascii")


def _encode_vertices(point_cloud: PointCloud) -> bytes:
    return b"".join(
        _VERTEX_STRUCT.pack(point.x, point.y, point.z, point.r, point.g, point.b)
        for point in point_cloud.points
    )


def write(point_cloud: PointCloud, output_path: Path) -> None:
    """Write ``point_cloud`` as binary little-endian PLY to ``output_path``."""
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = _build_header(point_cloud.count) + _encode_vertices(point_cloud)
    output_path.write_bytes(payload)


__all__ = ["BYTES_PER_VERTEX", "name", "write"]
