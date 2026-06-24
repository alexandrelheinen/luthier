"""Acceptance tests for end-to-end reconstruction (AC-REC-01 … AC-REC-04)."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import GOLDEN_IMAGES_DIR, requires_golden_images  # type: ignore[import-not-found]
from luthier.exceptions import NotImplementedPipelineError
from luthier.pipeline import reconstruct_from_directory

pytestmark = [pytest.mark.acceptance, requires_golden_images]


@pytest.mark.xfail(
    reason="AC-REC-01: enable when M1 reconstruction pipeline is implemented",
    raises=NotImplementedPipelineError,
    strict=True,
)
def test_golden_dataset_produces_point_cloud(tmp_path: Path) -> None:
    """AC-REC-01."""
    result = reconstruct_from_directory(
        GOLDEN_IMAGES_DIR,
        output_path=tmp_path / "golden.ply",
    )
    assert result.output_path.exists()
    assert result.point_cloud.count >= 1_000


@pytest.mark.xfail(
    reason="AC-REC-03/04: enable when M1 reconstruction pipeline is implemented",
    raises=NotImplementedPipelineError,
    strict=True,
)
def test_result_paths_are_consistent(tmp_path: Path) -> None:
    """AC-REC-03 and AC-REC-04."""
    output = tmp_path / "scene.ply"
    result = reconstruct_from_directory(
        GOLDEN_IMAGES_DIR,
        output_path=output,
    )
    assert result.output_path == output.resolve()
    assert result.output_path.is_file()
