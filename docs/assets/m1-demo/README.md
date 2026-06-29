# M1 documentation assets — COLMAP South Building

Visual proof that luthier **v0.3.0** reconstructs a sparse colored point cloud
from the same golden reference images used in acceptance tests (AC-REC-01 …
AC-REC-05).

## Reference dataset

| Field | Value |
| --- | --- |
| **Scene** | South Building facade, UNC Chapel Hill (USA) |
| **Dataset** | [COLMAP South Building](https://colmap.github.io/datasets.html) |
| **Download** | [`south-building.zip`](https://github.com/colmap/colmap/releases/download/3.11.1/south-building.zip) (COLMAP release 3.11.1) |
| **Manifest** | [`tests/data/golden/colmap.yml`](../../tests/data/golden/colmap.yml) |
| **Subset used** | 20 JPEG images (sorted filenames; same default as CI) |
| **Image author** | Christopher Zach (COLMAP research distribution) |

Input images are **not** committed to the repository. They are downloaded by
[`scripts/fetch_golden_colmap.sh`](../../scripts/fetch_golden_colmap.sh) into
`tests/data/golden/images/` (gitignored).

## Committed artifacts (this folder)

| File | Description |
| --- | --- |
| [`south-building-input-montage.jpg`](south-building-input-montage.jpg) | Grid of 8 sample input photos |
| [`south-building-scene.ply`](south-building-scene.ply) | Binary colored PLY output (~5k points) |
| [`south-building-front.png`](south-building-front.png) | Point cloud render (front) |
| [`south-building-side.png`](south-building-side.png) | Point cloud render (side) |
| [`south-building-flythrough.mp4`](south-building-flythrough.mp4) | Orbit animation (Open3D offscreen) |
| [`manifest.json`](manifest.json) | Machine-readable provenance and run stats |

Latest run stats are in `manifest.json` (point count, cameras, timing).

## Regenerate

From the repository root (requires `[reconstruction]` dependencies):

```bash
./scripts/fetch_golden_colmap.sh --count 20
pip install -e ".[dev,reconstruction]"
python scripts/generate_m1_doc_artifacts.py
```

Options:

```bash
python scripts/generate_m1_doc_artifacts.py --fetch          # auto-fetch if missing
python scripts/generate_m1_doc_artifacts.py --output-dir /tmp/demo
```

## Use in documentation

Embed in Markdown (paths relative to repo root):

```markdown
![South Building input photos](docs/assets/m1-demo/south-building-input-montage.jpg)
![Reconstructed point cloud](docs/assets/m1-demo/south-building-front.png)
```

Full walkthrough: [`docs/m1-demo.md`](../m1-demo.md).
