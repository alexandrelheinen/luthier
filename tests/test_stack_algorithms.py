"""Tests for stack.yml algorithm registration and option wiring."""

from __future__ import annotations

from pathlib import Path

import pycolmap
import pytest

from luthier.reconstruction.colmap import (
    apply_bundle_adjustment_options,
    apply_triangulation_options,
    build_feature_matching_options,
    build_incremental_options,
    build_pairing_options,
    build_verification_options,
)
from luthier.stack import SlotConfig, load_algorithms, load_stack_config, resolve
from luthier.stack.registry import registered_algorithms


@pytest.mark.parametrize(
    "algorithm",
    [
        "colmap_exhaustive_pairs",
        "colmap_exhaustive_match",
        "colmap_ransac",
        "colmap_incremental",
        "colmap_bundle_adjustment",
        "colmap_triangulation",
        "colmap_median_rgb",
    ],
)
def test_default_stack_reconstruction_algorithms_resolve(algorithm: str) -> None:
    load_algorithms()
    strategy = resolve("reconstruction", SlotConfig(algorithm=algorithm))
    assert strategy.name == algorithm


def test_default_stack_registers_all_reconstruction_algorithms() -> None:
    load_algorithms()
    config = load_stack_config(Path("config/stack.yml"))
    registered = registered_algorithms("reconstruction")
    for slot_name in (
        "pair_selection",
        "matcher",
        "verifier",
        "sfm",
        "bundle_adjustment",
        "triangulation",
        "coloring",
    ):
        algorithm = config.slot("reconstruction", slot_name).algorithm
        assert algorithm in registered


def test_build_pairing_options_reads_block_size() -> None:
    options = build_pairing_options({"block_size": 25})
    assert options.block_size == 25


def test_build_feature_matching_options_reads_sift_params() -> None:
    options = build_feature_matching_options(
        {"max_ratio": 0.7, "max_distance": 0.6, "cross_check": False}
    )
    assert options.sift.max_ratio == pytest.approx(0.7)
    assert options.sift.max_distance == pytest.approx(0.6)
    assert options.sift.cross_check is False


def test_build_verification_options_reads_ransac_params() -> None:
    options = build_verification_options({"max_error": 3.5, "min_inlier_ratio": 0.3})
    assert options.ransac.max_error == pytest.approx(3.5)
    assert options.min_inlier_ratio == pytest.approx(0.3)


def test_apply_bundle_adjustment_options_reads_refine_flags() -> None:
    options = pycolmap.IncrementalPipelineOptions()
    apply_bundle_adjustment_options(
        options,
        {
            "refine_focal_length": False,
            "refine_principal_point": True,
            "refine_extra_params": False,
        },
    )
    assert options.ba_refine_focal_length is False
    assert options.ba_refine_principal_point is True
    assert options.ba_refine_extra_params is False


def test_apply_triangulation_options_reads_min_angle() -> None:
    options = pycolmap.IncrementalPipelineOptions()
    apply_triangulation_options(options, {"min_tri_angle_deg": 2.0})
    assert options.triangulation.min_angle == pytest.approx(2.0)


def test_build_incremental_options_composes_sfm_bundle_and_triangulation() -> None:
    options = build_incremental_options(
        {"min_num_matches": 20},
        bundle_params={"refine_focal_length": False},
        triangulation_params={"min_tri_angle_deg": 1.5},
    )
    assert options.min_num_matches == 20
    assert options.ba_refine_focal_length is False
    assert options.triangulation.min_angle == pytest.approx(1.5)
