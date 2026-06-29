"""Tests for committed M1 documentation artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "docs" / "assets" / "m1-demo"
MANIFEST_PATH = ASSETS_DIR / "manifest.json"


def test_m1_doc_assets_manifest_exists() -> None:
    assert MANIFEST_PATH.is_file()


def test_m1_doc_assets_manifest_lists_committed_files() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    artifacts = manifest["artifacts"]
    reconstruction = manifest["reconstruction"]
    dataset = manifest["dataset"]

    assert dataset["id"] == "south-building"
    assert reconstruction["point_count"] >= 1_000
    assert reconstruction["camera_count"] >= 10

    for key in (
        "ply",
        "input_montage",
        "render_front",
        "render_side",
        "flythrough",
        "manifest",
    ):
        path = ASSETS_DIR / artifacts[key]
        assert path.is_file(), f"Missing documentation asset: {path}"
        assert path.stat().st_size > 0


def test_m1_doc_ply_is_binary_little_endian() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    ply_path = ASSETS_DIR / manifest["artifacts"]["ply"]
    header = ply_path.read_bytes()[:64]
    assert b"format binary_little_endian 1.0" in header


@pytest.mark.parametrize(
    "image_key",
    ["input_montage", "render_front", "render_side"],
)
def test_m1_doc_images_are_readable(image_key: str) -> None:
    import cv2

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    image_path = ASSETS_DIR / manifest["artifacts"][image_key]
    array = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    assert array is not None
    assert array.shape[0] >= 100
    assert array.shape[1] >= 100
