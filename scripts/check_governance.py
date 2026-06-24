#!/usr/bin/env python3
"""Governance checks that mechanically enforce the project method.

This script is the executable side of CONTRIBUTING.md § "Method enforcement
(CI/CD)". It is intentionally dependency-light (stdlib + PyYAML, a dev
dependency) so it runs locally and in the ``governance`` CI job identically.

Checks (all hard failures):

1. Single constitution      — no duplicate AI-guideline files exist.
2. Spec artifacts present    — required docs and README exist.
3. Requirement traceability  — every ``AC-*`` in the spec is referenced by a
   test or by docs/testing.md.
4. Stack/code consistency    — every ``{algorithm_name}.py`` module's ``name``
   matches its filename; every stack.yml layer/slot is documented and backed by
   a layer package.

Run from the repository root::

    python scripts/check_governance.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files that would duplicate CONTRIBUTING.md as a "constitution". The project
# keeps a single guideline document; these must not exist.
FORBIDDEN_GUIDELINE_PATHS = (
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".windsurfrules",
    ".cursorrules",
    ".cursor/rules",
    ".github/copilot-instructions.md",
)

REQUIRED_DOCS = (
    "README.md",
    "CONTRIBUTING.md",
    "docs/specification.md",
    "docs/architecture.md",
    "docs/testing.md",
    "docs/decisions.md",
    "docs/algorithms.md",
)

# Layer packages that may host one-file-per-algorithm strategy modules.
ALGORITHM_LAYERS = ("io", "features", "reconstruction", "postprocess", "output")

AC_PATTERN = re.compile(r"AC-[A-Z]+-\d+")


def _add(errors: list[str], message: str) -> None:
    errors.append(message)


def check_single_constitution(errors: list[str]) -> None:
    for rel in FORBIDDEN_GUIDELINE_PATHS:
        if (REPO_ROOT / rel).exists():
            _add(
                errors,
                f"Duplicate guideline file present: {rel}. CONTRIBUTING.md is the "
                "single constitution; remove the duplicate.",
            )


def check_required_docs(errors: list[str]) -> None:
    for rel in REQUIRED_DOCS:
        if not (REPO_ROOT / rel).is_file():
            _add(errors, f"Required documentation artifact missing: {rel}")


def check_traceability(errors: list[str]) -> None:
    spec = REPO_ROOT / "docs" / "specification.md"
    if not spec.is_file():
        return  # reported by check_required_docs
    defined = set(AC_PATTERN.findall(spec.read_text(encoding="utf-8")))

    referenced: set[str] = set()
    search_roots = [REPO_ROOT / "tests", REPO_ROOT / "docs" / "testing.md"]
    for root in search_roots:
        files = root.rglob("*.py") if root.is_dir() else [root]
        for path in files:
            if path.is_file():
                referenced.update(
                    AC_PATTERN.findall(path.read_text(encoding="utf-8"))
                )

    missing = sorted(defined - referenced)
    if missing:
        _add(
            errors,
            "Acceptance criteria with no verification (add a test or a "
            f"docs/testing.md mapping): {', '.join(missing)}",
        )


def _module_name_assignment(path: Path) -> str | None:
    """Return the value of a top-level ``name = "..."`` assignment, if any."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if (
                isinstance(target, ast.Name)
                and target.id == "name"
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                return node.value.value
    return None


def check_algorithm_module_names(errors: list[str]) -> None:
    base = REPO_ROOT / "src" / "luthier"
    for layer in ALGORITHM_LAYERS:
        layer_dir = base / layer
        if not layer_dir.is_dir():
            _add(errors, f"Missing algorithm layer package: src/luthier/{layer}")
            continue
        for module in sorted(layer_dir.glob("*.py")):
            if module.name == "__init__.py":
                continue
            declared = _module_name_assignment(module)
            if declared is None:
                continue  # shim / contract module, not a registered algorithm
            if declared != module.stem:
                _add(
                    errors,
                    f"Algorithm module name mismatch: {module.relative_to(REPO_ROOT)} "
                    f"declares name={declared!r} but file stem is {module.stem!r}. "
                    "File name must match the stack.yml algorithm id.",
                )


def check_stack_consistency(errors: list[str]) -> None:
    stack_path = REPO_ROOT / "config" / "stack.yml"
    if not stack_path.is_file():
        _add(errors, "Missing config/stack.yml")
        return
    try:
        import yaml
    except ModuleNotFoundError:
        _add(errors, "PyYAML not installed; run 'pip install -e .[dev]'")
        return

    raw = yaml.safe_load(stack_path.read_text(encoding="utf-8"))
    layers = (raw or {}).get("layers", {})
    architecture = (REPO_ROOT / "docs" / "architecture.md").read_text(
        encoding="utf-8"
    )
    base = REPO_ROOT / "src" / "luthier"

    for layer, slots in layers.items():
        if not (base / layer).is_dir():
            _add(
                errors,
                f"stack.yml references layer {layer!r} with no package "
                f"src/luthier/{layer}",
            )
        if not isinstance(slots, dict):
            continue
        for slot, slot_cfg in slots.items():
            if slot not in architecture:
                _add(
                    errors,
                    f"stack.yml slot {layer}.{slot} is not documented in "
                    "docs/architecture.md (drift between config and design).",
                )
            algorithm = (slot_cfg or {}).get("algorithm")
            if not algorithm:
                continue
            module = base / layer / f"{algorithm}.py"
            if module.is_file():
                declared = _module_name_assignment(module)
                if declared is not None and declared != algorithm:
                    _add(
                        errors,
                        f"stack.yml {layer}.{slot} -> {algorithm!r} but module "
                        f"declares name={declared!r}.",
                    )


def main() -> int:
    errors: list[str] = []
    check_single_constitution(errors)
    check_required_docs(errors)
    check_traceability(errors)
    check_algorithm_module_names(errors)
    check_stack_consistency(errors)

    if errors:
        print("Governance check FAILED:\n", file=sys.stderr)
        for item in errors:
            print(f"  - {item}", file=sys.stderr)
        print(
            f"\n{len(errors)} problem(s). See CONTRIBUTING.md "
            "# method-enforcement-cicd.",
            file=sys.stderr,
        )
        return 1
    print("Governance check passed: method invariants hold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
