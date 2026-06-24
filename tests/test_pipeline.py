"""Tests for the reconstruction pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest

from luthier.exceptions import NotImplementedPipelineError
from luthier.pipeline import reconstruct_from_directory


def test_reconstruct_from_directory_not_implemented(tmp_path: Path) -> None:
    image_dir = tmp_path / "photos"
    image_dir.mkdir()
    (image_dir / "a.jpg").write_bytes(b"\xff\xd8\xff")
    with pytest.raises(NotImplementedPipelineError, match="not implemented"):
        reconstruct_from_directory(
            image_dir,
            output_path=tmp_path / "out.ply",
        )


@pytest.mark.not_implemented
@pytest.mark.skip(
    reason="AC-REC-02: enable when reconstruction pipeline is implemented"
)
def test_reconstruct_requires_at_least_two_images(tmp_path: Path) -> None:
    """AC-REC-02 — red phase until pipeline is implemented."""
    image_dir = tmp_path / "photos"
    image_dir.mkdir()
    (image_dir / "only.jpg").write_bytes(b"\xff\xd8\xff")
    with pytest.raises(NotImplementedPipelineError):
        reconstruct_from_directory(
            image_dir,
            output_path=tmp_path / "out.ply",
        )
