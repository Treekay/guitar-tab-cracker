---
name: guitar-tab-cracker
description: Autonomously reconstruct guitar-tab videos, accessible video URLs, or overlapping screenshots into ordered source-faithful measure images and a source-faithful visual score with A4 PNG/PDF. Core ordered score images become canonical structured music and editable Guitar Pro through alphaTab, with source-based verification, error localization and round-trip validation; no OCR/OMR.
---

# Guitar Tab Cracker

Codex is the visual agent and workflow executor. Core input is complete guitar-tab
images or ordered measures; video, accessible URLs and overlapping screenshots
are upstream convenience inputs. Codex decides timestamps, score regions,
boundaries, identities, duplicates, order, source selection and page breaks.
Tools execute explicit decisions. Never use CV/OCR, projection or matching/ordering
algorithms to decide measure identity, boundaries, source selection or layout.
Preserve selected source pixels; helpers only execute explicit extraction, crop,
order and presentation decisions.
No string/fret, rhythm, technique, chord or other musical transcription in V2.

Read docs/PRODUCT_REQUIREMENTS.md and docs/EXECUTION_PLAN.md before scope or
architecture changes. **V1 COMPLETE; V2 COMPLETE; V3 STRUCTURED SCORE COMPLETE.** Preserve V1 without
further polish. V2 exports selected source crops directly. V3 phase 1 ends at
canonical structured JSON; phase 2 exports editable GP with round-trip validation.
**V3 GUITAR PRO EXPORT COMPLETE; CORE PIPELINE COMPLETE.** Keep evidence private.
Local-video reconstruction is validated on the light-background and translucent
fixtures. URL acquisition is supported but unvalidated; no universal robustness
claim. Normalization is only an optional future presentation enhancement, never
required by V2 or V3. Do not perform it in new runs.

Prioritize complete coverage, correct order, no accidental duplicates, cleanest
source frame, faithful crop and readable preview/PDF, in that order. Visual
uniformity is secondary. Avoid cursors/overlays by finding cleaner observations.
Users never supply timestamps, sampling rates, ROI, coordinates, measure labels,
duplicate relationships, order or page breaks.

## V2 — video to ordered clean measures

### Phase 1 — Acquire video

For the browser-extension MVP, the user opens/plays an authorized video and explicitly clicks the local Chromium extension. Read browser-extension/README.md and local-companion/README.md. Start the localhost-only companion and prepare pairing before asking the user to load/click the extension. Never ask them to send the pairing token or cookies in chat. Read the resulting run status and validate/extract/view a frame before reporting browser-session acquisition success. A blob URL alone is not downloadable. Unsupported/DRM/session-dependent streams remain explicit failures. Do not operate video pages for the user or add anonymous scraping workarounds. The extension handles discovery only; hand off its validated local path to unchanged V2/V3/V4. For an acquisition-only task, do not start a full conversion.

Backend acquisition only: local file → direct public HTTP media → anonymous yt-dlp → opt-in authorized browser-session fallback → structured failure and local-file request. Do not navigate video sites in a browser or use third-party download websites. Do not bypass authentication, DRM or paywalls. See `tools/acquisition/README.md` (repository root) for commands and tested compatibility.
For user-authorized existing sessions, use --cookies-from-browser edge|chrome|firefox or --auto-browser-cookies with GTC_BROWSER_COOKIE_SOURCES. Ask which browser is logged in when necessary; do not read unspecified profiles implicitly. Automatic fallback only follows authentication/session/access challenges, not general network errors. Use yt-dlp native integration, never manually parse browser databases, bypass encryption, kill browsers, log cookie values, or persist cookie exports. This is a local desktop/development capability.
Use tools/acquisition/acquire.py; only pass a successfully validated local path to V2. Capture structured failures and request a local original if acquisition fails.

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

