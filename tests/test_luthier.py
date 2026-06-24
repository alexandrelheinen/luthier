"""Package metadata tests."""

from luthier import __version__, reconstruct_from_directory


def test_version_is_semver_like() -> None:
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_public_api_exports_reconstruct() -> None:
    assert callable(reconstruct_from_directory)
