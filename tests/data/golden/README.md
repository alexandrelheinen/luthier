# Golden acceptance dataset

Place **≥ 10 overlapping photographs** in the `images/` subdirectory for
acceptance tests (`pytest -m acceptance`).

Each file should use a supported suffix: `.jpg`, `.jpeg`, `.png`, `.tif`,
`.tiff`, or `.bmp`.

## Required metadata (fill in when adding images)

| Field | Value |
| --- | --- |
| Source | _TBD — URL or description_ |
| License | _TBD — must allow use in CI_ |
| Expected min points | 1 000 (per AC-REC-01) |

Until this directory contains images, acceptance tests are skipped automatically.
