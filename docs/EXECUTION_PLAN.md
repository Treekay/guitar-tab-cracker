# Execution Plan

## V1 COMPLETE

Preserve the accepted 10-screenshot / 26-measure / 2-page result. No V1 polish.

## V2 COMPLETE — local raw-video acceptance passed

The user supplied a raw local video. Codex chose all timestamps and crops,
reconciled overlap, revisited gaps/obstructed candidates, exported the ordered
set, returned to the video independently and visually reviewed final outputs.

- Source: 209.95 seconds, 986 × 720, approximately 30 fps.
- 69 inspected frames: 6 initial, 37 adaptive, 13 recovery, 13 second-pass.
- 57 complete logical occurrences (1–57), no unresolved partials or known
  omissions/duplicates/order errors.
- Stable measures/001.png–057.png with source timestamp, crop, confidence,
  boundary context and core_bbox_in_output metadata.
- Full score image, 3 A4 landscape page PNGs and PDF; every selected crop and
  actual PDF page visually reviewed. Embedded PDF pixels equal page PNGs.
- Original user-owned video remains unchanged; no downloaded video copy exists.

See [acceptance](../acceptance/V2_ACCEPTANCE.md) and the private
[result report](../runs/v2-yukinohana/result/report.md). Explicit decisions and
coverage evidence remain in runs/v2-yukinohana/working/. No CV/OMR or musical
transcription was implemented. Tools only execute selected timestamps, regions,
pointwise tone, ordering and placement.

FFmpeg is available from the project temporary imageio-ffmpeg wheel; ReportLab
and Pillow are in the bundled Python runtime; Poppler rendered the actual PDF.
The ffprobe-based metadata command remains available when ffprobe is installed;
this run used FFmpeg's input inventory and the same explicit extraction helper.

## Remaining robustness validation

Validate another genuinely different video style before a public robustness
claim. The earlier Bilibili URL returned HTTP 412; Xiazaitool is the authorized
normal-interface fallback but has not passed an acquisition test. Do not equate
local-file success with proven website compatibility.

For future URL runs: try direct acquisition, then https://www.xiazaitool.com/,
then request local input if tools/access prevent acquisition. After final QA,
remove only exact run-owned temporary video/partial-download files. Preserve
user originals, outputs and provenance; record cleanup status.

## V3 NEXT — not started

Ordered clean measure set → structured music → Guitar Pro. Requires a separate
explicit advance; V2 completion does not authorize beginning V3.
