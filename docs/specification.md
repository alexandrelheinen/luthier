# Luthier — product specification (SDD)

This document is the **spec-as-source** artifact for the luthier photogrammetry
library. Code, tests, and user documentation must be derived from and validated
against this specification.

**Status:** v0.3.0 — M1 sparse SfM pipeline implemented (local directory → binary PLY).

**Related documents:**

| Document | Role |
| --- | --- |
| [architecture.md](architecture.md) | System design and module boundaries |
| [algorithms.md](algorithms.md) | Algorithm & OSS library research per layer |
| [testing.md](testing.md) | TDD strategy, test levels, and CI mapping |
| [../README.md](../README.md) | User-facing documentation and quick start |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Development constitution (SDD + V-cycle + TDD) |
| [decisions.md](decisions.md) | Resolved architecture decisions |

---

## 1. Intent

**luthier** is a Python library and CLI that reconstructs a **3D point cloud**
from a set of **overlapping photographs**, using photogrammetry (Structure from
Motion and related stages).

The first supported **input source** is the **local filesystem**: a directory of
image files. Additional input sources (remote URLs, object storage, databases)
will be specified in future revisions without breaking the local workflow.

The library produces a **single output artifact** per run: a **colored point
cloud file** suitable for inspection in an external open-source viewer.

---

## 2. Scope

### 2.1 In scope (v0.2.0 — specification and framework)

| Item | Description |
| --- | --- |
| CLI | `luthier --dir DIR [--output FILE]` |
| Python API | `reconstruct_from_directory(image_dir, output_path=...)` |
| Local input | Directory of raster images on disk |
| Output format | Binary **PLY** with per-vertex RGB (default and only format in v0.2.0) |
| Image discovery | Enumerate supported images in the input directory (non-recursive) |
| Error reporting | Clear errors for invalid input; exit code contract for CLI |
| Documentation | README, architecture, this specification, testing strategy |
| Tests | Specification tests (unit + integration + acceptance scaffolding) |

### 2.2 In scope (M1 — sparse SfM, v0.3.0)

| Milestone | Deliverable | Status |
| --- | --- | --- |
| M1 — Sparse SfM | Camera poses + sparse colored point cloud | **Implemented** |
| M2 — Dense / MVS | Denser point cloud (optional refinement stage) | Planned |
| M3 — Second input source | Non-local image source (TBD by follow-up spec) | Planned |
| M4 — Formats | Optional LAZ/PCD export | Planned |

### 2.3 Out of scope (v0.2.0)

- Mesh generation, texturing, or UV mapping
- GUI or web viewer bundled with luthier
- Video input or live capture
- GPU requirement in the specification (implementation may use GPU optionally)
- Cloud deployment or hosted reconstruction service

---

## 3. Stakeholders and use cases

| Actor | Use case |
| --- | --- |
| Developer | Call `reconstruct_from_directory` from Python pipelines |
| Operator | Run `luthier --dir ./photos` from the shell |
| Reviewer | Open output `.ply` in **CloudCompare** for quality inspection |

---

## 4. Input specification — local directory (`--dir`)

### 4.1 CLI

```text
luthier --dir DIR [--output FILE]
```

| Argument | Required | Description |
| --- | --- | --- |
| `--dir DIR` | **Yes** (v0.2.0) | Path to a directory containing input images |
| `--output FILE` | No | Output point cloud path. If omitted, a temporary `.ply` file is created and its path is printed to stdout on success |
| `--version` | No | Print version and exit |

Future input flags (not implemented; reserved in planning):

| Argument | Purpose |
| --- | --- |
| `--url URL` | Remote archive or manifest (future) |
| `--manifest FILE` | JSON/YAML list of image paths or URLs (future) |

### 4.2 Image directory rules

1. `--dir` must exist and be a directory.
2. Only **files directly inside** `DIR` are considered (no recursive subfolders in v0.2.0).
3. Supported suffixes (case-insensitive): `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`, `.bmp`.
4. At least **two** images are required for reconstruction (enforced at pipeline stage; discovery may return fewer and fail later with a clear error).
5. For acceptance testing, the golden dataset must contain **≥ 10** images with sufficient overlap (see [testing.md](testing.md)).

### 4.3 Python API

```python
from pathlib import Path
from luthier import reconstruct_from_directory

result = reconstruct_from_directory(
    Path("/data/photos"),
    output_path=Path("/data/out/scene.ply"),
    stack_path=Path("config/stack.yml"),  # optional
)
print(result.output_path, result.point_cloud.count, len(result.cameras))
```

---

## 5. Output specification — point cloud format

### 5.1 Default format: binary PLY

**Rationale:** PLY is the de facto interchange format in photogrammetry (COLMAP,
MeshLab, CloudCompare, Open3D). Binary PLY balances file size and broad tool
support.

