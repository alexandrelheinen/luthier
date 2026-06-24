"""Typed data models for reconstruction inputs and outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Point3D:
    """A single point in a 3D point cloud."""

    x: float
    y: float
    z: float
    r: int = 128
    g: int = 128
    b: int = 128

    def __post_init__(self) -> None:
        for channel, name in ((self.r, "r"), (self.g, "g"), (self.b, "b")):
            if not 0 <= channel <= 255:
                msg = f"Color channel {name} must be in [0, 255], got {channel}"
                raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class PointCloud:
    """A colored 3D point cloud produced by reconstruction."""

    points: tuple[Point3D, ...] = field(default_factory=tuple)

    @property
    def count(self) -> int:
        """Return the number of points in the cloud."""
        return len(self.points)


@dataclass(frozen=True, slots=True)
class LocalImageInput:
    """Local filesystem input: a directory of image files."""

    image_dir: Path

    def __post_init__(self) -> None:
        if not self.image_dir.exists():
            msg = f"Image directory does not exist: {self.image_dir}"
            raise ValueError(msg)
        if not self.image_dir.is_dir():
            msg = f"Image path is not a directory: {self.image_dir}"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class ReconstructionResult:
    """Result of a completed reconstruction run."""

    point_cloud: PointCloud
    output_path: Path
    source: LocalImageInput
