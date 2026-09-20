# Fresh V1 benchmark

Date: 2026-09-20. Architecture: Codex visual reasoning + mechanical execution.
Scope: screenshot reconstruction only; no music transcription, V2 or V3.

## Result

- Sources: **10** current screenshots in `input/`.
- Candidate crops: **47**, including partial screenshot edges.
- Reconstructed logical measures: **26**, ordered 1-26, each once.
- Unresolved fragments: **0**; all visible partials map to complete selections.
- Remaining duplicates: **none found in visual review**.
- Visible measures omitted: **none found in visual review**.
- A4 portrait pages: **2** (nine rows, consistent scale).

This establishes coverage of the supplied screenshots, not general reliability
on other scores. Old nine-image benchmark results are not current ground truth:
current `6.png` adds the middle view covering 14-16. It resolves the apparent
14/15 gap in the older set. Old images 6-9 are now 7-10.

## Visual source reconciliation

| Input | Visible measures (p = partial edge) | Final selection |
| --- | --- | --- |
| 1.png | 1-3, 4p | 1-3; retain opening TAB/time/capo context |
| 2.png | 3p, 4-5, 6p | 4-5 and clean beginning of 6 |
| 3.png | 5p, 6-8, 9p | clean end of 6; 7-8 |
| 4.png | 8-11, 12p | 9-11 |
| 5.png | 10p, 11-13, 14p | 12-13; clean beginning of 14 |
| 6.png | 13p, 14-16, 17p | clean end of 14; 15-16 |
| 7.png | 15p, 16-18, 19p | 17-18 |
| 8.png | 18p, 19-21, 22p | 19-21 |
| 9.png | 20p, 21-23, 24p | 22-23 |
| 10.png | 23p, 24-26 | 24-26, including final double bar |

Codex opened all sources and chose the rectangles, identities, order, joins and
page groups. `decisions.json` records those explicit decisions. Printed numbers,
adjacent visual content and overlapping screenshots support the sequence.
Similar-looking later passages (including 22-24) remain distinct measures.

Measures 6 and 14 use complementary visually aligned pieces from adjacent
screenshots to avoid playback cursors. Measure 16 uses current image 6 rather
than the obstructed next screenshot. Neither composite invents content.
Historical note JSON and retired detection geometry were not V1 dependencies.

## Final visual QA and corrections

Codex inspected the full-score PNG in nine readable sections, page PNGs and
both pages rasterized from the actual PDF with Poppler. Reviewed the selected
content against the source views, including the two joins, opening annotations,
first-ending/repeat marks at 4, cross-boundary ties at 11/12 and 20/21, technique
marks above the strings, stems/beams below them, and the ending at 26.

After the initial render, reduced visually empty top padding on ordinary rows,
kept the taller opening/first-ending context, and copied existing source boundary
strips to row ends. Boundary strips are original barline pixels, not extra
measures or newly drawn notation. Corrected the boundary-column background and
regenerated/reviewed both PDF pages. No measure is split across rows.

Remaining source limitations: measure 1 retains a playback cursor/progress
overlay; photographed backgrounds and differing source tones remain visible.
This is source-faithful image reconstruction, not newly engraved white-paper
notation. No obscured symbols were invented. Dark source panels consume more
printer ink than an engraved score.

## Checks

- Ten source SHA-256 hashes recorded in `result/execution-checks.json`.
- All 58 previously tracked benchmark source/evidence files preserved byte-for-byte
  against Git HEAD before this reset commit, allowing the documented image renames.
- All 47 candidate identities accounted for by selected measures 1-26.
- Selected source pieces exactly match their saved measure pixels.
- All 26 measure bodies exactly match their slices in the full-score PNG.
- Explicit page order equals full-score order; each selected measure occurs once.
- Full score: 10821 x 358 px; page PNGs: 2480 x 3508 px at 300 dpi.
- PDF: two unencrypted pages, 595.276 x 841.890 points (A4 portrait).
- Mechanical helper syntax check and skill-creator `quick_validate.py`: passed.
  The bundled PDF runtime lacked PyYAML; skill validation passed in the preserved
  local virtual environment. No obsolete application tests were run or retained.
- `git diff --check`: passed.

## Outputs and replay

- [Full score PNG](result/full_score.png)
- [A4 page 1 PNG](result/page_001.png)
- [A4 page 2 PNG](result/page_002.png)
- [A4 PDF](result/full_score.pdf)
- [Selected measure crops](result/measures/)
- [Explicit visual decisions](decisions.json)
- [Mechanical execution checks](result/execution-checks.json)

Candidate crops, row inspections, full-strip sections and PDF rasterizations are
local working evidence under ignored `result/inspection/`.

With Pillow and ReportLab available, replay these already-made visual decisions:

```text
python tools/compose.py benchmark/decisions.json benchmark/result
```

This is an export replay, not an autonomous detector. Another image set requires
fresh Codex inspection and decisions using the rewritten skill.