| Property | Value |
| --- | --- |
| Format identifier | `ply` |
| Encoding | Binary little-endian PLY 1.0 |
| Element | `vertex` |
| Properties per vertex | `x`, `y`, `z` (`float`), `red`, `green`, `blue` (`uchar`) |
| Coordinate system | Right-handed, metric scale (implementation-defined origin) |
| Default file suffix | `.ply` |

#### ASCII header template (binary body follows)

```text
ply
format binary_little_endian 1.0
element vertex <N>
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
```

Each vertex record is **15 bytes**: 3× `float32` + 3× `uint8`.

### 5.2 Temporary output path

When `--output` is omitted:

1. Create a temporary file with prefix `luthier-` and suffix `.ply`.
2. The file must **not** be deleted automatically at process exit (operator may inspect it).
3. On **successful** reconstruction, print the absolute path to **stdout** (one line, no extra decoration).
4. On failure, do not print a path unless an explicit `--output` was given and partially written (implementation must document partial-write behavior in a later revision).

### 5.3 Output path resolution

When `--output` is provided:

1. Expand `~` and resolve to an absolute path.
2. Create parent directories if they do not exist (implementation milestone).
3. Overwrite existing file if present (implementation milestone; must be documented in README when implemented).

---

## 6. Point cloud viewer (external)

luthier does **not** ship a viewer. Inspect output with open-source software.

### 6.1 Recommended viewer: CloudCompare

