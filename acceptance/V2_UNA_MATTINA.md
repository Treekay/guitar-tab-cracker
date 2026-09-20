# Una Mattina V2 test — reconstruction passed, normalization not passed

The supplied local video was tested after acquisition of Bilibili BV123tP6bEPw
failed (direct HTTP 412; Xiazaitool eventually reported its daily request limit).
This local-file run does not validate URL acquisition.

- Input: Una Mattina - Roxane Elfasci.mp4, 185.78 seconds, 1280 x 720, 30 fps.
- Different source style: white/gray notation over a translucent dark panel and
  moving performance imagery, with scrolling, repeats and first/second endings.
- 61 frames actually inspected: 6 survey, 18 adaptive, 24 coverage/source
  revisits, 13 independent final cross-checks. Timestamps were agent-selected.
- 45 ordered units: an unnumbered opening followed by printed measures 1–44.
  Repeat playback observations support the same printed score identities;
  written repeat signs/endings remain in the score. Similar later measures are
  retained independently. No known missing, duplicated or misordered score units.
- Cleaner timestamps replaced crops crossed by the playback cursor. Source
  boxes include opening annotations, thin lines, multidigit frets, dots, beams,
  curves, parentheses, slide labels, repeat signs and final double bar. Boundary
  context is retained with explicit core coordinates; composition uses cores.

## Normalization limitation

Compared three processing candidates on representative source crops: min-channel
grayscale inversion, levels plus inversion, and local background subtraction.
Inversion retained moving scenery; stronger whitening erased faint string lines;
local subtraction strengthened guitar texture into false-looking strokes. These
trials did not establish a safe white-background output for this source style.

All 45 outputs therefore use `source_preserved`, with explicit uncertainty about
safe background removal. Both source_measures/ and measures/ contain the exact
selected RGB crops; normalized 0, partial 0, source_preserved 45. Fidelity is
preserved without claiming normalization success. No hidden music was invented
or redrawn. This is a successful safety fallback, not full second-style
normalization acceptance or evidence that the source cannot ever be normalized.

## Output verification

Every source/output pair was visually checked at readable scale, with enlarged
checks for the opening harmonic, slide/repeat boundary, parenthesized note,
multidigit frets, thin lines and ending. All full-score sections, three page PNGs
and three actual Poppler-rendered PDF pages were reviewed. A final source
replacement and its affected row/page were rechecked.

Mechanical checks confirm 45 contiguous sequence indices, printed 1–44 plus
the opening, exact source-frame crop pixels, exact fallback copies, full-score
pixels matching preferred cores, A4 landscape dimensions and embedded PDF pixels
equal to page PNGs. The user-owned video's SHA-256 is unchanged. No video copy
was downloaded for this run, so no video deletion was required.

Moving imagery, uneven backgrounds and faint source lines remain visible. The
score is usable as source evidence; the clean white-background target is unmet.
No reusable helper changes or V3 implementation were needed for this test.

Private output: runs/v2-una-mattina/result/. Decisions and the frame/coverage
ledger are in working/decisions.json and working/coverage.json. Inspection evidence
includes pair sheets, rejected processing comparisons, enlarged crops, full-score
sections, actual PDF renders and verification.json. The delivery ZIP retains both
measure versions and provenance; useful full frames remain in the run directory.
