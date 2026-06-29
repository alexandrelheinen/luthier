"""COLMAP incremental SfM backend.

Stack slots: ``reconstruction.sfm`` and related sub-stages via pycolmap.
Implements :class:`~luthier.protocols.reconstruction.ReconstructionBackend`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from luthier.models import FeatureSet, ImageSet, ReconstructionScene
from luthier.reconstruction.colmap import (
    build_incremental_options,
    run_incremental_sfm,
    scene_from_reconstruction,
)
from luthier.stack.config import StackConfig
from luthier.stack.registry import resolve

name = "colmap_incremental"


def reconstruct(
    features: FeatureSet,
    *,
    images: ImageSet,
    params: Mapping[str, Any] | None = None,
    stack: StackConfig | None = None,
) -> ReconstructionScene:
    """Run matching and incremental SfM on a COLMAP feature database."""
    if stack is None:
        msg = "colmap_incremental requires a StackConfig to resolve sub-slots."
        raise ValueError(msg)

    pair_strategy = resolve(
        "reconstruction", stack.slot("reconstruction", "pair_selection")
    )
    matcher = resolve("reconstruction", stack.slot("reconstruction", "matcher"))
    verifier = resolve("reconstruction", stack.slot("reconstruction", "verifier"))
    bundle_adjustment = resolve(
        "reconstruction", stack.slot("reconstruction", "bundle_adjustment")
    )
    triangulation = resolve(
        "reconstruction", stack.slot("reconstruction", "triangulation")
    )
    coloring = resolve("reconstruction", stack.slot("reconstruction", "coloring"))

    pairing_options = pair_strategy.configure(
        dict(stack.slot("reconstruction", "pair_selection").params)
    )
    verification_options = verifier.configure(
        dict(stack.slot("reconstruction", "verifier").params)
    )
    matcher.match(
        features.database_path,
        pairing_options=pairing_options,
        verification_options=verification_options,
        params=dict(stack.slot("reconstruction", "matcher").params),
    )

    sparse_dir = features.workspace_dir / "sparse"
    pipeline_options = build_incremental_options(params or {})
    pipeline_options = bundle_adjustment.configure(
        pipeline_options,
        dict(stack.slot("reconstruction", "bundle_adjustment").params),
    )
    pipeline_options = triangulation.configure(
        pipeline_options,
        dict(stack.slot("reconstruction", "triangulation").params),
    )
    reconstruction = run_incremental_sfm(
        features.database_path,
        images,
        sparse_dir,
        options=pipeline_options,
    )
    scene = scene_from_reconstruction(reconstruction)
    colored: ReconstructionScene = coloring.apply(
        scene,
        images=images,
        params=dict(stack.slot("reconstruction", "coloring").params),
    )
    return colored


__all__ = ["name", "reconstruct"]
