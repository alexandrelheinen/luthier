"""pycolmap adapter for sparse reconstruction (M1).

Systems contract (see docs/architecture.md §9.3.3):
  Input:  FeatureSet, ImageSet
  Output: ReconstructionScene — cameras, colored 3D points, observations

Maps backend failures to ``ReconstructionError``.
"""
