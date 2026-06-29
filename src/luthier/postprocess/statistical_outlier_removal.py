"""Statistical outlier removal via Open3D.

Stack slot: ``postprocess.outliers`` → ``algorithm: statistical_outlier_removal``
Implements :class:`~luthier.protocols.postprocess.PointCloudFilter`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import open3d as o3d

from luthier.models import Point3D, PointCloud

name = "statistical_outlier_removal"


def filter(
    point_cloud: PointCloud,
    *,
    params: Mapping[str, Any] | None = None,
    **_: Any,
) -> PointCloud:
    """Remove statistical outliers using Open3D's k-NN filter."""
    if point_cloud.count == 0:
        return point_cloud

    slot_params = params or {}
    nb_neighbors = int(slot_params.get("nb_neighbors", 20))
    std_ratio = float(slot_params.get("std_ratio", 2.0))
    if point_cloud.count <= nb_neighbors:
        return point_cloud

    coordinates = np.array(
        [(point.x, point.y, point.z) for point in point_cloud.points],
        dtype=np.float64,
    )
    colors = (
        np.array(
            [(point.r, point.g, point.b) for point in point_cloud.points],
            dtype=np.float64,
        )
        / 255.0
    )
    geometry = o3d.geometry.PointCloud()
    geometry.points = o3d.utility.Vector3dVector(coordinates)
    geometry.colors = o3d.utility.Vector3dVector(colors)
    _, inlier_indices = geometry.remove_statistical_outlier(
        nb_neighbors=nb_neighbors,
        std_ratio=std_ratio,
    )
    if not inlier_indices:
        return point_cloud

    filtered_points = tuple(point_cloud.points[index] for index in inlier_indices)
    return PointCloud(points=filtered_points)


__all__ = ["filter", "name"]
