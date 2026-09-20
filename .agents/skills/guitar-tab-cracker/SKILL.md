---
name: guitar-tab-cracker
description: Autonomously reconstruct guitar-tab videos, accessible video URLs, or overlapping screenshots into ordered source and normalized measure images and a source-faithful visual score with A4 PNG/PDF. No musical transcription or Guitar Pro export.
---

# Guitar Tab Cracker

Codex is the visual agent and workflow executor. Users provide only a video,
accessible URL or screenshots. Codex decides timestamps, score regions,
boundaries, identities, duplicates, order, source selection and page breaks.
Tools execute explicit decisions. Never use CV/OCR, projection or matching/ordering
algorithms to decide measure identity, boundaries, source selection or layout.
Mechanical image processing for agent-selected normalization is allowed; the
agent chooses methods and parameters and verifies visual fidelity.
No string/fret, rhythm, technique, chord or other musical transcription in V2.

Read docs/PRODUCT_REQUIREMENTS.md and docs/EXECUTION_PLAN.md before scope or
architecture changes. **V1 COMPLETE; V2 CORE COMPLETE; V3 ACTIVE.** Preserve V1 without
further polish. V2 includes source-preserving normalization and generic export;
the current enhancement stops after verification and commit without implementing V3. Keep implementation/evidence private.
Local-video V2 is validated. URL acquisition is supported in the workflow but
unvalidated; a second video style is unvalidated. Neither gap blocks V3.
The subsequent normalization request adds final V2 preparation; perfect raster
publication polish is not a prerequisite for V3.
Users never supply timestamps, sampling rates, ROI, coordinates, measure labels,
duplicate relationships, order or page breaks.

## V2 — video to ordered clean measures

### Phase 1 — Acquire video

Inspect local input directly. For URLs determine whether available tools can
access/download without bypassing login, DRM, paywalls or access restrictions.
If direct acquisition fails, use the user-selected fallback
https://www.xiazaitool.com/: paste the public video URL into its input, select
解析链接, then download the available video using the normal interface. Use
available browser tools; do not claim to submit a form if only page reading is
available. This fallback is authorized for future video conversions in this
project without asking again. Reconstruction remains website-independent.
If the service fails, cannot be operated with available tools or requires
unavailable access, state the concrete blocker and ask for a local file. Do not
bypass login, DRM, paywalls or access restrictions via the fallback.

Keep downloaded bytes unchanged throughout processing. Put downloads in a
run-specific temporary directory; record source URL, acquisition method, local
path, hash and exact run-owned download/partial-download paths in
result/source/source.json. Never fabricate video from screenshots.

### Phase 2 — Video inventory

Inspect duration, resolution, approximate frame rate and general structure.
Open a small representative frame set. Establish actual behavior: scrolling,
page replacement, fixed score/moving playhead, multiple visible measures,
changing zoom/position or combinations. Do not assume one behavior.
tools/extract_frames.py probe provides mechanical metadata; use --help.

### Phase 3 — Coarse visual survey

Choose several timestamps across the video; extract with ffmpeg or
tools/extract_frames.py frames. Open frames, using contact sheets if useful.
Visually estimate change speed, visible measures, overlap and transitions to
decide where to inspect next. This is not fixed sampling or proof of coverage.

### Phase 4 — Adaptive frame collection

Dynamically choose timestamps: sparse for slow changes, dense for fast changes,
nearby additional frames at unclear transitions. Seek every logical occurrence
at least once, preferably repeatedly. For playheads, cursors, highlights, blur
or overlays, search before/after for clean views. Do not settle for a dirty
source if a cleaner observation can reasonably be found. Keep useful frames
in result/frames/. Tools never choose timestamps or detect content changes.

### Phase 5 — Working coverage ledger

Maintain working/coverage.md or .json with operational facts: source frame and
timestamp, visible logical occurrences, partials, newly observed content,
duplicate observations, suspicious intervals, preferred sources and unresolved
gaps. Distinguish actually inspected from merely extracted frames; track extra
gap-recovery inspections. No chain-of-thought or user-maintained state.

### Phase 6 — Extract measure candidates

Visually choose every useful complete/partial box and mechanically crop into
working/candidates/. Record box, frame/timestamp, identity evidence and boundary
state (complete, partial_left, partial_right, partial_both).
Preserve all six TAB lines, stems/beams, techniques above/below, ties/slurs,
opening annotations and useful boundaries. Avoid excessive scenery; never crop
meaningful notation. Enlarge explicit regions when needed.

### Phase 7 — Cross-frame reconciliation

Visually determine identity, partial versus complete, continuity, global order
and preferred sources. Printed numbers help but are optional. Use chronology
and neighboring context to distinguish repeated musical occurrences from
duplicate observations. Never collapse occurrences merely because they look
alike, or substitute a later repetition for missing material. Preserve ambiguous
alternatives and account for each useful partial.

