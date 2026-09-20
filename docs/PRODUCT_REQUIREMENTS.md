# Guitar Tab Cracker — Product Requirements

**V1 COMPLETE · V2 COMPLETE · V3 STRUCTURED SCORE PASS**

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

Acquire with available tools; preserve supplied source information and keep
video bytes unchanged during processing. If direct URL acquisition fails, use
the user's chosen fallback https://www.xiazaitool.com/: paste the public video
URL, parse it and download the available video through its normal interface.
This is an acquisition fallback; visual reconstruction remains site-independent.
Do not bypass login, DRM, paywalls or access restrictions. If the fallback is
unavailable, fails or needs unavailable access, explain the specific blocker and
request a local file. Never claim acquisition succeeded without a usable file.

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
[test record](../acceptance/V2_UNA_MATTINA.md). URL/Xiazaitool acquisition remains
unvalidated, and these two fixtures do not establish universal robustness.

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

## V3 STRUCTURED SCORE PASS

Source-faithful ordered measure images → structured music → Guitar Pro.
V3 consumes measures/ directly; the multimodal model must handle the actual
visual source style. There is no monochrome normalization prerequisite.
V3 phase 1 ends at canonical score.json; Guitar Pro export is next. Local-video V2
is validated on the tested fixtures; URL acquisition is supported in the workflow
but unvalidated. A future hosted runtime may use a multimodal API agent with
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
and [acceptance](../acceptance/V3_STRUCTURED_SCORE.md). Guitar Pro export is next.
