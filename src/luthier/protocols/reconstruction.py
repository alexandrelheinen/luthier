"""Optimization / reconstruction layer protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ReconstructionBackend(Protocol):
    """Run matching, SfM, triangulation, and color propagation."""

    name: str

    def reconstruct(self, features: object, *, images: object) -> object:
        """FeatureSet + ImageSet in, ReconstructionScene out."""
