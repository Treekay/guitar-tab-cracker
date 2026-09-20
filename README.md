# tabstitch

Private CLI-first tooling for reconstructing printable guitar tablature from overlapping screenshots.

The repository is at **V1 Task 2 / Milestone V1.1**: image ingestion, manual normalized ROI, and preview. Barline detection, measure extraction, matching, ordering, and score rendering remain later tasks.

## Setup and commands

Requires Python 3.11+.

```bash
python -m venv .venv
```

Activate `.venv` (`.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` on Linux/macOS), then:

```bash
python -m pip install -e ".[dev]"
tabstitch --help
tabstitch config --config config.example.toml
tabstitch inspect tests/fixtures/vision-benchmark/input
tabstitch inspect tests/fixtures/vision-benchmark/input --preview runs/benchmark-preview.png
tabstitch build tests/fixtures/vision-benchmark/input --run-id demo --config config.example.toml
tabstitch layout runs/demo/manifest.json
python -m pytest
python -m compileall -q src tests
python -m tabstitch --help
```

Pillow is the only runtime dependency. `examples/input-images/` is an empty placeholder; add screenshots before using it as an input directory.

Configuration combines built-in defaults with an optional TOML file. Relative paths are resolved from the current working directory. `build --output <root>` overrides `workspace.root`; the run ID is appended (for example, `--output runs --run-id demo` produces `runs/demo`).

`inspect` validates all images and writes JSON metadata and effective normalized/pixel ROI to stdout. It creates no run. Optional `--preview <new-path.png>` writes a labelled contact sheet. `build` copies originals, saves ROI PNGs and a preview, and updates the manifest/report. `layout` remains an explicit placeholder for V1 Task 9.

## Input and ROI policy

- Discover only immediate files with PNG, JPG/JPEG, or WebP extensions (case-insensitive); ignore unrelated files and subdirectories. Configuration can restrict this set.
- Sort by case-sensitive Unicode filename, assigning indices starting at 1. This is deterministic input order, not musical order.
- Verify structure and fully decode each image before creating a run. An empty directory or any corrupt supported image fails the operation with the offending path; nothing is silently skipped. Animated/multi-frame images, unsupported decoded formats, and Pillow decompression-bomb warnings/errors are rejected.
- Read one full image at a time. Metadata persists; full source pixel buffers do not. The contact sheet uses bounded thumbnails, with total canvas memory proportional to image count.
- ROI coordinates refer to stored source pixels. EXIF orientation is not applied; the ROI PNG omits orientation metadata. Portrait and landscape images are accepted without assuming TAB geometry. Originals retain all bytes and metadata.
- `inputs/` contains byte-for-byte copies. `normalized/` contains RGB/RGBA PNG crops, preserving alpha and original crop resolution. No scaling is applied to these crops; preview thumbnails preserve aspect ratio.

Configure ROI in [config.example.toml](config.example.toml). When disabled, the effective rectangle is the full image. All configured values are validated even when disabled: finite numbers, non-negative x/y, positive width/height, and x+width/y+height at most 1. Invalid values are rejected, never clamped.

Pixel conversion floors left/top and ceils right/bottom (exclusive), preserving all intersecting pixels. Arithmetic uses exact fractions of the decimal configuration values to avoid floating-point one-pixel overflow. For 1200 x 800 and `(x=.10, y=.70, width=.80, height=.25)`, the box is `(120, 560, 1080, 760)`.

## Artifacts and manifest

```text
runs/<id>/
  inputs/0001_original.png
  normalized/0001_roi.png
  outputs/preview_contact_sheet.png
  crops/       # reserved for future measure extraction
  matches/     # reserved for future matching
  manifest.json
  summary.md
```

Existing run directories and preview files are never overwritten. Input and ROI filenames use stable four-digit indices (expanding beyond 9999); original filenames remain in the manifest and preview labels.

Manifest schema version **1** is retained with additive input/ROI fields: each input records its index, resolved source path, original filename, copied artifact, width/height, decoded format/mode, effective normalized ROI, half-open pixel bbox, and ROI artifact. It also records the effective config, preview output, and `images_ready` status. Existing empty measure placeholders are retained. Artifact paths are relative to the run directory.

Validation failures create no run. Failures while writing artifacts retain the partial run for inspection and record `failed` plus an error when the filesystem remains writable. Use a new run ID after resolving a failure. `summary.md` includes image count, dimensions, source and artifact locations, ROI, and the explicit statement that no measure detection occurred.

Tests generate small inputs covering supported formats, corruption, ROI precision, portrait/landscape dimensions, alpha, EXIF policy, CLI artifacts, and overwrite protection. Existing benchmark evidence is read-only input to smoke tests; generated runs are ignored by Git.

## Product references

- [Product requirements](docs/PRODUCT_REQUIREMENTS.md)
- [Execution plan](docs/EXECUTION_PLAN.md)
- [Product skill](.agents/skills/guitar-tab-product/SKILL.md)

V1 excludes video, score recognition, AI runtime integration, Guitar Pro export, web UI, billing, authentication, and MCP integration.
