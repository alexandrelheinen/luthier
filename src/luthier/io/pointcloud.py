"""Point cloud serialization."""

from __future__ import annotations

from pathlib import Path

from luthier.exceptions import NotImplementedPipelineError
from luthier.models import PointCloud

POINT_CLOUD_FORMAT_PLY = "ply"
DEFAULT_POINT_CLOUD_FORMAT = POINT_CLOUD_FORMAT_PLY


def write_point_cloud(
    point_cloud: PointCloud,
    output_path: Path,
    *,
    file_format: str = DEFAULT_POINT_CLOUD_FORMAT,
) -> Path:
    """Write ``point_cloud`` to ``output_path`` in the requested format.

    The default format is binary PLY with per-vertex RGB colors. See
    ``docs/specification.md`` for the on-disk layout.

    Raises:
        ValueError: If ``file_format`` is not supported.
        NotImplementedPipelineError: Until serialization is implemented.
    """
    if file_format != POINT_CLOUD_FORMAT_PLY:
        msg = f"Unsupported point cloud format: {file_format}"
        raise ValueError(msg)
    raise NotImplementedPipelineError(
        "Point cloud serialization is not implemented yet. "
        "See docs/specification.md and docs/testing.md."
    )
