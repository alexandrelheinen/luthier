"""Command-line interface for luthier."""

from __future__ import annotations

import argparse
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from luthier import __version__
from luthier.exceptions import LuthierError, NotImplementedPipelineError
from luthier.pipeline import reconstruct_from_directory

CLI_PROG = "luthier"
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_NOT_IMPLEMENTED = 2


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the ``luthier`` CLI."""
    parser = argparse.ArgumentParser(
        prog=CLI_PROG,
        description=("Reconstruct a 3D point cloud from photographs (photogrammetry)."),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    input_group = parser.add_argument_group("input sources")
    input_group.add_argument(
        "--dir",
        dest="image_dir",
        type=Path,
        metavar="DIR",
        help="Directory containing input image files (local filesystem).",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        type=Path,
        metavar="FILE",
        help=(
            "Output point cloud file path. Defaults to a temporary .ply file; "
            "the chosen path is printed on success."
        ),
    )
    parser.add_argument(
        "--stack",
        dest="stack_path",
        type=Path,
        metavar="FILE",
        help=(
            "Algorithm stack YAML file. Defaults to config/stack.yml in the "
            "project checkout or install layout."
        ),
    )
    return parser


def resolve_output_path(output_path: Path | None) -> Path:
    """Return an explicit output path or create a temporary ``.ply`` file."""
    if output_path is not None:
        return output_path.expanduser().resolve()
    with tempfile.NamedTemporaryFile(
        suffix=".ply",
        prefix="luthier-",
        delete=False,
    ) as handle:
        return Path(handle.name).resolve()


def validate_args(
    args: argparse.Namespace,
) -> tuple[Path, Path | None, Path | None]:
    """Validate parsed CLI arguments.

    Returns:
        ``(image_dir, output_path, stack_path)`` with paths expanded and
        resolved where applicable.
    """
    if args.image_dir is None:
        msg = "Missing required input. Provide --dir DIR with a folder of images."
        raise LuthierError(msg)
    image_dir = args.image_dir.expanduser().resolve()
    if not image_dir.exists():
        msg = f"Image directory does not exist: {image_dir}"
        raise LuthierError(msg)
    if not image_dir.is_dir():
        msg = f"Image path is not a directory: {image_dir}"
        raise LuthierError(msg)
    output_path = (
        args.output_path.expanduser().resolve()
        if args.output_path is not None
        else None
    )
    stack_path = (
        args.stack_path.expanduser().resolve() if args.stack_path is not None else None
    )
    return image_dir, output_path, stack_path


def run(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, run reconstruction, and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        image_dir, requested_output, stack_path = validate_args(args)
        output_path = resolve_output_path(requested_output)
        reconstruct_from_directory(
            image_dir,
            output_path=output_path,
            stack_path=stack_path,
        )
    except NotImplementedPipelineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_NOT_IMPLEMENTED
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except LuthierError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    print(output_path)
    return EXIT_SUCCESS


def main() -> None:
    """Console entry point for ``luthier``."""
    raise SystemExit(run())
