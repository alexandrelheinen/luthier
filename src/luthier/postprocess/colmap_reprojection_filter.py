"""COLMAP reprojection-error geometric filter.

Stack slot: ``postprocess.geometric_filter`` → ``algorithm: colmap_reprojection_filter``
Implements :class:`~luthier.protocols.postprocess.PointCloudFilter`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from luthier.models import PointCloud
from luthier.reconstruction.colmap import reconstruction_to_point_cloud

name = "colmap_reprojection_filter"


def filter(
    point_cloud: PointCloud,
    *,
    params: Mapping[str, Any] | None = None,
    reconstruction: Any = None,
) -> PointCloud:
    """Drop 3D points above the configured mean reprojection error."""
    if reconstruction is None:
        return point_cloud
    max_error = float((params or {}).get("max_reprojection_error", 4.0))
    return reconstruction_to_point_cloud(
        reconstruction,
        max_reprojection_error=max_error,
    )


__all__ = ["filter", "name"]