### Phase 8 — Build final logical measure set

Retain selected source crops before tonal processing in result/source_measures/001.png,
002.png, ... . The PRIMARY product is result/measures/ with matching names: the
preferred normalized version of each logical occurrence in the same global order,
without silent omissions or accidental duplication. Source evidence remains
available to V3 when normalized notation is ambiguous. Preserve notation
and boundary context. Combining complementary observations requires visually
established identity/alignment and review of the join. Never invent pixels to
erase obscuring overlays.

Write result/measures.json as an ordered array of operational records:
sequence_index, printed_measure_number (nullable), source_timestamp in seconds,
source_frame, source_output (e.g. source_measures/001.png), output (e.g. measures/001.png),
confidence and uncertainty. Add normalization status, confidence, source_faithful
and uncertainty; keep these separate from source-selection confidence.
When boundary context extends beyond a logical measure, record core_bbox_in_output
and context extents explicitly; compose cores only to avoid repeated notation.
Retain crop boxes; for composites list every contributing frame/timestamp,
box and placement. No musical transcription. Unknown numbers stay null.
Partial/gap status must remain explicit, not presented as complete recovery.

### Phase 9 — Explicit gap audit

Before composition inspect unobserved transitions, briefly visible content,
beginning, ending, unmatched partials and similar-looking separate occurrences.
For EVERY suspicious interval return to the video, extract additional chosen
frames and inspect again. Do not finalize until coverage is reasonably complete.
If true source gaps cannot be resolved, finish available work with explicit
gap/partial labels in output and report, and state what additional source is
needed. Incomplete source recovery does not pass the completion gate.

### Phase 9b — Source-faithful score normalization

Inspect representative selected measures for actual source style and song-level
consistency. Choose and compare suitable transformations using any available
mechanical local tools. No fixed recipe is prescribed: light/dark/translucent
backgrounds, moving imagery, overlays and antialiasing may require different
methods. Use a consistent song-level treatment where safe and explicit
per-measure exceptions where needed. Do not force white backgrounds at the cost
of information. Never redraw, invent music or reconstruct hidden pixels.

Preserve original selected evidence in source_measures/. Visually compare EVERY
source/output pair at native/readable scale. Preserve six lines, barlines, frets
including multi-digit numbers, stems, beams, rests, dots, tuplets, ties/slurs,
slides, bends, harmonics, parentheses/ghost notes, X marks, H/P/sl labels, accents
and all other meaningful marks. Check erased thin lines, merged/broken digits,
lost curves and false notation from background noise. Keep antialiasing if useful.

Record normalized only after visual confirmation of fidelity; partial for safe
but incomplete cleanup (or explicitly unreviewed candidates), source_preserved
for original-pixel fallback. If uncertain, use the source crop and explain why.
Always record confidence, source_faithful and uncertainty honestly. Keep crop
geometry, core context, identities and order stable. Methods and parameters belong
in run decisions, not song-specific helper constants or a universal skill recipe.
See docs/NORMALIZATION.md for operations, external prepared images, song-level
profiles and per-measure overrides. Other evidence-based tools remain allowed.

### Phase 10 — Visual score output

Compose the preferred normalized measures/ set into result/full_score.png, multi-line A4 page_001.png
and subsequent pages, and full_score.pdf. Choose scale, staff alignment, row
groups and placements visually. Preserve aspect ratio, readable consistent
scale, sensible margins and cross-boundary annotation context. Never split a
measure. PDF pages must be actual A4. Content quality exceeds publication polish.

Use mechanical helpers when they save repeated work. tools/export_visual_score.py
executes explicit source boxes, context extents, normalization decisions, order
and placements, exporting both three-digit source and preferred images with
metadata. tools/normalize_measures.py executes chosen operations or uses an
externally prepared image; tools never choose methods or claim visual fidelity.
The export plan may supply title and artist; omit unknown metadata. Optional
font paths are relative to the plan, otherwise use Pillow's portable bundled
font. Supply a suitable font for glyphs outside its coverage; do not commit
proprietary fonts. Normal headers contain only supplied metadata and page numbers.
show_header=false hides the header; debug=true opts into engineering labels.
Presentation-only changes must preserve measures/ and measures.json. Verify
against the accepted run rather than repeating raw-video reconstruction.
tools/compose.py consumes
explicit V1 plans with input/ beside the plan; its mNN.png names are not the V2
contract. When reusing it, explicitly export selected tiles to three-digit V2
names with provenance, or mechanically compose the already exported ordered
set. Benchmark decisions are one run's evidence, never another song's template.
Build each revision in a fresh run directory so stale measure/page files cannot
remain in the delivered set. Do not invent automatic musical layout logic.

