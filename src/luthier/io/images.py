"""Image discovery and validation for local directory input.

Public API re-exports the default ``pathlib_discover`` algorithm. New
implementations belong in ``{algorithm_name}.py`` modules; see README.
"""

from luthier.io.pathlib_discover import (
    SUPPORTED_IMAGE_SUFFIXES,
    discover_images,
)

__all__ = ["SUPPORTED_IMAGE_SUFFIXES", "discover_images"]
