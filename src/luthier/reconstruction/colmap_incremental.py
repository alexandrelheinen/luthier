"""COLMAP incremental SfM backend (placeholder).

Stack slots: ``reconstruction.sfm``, matching, coloring sub-stages via pycolmap.
Implements :class:`~luthier.protocols.reconstruction.ReconstructionBackend`.
"""

from __future__ import annotations

name = "colmap_incremental"


def reconstruct(features: object, *, images: object) -> object:
    """FeatureSet + ImageSet in, ReconstructionScene out (M1)."""
    raise NotImplementedError("colmap_incremental is not implemented yet.")
