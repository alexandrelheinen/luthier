"""Tests for the pycolmap adapter."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from luthier.exceptions import ReconstructionError
from luthier.io.prepare import prepare_image_set
from luthier.reconstruction.colmap import (
    extract_features,
    match_features,
    reconstruction_to_cameras,
    reconstruction_to_point_cloud,
    run_incremental_sfm,
    scene_from_reconstruction,
)


def _write_overlapping_images(image_dir: Path, count: int) -> None:
    image_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    base = rng.integers(0, 256, (400, 600, 3), dtype=np.uint8)
    for index in range(count):
        shift = index * 20
        canvas = np.zeros_like(base)
        width = base.shape[1] - shift
        canvas[:, shift : shift + width] = base[:, :width]
        image_path = image_dir / f"img{index:02d}.png"
        bgr = cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)
        assert cv2.imwrite(str(image_path), bgr)


def test_reconstruction_to_point_cloud_maps_colors(tmp_path: Path) -> None:
    image_dir = tmp_path / "photos"
    _write_overlapping_images(image_dir, 5)
    images = prepare_image_set(image_dir)
    database_path = tmp_path / "database.db"
    extract_features(database_path, images)
    match_features(database_path)
    sparse_dir = tmp_path / "sparse"
    reconstruction = run_incremental_sfm(database_path, images, sparse_dir)
    scene = scene_from_reconstruction(reconstruction)

    assert scene.point_cloud.count == reconstruction.num_points3D()
    point = scene.point_cloud.points[0]
    assert 0 <= point.r <= 255
    assert 0 <= point.g <= 255
    assert 0 <= point.b <= 255


def test_reconstruction_to_cameras_exports_registered_poses(tmp_path: Path) -> None:
    image_dir = tmp_path / "photos"
    _write_overlapping_images(image_dir, 5)
    images = prepare_image_set(image_dir)
    database_path = tmp_path / "database.db"
    extract_features(database_path, images)
    match_features(database_path)
    reconstruction = run_incremental_sfm(database_path, images, tmp_path / "sparse")

    cameras = reconstruction_to_cameras(reconstruction)

    assert len(cameras) == reconstruction.num_reg_images()
    assert all(camera.name for camera in cameras)
    assert all(camera.intrinsics.focal_length > 0 for camera in cameras)
    assert all(
        all(value == value for value in camera.translation) for camera in cameras
    )


def test_run_incremental_sfm_raises_when_no_model(tmp_path: Path) -> None:
    image_dir = tmp_path / "flat"
    image_dir.mkdir()
    for index in range(3):
        array = np.full((100, 100, 3), index * 40, dtype=np.uint8)
        cv2.imwrite(
            str(image_dir / f"flat{index}.png"),
            cv2.cvtColor(array, cv2.COLOR_RGB2BGR),
        )
    images = prepare_image_set(image_dir)
    database_path = tmp_path / "database.db"
    extract_features(database_path, images)
    with pytest.raises(ReconstructionError, match="did not produce"):
        run_incremental_sfm(database_path, images, tmp_path / "sparse")


def test_reconstruction_to_point_cloud_filters_by_reprojection_error(
    tmp_path: Path,
) -> None:
    image_dir = tmp_path / "photos"
    _write_overlapping_images(image_dir, 5)
    images = prepare_image_set(image_dir)
    database_path = tmp_path / "database.db"
    extract_features(database_path, images)
    match_features(database_path)
    reconstruction = run_incremental_sfm(database_path, images, tmp_path / "sparse")

    unfiltered = reconstruction_to_point_cloud(reconstruction)
    filtered = reconstruction_to_point_cloud(
        reconstruction,
        max_reprojection_error=0.001,
    )

    assert filtered.count < unfiltered.count


def test_reconstruction_to_point_cloud_raises_when_empty() -> None:
    import pycolmap

    reconstruction = pycolmap.Reconstruction()
    with pytest.raises(ReconstructionError, match="no triangulated"):
        reconstruction_to_point_cloud(reconstruction)


def test_reconstruction_to_cameras_raises_when_empty() -> None:
    import pycolmap

    reconstruction = pycolmap.Reconstruction()
    with pytest.raises(ReconstructionError, match="no registered camera"):
        reconstruction_to_cameras(reconstruction)
