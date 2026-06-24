# Luthier — architecture decisions (Step 1, M1)

This document records **resolved** open decisions from
[specification.md](specification.md) §14. It is the spec-anchored input for M1
implementation (sparse SfM → binary PLY). For the full algorithm catalog see
[algorithms.md](algorithms.md).

**Status:** Approved for M1 unless a maintainer opens a follow-up issue.

---

## AD-01 — Minimum image count (was OD-01)

| Field | Decision |
| --- | --- |
| **Reconstruction minimum** | **2** images — `InvalidInputError` if fewer |
| **Golden acceptance set** | **≥ 10** images with overlap (AC-REC-01) |
| **Rationale** | Two views are the mathematical minimum for stereo; ten images give stable CI acceptance |

---

## AD-02 — Directory layout (was OD-02)

| Field | Decision |
| --- | --- |
| **Recursive scan** | **No** in M1 — only files directly in `--dir` |
| **Rationale** | Predictable inputs; recursive scan deferred to a future spec amendment |

---

## AD-03 — SfM backend (was OD-03)

| Field | Decision |
| --- | --- |
| **Primary backend** | **[pycolmap](https://github.com/colmap/pycolmap)** (Python bindings to COLMAP) |
| **Fallback** | COLMAP CLI on `PATH` via subprocess if pycolmap unavailable (optional adapter) |
| **Rejected for M1** | Pure-Python SfM from scratch — too slow to reach quality; reinventing COLMAP |
| **Rationale** | Production-grade sparse reconstruction; each pipeline stage maps to a mature library; luthier owns orchestration, types, I/O, tests |

### Pipeline block → third-party owner

| luthier module | Responsibility (ours) | Third-party block |
| --- | --- | --- |
| `io.images` | Discover paths, validate count | stdlib `pathlib` |
| `sfm.colmap` | Adapter interface, error mapping | **pycolmap** (feature extraction, matching, incremental SfM) |
| `io.pointcloud` | PLY contract, `PointCloud` → bytes | stdlib `struct` (+ **numpy** optional for bulk arrays) |
| `pipeline` | Stage order, logging hooks, result types | — (orchestration only) |
| `cli` | Args, exit codes | stdlib `argparse` |

**Principle:** use third-party libraries for **individual algorithm blocks**; keep
a **single instrumented pipeline** under `luthier.pipeline` with unit and
integration tests at every boundary.

---

## AD-04 — Runtime dependencies (M1)

Approved for `pip install luthier` (or `pip install luthier[reconstruction]` if we split heavy deps):

| Package | Role |
| --- | --- |
| `numpy` | Point coordinates, pycolmap interop |
| `pycolmap` | Sparse SfM pipeline |
| `opencv-python-headless` | Image read/metadata where pycolmap does not cover discovery |

COLMAP algorithms ship with pycolmap wheels on supported platforms; no separate
COLMAP install required for the default path.

---

## AD-05 — Viewer (unchanged)

| Field | Decision |
| --- | --- |
| **Viewer** | External **[CloudCompare](https://www.cloudcompare.org/)** |
| **Output format** | Binary **PLY** with RGB |
| **In scope** | No embedded Python viewer (no matplotlib / Plotly for point clouds) |

---

## AD-06 — Unit test coverage gate

| Field | Decision |
| --- | --- |
| **Minimum line coverage** | **80%** on `src/luthier` for default CI unit tests |
| **Configuration** | `fail_under` in `[tool.coverage.report]` in `pyproject.toml` |
| **Enforcement** | `pytest --cov=luthier` fails when below threshold |

---

## AD-07 — Second input source (was OD-04)

| Field | Decision |
| --- | --- |
| **Status** | **Deferred** — new spec section when chosen |
| **Constraint** | Must normalize to local `Path` list before `pipeline` |

---

## AD-08 — Config-driven algorithm stack

| Field | Decision |
| --- | --- |
| **Pattern** | Strategy + Registry + Pipeline (see [architecture.md §10](architecture.md#10-config-driven-algorithm-stack)) |
| **Config file** | [`config/stack.yml`](../config/stack.yml) — swap `algorithm:` per slot |
| **Naming** | One module per algorithm: `src/luthier/{layer}/{algorithm_name}.py` |
| **Shared code** | Domain models + `protocols/` + `stack/` only; no algorithm names in `pipeline.py` |
| **Rationale** | M1 uses pycolmap but later slots (hloc, Open3D filters) must be YAML-swappable |

---

## Decision log

| ID | Date | Summary |
| --- | --- | --- |
| AD-01 … AD-07 | 2026-06-24 | Step 1 closed; pycolmap backend; 80% coverage gate |
| AD-08 | 2026-06-24 | `stack.yml` + Strategy/Registry; `{algorithm_name}.py` modules |
