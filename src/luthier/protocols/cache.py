"""Artifact cache protocol — cross-cutting, for resumable/distributed runs.

See docs/architecture.md §11.4 and decisions.md AD-11. Caching is opt-in per
stage and must never change results — only whether a stage is recomputed. The
default null cache always misses, preserving current behavior.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ArtifactCache(Protocol):
    """Persist and retrieve intermediate pipeline artifacts by content key."""

    def key(self, stage: str, inputs: object) -> str:
        """Return a deterministic cache key for ``stage`` given ``inputs``."""

    def get(self, key: str) -> object | None:
        """Return the cached artifact for ``key`` or ``None`` on miss."""

    def put(self, key: str, artifact: object) -> None:
        """Store ``artifact`` under ``key``."""


class NullArtifactCache:
    """Default cache that never stores or returns artifacts (always misses)."""

    def key(self, stage: str, inputs: object) -> str:
        return f"{stage}:null"

    def get(self, key: str) -> object | None:
        return None

    def put(self, key: str, artifact: object) -> None:
        return None
