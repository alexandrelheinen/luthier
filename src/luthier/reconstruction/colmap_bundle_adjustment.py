"""COLMAP bundle adjustment configuration.

Stack slot: ``reconstruction.bundle_adjustment``
→ ``algorithm: colmap_bundle_adjustment``
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pycolmap

from luthier.reconstruction.colmap import apply_bundle_adjustment_options

name = "colmap_bundle_adjustment"


def configure(
    options: pycolmap.IncrementalPipelineOptions,
    params: Mapping[str, Any],
) -> pycolmap.IncrementalPipelineOptions:
    """Apply bundle-adjustment params to incremental pipeline options."""
    return apply_bundle_adjustment_options(options, params)


__all__ = ["configure", "name"]
