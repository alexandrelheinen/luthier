"""Binary little-endian PLY serializer (placeholder).

Stack slot: ``output.serializer`` → ``algorithm: ply_binary_le``
Implements :class:`~luthier.protocols.output.PointCloudSerializer`.
"""

from __future__ import annotations

from pathlib import Path

from luthier.io.pointcloud import (
    DEFAULT_POINT_CLOUD_FORMAT,
    POINT_CLOUD_FORMAT_PLY,
    write_point_cloud,
)
from luthier.models import PointCloud

name = "ply_binary_le"


def write(point_cloud: PointCloud, output_path: Path) -> None:
    """Write binary PLY; delegates to ``write_point_cloud`` during transition."""
    write_point_cloud(
        point_cloud,
        output_path,
        file_format=DEFAULT_POINT_CLOUD_FORMAT,
    )


__all__ = [
    "DEFAULT_POINT_CLOUD_FORMAT",
    "POINT_CLOUD_FORMAT_PLY",
    "name",
    "write",
    "write_point_cloud",
]
