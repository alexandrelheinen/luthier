# Luthier — testing strategy (TDD + V-cycle)

This document defines how tests map to [specification.md](specification.md)
acceptance criteria and how contributors apply TDD inside the V-cycle described
in [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## 1. Verification pyramid

```text
                    Acceptance  (AC-REC-*, golden dataset)
                   ─────────────────────────────────────
                  Integration   (CLI → pipeline → io, stubbed SfM)
                 ─────────────────────────────────────────────
                Unit            (models, discover_images, PLY, CLI helpers)
               ───────────────────────────────────────────────────
```

| Level | Directory / marker | Proves |
| --- | --- | --- |
| **Unit** | `tests/test_*.py` (default) | Functions and types in isolation |
| **Integration** | `tests/test_cli.py`, `tests/test_pipeline.py` | Modules wired together |
| **Acceptance** | `@pytest.mark.acceptance` | End-to-end on golden images |

---

## 2. TDD workflow per module

For each behavior in the specification:

1. **Red** — Add or extend a test that encodes one acceptance criterion (or a
   fragment of it). The test must fail for the right reason.
2. **Green** — Implement the minimum code in `src/luthier/` to pass.
3. **Refactor** — Clean types and duplication; keep mypy strict green.

Do not implement reconstruction stages without a failing test linked to an
`AC-*` ID in [specification.md](specification.md).

---

## 3. Test modules and traceability

| Test file | Acceptance criteria | Status |
| --- | --- | --- |
| `tests/test_cli.py` | AC-CLI-01 … AC-CLI-06 | Active (framework) |
| `tests/test_models.py` | Domain invariants | Active |
| `tests/test_images.py` | AC-IN-01, AC-IN-02 | Active |
| `tests/test_pointcloud.py` | AC-OUT-01, AC-OUT-02 | Red (not implemented) |
| `tests/test_pipeline.py` | AC-REC-* stubs, not-implemented | Red |
| `tests/test_acceptance.py` | AC-REC-01 … AC-REC-04 | Skipped until golden data |

---

## 4. Pytest markers

Configured in `pyproject.toml`:

| Marker | Meaning |
| --- | --- |
| `acceptance` | Golden dataset end-to-end tests (slow, needs `tests/data/golden/`) |
| `not_implemented` | Specifies future behavior; may xfail until milestone |

Run subsets:

```bash
# Default CI: unit + integration, no acceptance
pytest

# Only acceptance (after golden data is added)
pytest -m acceptance

# Everything including expected failures
pytest --runxfail
```

---

## 5. CLI testing approach

Use `luthier.cli.run(argv)` with explicit `argv` lists to avoid subprocess
overhead. Assert:

- Return code (`0`, `1`, `2`)
- `stderr` messages (caplog or redirect with `capsys`)
- `stdout` path when applicable

Example pattern:

```python
def test_missing_dir_returns_error() -> None:
    assert run([]) == 1
```

Entry point smoke test:

```bash
luthier --help
python -m luthier --version
```

---

## 6. Point cloud / PLY testing

When `write_point_cloud` is implemented:

1. **Unit:** Build a small `PointCloud` (3 vertices), write to `tmp_path`, read
   back header and byte length (`15 * N` bytes after header).
2. **Unit:** Assert header contains `format binary_little_endian 1.0` and six
   property lines.
3. **Integration:** `reconstruct_from_directory` on golden set produces parseable
   PLY.

Optional dev dependency for tests (future PR): `numpy` for byte unpacking.

---

## 7. Golden dataset (acceptance)

### 7.1 Location

```text
tests/data/golden/
  images/          # ≥ 10 JPEG/PNG photographs
  README.md        # provenance and license
```

### 7.2 Provenance requirements

The golden `README.md` must state:

- Source of images (self-captured, public dataset URL)
- License allowing redistribution in the repo or CI artifact
- Expected minimum point count (default: 1 000 per AC-REC-01)

### 7.3 Until golden data exists

`tests/test_acceptance.py` uses `@pytest.mark.acceptance` and
`pytest.importorskip` or `skipif` when `tests/data/golden/images` is absent.
CI runs acceptance tests in **deselected** mode by default (`addopts -m "not acceptance"`).

When images are added, remove deselection or add a dedicated CI job.

---

## 8. Coverage expectations

| Area | Minimum expectation |
| --- | --- |
| `luthier.cli` | All branches of `validate_args`, `resolve_output_path`, `run` |
| `luthier.io.images` | Discovery success and empty directory |
| `luthier.models` | Validation errors on `Point3D`, `LocalImageInput` |
| `luthier.pipeline` | Not-implemented path; future success path |
| `luthier.io.pointcloud` | Format guard; full write path when implemented |

CI command:

```bash
pytest --cov=luthier --cov-report=term-missing
```

---

## 9. CI mapping

| CI step | V-cycle right side |
| --- | --- |
| `black --check` | Coding standard |
| `ruff check` | Lint / import order |
| `mypy` | Detailed design (types) |
| `pytest` | Unit + integration tests |
| `luthier --help` | AC-CLI-01 smoke |
| (future) `pytest -m acceptance` | AC-REC-* on golden data |

See [.github/workflows/ci.yml](../.github/workflows/ci.yml).

---

## 10. Regression policy

1. Reproduce with a failing test (red).
2. Fix implementation (green).
3. Reference the `AC-*` ID or issue in the commit message.

---

## 11. Adding a new test checklist

- [ ] Linked to at least one `AC-*` criterion in `specification.md`
- [ ] Single behavior per test function
- [ ] Fully typed (`mypy` clean)
- [ ] No network or GPU in unit tests unless marked and optional
- [ ] Golden / acceptance tests marked `acceptance`
