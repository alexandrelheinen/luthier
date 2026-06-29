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
from luthier.models import ImageSet, Point3D, PointCloud, ReconstructionScene

__all__ = [
    "build_extraction_options",
    "build_incremental_options",
    "build_matching_options",
    "extract_features",
    "match_features",
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


def build_matching_options(
    params: Mapping[str, Any],
) -> tuple[pycolmap.FeatureMatchingOptions, pycolmap.ExhaustivePairingOptions]:
    """Build pycolmap matching options from stack params."""
    matching = pycolmap.FeatureMatchingOptions()
    pairing = pycolmap.ExhaustivePairingOptions()
    if "block_size" in params:
        pairing.block_size = int(params["block_size"])
    if "max_ratio" in params:
        matching.sift.max_ratio = float(params["max_ratio"])
    if "max_distance" in params:
        matching.sift.max_distance = float(params["max_distance"])
    if "cross_check" in params:
        matching.sift.cross_check = bool(params["cross_check"])
    return matching, pairing


def build_incremental_options(
    params: Mapping[str, Any],
) -> pycolmap.IncrementalPipelineOptions:
    """Build pycolmap incremental-mapping options from stack params."""
    options = pycolmap.IncrementalPipelineOptions()
    if "min_num_matches" in params:
        options.min_num_matches = int(params["min_num_matches"])
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
) -> None:
    """Run exhaustive feature matching on a COLMAP database."""
    merged = dict(matcher_params or {})
    merged.update(pair_params or {})
    matching_options, pairing_options = build_matching_options(merged)
    pycolmap.match_exhaustive(
        database_path,
        matching_options=matching_options,
        pairing_options=pairing_options,
    )


def run_incremental_sfm(
    database_path: Path,
    images: ImageSet,
    output_path: Path,
    *,
    params: Mapping[str, Any] | None = None,
) -> pycolmap.Reconstruction:
    """Run incremental mapping and return the largest reconstruction."""
    output_path.mkdir(parents=True, exist_ok=True)
    options = build_incremental_options(params or {})
    reconstructions = pycolmap.incremental_mapping(
        database_path,
        images.source_dir,
        output_path,
        options=options,
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


def scene_from_reconstruction(
    reconstruction: pycolmap.Reconstruction,
) -> ReconstructionScene:
    """Wrap a pycolmap reconstruction as a reconstruction scene."""
    return ReconstructionScene(
        point_cloud=reconstruction_to_point_cloud(reconstruction),
        reconstruction=reconstruction,
    )
