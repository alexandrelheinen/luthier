"""OpenCV image decode (IO layer, placeholder).

Stack slot: ``io.decode`` → ``algorithm: opencv_decode``
Implements :class:`~luthier.protocols.io.ImageDecoder`.
"""

from __future__ import annotations

from pathlib import Path

name = "opencv_decode"


def decode(path: Path) -> object:
    """Decode raster at ``path`` to an RGB array (not implemented until M1)."""
    raise NotImplementedError("opencv_decode is not implemented yet.")
