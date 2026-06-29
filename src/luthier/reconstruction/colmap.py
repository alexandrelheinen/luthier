"""pycolmap adapter for sparse reconstruction (M1).

Maps COLMAP / pycolmap primitives to luthier domain types and raises
:class:`~luthier.exceptions.ReconstructionError` on backend failure.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pycolmap

from luthier.exceptions import ReconstructionError
from luthier.models import (
    CameraIntrinsics,
    CameraPose,
    ImageSet,
    Point3D,
    PointCloud,
    ReconstructionScene,
)

__all__ = [
    "apply_bundle_adjustment_options",
    "apply_triangulation_options",
    "build_extraction_options",
    "build_feature_matching_options",
    "build_incremental_options",
    "build_matching_options",
    "build_pairing_options",
    "build_verification_options",
    "extract_features",
    "match_features",
    "reconstruction_to_cameras",
    "reconstruction_to_point_cloud",
    "run_incremental_sfm",
    "scene_from_reconstruction",
]


def build_extraction_options(
    params: Mapping[str, Any],
) -> pycolmap.FeatureExtractionOptions:
    """Build pycolmap feature-extraction options from stack params."""
    options = pycolmap.FeatureExtractionOptions()
    if "max_image_size" in params:
        options.max_image_size = int(params["max_image_size"])
    if "max_num_features" in params:
        options.sift.max_num_features = int(params["max_num_features"])
    return options


def build_pairing_options(
    params: Mapping[str, Any],
) -> pycolmap.ExhaustivePairingOptions:
    """Build pycolmap exhaustive-pairing options from stack params."""
    pairing = pycolmap.ExhaustivePairingOptions()
    if "block_size" in params:
        pairing.block_size = int(params["block_size"])
    return pairing


def build_feature_matching_options(
    params: Mapping[str, Any],
) -> pycolmap.FeatureMatchingOptions:
    """Build pycolmap feature-matching options from stack params."""
    matching = pycolmap.FeatureMatchingOptions()
    if "max_ratio" in params:
        matching.sift.max_ratio = float(params["max_ratio"])
    if "max_distance" in params:
        matching.sift.max_distance = float(params["max_distance"])
    if "cross_check" in params:
        matching.sift.cross_check = bool(params["cross_check"])
    return matching


def build_verification_options(
    params: Mapping[str, Any],
) -> pycolmap.TwoViewGeometryOptions:
    """Build pycolmap two-view geometry / RANSAC options from stack params."""
    options = pycolmap.TwoViewGeometryOptions()
    if "max_error" in params:
        options.ransac.max_error = float(params["max_error"])
    if "min_inlier_ratio" in params:
        options.min_inlier_ratio = float(params["min_inlier_ratio"])
    return options


def build_matching_options(
    params: Mapping[str, Any],
) -> tuple[pycolmap.FeatureMatchingOptions, pycolmap.ExhaustivePairingOptions]:
    """Build pycolmap matching and pairing options from stack params."""
    return build_feature_matching_options(params), build_pairing_options(params)


def apply_bundle_adjustment_options(
    options: pycolmap.IncrementalPipelineOptions,
    params: Mapping[str, Any],
) -> pycolmap.IncrementalPipelineOptions:
    """Apply bundle-adjustment stack params to incremental pipeline options."""
    if "refine_focal_length" in params:
        options.ba_refine_focal_length = bool(params["refine_focal_length"])
    if "refine_principal_point" in params:
        options.ba_refine_principal_point = bool(params["refine_principal_point"])
    if "refine_extra_params" in params:
        options.ba_refine_extra_params = bool(params["refine_extra_params"])
    return options


def apply_triangulation_options(
    options: pycolmap.IncrementalPipelineOptions,
    params: Mapping[str, Any],
) -> pycolmap.IncrementalPipelineOptions:
    """Apply triangulation stack params to incremental pipeline options."""
    if "min_tri_angle_deg" in params:
        options.triangulation.min_angle = float(params["min_tri_angle_deg"])
    return options


def build_incremental_options(
    params: Mapping[str, Any],
    *,
    bundle_params: Mapping[str, Any] | None = None,
    triangulation_params: Mapping[str, Any] | None = None,
) -> pycolmap.IncrementalPipelineOptions:
    """Build pycolmap incremental-mapping options from stack params."""
    options = pycolmap.IncrementalPipelineOptions()
    if "min_num_matches" in params:
        options.min_num_matches = int(params["min_num_matches"])
    if bundle_params:
        apply_bundle_adjustment_options(options, bundle_params)
    if triangulation_params:
        apply_triangulation_options(options, triangulation_params)
    return options


def extract_features(
    database_path: Path,
    images: ImageSet,
    *,
    params: Mapping[str, Any] | None = None,
) -> None:
    """Extract SIFT features into a COLMAP database."""
    extraction_options = build_extraction_options(params or {})
    image_names = [image.path.name for image in images.images]
    pycolmap.extract_features(
        database_path,
        images.source_dir,
        image_names=image_names,
        extraction_options=extraction_options,
    )


def match_features(
    database_path: Path,
    *,
    matcher_params: Mapping[str, Any] | None = None,
    pair_params: Mapping[str, Any] | None = None,
    verifier_params: Mapping[str, Any] | None = None,
    matching_options: pycolmap.FeatureMatchingOptions | None = None,
    pairing_options: pycolmap.ExhaustivePairingOptions | None = None,
    verification_options: pycolmap.TwoViewGeometryOptions | None = None,
) -> None:
    """Run exhaustive feature matching on a COLMAP database."""
    resolved_matching = matching_options or build_feature_matching_options(
        matcher_params or {}
    )
    resolved_pairing = pairing_options or build_pairing_options(pair_params or {})
    resolved_verification = verification_options or build_verification_options(
        verifier_params or {}
    )
    pycolmap.match_exhaustive(
        database_path,
        matching_options=resolved_matching,
        pairing_options=resolved_pairing,
        verification_options=resolved_verification,
    )


def run_incremental_sfm(
    database_path: Path,
    images: ImageSet,
    output_path: Path,
    *,
    params: Mapping[str, Any] | None = None,
    options: pycolmap.IncrementalPipelineOptions | None = None,
    bundle_params: Mapping[str, Any] | None = None,
    triangulation_params: Mapping[str, Any] | None = None,
) -> pycolmap.Reconstruction:
    """Run incremental mapping and return the largest reconstruction."""
    output_path.mkdir(parents=True, exist_ok=True)
    pipeline_options = options or build_incremental_options(
        params or {},
        bundle_params=bundle_params,
        triangulation_params=triangulation_params,
    )
    reconstructions = pycolmap.incremental_mapping(
        database_path,
        images.source_dir,
        output_path,
        options=pipeline_options,
    )
    if not reconstructions:
        msg = "Incremental SfM did not produce a sparse reconstruction."
        raise ReconstructionError(msg)
    return reconstructions[max(reconstructions.keys())]


def reconstruction_to_point_cloud(
    reconstruction: pycolmap.Reconstruction,
    *,
    max_reprojection_error: float | None = None,
) -> PointCloud:
    """Convert a pycolmap reconstruction to a colored point cloud."""
    points: list[Point3D] = []
    for point in reconstruction.points3D.values():
        if (
            max_reprojection_error is not None
            and float(point.error) > max_reprojection_error
        ):
            continue
        points.append(
            Point3D(
                x=float(point.xyz[0]),
                y=float(point.xyz[1]),
                z=float(point.xyz[2]),
                r=int(point.color[0]),
                g=int(point.color[1]),
                b=int(point.color[2]),
            )
        )
    if not points:
        msg = "Sparse reconstruction contains no triangulated 3D points."
        raise ReconstructionError(msg)
    return PointCloud(points=tuple(points))


def reconstruction_to_cameras(
    reconstruction: pycolmap.Reconstruction,
) -> tuple[CameraPose, ...]:
    """Convert a pycolmap reconstruction to registered camera poses."""
    cameras: list[CameraPose] = []
    for image_id in sorted(reconstruction.images):
        image = reconstruction.images[image_id]
        camera = reconstruction.cameras[image.camera_id]
        pose = image.cam_from_world()
        quaternion = tuple(float(value) for value in pose.rotation.quat)
        translation = tuple(float(value) for value in pose.translation)
        intrinsics = CameraIntrinsics(
            model=camera.model.name,
            width=int(camera.width),
            height=int(camera.height),
            focal_length=float(camera.focal_length),
            params=tuple(float(value) for value in camera.params),
        )
        cameras.append(
            CameraPose(
                image_id=int(image_id),
                name=str(image.name),
                rotation=(
                    quaternion[0],
                    quaternion[1],
                    quaternion[2],
                    quaternion[3],
                ),
                translation=(
                    translation[0],
                    translation[1],
                    translation[2],
                ),
                intrinsics=intrinsics,
            )
        )
    if not cameras:
        msg = "Sparse reconstruction contains no registered camera poses."
        raise ReconstructionError(msg)
    return tuple(cameras)


def scene_from_reconstruction(
    reconstruction: pycolmap.Reconstruction,
) -> ReconstructionScene:
    """Wrap a pycolmap reconstruction as a reconstruction scene."""
    return ReconstructionScene(
        point_cloud=reconstruction_to_point_cloud(reconstruction),
        reconstruction=reconstruction,
    )
