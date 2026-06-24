# Golden acceptance dataset

The golden set is defined in **[colmap.yml](colmap.yml)** — a public COLMAP
benchmark (**South Building**, UNC Chapel Hill).

## Quick start

From the repository root:

```bash
chmod +x scripts/fetch_golden_colmap.sh   # once
./scripts/fetch_golden_colmap.sh          # downloads 20 images (CI-friendly subset)
```

Options:

```bash
./scripts/fetch_golden_colmap.sh --all           # all 128 images (~234 MB download)
./scripts/fetch_golden_colmap.sh --count 30      # custom subset size
```

Images are written to `images/` (gitignored). They are **not** committed to the repo.

## Dataset summary

| Field | Value |
| --- | --- |
| **Scene** | South Building facade (UNC Chapel Hill) |
| **Source** | [COLMAP release 3.11.1](https://github.com/colmap/colmap/releases/tag/3.11.1) |
| **Download** | `south-building.zip` — see `colmap.yml` → `download.primary_url` |
| **Images in archive** | 128 × JPEG (`.JPG`) |
| **Default subset for dev/CI** | 20 images (sorted by filename) |
| **License** | COLMAP research distribution; images by Christopher Zach |
| **Expected min points (AC-REC-01)** | 1 000 |

## Acceptance tests

```bash
pytest -m acceptance
```

Tests stay skipped until `images/` is populated **and** the M1 reconstruction
pipeline is implemented.

## Your photos later

When you have your own photos for final validation, add a separate manifest
(e.g. `user.yml`) — do not replace this COLMAP golden set without updating the
spec and tests.
