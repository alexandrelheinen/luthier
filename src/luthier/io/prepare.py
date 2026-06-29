"""Build an :class:`~luthier.models.ImageSet` from a local image directory."""

from __future__ import annotations

from pathlib import Path

from luthier.io.opencv_decode import decode
from luthier.io.pathlib_discover import discover
from luthier.models import ImageSet, PreparedImage


def prepare_image_set(image_dir: Path) -> ImageSet:
    """Discover, decode, and validate images directly inside ``image_dir``."""
    resolved_dir = image_dir.expanduser().resolve()
    paths = discover(resolved_dir)
    prepared = tuple(
        _prepare_image(image_id, path) for image_id, path in enumerate(paths)
    )
    return ImageSet(images=prepared, source_dir=resolved_dir)


def _prepare_image(image_id: int, path: Path) -> PreparedImage:
    pixels = decode(path)
    height, width = pixels.shape[:2]
    return PreparedImage(
        id=image_id,
        path=path,
        width=width,
        height=height,
        pixels=pixels,
    )


__all__ = ["prepare_image_set"]
