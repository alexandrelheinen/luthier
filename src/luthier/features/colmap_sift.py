"""COLMAP SIFT feature extraction (placeholder).

Stack slot: ``features.extractor`` → ``algorithm: colmap_sift``
Implements :class:`~luthier.protocols.features.FeatureExtractor`.
"""

from __future__ import annotations

name = "colmap_sift"


def extract(images: object) -> object:
    """ImageSet in, FeatureSet out (not implemented until M1)."""
    raise NotImplementedError("colmap_sift is not implemented yet.")