### Phase 11 — Independent video cross-check

After generation return to the original video. Inspect beginning, early,
middle and late transitions, and ending, using different timestamps where
useful. Compare with measures/ and full_score.png. Autonomously repair missing
or duplicated occurrences, incorrect order and poor source selections, then
regenerate affected outputs and metadata.

### Phase 12 — Final output QA

Open EVERY source/normalized measure pair and readable contact sheets, full_score.png
at readable scale (sections if long), every page PNG and rendered pages of the
actual PDF. Enlarge representative difficult notation against original crops. Verify all logical
occurrences, no accidental duplicates, order against video, unclipped notation,
cleanest practical sources, readability and PDF/page agreement. Correct and
regenerate; successful script execution does not establish visual correctness.
Hashes, counts and geometry checks supplement mandatory visual inspection.

Write concise result/report.md: source video/URL, duration, frames actually
inspected, extra gap-recovery frames, logical measure count, unresolved
fragments/gaps, unavoidable artifacts, duplicate/omission findings, page count,
final paths and remaining source limitations. Include normalization method, status
counts, pair-review coverage, fallback reasons and known uncertainty. No chain-of-thought.

### Post-QA — Download cleanup

After reconstruction and all final visual/video checks are finished, delete the
video copies downloaded for this run, including partial downloads. This cleanup
is explicitly user-authorized; do not request permission again. Before deletion,
resolve each exact path and verify it stays inside this run's temporary download
directory. Delete individual files, never recursively delete a directory or use
broad wildcard removal. Never delete user-supplied local originals, frames,
measure images, scores, PDFs, ledgers or source metadata. Retain URL/hash and mark
local video as removed, with cleanup status and removed paths in source.json
and report.md. If interrupted while video is needed to resume, record cleanup
pending; remove it once processing finishes or the run is abandoned.

## Development and completion

Test from at least one REAL raw guitar-tab video without prepared screenshots
or user timestamp/crop instructions. If no fixture exists, request a
representative video while completing independent implementation. Never
manufacture a video benchmark.

V2 completes only after autonomous evidence collection and gap revisits,
independent video coverage review, no known duplicate/order/omission errors,
readable score/PDF and a clean ordered set suitable for V3. Prefer two video
styles before claiming public robustness. For normalization-only changes, reuse
the accepted selections and frames; do not repeat video reconstruction unless
changed mechanics or evidence require it. Review every pair and regenerated
artifact. Core acceptance and final hardening are complete; current status is V2 CORE COMPLETE / V3 ACTIVE. Further visual
beautification is not a prerequisite to the structured-music stage.

On failure classify insufficient survey, fast transition, incomplete gap audit,
reconciliation mistake, repeated occurrence confusion, crop, dirty source,
access or helper failure. Improve general instructions/mechanics and repeat.
Never embed fixture timestamps/answers in this skill or redesign as CV/OMR.

## Preserved V1 screenshot workflow

1. Recheck all source images, preserving original bytes/names. Filename order
   is not score order; mechanical inventory/dimensions are allowed.
2. Open EVERY source. Visually identify TAB regions, numbers, boundaries,
   partials, overlays and clean alternatives. Inspect above/below the strings.
3. Choose all useful complete/partial candidate boxes visually, crop mechanically
   and retain source, box, identity evidence and boundary state.
4. Reconcile overlaps, distinct repeated occurrences and partial-to-complete
   alternatives visually. Preserve ambiguities; do not substitute repetitions.
5. Keep a concise operational ledger of each logical occurrence, supporting
   sources, partials, order evidence, selection and uncertainty. Audit coverage
   and numbering jumps; an unlabeled edge does not establish missing contents.
6. Select sharp, complete, unobstructed sources with minimal overlays. Preserve
   original color unless visually verified tonal changes improve printing.
   Composite only established matching views; inspect joins, never invent music.
7. Execute explicit crop/order/scale/alignment decisions with mechanical tools.
   Choose A4 portrait row/page breaks visually, preserving annotation context
   and never splitting measures.
8. Export full_score.png, page_001.png and subsequent pages, full_score.pdf.
   Open the full score at readable scale, every PNG page and actual PDF renders;
   compare against all sources, correct and regenerate.
9. Report source/logical counts, complete/partial/gap coverage, duplicate and
   omission findings, page count, paths and source limitations. Finish resolvable
   work and label genuine gaps; never imply incomplete input yielded a full song.
   Recheck changed inputs before declaring gaps. Ask for more source only when
   genuinely necessary, not for routine coordinates or ordering.

## V3 ACTIVE — handoff boundary

Ordered clean measure images → visual transcription → structured music →
independent alphaTab/MusicXML/Guitar Pro export tools. A future hosted runtime
may use a multimodal API agent with controlled tools. These stages are outside V2.
