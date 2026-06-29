"""High-level reconstruction pipeline."""

from __future__ import annotations

import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from luthier.exceptions import InvalidInputError
from luthier.io.prepare import prepare_image_set
from luthier.models import (
    CameraPose,
    ImageSet,
    LocalImageInput,
    PointCloud,
    PreparedImage,
    ReconstructionResult,
    ReconstructionScene,
)
from luthier.reconstruction.colmap import reconstruction_to_cameras
from luthier.stack.bootstrap import load_algorithms
from luthier.stack.config import StackConfig, load_stack_config
from luthier.stack.registry import resolve

MIN_RECONSTRUCTION_IMAGES = 2


def reconstruct_from_directory(
    image_dir: Path,
    *,
    output_path: Path,
    stack_path: Path | None = None,
) -> ReconstructionResult:
    """Run photogrammetric reconstruction on images in ``image_dir``.

    Writes a colored point cloud to ``output_path`` and returns metadata
    about the result.

    Raises:
        InvalidInputError: If ``image_dir`` is invalid or has too few images.
        ReconstructionError: If reconstruction fails.
    """
    source = LocalImageInput(image_dir=image_dir.resolve())
    load_algorithms()
    stack = load_stack_config(stack_path)
    image_set = _prepare_images(stack, source.image_dir)
    _require_minimum_images(image_set)
    workspace_dir = Path(tempfile.mkdtemp(prefix="luthier-workspace-"))
    feature_set = _extract_features(stack, image_set, workspace_dir)
    scene = _reconstruct_scene(stack, feature_set, image_set)
    cameras = _extract_cameras(scene)
    point_cloud = _postprocess_scene(stack, scene)
    resolved_output = _write_point_cloud(stack, point_cloud, output_path)
    return ReconstructionResult(
        point_cloud=point_cloud,
        cameras=cameras,
        output_path=resolved_output,
        source=source,
    )


def _prepare_images(stack: StackConfig, image_dir: Path) -> ImageSet:
    discover_slot = stack.slot("io", "discover")
    decode_slot = stack.slot("io", "decode")
    if (
        discover_slot.algorithm == "pathlib_discover"
        and decode_slot.algorithm == "opencv_decode"
    ):
        return prepare_image_set(image_dir)

    discoverer = resolve("io", discover_slot)
    paths = discoverer.discover(image_dir)
    decoder = resolve("io", decode_slot)
    prepared = tuple(
        _decode_image(image_id, path, decoder, decode_slot.params)
        for image_id, path in enumerate(paths)
    )
    return ImageSet(images=prepared, source_dir=image_dir.resolve())


def _decode_image(
    image_id: int,
    path: Path,
    decoder: Any,
    params: Mapping[str, Any],
) -> PreparedImage:
    _ = params
    pixels = decoder.decode(path)
    height, width = pixels.shape[:2]
    return PreparedImage(
        id=image_id,
        path=path,
        width=width,
        height=height,
        pixels=pixels,
    )


def _require_minimum_images(image_set: ImageSet) -> None:
    if image_set.count < MIN_RECONSTRUCTION_IMAGES:
        msg = (
            f"At least {MIN_RECONSTRUCTION_IMAGES} images are required for "
            f"reconstruction, found {image_set.count}."
        )
        raise InvalidInputError(msg)


def _extract_features(
    stack: StackConfig,
    image_set: ImageSet,
    workspace_dir: Path,
) -> Any:
    extractor_slot = stack.slot("features", "extractor")
    extractor = resolve("features", extractor_slot)
    return extractor.extract(
        image_set,
        params=extractor_slot.params,
        workspace_dir=workspace_dir,
    )


def _reconstruct_scene(
    stack: StackConfig, feature_set: Any, image_set: ImageSet
) -> ReconstructionScene:
    sfm_slot = stack.slot("reconstruction", "sfm")
    backend = resolve("reconstruction", sfm_slot)
    scene = backend.reconstruct(
        feature_set,
        images=image_set,
        params=sfm_slot.params,
        stack=stack,
    )
    if not isinstance(scene, ReconstructionScene):
        msg = "Reconstruction backend must return a ReconstructionScene."
        raise TypeError(msg)
    return scene


def _extract_cameras(scene: ReconstructionScene) -> tuple[CameraPose, ...]:
    reconstruction = scene.reconstruction
    if reconstruction is None:
        msg = "Reconstruction backend did not attach a reconstruction handle."
        raise TypeError(msg)
    return reconstruction_to_cameras(reconstruction)


def _postprocess_scene(stack: StackConfig, scene: ReconstructionScene) -> PointCloud:
    point_cloud = scene.point_cloud
    point_cloud = _apply_postprocess_slot(
        stack,
        "geometric_filter",
        point_cloud,
        reconstruction=scene.reconstruction,
    )
    return _apply_postprocess_slot(stack, "outliers", point_cloud)


def _apply_postprocess_slot(
    stack: StackConfig,
    slot_name: str,
    point_cloud: PointCloud,
    *,
    reconstruction: Any = None,
) -> PointCloud:
    slot = stack.slot("postprocess", slot_name)
    if slot.algorithm is None:
        return point_cloud
    try:
        filt = resolve("postprocess", slot)
    except KeyError:
        return point_cloud
    filtered: PointCloud = filt.filter(
        point_cloud,
        params=slot.params,
        reconstruction=reconstruction,
    )
    return filtered


def _write_point_cloud(
    stack: StackConfig,
    point_cloud: PointCloud,
    output_path: Path,
) -> Path:
    serializer_slot = stack.slot("output", "serializer")
    serializer = resolve("output", serializer_slot)
    resolved = output_path.expanduser().resolve()
    serializer.write(point_cloud, resolved)
    return resolved
