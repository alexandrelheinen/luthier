"""Output layer — serialize PointCloud to consumer file formats.

Distinct from IO input preparation. See docs/architecture.md §9.3.5.
"""

from luthier.output.serialize import write_point_cloud

__all__ = ["write_point_cloud"]
