# Canonical Guitar Pro export

Node.js 22+, Python with `jsonschema`, and the existing V3 measure manifest are
required. Install the pinned Node dependencies with `npm ci`.

```sh
npm test
node tools/guitar-pro/export.mjs runs/v2-una-mattina/result/v3/score.json --render
node tools/guitar-pro/export.mjs runs/v2-yukinohana/result/v3/score.json --sample 1,16,29,30 --render
```

Use `--python PATH` for the Python interpreter, `--output DIR` for another
dedicated output directory. Default output is the canonical file's sibling
`export/`. Source manifests remain required for coverage validation; prepare
ordered measure images and their manifest before invoking this CLI.

The CLI runs the existing canonical validator, constructs an alphaTab model,
writes `score.gp` using Gp7Exporter, reloads those saved bytes with ScoreLoader,
and compares musical semantics against an independent canonical projection.
Unexpected mismatches fail the command. Internal object IDs are never compared.
There is no recognition, rhythm inference, manual GP encoding or canonical edit.

Outputs are `score.gp`, `export_mapping.json`, `export_report.md`,
`roundtrip_validation.json`, `canonical_validation.json` and
`semantic_comparison.json`. Optional `--render` creates SVG/PNG system chunks
from the re-imported model, indexed by `rendered/score_render.json`. These are
notation previews, not A4 pages. PNGs are portable; SVG music glyphs require
Bravura. Rendering completion alone does not establish visual acceptance.

Review difficult source measures against those PNGs and record `visual_review.md`
with the GP hash, inspected paths, musical findings and known display differences.
Repeat visual review after changing musical mappings. Do not reuse a previous
review for a changed GP hash without checking the resulting rendering.

`adapter.mjs` owns all target-library mappings/defaults; `compare.mjs` owns
semantic expectations and import projection; `render.mjs` owns preview rendering.
The Python canonical model remains independent. Tests exercise adapter mechanics
and corruption detection; they do not validate transcription accuracy.

See [field mapping](../../docs/GUITAR_PRO_MAPPING.md) and
[accepted exports](../../acceptance/V3_GUITAR_PRO.md) for limits and evidence.
