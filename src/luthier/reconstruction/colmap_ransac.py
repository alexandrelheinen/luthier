"""COLMAP two-view geometry verification (RANSAC).

Stack slot: ``reconstruction.verifier`` → ``algorithm: colmap_ransac``
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pycolmap

from luthier.reconstruction.colmap import build_verification_options

name = "colmap_ransac"


def configure(params: Mapping[str, Any]) -> pycolmap.TwoViewGeometryOptions:
    """Build two-view geometry / RANSAC options from stack params."""
    return build_verification_options(params)


__all__ = ["configure", "name"]
