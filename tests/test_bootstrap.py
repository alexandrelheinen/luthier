"""Tests for algorithm bootstrap and cross-cutting protocols (AD-09..AD-11)."""

from __future__ import annotations

import importlib.metadata
from typing import Any

import pytest

from luthier.protocols import (
    ArtifactCache,
    NullArtifactCache,
    NullProgressReporter,
    ProgressReporter,
)
from luthier.stack import (
    SlotConfig,
    bootstrap,
    load_algorithms,
    load_builtin_algorithms,
    registered_algorithms,
    resolve,
)


def test_load_builtin_algorithms_populates_registry() -> None:
    load_builtin_algorithms()
    assert "pathlib_discover" in registered_algorithms("io")
    assert "opencv_decode" in registered_algorithms("io")
    assert "colmap_sift" in registered_algorithms("features")
    assert "colmap_incremental" in registered_algorithms("reconstruction")
    assert "colmap_reprojection_filter" in registered_algorithms("postprocess")
    assert "statistical_outlier_removal" in registered_algorithms("postprocess")
    assert "ply_binary_le" in registered_algorithms("output")


def test_resolve_returns_named_strategy_module() -> None:
    load_builtin_algorithms()
    strategy = resolve("output", SlotConfig(algorithm="ply_binary_le"))
    assert strategy.name == "ply_binary_le"
    assert callable(strategy.write)


def test_load_algorithms_is_idempotent() -> None:
    bootstrap._loaded = False
    load_algorithms()
    assert bootstrap._loaded is True
    load_algorithms()  # second call returns early; must not raise


def test_load_plugins_invokes_callable_entry_points(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    class _FakeEntry:
        def load(self) -> Any:
            def registrar() -> None:
                calls.append("registered")

            return registrar

    def fake_entry_points(*, group: str) -> list[_FakeEntry]:
        assert group == bootstrap.ENTRY_POINT_GROUP
        return [_FakeEntry()]

    monkeypatch.setattr(importlib.metadata, "entry_points", fake_entry_points)
    bootstrap.load_plugins()
    assert calls == ["registered"]


def test_null_progress_reporter_satisfies_protocol() -> None:
    reporter: ProgressReporter = NullProgressReporter()
    assert isinstance(reporter, ProgressReporter)
    reporter.start("features", total=3)
    reporter.advance("features", 1)
    reporter.event("features", "extracted", count=10)
    reporter.finish("features")


def test_null_artifact_cache_satisfies_protocol() -> None:
    cache: ArtifactCache = NullArtifactCache()
    assert isinstance(cache, ArtifactCache)
    cache_key = cache.key("features", inputs=("a", "b"))
    assert isinstance(cache_key, str)
    assert cache.get(cache_key) is None
    cache.put(cache_key, artifact=object())
    assert cache.get(cache_key) is None
