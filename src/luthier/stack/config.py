"""Stack configuration loading and validation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class SlotConfig:
    """One configurable slot inside a layer (e.g. features.extractor)."""

    algorithm: str | None
    params: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class StackConfig:
    """Parsed ``stack.yml`` — selects algorithms per layer slot."""

    version: int
    name: str
    description: str
    layers: Mapping[str, Mapping[str, SlotConfig]]

    def slot(self, layer: str, slot: str) -> SlotConfig:
        """Return slot config or raise ``KeyError`` with a clear message."""
        try:
            return self.layers[layer][slot]
        except KeyError as exc:
            msg = f"Unknown stack slot {layer}.{slot}"
            raise KeyError(msg) from exc


def load_stack_config(path: Path | None = None) -> StackConfig:
    """Load and validate a stack YAML file.

    Args:
        path: Config file path. Defaults to ``config/stack.yml`` under the
            package project root when run from a checkout.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the YAML structure is invalid.
    """
    import yaml

    config_path = path or _default_stack_path()
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return _parse_stack_config(raw, source=str(config_path))


def _default_stack_path() -> Path:
    """Best-effort default stack file for development checkouts."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "config" / "stack.yml"
        if candidate.is_file():
            return candidate
    msg = "Default config/stack.yml not found; pass path explicitly."
    raise FileNotFoundError(msg)


def _parse_stack_config(raw: object, *, source: str) -> StackConfig:
    if not isinstance(raw, dict):
        msg = f"Stack config root must be a mapping: {source}"
        raise ValueError(msg)

    version = raw.get("version")
    name = raw.get("name")
    if not isinstance(version, int) or not isinstance(name, str):
        msg = f"Stack config requires integer version and string name: {source}"
        raise ValueError(msg)

    description = raw.get("description", "")
    if not isinstance(description, str):
        msg = f"description must be a string: {source}"
        raise ValueError(msg)

    layers_raw = raw.get("layers")
    if not isinstance(layers_raw, dict):
        msg = f"layers must be a mapping: {source}"
        raise ValueError(msg)

    layers: dict[str, dict[str, SlotConfig]] = {}
    for layer_name, slots in layers_raw.items():
        if not isinstance(layer_name, str) or not isinstance(slots, dict):
            msg = f"Invalid layer entry in {source}"
            raise ValueError(msg)
        layer_slots: dict[str, SlotConfig] = {}
        for slot_name, slot_raw in slots.items():
            if not isinstance(slot_name, str) or not isinstance(slot_raw, dict):
                msg = f"Invalid slot {layer_name}.{slot_name} in {source}"
                raise ValueError(msg)
            algorithm = slot_raw.get("algorithm")
            if algorithm is not None and not isinstance(algorithm, str):
                msg = f"algorithm must be string or null: {layer_name}.{slot_name}"
                raise ValueError(msg)
            params = slot_raw.get("params", {})
            if not isinstance(params, dict):
                msg = f"params must be a mapping: {layer_name}.{slot_name}"
                raise ValueError(msg)
            layer_slots[slot_name] = SlotConfig(
                algorithm=algorithm,
                params=params,
            )
        layers[layer_name] = layer_slots

    return StackConfig(
        version=version,
        name=name,
        description=description,
        layers=layers,
    )
