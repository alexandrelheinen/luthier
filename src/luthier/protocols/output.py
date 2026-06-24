"""Output layer protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from luthier.models import PointCloud


@runtime_checkable
class PointCloudSerializer(Protocol):
    """Serialize a domain point cloud to disk."""

    name: str

    def write(self, point_cloud: PointCloud, output_path: Path) -> None:
        """Write the point cloud to ``output_path``."""
