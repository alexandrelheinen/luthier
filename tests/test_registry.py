"""Tests for algorithm registry."""

from __future__ import annotations

import pytest

from luthier.stack.config import SlotConfig
from luthier.stack.registry import register, registered_algorithms, resolve


def test_register_and_resolve() -> None:
    layer = "test_layer_register"

    def factory(slot: SlotConfig) -> str:
        return f"{slot.algorithm}:{slot.params.get('x', 0)}"

    register(layer, "dummy_algo", factory)
    assert "dummy_algo" in registered_algorithms(layer)

    result = resolve(layer, SlotConfig(algorithm="dummy_algo", params={"x": 1}))
    assert result == "dummy_algo:1"


def test_resolve_null_algorithm() -> None:
    with pytest.raises(ValueError, match="null"):
        resolve("features", SlotConfig(algorithm=None))


def test_resolve_unknown_algorithm() -> None:
    with pytest.raises(KeyError, match="Unknown algorithm"):
        resolve("features", SlotConfig(algorithm="does_not_exist"))
