"""COLMAP incremental SfM backend.

Stack slots: ``reconstruction.sfm`` and related sub-stages via pycolmap.
Implements :class:`~luthier.protocols.reconstruction.ReconstructionBackend`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from luthier.models import FeatureSet, ImageSet, ReconstructionScene
from luthier.reconstruction.colmap import (
    match_features,
    run_incremental_sfm,
    scene_from_reconstruction,
)
from luthier.stack.config import StackConfig

name = "colmap_incremental"


def reconstruct(
    features: FeatureSet,
    *,
    images: ImageSet,
    params: Mapping[str, Any] | None = None,
    stack: StackConfig | None = None,
) -> ReconstructionScene:
    """Run matching and incremental SfM on a COLMAP feature database."""
    matcher_params = _slot_params(stack, "matcher")
    pair_params = _slot_params(stack, "pair_selection")
    match_features(
        features.database_path,
        matcher_params=matcher_params,
        pair_params=pair_params,
    )
    sparse_dir = features.workspace_dir / "sparse"
    reconstruction = run_incremental_sfm(
        features.database_path,
        images,
        sparse_dir,
        params=params,
    )
    return scene_from_reconstruction(reconstruction)


def _slot_params(stack: StackConfig | None, slot: str) -> Mapping[str, Any]:
    if stack is None:
        return {}
    return dict(stack.slot("reconstruction", slot).params)


__all__ = ["name", "reconstruct"]
