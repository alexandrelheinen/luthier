"""Observability protocol — cross-cutting progress and telemetry.

See docs/architecture.md §11.3 and decisions.md AD-10. The Interface layer
injects a reporter into the pipeline; algorithm modules emit progress through it
without importing the CLI or any transport. The default is a no-op.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProgressReporter(Protocol):
    """Receive progress and telemetry from pipeline stages."""

    def start(self, stage: str, total: int | None = None) -> None:
        """Signal that ``stage`` started, optionally with a total unit count."""

    def advance(self, stage: str, n: int = 1) -> None:
        """Report ``n`` more completed units of work in ``stage``."""

    def event(self, stage: str, message: str, **fields: Any) -> None:
        """Emit a structured log / telemetry point for ``stage``."""

    def finish(self, stage: str) -> None:
        """Signal that ``stage`` completed."""


class NullProgressReporter:
    """Default reporter that discards everything (zero overhead)."""

    def start(self, stage: str, total: int | None = None) -> None:
        return None

    def advance(self, stage: str, n: int = 1) -> None:
        return None

    def event(self, stage: str, message: str, **fields: Any) -> None:
        return None

    def finish(self, stage: str) -> None:
        return None
