# luthier

**Photogrammetry from photographs to 3D point clouds.**

luthier is a Python library and command-line tool that reconstructs a **colored
3D point cloud** from a folder of overlapping images. Version **0.2.0** ships the
**specification, CLI framework, and tests**; the reconstruction pipeline itself
is not implemented yet.

| Document | Description |
| --- | --- |
| [docs/specification.md](docs/specification.md) | Product spec and acceptance criteria (SDD) |
| [docs/architecture.md](docs/architecture.md) | System design and module layout |
| [docs/testing.md](docs/testing.md) | TDD strategy and test traceability |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development workflow and quality gates |

---

## What it does (target behavior)

```text
  photos/          luthier              scene.ply
 ┌─────────┐      ─────────►         ┌─────────────┐
 │ img1.jpg│      photogrammetry     │ 3D points   │
 │ img2.jpg│                        │ + RGB colors  │
 │  …      │                        └──────┬──────┘
 └─────────┘                               │
                                           ▼
                                    CloudCompare
                                    (viewer)
```

1. Read images from a **local directory** (`--dir`).
2. Run Structure-from-Motion and related stages (planned).
3. Write a **binary PLY** point cloud (`--output` or a temporary file).
4. Open the result in an external viewer — **[CloudCompare](https://www.cloudcompare.org/)** is recommended.

A **second input source** (remote URLs, manifests, etc.) will be added in a
future release without breaking the local workflow.

---

## Installation

Requires **Python 3.10+**.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

After installation the `luthier` command is available on your `PATH`.

---

## Command-line usage

### Basic reconstruction (local directory)

```bash
luthier --dir /path/to/photos --output /path/to/scene.ply
```

### Omit output path (temporary file)

When `--output` is not given, luthier creates a temporary `.ply` file and prints
its absolute path on **stdout** when reconstruction succeeds:

```bash
luthier --dir ./photos
# /tmp/luthier-abc123.ply   (printed on success)
```

The temporary file is **not** deleted automatically so you can inspect it.

### Help and version

```bash
luthier --help
luthier --version
python -m luthier --help
```

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Invalid input or reconstruction error |
| `2` | Pipeline not yet implemented (current state until M1) |

---

## Python API

```python
from pathlib import Path

from luthier import reconstruct_from_directory

result = reconstruct_from_directory(
    Path("/data/photos"),
    output_path=Path("/data/out/scene.ply"),
)

print(f"Wrote {result.point_cloud.count} points to {result.output_path}")
```

### Discover images only

```python
from pathlib import Path

from luthier.io import discover_images

paths = discover_images(Path("/data/photos"))
print(f"Found {len(paths)} images")
```

---

## Input requirements (`--dir`)

| Rule | Detail |
| --- | --- |
| Path | Must exist and be a directory |
| Layout | Images must sit **directly** in the folder (no subfolders in v0.2.0) |
| Formats | `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`, `.bmp` (case-insensitive) |
| Overlap | Photos should overlap substantially (typical photogrammetry practice) |
| Minimum count | ≥ 2 for reconstruction (≥ 10 for acceptance / golden tests) |

---

## Output format: binary PLY

luthier writes **binary little-endian PLY** with colored vertices:

| Property | Type |
| --- | --- |
| `x`, `y`, `z` | `float32` |
| `red`, `green`, `blue` | `uint8` (0–255) |

Default file extension: **`.ply`**

Full on-disk layout is defined in [docs/specification.md](docs/specification.md#5-output-specification--point-cloud-format).

---

## Viewing the point cloud

luthier does not include a viewer. Use open-source tools:

### Recommended: CloudCompare

- Website: [https://www.cloudcompare.org/](https://www.cloudcompare.org/)
- License: GPL-2.0
- Why: native PLY support, fast rendering, measurement and comparison tools

```bash
# Example (Linux, if installed)
cloudcompare.CloudCompare /path/to/scene.ply
```

Or open **File → Open** in the CloudCompare GUI.

### Alternatives

| Tool | Command / action |
| --- | --- |
| [MeshLab](https://www.meshlab.net/) | File → Import Mesh |
| [Open3D](https://www.open3d.org/) | `open3d draw scene.ply` |
| [ParaView](https://www.paraview.org/) | File → Open |

---

## Project layout

```text
src/luthier/
  cli.py              # luthier --dir … --output …
  pipeline.py         # reconstruct_from_directory (stub)
  models.py           # PointCloud, ReconstructionResult, …
  io/
    images.py         # discover_images
    pointcloud.py     # write_point_cloud (stub)
docs/
  specification.md    # SDD product specification
  architecture.md     # System design
  testing.md          # TDD / V-cycle testing strategy
tests/
  test_cli.py
  test_models.py
  test_images.py
  test_pointcloud.py
  test_pipeline.py
  test_acceptance.py
```

---

## Development

Install dev dependencies and run the same checks as CI:

```bash
pip install -e ".[dev]"
black src tests
ruff check src tests
mypy
pytest --cov=luthier --cov-report=term-missing
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for SDD → V-cycle → TDD workflow and
unitary commit rules.

### Running tests

```bash
# Default (excludes acceptance tests needing golden images)
pytest

# Acceptance tests only (after adding tests/data/golden/images/)
pytest -m acceptance
```

---

## Roadmap

| Milestone | Status |
| --- | --- |
| v0.2.0 — Spec, CLI framework, tests | **Current** |
| M1 — Sparse SfM → PLY | Planned |
| M2 — Denser point cloud | Planned |
| M3 — Second input source | Planned |

---

## License

MIT — see [LICENSE](LICENSE).