The PRIMARY product is result/measures/001.png, 002.png, ...: exactly one
source-faithful selected crop per logical occurrence in global order. Preserve
original notation pixels and boundary context. Do not create duplicate
source_measures/ folders unless a specific future debugging case requires one.
Combining complementary observations requires established identity/alignment,
source provenance and visual review of the join. Never invent hidden notation.

Write result/measures.json as ordered records: sequence_index,
printed_measure_number (nullable), source_timestamp, source_frame, output,
confidence and uncertainty. Do not add monochrome normalization status fields.
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

### Phase 10 — Visual score output

Compose the source-faithful measures/ set into result/full_score.png, multi-line A4 page_001.png
and subsequent pages, and full_score.pdf. Choose scale, staff alignment, row
groups and placements visually. Preserve aspect ratio, readable consistent
scale, sensible margins and cross-boundary annotation context. Never split a
measure. PDF pages must be actual A4. Content quality exceeds publication polish.

Use mechanical helpers when they save repeated work. tools/export_visual_score.py
executes explicit source boxes, context extents, order and placements, exporting
one measures/ folder and provenance. Do not compare inversion/thresholding methods,
whiten or remove backgrounds. V3 consumes the actual source style directly.
Legacy normalization or non-none tone settings are rejected before output; remove
them from a copied plan for a new run, preserving historical plans and artifacts.
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

Open EVERY selected measure against its source evidence and readable contact sheets, full_score.png
at readable scale (sections if long), every page PNG and rendered pages of the
actual PDF. Enlarge representative difficult notation against original crops. Verify all logical
occurrences, no accidental duplicates, order against video, unclipped notation,
cleanest practical sources, readability and PDF/page agreement. Correct and
regenerate; successful script execution does not establish visual correctness.
Hashes, counts and geometry checks supplement mandatory visual inspection.

Write concise result/report.md: source video/URL, duration, frames actually
inspected, extra gap-recovery frames, logical measure count, unresolved
fragments/gaps, unavoidable artifacts, duplicate/omission findings, page count,
final paths and remaining source limitations. No normalization method/status
reporting is needed. Record operational facts, not chain-of-thought.

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
styles before claiming public robustness. For mechanical export changes, reuse
the accepted selections and frames; do not repeat video reconstruction unless
changed mechanics or evidence require it. Review affected crops and regenerated
artifact against source evidence. Preserve accepted runs unchanged. Core acceptance and final hardening are complete; current status is V2 COMPLETE / V3 STRUCTURED SCORE COMPLETE. Further visual
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

## V3 structured written score — complete

Source-faithful ordered measure images → visual transcription → structured music →
independent canonical-to-alphaTab adapter and Gp7Exporter. A future hosted runtime
may use a multimodal API agent with controlled tools. V3 handles the actual source
style without normalization. These stages are outside V2.


Read docs/STRUCTURED_SCORE.md and schema/score.schema.json. Use accepted complete
ordered V2 measures directly. Codex is the recognizer: no OCR/OMR, fret/rhythm
detectors or visual parsing algorithms. Do not fetch music metadata. Revisit
source frames only if an individual crop is insufficient.

For every measure, open the image at readable resolution and explicitly record
written structure, chronological events, durations, dots/tuplets/rests,
simultaneous notes, strings/frets, parentheses, techniques and boundary context.
String 1 is top/highest, 6 bottom/lowest. Use stems/flags/beams, never spacing
alone. Write v3/measures/NNN.json. For V4 runs, use the independent source feature
sweep and field-level rereading policy in docs/VERIFICATION_PIPELINE.md.
Reopen every source to find omitted/suspicious features, then independently audit
high-risk fields and cross-boundary relations. On uncalibrated styles or repeated
errors, retain full event rereading. Mark pass2 inspected only for actually reopened
images; the verification ledger must state exact reviewed fields/scope rather
than imply all notes were re-transcribed.

Represent written order, not repeat playback. Preserve endings; unknown repeat
counts stay null. Use explicit cross-measure references. Context outside the core
is not another event. A tied continuation without a reprinted fret retains its
written duration and incoming tie, not a new attack. Parentheses alone do not
imply ghost articulation. Unknown metadata stays null.

