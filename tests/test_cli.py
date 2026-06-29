"""Tests for the luthier CLI (AC-CLI-01 … AC-CLI-06)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

from luthier.cli import (
    EXIT_ERROR,
    build_parser,
    resolve_output_path,
    run,
    validate_args,
)


def test_help_mentions_dir_and_output() -> None:
    """AC-CLI-01."""
    parser = build_parser()
    help_text = parser.format_help()
    assert "--dir" in help_text
    assert "--output" in help_text


def test_main_module_entry_point_help() -> None:
    """Cover ``python -m luthier`` entry and AC-CLI-01."""
    result = subprocess.run(
        [sys.executable, "-m", "luthier", "--version"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.3.0" in result.stdout


def test_installed_entry_point_help() -> None:
    """AC-CLI-01 smoke via subprocess."""
    result = subprocess.run(
        [sys.executable, "-m", "luthier", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--dir" in result.stdout


def test_missing_dir_exits_with_error(capsys: pytest.CaptureFixture[str]) -> None:
    """AC-CLI-02."""
    code = run([])
    captured = capsys.readouterr()
    assert code == EXIT_ERROR
    assert "Missing required input" in captured.err


def test_missing_directory_path_exits_with_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AC-CLI-03."""
    code = run(["--dir", "/nonexistent/luthier-test-dir"])
    captured = capsys.readouterr()
    assert code == EXIT_ERROR
    assert "does not exist" in captured.err


def test_not_a_directory_exits_with_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """AC-CLI-03 variant."""
    file_path = tmp_path / "not-a-dir.txt"
    file_path.write_text("x", encoding="utf-8")
    code = run(["--dir", str(file_path)])
    captured = capsys.readouterr()
    assert code == EXIT_ERROR
    assert "not a directory" in captured.err


def test_resolve_output_path_returns_absolute(tmp_path: Path) -> None:
    """AC-CLI-04."""
    output = tmp_path / "out" / "scene.ply"
    resolved = resolve_output_path(output)
    assert resolved.is_absolute()
    assert resolved == output.resolve()


def test_resolve_output_path_creates_temp_ply() -> None:
    """AC-CLI-05."""
    resolved = resolve_output_path(None)
    assert resolved.suffix == ".ply"
    assert resolved.name.startswith("luthier-")
    assert resolved.is_absolute()
    resolved.unlink(missing_ok=True)


def test_validate_args_resolves_output(
    tmp_path: Path,
) -> None:
    """AC-CLI-04 via validate_args."""
    image_dir = tmp_path / "photos"
    image_dir.mkdir()
    (image_dir / "a.jpg").write_bytes(b"\xff\xd8\xff")
    output = tmp_path / "out.ply"
    parser = build_parser()
    args = parser.parse_args(["--dir", str(image_dir), "--output", str(output)])
    parsed_dir, parsed_output = validate_args(args)
    assert parsed_dir == image_dir.resolve()
    assert parsed_output == output.resolve()


def test_pipeline_single_image_exit_code(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Fewer than two images returns exit code 1 (AC-REC-02 via CLI)."""
    image_dir = tmp_path / "photos"
    image_dir.mkdir()
    array = np.zeros((32, 32, 3), dtype=np.uint8)
    cv2.imwrite(
        str(image_dir / "only.png"),
        cv2.cvtColor(array, cv2.COLOR_RGB2BGR),
    )
    code = run(["--dir", str(image_dir), "--output", str(tmp_path / "out.ply")])
    captured = capsys.readouterr()
    assert code == EXIT_ERROR
    assert "at least 2 images" in captured.err.lower()
