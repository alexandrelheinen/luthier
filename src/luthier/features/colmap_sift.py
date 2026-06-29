"""COLMAP SIFT feature extraction.

Stack slot: ``features.extractor`` → ``algorithm: colmap_sift``
Implements :class:`~luthier.protocols.features.FeatureExtractor`.
"""

from __future__ import annotations

import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from luthier.models import FeatureSet, ImageSet
from luthier.reconstruction.colmap import extract_features

name = "colmap_sift"


def extract(
    images: ImageSet,
    *,
    params: Mapping[str, Any] | None = None,
    workspace_dir: Path | None = None,
) -> FeatureSet:
    """Extract SIFT features from ``images`` into a COLMAP database."""
    workspace = workspace_dir or Path(tempfile.mkdtemp(prefix="luthier-colmap-"))
    workspace.mkdir(parents=True, exist_ok=True)
    database_path = workspace / "database.db"
    extract_features(database_path, images, params=params)
    image_names = tuple(image.path.name for image in images.images)
    return FeatureSet(
        database_path=database_path,
        image_dir=images.source_dir,
        image_names=image_names,
        workspace_dir=workspace,
    )


__all__ = ["extract", "name"]