Mark ambiguity with confidence, uncertainty and root unresolved records. Helpers
may merge JSON, validate schema/references/coverage/repeats and calculate dotted
and tuplet totals; they must not infer music. A mismatch requires image review,
never a duration edit merely to fit. Genuine ambiguity may remain explicit.

Assemble result/v3/score.json from finalized records in exact V2 written order.
Export schema/score.schema.json, validation.json and TRANSCRIPTION_REPORT.md.
Include difficult source images, JSON links, readable event tables, counts,
repeats/endings, techniques, warnings and uncertain items. Globally recheck
coverage/order, opening metadata, final bar and cross-boundary notation after
assembly. Test validation separately; synthetic tests do not prove visual accuracy.
Preserve V1/V2 artifacts. Label limited second-style samples explicitly and record
relations into unsampled measures. Never embed fixture answers in this skill.
Structured-score phase 1 and Guitar Pro export phase 2 both pass on the documented acceptance inputs.


## Core input hierarchy

Ordered complete score measures → canonical structured score → editable Guitar Pro.
Video is not required. Single full-score image/PDF → measure preparation → core
(preparation is an extended input, not implemented by this phase). Overlapping
screenshots → V1 → core. Local video → V2 → core. Video URL → backend acquisition → local video → V2 → core. Provider limitations must
not block local core completion. Do not implement unrelated input layers during export.

## V3 Guitar Pro export — complete

Read docs/GUITAR_PRO_MAPPING.md and tools/guitar-pro/README.md. Use accepted
score.json directly; do not retranscribe, change canonical schema to fit the
library, infer missing music or return to video/normalization during export.
Keep Python recognition/validation, deterministic Node adapter and alphaTab
separate. No AI decisions inside export code; no manual GP archive implementation.

Run npm ci, then node tools/guitar-pro/export.mjs PATH/score.json --render.
Use --sample with the exact selected V2 indices for an accepted sample, and
--python when the validator requires a different interpreter. The existing
measure manifest is required to validate coverage. Primary output is the sibling
export/score.gp, produced by alphaTab Gp7Exporter and reloaded from disk by
ScoreLoader. Never call a renamed image/PDF an editable Guitar Pro score.

Canonical strings 1..6 map to alphaTab note strings 6..1; tuning arrays remain
top-first. Map duration denominators explicitly, preserving dots, tuplets,
voices, rests/chords and ties without re-attacking continuations. Preserve
written repeats/endings without duplication. Unknown repeat count may use the
recorded target default 2; unknown metadata stays null in canonical JSON.
Record every technical/default mapping, partial feature and skipped unresolved
endpoint in export_mapping.json and export_report.md. Do not guess endpoints.

Require roundtrip_validation.json with actual counts, semantic comparisons and
no UNEXPECTED_MISMATCH. Compare against canonical semantics, not object IDs or
only the pre-export target model. Distinguish EXACT, EXPECTED_EXPORT_DEFAULT,
KNOWN_UNSUPPORTED_MAPPING and UNEXPECTED_MISMATCH. Investigate adapter/API/model/
exporter limitations before considering MusicXML, MCP or GP5 fallback.

Open re-imported render PNGs and compare difficult source measures: harmonics,
parenthesized/tied notes, chords, slides, repeat bars, first/second endings,
multidigit frets and final bar. Record a hash-bound visual_review.md. Rendering
alone is not acceptance. Document target-controlled tie engraving and other
known differences; do not equate parenthesized notation with ghost playback.
Optional PDF must not delay correct GP, round trip and visual QA. Tests validate
mechanics, not transcription. Report primary and sample scope separately.

Current evidence: acceptance/V3_GUITAR_PRO.md. V1 COMPLETE; V2 COMPLETE;
V3 STRUCTURED SCORE COMPLETE; V3 GUITAR PRO EXPORT COMPLETE; CORE PIPELINE COMPLETE.


