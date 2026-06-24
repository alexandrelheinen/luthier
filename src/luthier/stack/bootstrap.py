"""Algorithm registration and discovery (AD-09).

The registry in :mod:`luthier.stack.registry` is empty until algorithm modules
register themselves. This module performs that wiring for luthier's built-in
strategies and for third-party plugins advertised via the ``luthier.algorithms``
entry-point group. See docs/architecture.md §11.2.

A built-in strategy is a module exposing ``name`` plus its layer protocol method
(``discover`` / ``decode`` / ``extract`` / ``reconstruct`` / ``filter`` /
``write``); the module itself is registered as the Strategy.
"""

from __future__ import annotations

import importlib
from importlib import metadata
from types import ModuleType

from luthier.stack.config import SlotConfig
from luthier.stack.registry import register

ENTRY_POINT_GROUP = "luthier.algorithms"

# Layer -> built-in modules providing one strategy each (one algorithm per file).
_BUILTIN_MODULES: dict[str, tuple[str, ...]] = {
    "io": ("luthier.io.pathlib_discover", "luthier.io.opencv_decode"),
    "features": ("luthier.features.colmap_sift",),
    "reconstruction": ("luthier.reconstruction.colmap_incremental",),
    "postprocess": ("luthier.postprocess.statistical_outlier_removal",),
    "output": ("luthier.output.ply_binary_le",),
}

_loaded = False


def _register_module(layer: str, module: ModuleType) -> None:
    name = getattr(module, "name", None)
    if not isinstance(name, str):
        msg = f"Algorithm module {module.__name__} has no string 'name' attribute"
        raise ValueError(msg)

    def factory(slot: SlotConfig, _module: ModuleType = module) -> ModuleType:
        return _module

    register(layer, name, factory)


def load_builtin_algorithms() -> None:
    """Import and register luthier's built-in strategy modules (idempotent)."""
    for layer, module_paths in _BUILTIN_MODULES.items():
        for module_path in module_paths:
            module = importlib.import_module(module_path)
            _register_module(layer, module)


def load_plugins() -> None:
    """Register third-party strategies from the ``luthier.algorithms`` group.

    Each entry point is loaded for its import side effects; if it resolves to a
    zero-argument callable, it is also called as an explicit registrar.
    """
    for entry in metadata.entry_points(group=ENTRY_POINT_GROUP):
        loaded = entry.load()
        if callable(loaded):
            loaded()


def load_algorithms(*, force: bool = False) -> None:
    """Load built-in and plugin algorithms once.

    Args:
        force: Re-run loading even if it already ran in this process.
    """
    global _loaded
    if _loaded and not force:
        return
    load_builtin_algorithms()
    load_plugins()
    _loaded = True
