#!/usr/bin/env python3
"""Generate M1 documentation artifacts from the golden COLMAP dataset.

Runs a full reconstruction on the South Building golden subset and writes
PLY, PNG renders, an input montage, and an orbit video under ``docs/assets/``.

Prerequisites (repository root)::

    ./scripts/fetch_golden_colmap.sh --count 20
    pip install -e ".[dev,reconstruction]"

Example::

    python scripts/generate_m1_doc_artifacts.py
    python scripts/generate_m1_doc_artifacts.py --output-dir docs/assets/m1-demo
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import cv2
import numpy as np
import open3d as o3d

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IMAGES_DIR = REPO_ROOT / "tests" / "data" / "golden" / "images"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "assets" / "m1-demo"
GOLDEN_MANIFEST = REPO_ROOT / "tests" / "data" / "golden" / "colmap.yml"
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_golden_colmap.sh"
DATASET_URL = (
    "https://github.com/colmap/colmap/releases/download/3.11.1/south-building.zip"
)
MIN_GOLDEN_IMAGES = 10
MONTAGE_MAX_IMAGES = 8
MONTAGE_COLS = 4
RENDER_WIDTH = 1280
RENDER_HEIGHT = 720
VIDEO_FPS = 12
VIDEO_FRAMES = 48


@dataclass(frozen=True, slots=True)
class ArtifactPaths:
    """Relative artifact filenames inside the output directory."""

    ply: str = "south-building-scene.ply"
    input_montage: str = "south-building-input-montage.jpg"
    render_front: str = "south-building-front.png"
    render_side: str = "south-building-side.png"
    flythrough: str = "south-building-flythrough.mp4"
    manifest: str = "manifest.json"


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--images-dir",
        type=Path,
        default=DEFAULT_IMAGES_DIR,
        help="Directory with golden JPEG images (default: tests/data/golden/images)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for committed documentation assets",
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Run fetch_golden_colmap.sh --count 20 when images are missing",
    )
    parser.add_argument(
        "--image-count",
        type=int,
        default=20,
        help="Subset size when --fetch is used (default: 20)",
    )
    return parser.parse_args(argv)


def _ensure_golden_images(images_dir: Path, *, fetch: bool, image_count: int) -> int:
    suffixes = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
    existing = sorted(
        path
        for path in images_dir.iterdir()
        if path.is_file() and path.suffix.lower() in suffixes
    )
    if len(existing) >= MIN_GOLDEN_IMAGES:
        return len(existing)
    if not fetch:
        msg = (
            f"Need at least {MIN_GOLDEN_IMAGES} images in {images_dir}. "
            f"Run ./scripts/fetch_golden_colmap.sh or pass --fetch."
        )
        raise FileNotFoundError(msg)
    if not FETCH_SCRIPT.is_file():
        msg = f"Fetch script not found: {FETCH_SCRIPT}"
        raise FileNotFoundError(msg)
    subprocess.run(
        [str(FETCH_SCRIPT), "--count", str(image_count)],
        check=True,
        cwd=REPO_ROOT,
    )
    existing = sorted(
        path
        for path in images_dir.iterdir()
        if path.is_file() and path.suffix.lower() in suffixes
    )
    if len(existing) < MIN_GOLDEN_IMAGES:
        msg = f"Fetch completed but {images_dir} still has too few images."
        raise FileNotFoundError(msg)
    return len(existing)


def _build_input_montage(images_dir: Path, output_path: Path) -> list[str]:
    suffixes = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
    image_paths = sorted(
        path
        for path in images_dir.iterdir()
        if path.is_file() and path.suffix.lower() in suffixes
    )[:MONTAGE_MAX_IMAGES]
    if not image_paths:
        msg = f"No images found in {images_dir}"
        raise FileNotFoundError(msg)

    thumb_size = (320, 240)
    thumbs: list[np.ndarray] = []
    names: list[str] = []
    for path in image_paths:
        bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if bgr is None:
            continue
        thumbs.append(cv2.resize(bgr, thumb_size, interpolation=cv2.INTER_AREA))
        names.append(path.name)

    rows = math.ceil(len(thumbs) / MONTAGE_COLS)
    canvas = np.zeros(
        (rows * thumb_size[1], MONTAGE_COLS * thumb_size[0], 3),
        dtype=np.uint8,
    )
    for index, thumb in enumerate(thumbs):
        row, col = divmod(index, MONTAGE_COLS)
        y0 = row * thumb_size[1]
        x0 = col * thumb_size[0]
        canvas[y0 : y0 + thumb_size[1], x0 : x0 + thumb_size[0]] = thumb
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    return names


def _render_point_cloud_views(
    ply_path: Path,
    *,
    front_path: Path,
    side_path: Path,
    flythrough_path: Path,
) -> None:
    point_cloud = o3d.io.read_point_cloud(str(ply_path))
    if point_cloud.is_empty():
        msg = f"Point cloud is empty: {ply_path}"
        raise ValueError(msg)

    center = point_cloud.get_center()
    vis = o3d.visualization.Visualizer()
    vis.create_window(width=RENDER_WIDTH, height=RENDER_HEIGHT, visible=False)
    vis.add_geometry(point_cloud)
    render_options = vis.get_render_option()
    render_options.background_color = np.array([0.11, 0.11, 0.13])
    render_options.point_size = 2.5
    controller = vis.get_view_control()

    def _capture(front: list[float], up: list[float], path: Path) -> None:
        controller.set_lookat(center)
        controller.set_front(front)
        controller.set_up(up)
        controller.set_zoom(0.55)
        vis.poll_events()
        vis.update_renderer()
        vis.capture_screen_image(str(path))

    front_path.parent.mkdir(parents=True, exist_ok=True)
    _capture([0.0, -0.15, -1.0], [0.0, -1.0, 0.0], front_path)
    _capture([-1.0, -0.15, 0.0], [0.0, -1.0, 0.0], side_path)

    frames: list[np.ndarray] = []
    for index in range(VIDEO_FRAMES):
        angle = 2.0 * math.pi * index / VIDEO_FRAMES
        controller.set_lookat(center)
        controller.set_front([math.sin(angle), -0.2, math.cos(angle)])
        controller.set_up([0.0, -1.0, 0.0])
        controller.set_zoom(0.55)
        vis.poll_events()
        vis.update_renderer()
        buffer = vis.capture_screen_float_buffer(do_render=True)
        rgb = (np.asarray(buffer) * 255.0).astype(np.uint8)
        frames.append(rgb[:, :, ::-1])
    vis.destroy_window()

    writer = cv2.VideoWriter(
        str(flythrough_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        VIDEO_FPS,
        (RENDER_WIDTH, RENDER_HEIGHT),
    )
    if not writer.isOpened():
        msg = f"Could not open video writer for {flythrough_path}"
        raise OSError(msg)
    for frame in frames:
        writer.write(frame)
    writer.release()


def generate_doc_artifacts(
    *,
    images_dir: Path,
    output_dir: Path,
    fetch: bool = False,
    image_count: int = 20,
) -> dict[str, object]:
    """Run reconstruction and write documentation assets."""
    from luthier import __version__
    from luthier.pipeline import reconstruct_from_directory

    resolved_images = images_dir.expanduser().resolve()
    resolved_output = output_dir.expanduser().resolve()
    resolved_output.mkdir(parents=True, exist_ok=True)

    image_total = _ensure_golden_images(
        resolved_images,
        fetch=fetch,
        image_count=image_count,
    )
    names = ArtifactPaths()
    ply_path = resolved_output / names.ply

    started = time.perf_counter()
    result = reconstruct_from_directory(
        resolved_images,
        output_path=ply_path,
    )
    elapsed = time.perf_counter() - started

    montage_names = _build_input_montage(
        resolved_images,
        resolved_output / names.input_montage,
    )
    _render_point_cloud_views(
        ply_path,
        front_path=resolved_output / names.render_front,
        side_path=resolved_output / names.render_side,
        flythrough_path=resolved_output / names.flythrough,
    )

    manifest: dict[str, object] = {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "luthier_version": __version__,
        "dataset": {
            "id": "south-building",
            "name": "South Building (UNC Chapel Hill)",
            "provider": "COLMAP benchmark — Christopher Zach (images)",
            "source_url": DATASET_URL,
            "documentation": "https://colmap.github.io/datasets.html",
            "manifest": str(GOLDEN_MANIFEST.relative_to(REPO_ROOT)),
            "images_dir": str(resolved_images.relative_to(REPO_ROOT)),
            "image_count_used": image_total,
            "montage_samples": montage_names,
        },
        "reconstruction": {
            "stack": "config/stack.yml",
            "point_count": result.point_cloud.count,
            "camera_count": len(result.cameras),
            "elapsed_seconds": round(elapsed, 2),
            "output_ply_bytes": ply_path.stat().st_size,
        },
        "artifacts": asdict(names),
    }
    manifest_path = resolved_output / names.manifest
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        manifest = generate_doc_artifacts(
            images_dir=args.images_dir,
            output_dir=args.output_dir,
            fetch=args.fetch,
            image_count=args.image_count,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    reconstruction = manifest["reconstruction"]
    assert isinstance(reconstruction, dict)
    print(f"Wrote documentation assets to {args.output_dir.resolve()}")
    print(
        "Reconstruction:",
        reconstruction["point_count"],
        "points,",
        reconstruction["camera_count"],
        "cameras,",
        f"{reconstruction['elapsed_seconds']}s",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
