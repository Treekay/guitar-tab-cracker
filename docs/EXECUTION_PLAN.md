# Execution Plan

**V1 COMPLETE / V2 COMPLETE / V3 STRUCTURED SCORE COMPLETE / V3 GUITAR PRO EXPORT COMPLETE / CORE PIPELINE COMPLETE**

## Core capability and input hierarchy

**Core: complete guitar-tab images / ordered score measures → canonical structured score → editable Guitar Pro.**
Video reconstruction is an upstream convenience layer; video input is not required.

- Prepared ordered measure images → core pipeline (implemented).
- Single full-score image / PDF → measure preparation → core pipeline (extended input; preparation not implemented in this phase).
- Overlapping screenshots → V1 → core pipeline.
- Local video → V2 → core pipeline.
- Public video URL → backend acquisition → local video → V2 → core pipeline (provider-dependent; see hardening acceptance).

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
ordering and placement. Historical tonal experiments are retained as evidence only.

FFmpeg is available from the project temporary imageio-ffmpeg wheel; ReportLab
and Pillow are in the bundled Python runtime; Poppler rendered the actual PDF.
The ffprobe-based metadata command remains available when ffprobe is installed;
this run used FFmpeg's input inventory and the same explicit extraction helper.

## Remaining robustness validation

The translucent Una Mattina fixture passed source-faithful reconstruction: 61
inspected frames, 45 ordered units, 3 checked PDF pages. Whitening did not pass
and is no longer required. Broader robustness still needs more evidence.
Historical Bilibili HTTP 412 did not validate website compatibility.

Backend acquisition only: local file → direct public HTTP media → anonymous yt-dlp → opt-in authorized browser-session fallback → structured failure and local-file request. Do not navigate video sites in a browser or use third-party download websites. Do not bypass authentication, DRM or paywalls. See `tools/acquisition/README.md` (repository root) for commands and tested compatibility.
After final QA, remove only recorded run-owned downloads; preserve user originals and provenance.

## V3 STRUCTURED SCORE COMPLETE

Source-faithful ordered measures → structured music → Guitar Pro. The multimodal
model consumes the actual source style directly, without monochrome preparation.
V1 COMPLETE / V2 COMPLETE / V3 STRUCTURED SCORE COMPLETE. V3 GUITAR PRO EXPORT COMPLETE / CORE PIPELINE COMPLETE.
Backend URL acquisition remains independent of V3; page-provider limitations do not block local conversion.

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
normalization. The historical cleanup is complete; V3 phase 1 is described above.

## Structured-score execution evidence

- All 45 accepted Una Mattina units visually transcribed and independently
  reopened: 628 events, 692 note records, two repeat regions, two pairs of
  alternate endings, 14 ties, seven descending slides and the opening harmonic.
- Canonical schema, assembler, exact-fraction validator and readable QA report
  implemented in phase 1 without recognition code or normalization. Guitar Pro
  output is provided by the separate completed phase 2 adapter below.
- Zero rhythmic warnings. One first-ending slide destination remains unknown.
  All three full-score sections were globally rechecked after assembly.
- Yuki no Hana printed 1, 16, 29, 30 are a limited second-style sample covering
  chords, H/P, triplets, slides/slurs and outgoing sample-boundary ties.
- V1/V2 artifacts are unchanged. Deterministic tests are separate from visual
  acceptance; see [acceptance](../acceptance/V3_STRUCTURED_SCORE.md).

## V3 Guitar Pro export acceptance complete

The canonical recognition model, deterministic alphaTab adapter and target-format
library are separate. Python validation remains authoritative; Node.js builds the
alphaTab Score, calls Gp7Exporter and reloads the saved `.gp` with ScoreLoader.
No alphaTab fields or technical defaults enter canonical JSON.

Acceptance requires actual re-import, canonical-to-import semantic comparison
(strings/frets, durations/dots/tuplets, rests/chords/voices, ties/techniques,
written order, meters, repeat counts/endings and final bar), no unexplained
mismatch, and selected difficult measures visually checked against source images.
Differences are EXACT, EXPECTED_EXPORT_DEFAULT, KNOWN_UNSUPPORTED_MAPPING or
UNEXPECTED_MISMATCH. Generated IDs are excluded. Rendering alone cannot pass QA.

Una Mattina passes 45/628/692 measures/events/notes; Yuki no Hana passes 4/42/54
as a sample. One Una slide target and three outgoing sample ties remain unknown
and are omitted with exact provenance. Default metadata, playback settings and
repeat counts are exporter assumptions, not recognized data. Source JSON and
V1/V2 assets are unchanged. 25 adapter tests and 16 existing validator tests pass.
See [mapping](GUITAR_PRO_MAPPING.md), [commands](../tools/guitar-pro/README.md)
and [acceptance](../acceptance/V3_GUITAR_PRO.md). Optional standardized PDF is
not required; re-imported SVG/PNG previews provide visual review evidence.

## V4 verification layer

Verification now separates source/reference disagreement from transcription,
assembly, adapter and target-rendering faults. Keep full deterministic assembly,
validator and GP round-trip checks; focus independent visual effort on source
feature sweeping, high-risk fields and target-limited rendering. Do not rerun
accepted V2 reconstruction or copy manual-GP values into canonical automatically.

Record VERIFIED, AUTO_CORRECTED, USER_REVIEW_REQUIRED and KNOWN_EXPORT_LIMITATION
at item/field level with hashes and exact review locations. Corrections require
clear source rereading, minimal field patches and fresh downstream validation.
Una Mattina has no justified canonical correction from the current reference
comparison; two slide-interpretation issue groups remain user review. The first
repeat endings are visible in source and must be preserved.
See [pipeline](VERIFICATION_PIPELINE.md) and
[analysis](../acceptance/V4_VERIFICATION_ANALYSIS.md). V4 analysis/design and
verification tooling are implemented; this is not a universal accuracy claim.

## Timing, delivery reporting and backend acquisition

Every future run begins explicit monotonic timing before acquisition and brackets visual work as well as commands. Unexecuted/reused stages stay null; historical timings are never reconstructed. Finish timing after final QA and generate `result/final_report.json` and `.md` from existing V4 evidence. Reports include phase/total durations and the three slowest phases.

Delivery statuses are `READY_FOR_DELIVERY`, `REVIEW_RECOMMENDED`, and `REVIEW_REQUIRED`. Detail every correction, unresolved item, known export limitation and unexpected mismatch with exact musical location, values, source/generated paths and correction history. Summarize verified groups; do not invent an accuracy percentage. A valid GP round-trip alone does not establish source accuracy.

See [workflow commands](../tools/pipeline/README.md), [backend](../tools/acquisition/README.md), and [measured acceptance](../acceptance/HARDENING_ACCEPTANCE.md).

Browser-session acquisition is an opt-in local development/desktop capability: `--cookies-from-browser edge|chrome|firefox`, or `--auto-browser-cookies` with `GTC_BROWSER_COOKIE_SOURCES`. Automatic cookies are limited to authentication/session challenges, never arbitrary network errors. Existing accessible sessions do not authorize bypassing DRM, paywalls or private permissions. Raw cookies/headers are never persisted; safe attempt diagnostics and media validation remain mandatory. Remote web-server profile access is not an intended product interface. See `tools/acquisition/README.md` and `acceptance/BROWSER_COOKIE_ACQUISITION.md` from the repository root.
