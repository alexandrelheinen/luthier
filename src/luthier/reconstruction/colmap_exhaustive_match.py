"""COLMAP exhaustive feature matching.

Stack slot: ``reconstruction.matcher`` → ``algorithm: colmap_exhaustive_match``
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pycolmap

from luthier.reconstruction.colmap import build_feature_matching_options, match_features

name = "colmap_exhaustive_match"


def match(
    database_path: Path,
    *,
    pairing_options: pycolmap.ExhaustivePairingOptions,
    verification_options: pycolmap.TwoViewGeometryOptions,
    params: Mapping[str, Any] | None = None,
) -> None:
    """Run exhaustive feature matching with pre-built pairing and verification."""
    matching_options = build_feature_matching_options(params or {})
    match_features(
        database_path,
        matching_options=matching_options,
        pairing_options=pairing_options,
        verification_options=verification_options,
    )


__all__ = ["match", "name"]
