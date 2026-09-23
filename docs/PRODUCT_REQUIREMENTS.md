# Guitar Tab Cracker — Product Requirements

**V1 COMPLETE / V2 COMPLETE / V3 STRUCTURED SCORE COMPLETE / V3 GUITAR PRO EXPORT COMPLETE / CORE PIPELINE COMPLETE**

## Core capability and input hierarchy

**Core: complete guitar-tab images / ordered score measures → canonical structured score → editable Guitar Pro.**
Video reconstruction is an upstream convenience layer; video input is not required.

- Prepared ordered measure images → core pipeline (implemented).
- Single full-score image / PDF → measure preparation → core pipeline (extended input; preparation not implemented in this phase).
- Overlapping screenshots → V1 → core pipeline.
- Local video → V2 → core pipeline.
- Public video URL → backend acquisition → local video → V2 → core pipeline (provider-dependent; see hardening acceptance).

**V1 COMPLETE · V2 COMPLETE · V3 STRUCTURED SCORE COMPLETE**

## Core model

Codex is the visual agent and workflow executor. Tools execute explicit
decisions; no CV/OMR algorithm decides score location, boundaries, content
changes, useful timestamps, duplicates, global order, best sources or layout.
No musical transcription in V1/V2. Preserve notation as pixels without parsing
string/fret numbers, durations, techniques, chords or other musical semantics.
Keep implementation and evidence private.

## V1 COMPLETE

Multiple screenshots → ordered measures → reconstructed printable score.
The existing [acceptance](../acceptance/V1_ACCEPTANCE.md) covers 10 screenshots,
26 logical measures and 2 A4 pages. Unseen-set reliability is not established.
Preserve this result and workflow; do not spend V2 effort polishing V1.

## V2 COMPLETE

Input is only one local raw guitar-tab video or an accessible video URL.
Users provide no screenshots, timestamps, sampling rate, ROI, crop coordinates,
measure numbers, duplicate relationships, ordering or page breaks.

Backend acquisition only: local file → direct public HTTP media → anonymous yt-dlp → opt-in authorized browser-session fallback → structured failure and local-file request. Do not navigate video sites in a browser or use third-party download websites. Do not bypass authentication, DRM or paywalls. See `tools/acquisition/README.md` (repository root) for commands and tested compatibility.

Use a run-specific temporary download directory and record exact downloaded
paths, acquisition method, source URL and file hash. After output generation and
all final QA passes, delete those downloaded video copies and partial downloads.
Verify each resolved deletion target belongs to this run's download directory;
do not recursively delete directories. Never delete user-supplied local originals,
selected frames, measures, scores, PDFs or provenance records. Record cleanup
status and removed paths in source metadata and the report. If processing is
interrupted and video is needed to resume, retain it as temporary working input
and disclose cleanup pending; clean it when processing finishes or is abandoned.

Inventory duration, resolution and approximate frame rate. Visually inspect a
small representative survey to establish actual video behavior, without assuming
scrolling, page replacement, a fixed score/playhead or constant zoom.
Codex then adaptively selects timestamps based on overlap, novelty, transitions
and coverage. Fixed sampling is not the product. Revisit unclear transitions
and search before/after obstructed frames for cleaner observations.

Maintain an internal operational ledger: source frames/timestamps, visible
occurrences, partials, new content, duplicate observations, preferred sources,
suspicious intervals and unresolved gaps. Record facts and uncertainty, not
chain-of-thought. Visually select useful complete/partial crops, preserving all
six TAB lines, stems/beams, ties/slurs, techniques and boundary context.
Avoid excessive scenery; never invent pixels to erase overlays.

Reconcile using visual evidence, chronology and neighboring context. Printed
numbers help but are optional. Separate repeated occurrences must not collapse
merely because they look alike. Never substitute a later repetition for missing
material. Combining complementary views requires established identity/alignment,
provenance for every contributing source and visual review of the join.

