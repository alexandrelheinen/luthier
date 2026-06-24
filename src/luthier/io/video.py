"""Video-to-ImageSet conversion (IO layer, future).

Systems contract (see docs/architecture.md §9.3.1):
  Input:  video file path, optional frame sampling policy
  Output: ImageSet — same artifact as directory-based IO

Frame extraction and decoding belong here; per-frame feature detection
belongs in ``luthier.features``.
"""
