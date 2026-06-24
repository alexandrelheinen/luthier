"""Golden-dataset and remote-cache sync helpers (IO layer).

Operational tools for aligning local test or staging directories with
authoritative sources (e.g. COLMAP South Building golden images).

Systems contract (see docs/architecture.md §9.3.1):
  Input:  sync manifest / dataset name, optional cache root
  Output: local directory path suitable for ``discover_images``

Not invoked by the default reconstruction pipeline.
"""
