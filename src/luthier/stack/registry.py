"""Algorithm registry — maps stack.yml algorithm names to implementations.

Registration happens at import time in each ``{algorithm_name}.py`` module or
via explicit ``register()`` calls from layer ``__init__.py`` files during M1.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from luthier.stack.config import SlotConfig

T = TypeVar("T")
Factory = Callable[[SlotConfig], T]

_REGISTRY: dict[str, dict[str, Factory[Any]]] = {}


def register(layer: str, algorithm: str, factory: Factory[Any]) -> None:
    """Register a factory for ``layer`` + ``algorithm`` (stack.yml value)."""
    _REGISTRY.setdefault(layer, {})[algorithm] = factory


def resolve(layer: str, slot: SlotConfig) -> Any:
    """Instantiate the implementation selected by a stack slot."""
    if slot.algorithm is None:
        msg = f"No algorithm configured for layer slot (null): {layer}"
        raise ValueError(msg)
    try:
        factory = _REGISTRY[layer][slot.algorithm]
    except KeyError as exc:
        msg = (
            f"Unknown algorithm {slot.algorithm!r} for layer {layer!r}. "
            "Implement it in {algorithm_name}.py and register it."
        )
        raise KeyError(msg) from exc
    return factory(slot)


def registered_algorithms(layer: str) -> frozenset[str]:
    """Return algorithm names registered for a layer (testing / introspection)."""
    return frozenset(_REGISTRY.get(layer, {}))
