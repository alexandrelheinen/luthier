"""Layer protocols — shared interfaces between algorithm implementations.

Each layer package implements these protocols in ``{algorithm_name}.py`` modules.
Only domain types from ``luthier.models`` (and future layer artifacts) cross
layer boundaries. See README § Pluggable algorithm stack.
"""

from luthier.protocols.cache import ArtifactCache, NullArtifactCache
from luthier.protocols.features import FeatureExtractor
from luthier.protocols.io import ImageDecoder, ImageDiscoverer
from luthier.protocols.observability import NullProgressReporter, ProgressReporter
from luthier.protocols.output import PointCloudSerializer
from luthier.protocols.postprocess import PointCloudFilter
from luthier.protocols.reconstruction import ReconstructionBackend

__all__ = [
    "ArtifactCache",
    "FeatureExtractor",
    "ImageDecoder",
    "ImageDiscoverer",
    "NullArtifactCache",
    "NullProgressReporter",
    "PointCloudFilter",
    "PointCloudSerializer",
    "ProgressReporter",
    "ReconstructionBackend",
]
