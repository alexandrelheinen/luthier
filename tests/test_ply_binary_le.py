"""Tests for output algorithm module."""

from pathlib import Path

import pytest

from luthier.exceptions import NotImplementedPipelineError
from luthier.models import PointCloud
from luthier.output.ply_binary_le import write


def test_ply_binary_le_write_delegates_not_implemented(tmp_path: Path) -> None:
    with pytest.raises(NotImplementedPipelineError):
        write(PointCloud(), tmp_path / "out.ply")