| Property | Detail |
| --- | --- |
| Name | [CloudCompare](https://www.cloudcompare.org/) |
| License | GPL-2.0 (open source) |
| Platforms | Windows, macOS, Linux |
| PLY support | Native import of ASCII and binary PLY |
| Why recommended | Industry-standard point cloud tool; fast visualization, measurement, comparison, and export |

**Open a reconstruction result:**

```bash
# Linux (if cloudcompare is on PATH)
cloudcompare.CloudCompare /path/to/output.ply

# Or use File → Open in the CloudCompare GUI
```

### 6.2 Alternative viewers

| Tool | License | Notes |
| --- | --- | --- |
| [MeshLab](https://www.meshlab.net/) | GPL | Strong mesh tools; good PLY support |
| [Open3D](https://www.open3d.org/) viewer | MIT | `open3d draw /path/to/output.ply` |
| [ParaView](https://www.paraview.org/) | BSD | Heavier; useful for large clouds |

**Project decision:** tests and documentation standardize on **PLY** because all
listed viewers import it without plugins.

---

## 7. Processing pipeline (M1)

Implementation follows this logical pipeline. Stages are orchestrated by
`pipeline.py` using `config/stack.yml`; they are not separate CLI commands.

```text
Images (--dir)
    → discover & decode (IO)
    → feature extraction (COLMAP SIFT)
    → matching, verification, incremental SfM, coloring
    → geometric filter + outlier removal (post-process)
    → colored PointCloud model + registered camera poses
    → write binary PLY (--output)
```

Failure at any stage raises `ReconstructionError` (API) or exits with code `1`
(CLI) and a human-readable message on stderr.

---

## 8. CLI exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success; output path printed to stdout |
| `1` | User error or reconstruction failure (`LuthierError` subclasses) |
| `2` | Reserved for unimplemented pipeline stages (`NotImplementedPipelineError`) |

---

## 9. Public Python API (v0.3.0)

### 9.1 Package entry (`luthier`)

| Symbol | Kind | Description |
| --- | --- | --- |
| `__version__` | `str` | Package version |
| `reconstruct_from_directory` | function | Main reconstruction entry point |
| `Point3D`, `PointCloud` | dataclass | Output geometry model |
| `CameraIntrinsics`, `CameraPose` | dataclass | Registered camera models |
| `LocalImageInput`, `ReconstructionResult` | dataclass | Input/output metadata |
| `LuthierError` | exception | Base error |
| `InvalidInputError` | exception | Bad user input |
| `ReconstructionError` | exception | Pipeline failure |
| `NotImplementedPipelineError` | exception | Reserved / future pipeline stages |

### 9.2 Submodule `luthier.io`

| Symbol | Description |
| --- | --- |
| `discover_images(image_dir)` | List supported images in a directory |
| `write_point_cloud(point_cloud, output_path)` | Serialize to PLY |
| `SUPPORTED_IMAGE_SUFFIXES` | Allowed image extensions |

---

## 10. Acceptance criteria (EARS)

Criteria are verified by automated tests described in [testing.md](testing.md).

### 10.1 CLI

- **AC-CLI-01:** When the user runs `luthier --help`, the system shall print usage text mentioning `--dir` and `--output`.
- **AC-CLI-02:** When the user runs `luthier` without `--dir`, the system shall exit with code `1` and print an error on stderr.
- **AC-CLI-03:** When the user runs `luthier --dir <missing>`, the system shall exit with code `1`.
- **AC-CLI-04:** When the user runs `luthier --dir <valid> --output <path>`, the system shall resolve `output` to an absolute path before reconstruction.
- **AC-CLI-05:** When the user runs `luthier --dir <valid>` without `--output`, the system shall allocate a temporary `.ply` path with prefix `luthier-`.
- **AC-CLI-06:** When reconstruction is not implemented, the system shall exit with code `2` and a clear message on stderr.

### 10.2 Input discovery

- **AC-IN-01:** When `discover_images` is called on a directory with supported images, the system shall return a sorted tuple of file paths.
- **AC-IN-02:** When `discover_images` is called on a directory with no supported images, the system shall raise `InvalidInputError`.

### 10.3 Output format

- **AC-OUT-01:** When `write_point_cloud` is implemented, the system shall write binary little-endian PLY with `x,y,z,red,green,blue` per vertex.
- **AC-OUT-02:** When `write_point_cloud` receives an unsupported format name, the system shall raise `ValueError`.

### 10.4 Reconstruction (implementation milestone)

- **AC-REC-01:** When `reconstruct_from_directory` is called with a golden image directory (≥ 10 images), the system shall produce a PLY with at least **1 000** points.
- **AC-REC-02:** When `reconstruct_from_directory` is called with fewer than two images, the system shall raise `InvalidInputError`.
- **AC-REC-03:** When reconstruction succeeds, `ReconstructionResult.output_path` shall equal the written file path.
- **AC-REC-04:** When reconstruction succeeds, `ReconstructionResult.point_cloud.count` shall match the vertex count in the PLY file.
- **AC-REC-05:** When reconstruction succeeds, `ReconstructionResult.cameras` shall contain one pose per registered image, each with non-empty `name`, finite `translation`, and positive `intrinsics.focal_length`.

### 10.5 Quality gates (repository)

- **AC-QG-01:** `black --check`, `ruff check`, `mypy`, and `pytest` shall pass on Python 3.12 in CI.
- **AC-QG-02:** When CI runs unit tests with coverage, total line coverage of `luthier` shall be **≥ 80%** (threshold in `pyproject.toml` → `[tool.coverage.report]` `fail_under`).

---

## 11. Constraints

| Constraint | Source |
| --- | --- |
| Python 3.12 | `pyproject.toml`, `.python-version` |
| Strict typing on public API | `CONTRIBUTING.md`, mypy strict |
| No new runtime dependencies until reconstruction milestone (justified in PR) | `CONTRIBUTING.md` |
| SDD → V-cycle → TDD workflow | `CONTRIBUTING.md` |
| Unitary commits | `CONTRIBUTING.md` |

---

## 12. Dependencies (M1 — approved)

Resolved in [decisions.md](decisions.md) (AD-03, AD-04). Introduced in the M1
implementation PR:

| Package | Purpose | Owner block |
| --- | --- | --- |
| `numpy` | Point arrays, pycolmap interop | `io.pointcloud`, `sfm` |
| `pycolmap` | Feature extraction, matching, incremental SfM | `sfm.colmap` |
| `opencv-python-headless` | Image metadata / validation helpers | `io.images` |

Install: `pip install luthier` (dependencies in `[project.dependencies]`) or
`pip install -e ".[reconstruction]"` during development if optional extra is used.

---

## 13. Specification change log

| Version | Date | Change |
| --- | --- | --- |
| 0.2.0 | 2026-06-24 | Initial photogrammetry specification; local `--dir` input; PLY output; CloudCompare viewer; CLI and API stubs |
| 0.3.0 | 2026-06-29 | M1 sparse SfM pipeline; camera poses on `ReconstructionResult`; post-process filters; golden acceptance in CI |
| 0.3.1 | 2026-06-29 | Single supported Python: 3.12 only (AD-13); CI matrix removed |

---

## 14. Decisions (resolved — Step 1)

Full rationale in [decisions.md](decisions.md).

| ID | Topic | Resolution |
| --- | --- | --- |
| AD-01 | Minimum image count | 2 for reconstruction; ≥ 10 for golden acceptance |
| AD-02 | Recursive `--dir` scan | No in M1 |
| AD-03 | SfM backend | **pycolmap** (COLMAP bindings); luthier orchestrates |
| AD-04 | Runtime dependencies | `numpy`, `pycolmap`, `opencv-python-headless` |
| AD-05 | Viewer | External CloudCompare; binary PLY output |
| AD-06 | Unit test coverage | **80%** minimum on `src/luthier` (CI enforced) |
| AD-07 | Second input source | Deferred |

### Still open

| ID | Question | When |
| --- | --- | --- |
| OD-04b | Shape of second input (`--url`, `--manifest`, …) | Before M3 spec |
