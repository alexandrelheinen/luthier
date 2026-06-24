"""Tests for stack.yml loading."""

from pathlib import Path

import pytest

from luthier.stack import StackConfig, load_stack_config


def test_load_default_stack_config() -> None:
    config = load_stack_config(Path("config/stack.yml"))
    assert isinstance(config, StackConfig)
    assert config.version == 1
    assert config.name == "m1-sparse-colmap-default"

    features = config.slot("features", "extractor")
    assert features.algorithm == "colmap_sift"
    assert features.params["max_num_features"] == 8192

    dense = config.slot("reconstruction", "dense")
    assert dense.algorithm is None

    serializer = config.slot("output", "serializer")
    assert serializer.algorithm == "ply_binary_le"


def test_load_stack_config_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_stack_config(tmp_path / "missing.yml")


def test_load_stack_config_invalid_root(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yml"
    bad.write_text("not a mapping\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        load_stack_config(bad)


def test_load_stack_config_invalid_version(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yml"
    bad.write_text("version: one\nname: x\nlayers: {}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="version"):
        load_stack_config(bad)


def test_load_stack_config_invalid_slot(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yml"
    bad.write_text(
        "version: 1\nname: x\nlayers:\n  io: not-a-map\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Invalid layer"):
        load_stack_config(bad)


def test_stack_config_slot_missing() -> None:
    config = load_stack_config(Path("config/stack.yml"))
    with pytest.raises(KeyError, match="Unknown stack slot"):
        config.slot("missing", "extractor")


def test_load_stack_config_invalid_algorithm_type(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yml"
    bad.write_text(
        "version: 1\nname: x\nlayers:\n  io:\n    discover:\n"
        "      algorithm: 1\n      params: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="algorithm must be string"):
        load_stack_config(bad)


def test_load_stack_config_invalid_params_type(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yml"
    bad.write_text(
        "version: 1\nname: x\nlayers:\n  io:\n    discover:\n"
        "      algorithm: pathlib_discover\n      params: []\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="params must be a mapping"):
        load_stack_config(bad)
