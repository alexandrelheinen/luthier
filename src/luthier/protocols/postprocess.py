"""Post-processing layer protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from luthier.models import PointCloud


@runtime_checkable
class PointCloudFilter(Protocol):
    """Filter or refine a point cloud without re-running SfM."""

    name: str

    def filter(self, point_cloud: PointCloud) -> PointCloud:
        """Return a cleaned point cloud."""
