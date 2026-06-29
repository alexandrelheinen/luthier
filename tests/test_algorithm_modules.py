"""Smoke tests for algorithm modules (name + import)."""

from __future__ import annotations

import importlib

import pytest

ALGORITHM_MODULES = [
    ("luthier.io.opencv_decode", "opencv_decode"),
    ("luthier.features.colmap_sift", "colmap_sift"),
    ("luthier.reconstruction.colmap_incremental", "colmap_incremental"),
    ("luthier.postprocess.colmap_reprojection_filter", "colmap_reprojection_filter"),
    ("luthier.postprocess.statistical_outlier_removal", "statistical_outlier_removal"),
    ("luthier.output.ply_binary_le", "ply_binary_le"),
]


@pytest.mark.parametrize(("module_path", "expected_name"), ALGORITHM_MODULES)
def test_algorithm_module_name(module_path: str, expected_name: str) -> None:
    module = importlib.import_module(module_path)
    assert module.name == expected_name