### Required artifacts

- `result/measures/001.png`, `002.png`, ...: PRIMARY product and direct V3 input.
  One source-faithful selected crop per logical occurrence, in complete global order.
  Preserve original notation pixels and boundary context. No duplicate source_measures/
  folder unless a specific future debugging case requires one.
- `result/measures.json`: ordered records with sequence_index,
  printed_measure_number (nullable), source_timestamp, source_frame, output,
  confidence and uncertainty. Preserve crop/context coordinates and contributing
  sources for composites. No monochrome normalization status or musical transcription.
- `result/source/source.json`: supplied source path/URL, acquired local path,
  video metadata and source identity; `result/frames/`: useful extracted frames.
- `result/inspection/`: optional contact sheets and review crops.
- `result/full_score.png`, multi-line A4 `page_001.png` and subsequent pages,
  `result/full_score.pdf`, concise `result/report.md`.

Before composition, explicitly audit beginning, ending, transitions, unmatched
partials and distinct repetitions. Could content have appeared briefly in an
unobserved interval? Revisit every suspicious interval before finalizing.
If a true source gap remains, finish resolvable work, label gaps/fragments and
report the limitation; never claim complete-song recovery or pass acceptance.

Codex chooses scale, staff alignment, row groups and page positions. Preserve
aspect ratios, annotation context and readable scale; never split measures.
Use actual A4 PDF dimensions. Complete, readable, correctly ordered and reasonably
consistent output is sufficient; content quality exceeds publication polish.
The exporter accepts optional title/artist metadata from its explicit plan and
omits unknown metadata. Use Pillow's portable default font or an explicit font
path relative to the plan; no proprietary font is committed. Normal pages show
only supplied metadata and page numbers. Engineering wording is debug-only.
Header/font/layout-only changes must preserve measure pixels and records.
### V2 priorities and source fidelity

Prioritize: (1) complete coverage, (2) correct order, (3) no accidental duplicates,
(4) cleanest available source frame, (5) faithful crop, (6) readable preview/PDF.
Choose another clean observation when cursors or overlays obscure notation.
Preserve original pixels, including faint lines, multidigit frets, dots, beams,
rests, ties/slurs, techniques, parentheses and all other meaningful marks.
Do not attempt inversion, thresholding, whitening, background removal or compare
cleanup methods in new V2 runs. Visual uniformity is secondary.

Normalization is only an optional future presentation enhancement. It is not a
V2 stage, an acceptance requirement or a V3 dependency. Keep accepted historical
runs and their evidence unchanged. New runs use a single measures/ folder.

After export, independently revisit the video beginning, early/middle/late
transitions and ending, using different timestamps where useful. Compare with
the ordered set and score; repair omissions, duplicates, order and poor source
selections, then regenerate. Open every selected measure, the full score at
readable scale, every page PNG and rendered pages of the actual PDF. Compare
against source evidence; mechanical success does not establish visual coverage.

The report includes source/URL, duration, frames actually inspected, extra
gap-recovery frames, logical count, unresolved fragments/gaps, unavoidable
artifacts, duplicate/omission findings, page count and final paths. No
chain-of-thought. Count inspected frames separately from merely extracted frames.

### Acceptance

Start at least one development run from a real raw guitar-tab video, never
screenshots converted into a fabricated video benchmark. If none exists, request
a representative video and complete independent implementation work meanwhile.
Raw-video acceptance passed on the local Yukinohana video: 209.95 seconds,
69 inspected frames, 57 complete logical measures and 3 A4 landscape pages.
See [acceptance](../acceptance/V2_ACCEPTANCE.md). The translucent Una Mattina
fixture also passed source-faithful reconstruction (45 units, 3 pages); see its
[test record](../acceptance/V2_UNA_MATTINA.md). Backend URL acceptance is documented separately; these fixtures do not establish universal robustness.

