"""Color propagation sub-stage of the optimization layer (placeholder).

Systems contract (see docs/architecture.md §9.3.3):
  Input:  triangulated 3D points, camera poses, ImageSet pixel data
  Output: per-point RGB (uint8) attached to ReconstructionScene

M1 may delegate this to pycolmap/COLMAP; this module documents the contract
when a standalone or testable color path is needed.
"""
