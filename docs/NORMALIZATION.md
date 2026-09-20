# V2 normalization plan contract

Codex inspects the source style, chooses processing and visually verifies every
measure. Helpers execute that decision without detecting notation, choosing
parameters or claiming fidelity from statistics. Preserve source crops before
all processing. The selected identity, geometry and core context remain stable.

Add `normalization` to the export plan for a song-level decision, or to an
individual `selection` item to replace it entirely. An absent decision (or null
override) preserves original pixels. A provisional decision can be:

```json
{
  "normalization": {
    "status": "partial",
    "confidence": "unknown",
    "source_faithful": null,
    "uncertainty": "Awaiting source-vs-output visual review",
    "visually_reviewed": false,
    "operations": [{"op": "invert"}]
  }
}
```

This is a schema example, not a recommended recipe. Available operations, in
explicit order, are `grayscale` (`mode`: `luma`, `max_rgb`, `min_rgb`), `invert`,
`levels` (explicit `black`, `white`, `gamma`), and `threshold` (explicit `value`,
after grayscale). Levels map each value to
`255 * clamp((value-black)/(white-black), 0, 1) ** gamma`.
No defaults choose thresholds or polarity. Other tools and methods remain allowed:
instead of operations, supply `prepared_image` (relative to the plan or absolute)
and a concise `method`. It must have the same crop geometry. Record contributing
source frames/coordinates and any masks or multi-frame preparation in the working
ledger. An external image is not proof of fidelity; inspect it against source.

After visually comparing every pair, update status and re-export:

- `normalized`: visually safe white-background/black-notation result;
  requires `visually_reviewed: true` and `source_faithful: true`.
- `partial`: safe but incomplete cleanup or a provisional candidate. State actual
  confidence and uncertainty; do not label unreviewed output as accepted.
- `source_preserved`: exact selected RGB pixels, no operations/prepared image.
  Use this override when processing is unsafe; explain why. Fidelity is true
  because pixels are preserved, not because an automated visual check passed.

`confidence` is `high`, `medium`, `low` or `unknown`. Keep source selection
confidence separate from normalization confidence. Unknown fidelity is null.
The helper records decisions; Codex is responsible for their truthfulness.
Legacy `tone: max_rgb_to_gray` remains executable but is recorded as unreviewed
`partial` unless replaced by an explicit reviewed normalization decision.

Outputs retain three-digit names: `source_measures/NNN.png` and `measures/NNN.png`.
`measures.json` links both via `source_output`/`output` and includes normalization
status, confidence, fidelity, uncertainty and method provenance. Composition uses
normalized cores, with the original explicit cross-boundary context handling.
V3 should prefer measures/ and consult source_measures/ whenever ambiguous.

Use a fresh run directory. Review every source/output pair, contact sheets,
full_score.png at readable scale, every page PNG and every actual PDF page;
enlarge difficult thin lines, multi-digit frets, curves, dots, parentheses and
techniques. Preserve information rather than force binary pixels or whiten an
unsafe background. No musical redrawing, invented pixels or hidden-note recovery.