## V4 verification and correction layer

Read docs/VERIFICATION_PIPELINE.md and tools/verification/README.md. Preserve
V1/V2/V3 architecture; add explicit independent observations and field-level
verification around it. Do not rerun accepted V2 reconstruction during V3 QA.
A manual GP is read-only reference evidence, not unconditional ground truth.
Align written measures independently and bind the reference and generated hashes
before benchmarking. Never put song-specific values into reusable logic.

Trace each discrepancy backwards: rendered score → actual re-imported GP →
adapter → canonical → per-measure/header → source crop → original frame if needed.
Assign one actual fault class: V2 source preparation error, V3 visual recognition
error, V3 canonical assembly/modeling error, exporter mapping error,
target-format/rendering artifact, or manual/reference ambiguity. Matches can have
no observed fault. Do not presume the requested diagnosis is proven.

Always run deterministic schema/rhythm/reference/coverage validation, exact
assembly equality and full canonical-to-GP-reimport comparison. These checks do
not establish source truth or external Guitar Pro desktop compatibility. Avoid
full AI rereading of exported notes when semantic checks pass; audit changed,
high-risk and target-limited render features. Library/mapping changes require
targeted regression and rendering checks.

Independent source sweeping must catch missing features absent from canonical
risk flags. Stronger rereading covers repeats/ending extents, string-line placement,
multidigit frets, dense chords, dots/tuplets, ties/ghosts/parentheses, slide
endpoints/articulation, harmonics and faint/cropped/overlaid marks. Consult neighbor
images for cross-bar relations. Do not trust audit flags without evidence scope.

Correct only clear source-supported fields. Log old/new values and source hashes,
patch dependent per-measure/header fields minimally, validate a candidate, export
and re-import it, inspect affected rendering, then promote and record correction.
Never replace whole measures or force rhythmic totals. A proposal is not a
completed correction; preserve prior accepted artifacts. Do not guess unclear
slide targets or infer legato attack solely from a directional stroke.

Use item-level VERIFIED, AUTO_CORRECTED, USER_REVIEW_REQUIRED and
KNOWN_EXPORT_LIMITATION. Export defaults remain explicit and may affect playback.
Report exact sequence/printed measure/event, current values, candidate meanings,
source/generated/reference images and all affected locations for unresolved
items. Generate result/v3/verification/verification.json, verification_report.md
and review packets. Hashes bind artifacts, not the truth of a visual observation.

Current V4 evidence: acceptance/V4_VERIFICATION_ANALYSIS.md. No canonical fix was
justified in this case; source/reference differences and target defaults were
separated. Analysis/tooling completion is distinct from unresolved score issues.

## Mandatory run timing and final delivery

Before any conversion work begin tools/pipeline/timing.py RUN begin. Bracket acquisition, V2, V3, guitar_pro and V4 and their executed substeps using start/stop or exec; include agent visual review wall time. Read tools/pipeline/README.md for the exact keys. Import GP exporter metrics only from the current timed run. Never estimate previous durations; reused stages remain null with provenance. Finish after final verification, then run tools/pipeline/final_report.py RUN/result.

Deliver result/timing.json and final_report.json/.md for every run. Summarize VERIFIED groups and detail every AUTO_CORRECTED, USER_REVIEW_REQUIRED, KNOWN_EXPORT_LIMITATION and UNEXPECTED_EXPORT_MISMATCH with exact locations, current/candidate values, source/generated evidence and correction before/after. Use READY_FOR_DELIVERY only with current passing evidence and no meaningful unresolved issue; low-impact limitations mean REVIEW_RECOMMENDED; unresolved musical content or failed evidence means REVIEW_REQUIRED. Never equate confidence or round-trip equality with accuracy. Include total/phase time and top three slowest phases.

After final QA/report use acquisition cleanup for remote downloads; never delete local originals. Regenerate the final report if cleanup metadata changes. URL providers are backend-only and return structured failure without browser/manual-download fallback.
