# Execution Plan

## V1 COMPLETE

Preserve the accepted 10-screenshot / 26-measure / 2-page result. No V1 polish.

## V2 CORE COMPLETE — local raw-video acceptance passed

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
ordering and placement. Historical tonal experiments are retained as evidence only.

FFmpeg is available from the project temporary imageio-ffmpeg wheel; ReportLab
and Pillow are in the bundled Python runtime; Poppler rendered the actual PDF.
The ffprobe-based metadata command remains available when ffprobe is installed;
this run used FFmpeg's input inventory and the same explicit extraction helper.

## Remaining robustness validation

The translucent Una Mattina fixture passed source-faithful reconstruction: 61
inspected frames, 45 ordered units, 3 checked PDF pages. Whitening did not pass
and is no longer required. Broader robustness still needs more evidence.
Bilibili acquisition returned HTTP 412; Xiazaitool is the authorized
normal-interface fallback but has not passed an acquisition test. Do not equate
local-file success with proven website compatibility.

For future URL runs: try direct acquisition, then https://www.xiazaitool.com/,
then request local input if tools/access prevent acquisition. After final QA,
remove only exact run-owned temporary video/partial-download files. Preserve
user originals, outputs and provenance; record cleanup status.

## V3 ACTIVE

Source-faithful ordered measures → structured music → Guitar Pro. The multimodal
model consumes the actual source style directly, without monochrome preparation.
V1 COMPLETE / V2 CORE COMPLETE / V3 ACTIVE. Do not implement V3 in this cleanup.
URL acquisition remains unvalidated but does not block V3.

## Current V2 output policy

Select the cleanest source observation and export its pixels directly to measures/.
Prioritize coverage, order, no duplicates, source selection, faithful crop and
readable PDF, in that order. No duplicate source_measures/ folder, normalization
status, method comparison or whitening stage in new runs. Visual uniformity is
secondary; normalization is only an optional future presentation enhancement.

Remove legacy normalization fields and non-none tone settings from copied plans
before source-faithful export. The exporter rejects them before writing outputs.
Reuse accepted selections for mechanical regression in a fresh directory; do not
reconstruct the videos or alter historical outputs. Verify exact crop pixels,
order, single-directory output and unchanged generic presentation behavior.

## Final V2 hardening complete

Generic optional title/artist metadata, portable default or explicit font,
minimal user-facing page headers, and debug-only engineering wording are in
place. No measure identity or visual decision logic was added.

Re-exported the existing accepted plan/frames without revisiting raw video.
All 57 measures, measures.json, full_score.png and 15 row images are byte-identical;
all 3 page bodies are pixel-identical. The regenerated A4 PDF opens and its three
actual rendered pages were visually checked. Five automated tests pass, including
five presentation variants. See [hardening evidence](../acceptance/V2_HARDENING.md).

## Historical normalization experiment — retired

Reused accepted source selections and frames in a new run. Retained 57 untouched
RGB crops in source_measures/ and generated 57 visually reviewed normalized
measures, with source_output and normalization records. Identities, timestamps,
crop/context geometry, order and layout remain unchanged. Methods live in explicit
run plans, with per-measure overrides and original-source fallback; no automatic
style or musical identity inference was added.

Every source/output pair, difficult enlarged examples, full score sections, three
page PNGs and all actual PDF pages were inspected. This validates one light-background
scrolling video only. See [normalization evidence](../acceptance/V2_NORMALIZATION.md).
Preserve these artifacts and the Una Mattina test evidence. New runs do not repeat
normalization. Stop after the source-faithful cleanup and commit; no V3 work.