V2 passes only after autonomous evidence collection and gap revisits, no user
screenshot/timestamp/crop instructions, complete occurrence coverage confirmed by
independent video cross-check, no known duplicate/omission/order errors, readable
score/PDF, and ordered clean measure images suitable for V3. Prefer two different
video styles before claiming public robustness.

Classify failures as insufficient survey, missed fast transition, incomplete
gap audit, reconciliation error, repeated occurrence confusion, wrong crop,
dirty source selection, access failure or helper failure. Improve general skill
or mechanical tools and repeat; never embed fixture timestamps/answers in the
skill or replace visual reasoning with CV.

## V3 STRUCTURED SCORE COMPLETE

Source-faithful ordered measure images → structured music → Guitar Pro.
V3 consumes measures/ directly; the multimodal model must handle the actual
visual source style. There is no monochrome normalization prerequisite.
V3 phase 1 produces canonical score.json; phase 2 exports and validates editable Guitar Pro. Local-video V2
is validated on the tested fixtures; backend URL acquisition has direct-media evidence and structured public-page failures. A future hosted runtime may use a multimodal API agent with
controlled tools; no hosting or application framework is required for V2.

### V3 phase 1 contract

Codex reads every accepted V2 measure twice and records the written score without
OCR/OMR or music detectors. Strings are top/highest 1 to bottom/lowest 6. Preserve
durations, dots, tuplets, rests, simultaneous notes, fret/string, parentheses,
visible techniques, ties/slurs, repeats/endings, pickup state and visible changes.
Adjacent context introduces no extra events. Unknown metadata remains null;
ambiguities carry confidence, uncertainty and root unresolved records.

Required result/v3/ outputs: schema/score.schema.json, all per-measure JSON files,
score.json, validation.json and TRANSCRIPTION_REPORT.md with difficult source
images, JSON links and readable event tables. Helpers only merge explicit data,
validate structure/references/coverage and calculate exact fractional rhythms.
A mismatch requires image review, never arithmetic editing to force a fit.

Phase 1 acceptance requires every written unit exactly once, both visual passes,
global visual audit, coherent repeats/endings and cross-boundary relations,
deterministic validation and explicit ambiguity. Una Mattina passes with 45 units
and one unknown slide target. Four difficult Yuki no Hana units test another
style; they do not claim full-song coverage. See [schema](STRUCTURED_SCORE.md)
and [acceptance](../acceptance/V3_STRUCTURED_SCORE.md). Guitar Pro export now passes; see [phase 2 acceptance](../acceptance/V3_GUITAR_PRO.md).

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

Event-level arpeggio/strum arrows and independent pick-direction symbols must
be formal canonical data and survive GP export, import and visual direction
review. Recognized clear marks must not be relegated to unresolved records just
because an adapter mapping is missing. See [stroke acceptance](../acceptance/EVENT_STROKES.md).

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

## Local browser-extension acquisition MVP

For an accessible video already playing in Chrome/Edge, the user can load `browser-extension/`, pair it with `python -m local_companion`, and send current-page media candidates to `127.0.0.1:8787`. The extension handles page/session discovery; the companion owns downloads, timing, run directories and existing media validation. The validated local path feeds the unchanged V2 → V3 → GP → V4 workflow. No score processing, cookie export, cloud account or browser automation is added.

Supported initial media: complete HTTP video and unencrypted finite HLS with local sanitized-manifest remux. DASH MPD, DRM, live/advanced HLS and resources requiring replay of browser credentials remain unsupported. Signed candidate URLs are transient; persisted query values are redacted. A shared installation token plus extension ID protects localhost, with foreign Origin/Host rejection. A real Chromium HTML5 fixture handoff passed; Bilibili browser-session acceptance remains pending until the user sends its actual playing-page candidates. This is not a completed-song conversion.

See [extension setup](../browser-extension/README.md), [companion setup](../local-companion/README.md), and [acceptance](../acceptance/BROWSER_EXTENSION_ACQUISITION.md).
