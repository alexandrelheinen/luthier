"""COLMAP exhaustive image-pair selection.

Stack slot: ``reconstruction.pair_selection`` → ``algorithm: colmap_exhaustive_pairs``
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pycolmap

from luthier.reconstruction.colmap import build_pairing_options

name = "colmap_exhaustive_pairs"


def configure(params: Mapping[str, Any]) -> pycolmap.ExhaustivePairingOptions:
    """Build exhaustive pairing options from stack params."""
    return build_pairing_options(params)


__all__ = ["configure", "name"]
