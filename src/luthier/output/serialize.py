"""Point cloud serialization (output layer).

Systems contract (see docs/architecture.md §9.3.5):
  Input:  PointCloud, output_path, file_format (default PLY)
  Output: binary little-endian PLY on disk (M1)

Implementation currently lives in ``luthier.io.pointcloud`` during transition.
"""

from luthier.io.pointcloud import write_point_cloud

__all__ = ["write_point_cloud"]
