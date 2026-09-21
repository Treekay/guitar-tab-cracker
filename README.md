# Guitar Tab Cracker

Private Codex-first workflow. Invoke [$guitar-tab-cracker](.agents/skills/guitar-tab-cracker/SKILL.md).

- **V1 COMPLETE:** screenshots → ordered measures → reconstructed visual score.
- **V2 COMPLETE:** local video → ordered clean measure set → visual score.
- **V3 STRUCTURED SCORE COMPLETE:** ordered measures → canonical written score JSON.
- **V3 GUITAR PRO EXPORT COMPLETE:** canonical JSON → editable `.gp` → re-import and visual validation.
- **CORE PIPELINE COMPLETE.**

## Core capability and input hierarchy

**Core: complete guitar-tab images / ordered score measures → canonical structured score → editable Guitar Pro.**
Video reconstruction is an upstream convenience layer; video input is not required.

- Prepared ordered measure images → core pipeline (implemented).
- Single full-score image / PDF → measure preparation → core pipeline (extended input; preparation not implemented in this phase).
- Overlapping screenshots → V1 → core pipeline.
- Local video → V2 → core pipeline.
- Public video URL → backend acquisition → local video → V2 → core pipeline (provider-dependent; see hardening acceptance).

For upstream video reconstruction, provide a local video and ask **Convert this guitar-tab
video.** Codex chooses inspection timestamps, extracts frames, revisits gaps,
reconciles observations, selects clean sources and visually verifies the output.
Users supply no screenshots, sampling rate, ROI, coordinates, numbering,
duplicate relationships, sequence order or page breaks.

The primary V2 artifact is `result/measures/001.png`, `002.png`, ...: the
source-faithful selected crops in global order, ready for V3. `measures.json`
records source timestamps, coordinates, confidence and uncertainty. New runs
create one measure folder, without normalization status or duplicate source crops.
Other outputs: source metadata, useful frames, `full_score.png`, A4 page PNGs,
`full_score.pdf` and concise `report.md`.

Priorities, in order: complete coverage, correct order, no accidental duplicates,
cleanest available source frame, faithful crop, readable preview/PDF. Preserve
original notation pixels; seek another observation to avoid cursors or overlays.
Do not invert, threshold, whiten or remove backgrounds. Visual uniformity is
secondary. Normalization is only an optional future presentation enhancement,
not a V2 stage or V3 prerequisite. V3 must handle the actual source style.

**Raw-video acceptance passed:** one 209.95-second local video → 69 inspected
frames → 57 ordered complete logical measures → 3 visually checked A4 landscape
pages. Coverage includes adaptive recovery and an independent second video pass.
See [V2 acceptance](acceptance/V2_ACCEPTANCE.md) and
[outputs](runs/v2-yukinohana/result/). No known omissions or duplicate occurrences
remain in this run. The user-owned original video is unchanged.

Local-video reconstruction is validated on the original light-background video
and the translucent Una Mattina fixture. This is not a universal robustness claim.
Backend direct-media acquisition is tested; public-page compatibility remains limited. V1 COMPLETE; V2 COMPLETE;
V3 STRUCTURED SCORE COMPLETE. Structured-score and Guitar Pro export acceptance both pass.

Codex makes every visual decision. Helpers execute explicit timestamps, crops,
order, scales and placements; they never detect notation or infer layout.
No CV/OMR application, ROI configuration or fixed-sampling product is involved.
URLs must be accessible without bypassing login, DRM, paywalls or restrictions.
Backend acquisition only: local file → direct public HTTP media → yt-dlp public-page extraction → structured failure and local-file request. Do not navigate video sites in a browser or use third-party download websites. Do not bypass authentication, DRM or paywalls. See `tools/acquisition/README.md` (repository root) for commands and tested compatibility.
After reconstruction and final QA, delete only video copies downloaded for this
run (including partial downloads); retain measure images, score/PDF and source
metadata. Never delete a user-supplied local original.

## Tools and evidence

- `tools/extract_frames.py`: video metadata and explicit-timestamp extraction,
  using ffprobe/ffmpeg on PATH or supplied executable paths. Run `--help`.
- `tools/export_visual_score.py`: V2 explicit crop/context/order/page exporter,
  using Pillow and ReportLab; saves stable three-digit measures and provenance.
  Optional plan keys: `title`, `artist`, `font`, `show_header`, `debug`. Metadata
  is omitted when unknown. The default font is Pillow's bundled font; an explicit
  font path is resolved relative to the plan. Supply a font with suitable glyph
  coverage when needed. Normal pages show only supplied metadata and page numbers;
  engineering labels require `debug: true`. `show_header: false` hides the header.
- `tools/compose.py`: existing mechanical crop/place/export helper, using Pillow
  and ReportLab. Its existing V1 plan format is preserved; the V2 skill describes
  adapting explicit paths and exporting the stable measure set.
- `benchmark/input/`: preserved V1 screenshots.
- `benchmark/decisions.json`: one run's evidence, never another song's template.
- `acceptance/`: preserved V1 acceptance artifacts.

V1 acceptance: **10 screenshots → 26 logical measures → 2 A4 pages**, with
source comparison and actual PDF verification. Only the existing set was
validated; residual source overlays are documented. See
[V1 acceptance](acceptance/V1_ACCEPTANCE.md),
[printable score](acceptance/v1-existing/full_score.pdf) and
[benchmark report](benchmark/REPORT.md). Do not further polish V1 for V2.

