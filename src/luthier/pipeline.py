"""High-level reconstruction pipeline."""

from __future__ import annotations

from pathlib import Path

from luthier.exceptions import NotImplementedPipelineError
from luthier.models import LocalImageInput, ReconstructionResult


def reconstruct_from_directory(
    image_dir: Path,
    *,
    output_path: Path,
) -> ReconstructionResult:
    """Run photogrammetric reconstruction on images in ``image_dir``.

    Writes a colored point cloud to ``output_path`` and returns metadata
    about the result.

    Raises:
        InvalidInputError: If ``image_dir`` is invalid or has no images.
        ReconstructionError: If reconstruction fails.
        NotImplementedPipelineError: Until the pipeline is implemented.
    """
    _ = LocalImageInput(image_dir=image_dir.resolve())
    raise NotImplementedPipelineError(
        "Photogrammetric reconstruction is not implemented yet. "
        "See docs/specification.md and docs/testing.md."
    )
