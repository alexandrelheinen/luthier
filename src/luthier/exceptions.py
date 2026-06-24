"""Domain-specific exceptions for the luthier reconstruction pipeline."""


class LuthierError(Exception):
    """Base exception for all luthier errors."""


class InvalidInputError(LuthierError):
    """Raised when user-provided input is missing, unreadable, or invalid."""


class ReconstructionError(LuthierError):
    """Raised when the reconstruction pipeline fails."""


class NotImplementedPipelineError(LuthierError):
    """Raised when a pipeline stage has not been implemented yet."""