Read [requirements](docs/PRODUCT_REQUIREMENTS.md) and
[execution plan](docs/EXECUTION_PLAN.md). Implementation and evidence remain
private. A future hosted runtime would use a multimodal agent with controlled
tools; no hosted application is implemented here. Codex now performs local V3 transcription visually.

The [V2 handoff regression](acceptance/V2_HARDENING.md) confirms unchanged
measure images, metadata and score order after generic PDF export.
Historical [normalization evidence](acceptance/V2_NORMALIZATION.md) and its
[outputs](runs/v2-yukinohana-normalized/result/) are retained unchanged. That
experiment is no longer the output policy; see [retirement note](docs/NORMALIZATION.md).

The [Una Mattina test](acceptance/V2_UNA_MATTINA.md) reconstructs 45 units from
translucent notation over moving footage, with 3 checked PDF pages. Whitening did
not pass; source pixels were retained. This motivated the source-faithful policy.
[Test outputs](runs/v2-una-mattina/result/).

## V3 structured score

All 45 accepted Una Mattina units have two-pass visual transcription: 628 events,
692 note records, two repeat regions and first/second endings. Validation passes
with no rhythmic warnings. One slide destination remains explicitly unresolved.
Four difficult Yuki no Hana measures are a separate limited sample.

- [Canonical score](runs/v2-una-mattina/result/v3/score.json)
- [Transcription report](runs/v2-una-mattina/result/v3/TRANSCRIPTION_REPORT.md)
- [Schema and tool usage](docs/STRUCTURED_SCORE.md)
- [Phase 1 acceptance](acceptance/V3_STRUCTURED_SCORE.md)

The transcription stage uses no OCR/OMR or normalization. Export consumes the accepted canonical JSON without re-transcription.

## Editable Guitar Pro export

Una Mattina: **45 written measures, 628 events, 692 notes** survive export and
re-import with zero unexpected mismatches. Yuki no Hana: **4 sample measures,
42 events, 54 notes**, also passes. Selected difficult renderings were compared
against the accepted source images. Unknown endpoints are omitted and reported,
never guessed; export defaults never change canonical metadata.

- [Una Mattina score.gp](runs/v2-una-mattina/result/v3/export/score.gp)
- [Export report](runs/v2-una-mattina/result/v3/export/export_report.md)
- [Round-trip validation](runs/v2-una-mattina/result/v3/export/roundtrip_validation.json)
- [Yuki no Hana sample.gp](runs/v2-yukinohana/result/v3/export/score.gp)
- [Commands and architecture](tools/guitar-pro/README.md)
- [Mapping and limits](docs/GUITAR_PRO_MAPPING.md)
- [Phase 2 acceptance](acceptance/V3_GUITAR_PRO.md)

Run artifacts remain local under ignored `runs/`; reusable code and acceptance
records are versioned. No Guitar Pro desktop application was used for acceptance.

## V4 verification and error localization

A separate verification layer compares independent source observations, checks
assembly and fresh GP round-trip, benchmarks an explicitly aligned human GP, and
builds localized source/generated/reference review packets. It preserves accepted
canonical data unless source evidence supports a minimal revalidated correction.

Una Mattina's reported first-ending error was not confirmed: its source images
contain those endings. The human GP also has one string-position discrepancy
where the source supports generated output. Slide articulation remains explicit
user review; matching GP round-trip does not prove transcription accuracy.

- [Verification policy](docs/VERIFICATION_PIPELINE.md)
- [Forensic analysis and reference metrics](acceptance/V4_VERIFICATION_ANALYSIS.md)
- [Current review report](runs/v2-una-mattina/result/v3/verification/verification_report.md)
- [Tool usage](tools/verification/README.md)

Yuki no Hana also has a complete local-video rerun (57 measures), superseding the
four-measure export sample for this input. Its GP round-trip passes; delivery is
`REVIEW_REQUIRED` because an unmetered slide onset is outside schema v1. The
source-only verification records all-measure rereads and localized limitations.
The user selected previously exposed material, so this is not an unseen-video
blind benchmark.

- [Full Yuki no Hana GP](runs/v4-yuki-source-only/result/v3/export/score.gp)
- [Source-only verification report](runs/v4-yuki-source-only/result/v3/verification/verification_report.md)
- [Run evidence and limitations](acceptance/V4_YUKI_SOURCE_ONLY.md)

## Timing, delivery reporting and backend acquisition

Every future run begins explicit monotonic timing before acquisition and brackets visual work as well as commands. Unexecuted/reused stages stay null; historical timings are never reconstructed. Finish timing after final QA and generate `result/final_report.json` and `.md` from existing V4 evidence. Reports include phase/total durations and the three slowest phases.

Delivery statuses are `READY_FOR_DELIVERY`, `REVIEW_RECOMMENDED`, and `REVIEW_REQUIRED`. Detail every correction, unresolved item, known export limitation and unexpected mismatch with exact musical location, values, source/generated paths and correction history. Summarize verified groups; do not invent an accuracy percentage. A valid GP round-trip alone does not establish source accuracy.

See [workflow commands](tools/pipeline/README.md), [backend](tools/acquisition/README.md), and [measured acceptance](acceptance/HARDENING_ACCEPTANCE.md).
