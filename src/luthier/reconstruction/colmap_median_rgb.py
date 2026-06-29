"""COLMAP median RGB point coloring.

Stack slot: ``reconstruction.coloring`` → ``algorithm: colmap_median_rgb``

M1 delegates coloring to pycolmap during incremental mapping; this strategy
documents the contract and passes the scene through unchanged.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from luthier.models import ImageSet, ReconstructionScene

name = "colmap_median_rgb"


def apply(
    scene: ReconstructionScene,
    *,
    images: ImageSet,
    params: Mapping[str, Any] | None = None,
) -> ReconstructionScene:
    """Return ``scene``; COLMAP already attached per-point RGB in M1."""
    _ = images
    _ = params
    return scene


__all__ = ["apply", "name"]
