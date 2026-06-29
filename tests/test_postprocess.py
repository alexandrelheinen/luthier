"""Tests for post-processing filters."""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest

from luthier.models import Point3D, PointCloud
from luthier.postprocess.colmap_reprojection_filter import filter as reprojection_filter
from luthier.postprocess.statistical_outlier_removal import (
    filter as statistical_outlier_filter,
)


def test_reprojection_filter_without_backend_returns_input() -> None:
    cloud = PointCloud(points=(Point3D(0.0, 0.0, 0.0),))
    assert reprojection_filter(cloud) is cloud


def test_reprojection_filter_uses_backend_and_params(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cloud = PointCloud(points=(Point3D(0.0, 0.0, 0.0),))
    reconstruction = MagicMock()
    filtered = PointCloud(points=(Point3D(1.0, 0.0, 0.0),))

    def fake_convert(
        _reconstruction: object,
        *,
        max_reprojection_error: float | None = None,
    ) -> PointCloud:
        assert max_reprojection_error == 2.5
        return filtered

    monkeypatch.setattr(
        "luthier.postprocess.colmap_reprojection_filter.reconstruction_to_point_cloud",
        fake_convert,
    )
    result = reprojection_filter(
        cloud,
        params={"max_reprojection_error": 2.5},
        reconstruction=reconstruction,
    )
    assert result is filtered


def test_statistical_outlier_filter_returns_small_clouds_unchanged() -> None:
    cloud = PointCloud(points=(Point3D(0.0, 0.0, 0.0), Point3D(1.0, 0.0, 0.0)))
    result = statistical_outlier_filter(cloud, params={"nb_neighbors": 20})
    assert result.count == cloud.count


def test_statistical_outlier_filter_removes_isolated_point() -> None:
    cluster = [
        Point3D(float(x), 0.0, 0.0) for x in np.linspace(0.0, 1.0, num=25)
    ]
    outlier = Point3D(100.0, 100.0, 100.0)
    cloud = PointCloud(points=(*cluster, outlier))

    filtered = statistical_outlier_filter(
        cloud,
        params={"nb_neighbors": 10, "std_ratio": 1.0},
    )

    assert filtered.count < cloud.count
    assert filtered.count >= 20
