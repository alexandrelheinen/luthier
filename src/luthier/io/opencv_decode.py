"""OpenCV image decode (IO layer).

Stack slot: ``io.decode`` → ``algorithm: opencv_decode``
Implements :class:`~luthier.protocols.io.ImageDecoder`.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from luthier.exceptions import InvalidInputError

name = "opencv_decode"


def decode(path: Path) -> np.ndarray:
    """Decode raster at ``path`` to an RGB ``uint8`` array with shape H×W×3."""
    resolved = path.expanduser().resolve()
    bgr = cv2.imread(str(resolved), cv2.IMREAD_COLOR)
    if bgr is None:
        msg = f"Could not decode image file: {resolved}"
        raise InvalidInputError(msg)
    rgb: np.ndarray = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return rgb


__all__ = ["decode", "name"]
