"""Statistical outlier removal (placeholder).

Stack slot: ``postprocess.outliers`` → ``algorithm: statistical_outlier_removal``
Implements :class:`~luthier.protocols.postprocess.PointCloudFilter`.
"""

from __future__ import annotations

from luthier.models import PointCloud

name = "statistical_outlier_removal"


def filter(point_cloud: PointCloud) -> PointCloud:
    """Return cloud with statistical outliers removed (not implemented until M1)."""
    raise NotImplementedError("statistical_outlier_removal is not implemented yet.")
