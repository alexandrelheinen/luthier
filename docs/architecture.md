# Luthier — system architecture

This document is the **spec-anchored** system and module design for luthier. It
implements the left side of the V-cycle (system design + architecture) for
[specification.md](specification.md).

---

## 1. System context

```text
┌─────────────────────────────────────────────────────────────────┐
│                         Operator / Developer                     │
└───────────────┬───────────────────────────────┬─────────────────┘
                │ CLI: luthier --dir …          │ Python API
                ▼                               ▼
┌───────────────────────────┐       ┌───────────────────────────┐
│      luthier.cli          │       │   luthier.pipeline        │
│  argparse, exit codes       │──────▶│ reconstruct_from_directory│
└───────────────────────────┘       └─────────────┬─────────────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    ▼                             ▼                             ▼
           ┌──────────────┐              ┌──────────────┐              ┌──────────────┐
           │ luthier.io   │              │  (future)    │              │ luthier.io   │
           │ .images      │              │  sfm / match │              │ .pointcloud  │
           │ discover     │              │  stages      │              │ write PLY    │
           └──────────────┘              └──────────────┘              └──────────────┘
                    │                             │                             │
                    └─────────────────────────────┴─────────────────────────────┘
                                                  │
                                                  ▼
                                        ┌──────────────────┐
                                        │  scene.ply       │
                                        │  (binary PLY)    │
                                        └────────┬─────────┘
                                                 │
                                                 ▼
                                        ┌──────────────────┐
                                        │  CloudCompare      │
                                        │  (external viewer) │
                                        └──────────────────┘
```

---

## 2. Layering

| Layer | Modules | Responsibility |
| --- | --- | --- |
| **Interface** | `cli`, `__main__` | Argument parsing, stdout/stderr, exit codes |
| **Application** | `pipeline` | Orchestrate reconstruction end-to-end |
| **Domain** | `models`, `exceptions` | Typed data and error taxonomy |
| **Infrastructure** | `io.images`, `io.pointcloud` | Filesystem and serialization |

Future stages (`features`, `sfm`, `mvs`) sit between **Application** and
**Infrastructure**, consuming images and producing `PointCloud`.

---

## 3. Module reference

### 3.1 `luthier.cli`

- Builds `argparse` parser (`build_parser`).
- Validates `--dir` presence and path (`validate_args`).
- Resolves output path or temp file (`resolve_output_path`).
- Maps exceptions to exit codes (`run`, `main`).

### 3.2 `luthier.pipeline`

- Single entry: `reconstruct_from_directory(image_dir, *, output_path)`.
- Validates `LocalImageInput`, runs stages, calls `write_point_cloud`.
- Returns `ReconstructionResult`.

### 3.3 `luthier.io.images`

- `discover_images(image_dir) -> tuple[Path, ...]`.
- `SUPPORTED_IMAGE_SUFFIXES` constant.

### 3.4 `luthier.io.pointcloud`

- `write_point_cloud(point_cloud, output_path, *, file_format="ply")`.
- `POINT_CLOUD_FORMAT_PLY`, `DEFAULT_POINT_CLOUD_FORMAT`.

### 3.5 `luthier.models`

| Type | Fields |
| --- | --- |
| `Point3D` | `x, y, z, r, g, b` |
| `PointCloud` | `points: tuple[Point3D, ...]` |
| `LocalImageInput` | `image_dir: Path` |
| `ReconstructionResult` | `point_cloud`, `output_path`, `source` |

### 3.6 `luthier.exceptions`

Hierarchy:

```text
LuthierError
├── InvalidInputError
├── ReconstructionError
└── NotImplementedPipelineError
```

---

## 4. Data flow (local input)

1. **CLI** parses `--dir` and optional `--output`.
2. **pipeline** constructs `LocalImageInput`.
3. **io.images** discovers image paths.
4. **(future)** SfM builds `PointCloud`.
5. **io.pointcloud** writes binary PLY to `output_path`.
6. **CLI** prints `output_path` on success.

---

## 5. Extension points (second input source)

Add a new input model (e.g. `RemoteImageInput`) and a registry or strategy in
`pipeline` without changing PLY output or CLI exit codes. CLI might gain `--url`
or `--manifest`; Python API might gain `reconstruct_from_manifest(...)`.

Keep **one** internal representation: `tuple[Path, ...]` of local paths (download
remote sources to a cache directory first).

---

## 6. Failure modes

| Condition | API | CLI |
| --- | --- | --- |
| Missing `--dir` | N/A | `LuthierError`, exit 1 |
| Bad directory | `ValueError` / `InvalidInputError` | exit 1 |
| No images | `InvalidInputError` | exit 1 |
| Pipeline failure | `ReconstructionError` | exit 1 |
| Not implemented | `NotImplementedPipelineError` | exit 2 |

---

## 7. Packaging and entry points

| Entry | Mechanism |
| --- | --- |
| `luthier` command | `[project.scripts]` → `luthier.cli:main` |
| `python -m luthier` | `luthier/__main__.py` |

---

## 8. Future module tree

```text
src/luthier/
  __init__.py
  __main__.py
  cli.py
  pipeline.py
  models.py
  exceptions.py
  io/
    __init__.py
    images.py
    pointcloud.py
  features/          # future
  sfm/               # future
```

Each new package requires updates to this document, `specification.md`, and
[testing.md](testing.md) before implementation.
