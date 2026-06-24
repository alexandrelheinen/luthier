"""Feature extraction layer protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class FeatureExtractor(Protocol):
    """Extract keypoints and descriptors from a prepared image set."""

    name: str

    def extract(self, images: object) -> object:
        """ImageSet in, FeatureSet out (types formalized at M1 implementation)."""
