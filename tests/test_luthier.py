"""Tests for the luthier package."""

from luthier import hello, __version__


def test_hello() -> None:
    assert hello() == "Hello from luthier!"


def test_version() -> None:
    assert __version__ == "0.1.0"
