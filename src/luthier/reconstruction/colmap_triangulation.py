"""COLMAP triangulation configuration.

Stack slot: ``reconstruction.triangulation`` → ``algorithm: colmap_triangulation``
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pycolmap

from luthier.reconstruction.colmap import apply_triangulation_options

name = "colmap_triangulation"


def configure(
    options: pycolmap.IncrementalPipelineOptions,
    params: Mapping[str, Any],
) -> pycolmap.IncrementalPipelineOptions:
    """Apply triangulation params to incremental pipeline options."""
    return apply_triangulation_options(options, params)


__all__ = ["configure", "name"]
