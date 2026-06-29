# M1 demo — South Building reconstruction

This page showcases a **real end-to-end run** of luthier on the public COLMAP
**South Building** benchmark — the same golden reference set used in acceptance
tests.

## Input (reference photos)

Eight of the twenty JPEG images used for the run (3072×2304, strong overlap):

![Sample input images from the COLMAP South Building dataset](assets/m1-demo/south-building-input-montage.jpg)

**Source:** [COLMAP datasets](https://colmap.github.io/datasets.html) —
`south-building.zip` from
[COLMAP 3.11.1](https://github.com/colmap/colmap/releases/tag/3.11.1).
Fetched via [`scripts/fetch_golden_colmap.sh`](../scripts/fetch_golden_colmap.sh);
manifest: [`tests/data/golden/colmap.yml`](../tests/data/golden/colmap.yml).

## Output (sparse colored point cloud)

Default stack (`config/stack.yml`), 20 images → **~5 000** triangulated points,
**20** registered cameras, binary PLY:

| View | Asset |
| --- | --- |
| Front | ![Front render](assets/m1-demo/south-building-front.png) |
| Side | ![Side render](assets/m1-demo/south-building-side.png) |

Download the point cloud: [`south-building-scene.ply`](assets/m1-demo/south-building-scene.ply)
(open in CloudCompare or Open3D).

## Orbit video

<video src="assets/m1-demo/south-building-flythrough.mp4" controls width="100%"></video>

*(If your Markdown viewer does not render HTML video, open
[`south-building-flythrough.mp4`](assets/m1-demo/south-building-flythrough.mp4)
directly.)*

## Reproduce

```bash
./scripts/fetch_golden_colmap.sh --count 20
pip install -e ".[dev,reconstruction]"
python scripts/generate_m1_doc_artifacts.py
```

Artifacts land in [`docs/assets/m1-demo/`](assets/m1-demo/). See
[`docs/assets/m1-demo/README.md`](assets/m1-demo/README.md) for provenance and
license notes.

## Run stats (committed manifest)

See [`docs/assets/m1-demo/manifest.json`](assets/m1-demo/manifest.json) for
`point_count`, `camera_count`, `elapsed_seconds`, and `luthier_version`.
