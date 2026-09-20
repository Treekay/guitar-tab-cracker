---
name: guitar-tab-cracker
description: Autonomously reconstruct overlapping guitar-tab screenshots into a source-faithful full score image and printable A4 PNG/PDF using Codex visual reasoning. Use for screenshot reconstruction; video and structured/Guitar Pro output are separate future stages.
---

# Guitar Tab Cracker

Codex is the visual agent and executor. Users supply images only. You decide
boundaries, identities, order, source selection and page breaks. Tools execute
explicit decisions. Do not build/invoke a CV detector, matching/ordering
algorithm, ROI application or automatic score-layout interpreter. No musical
transcription in V1.

In this repository read docs/PRODUCT_REQUIREMENTS.md and docs/EXECUTION_PLAN.md
before scope/architecture changes. V1 is active; do not start video/Guitar Pro
work without an explicit version advance. Keep implementation/evidence private.

## 1. Inventory

Find all source images, preserving original bytes and names. Recheck the actual
file set, not just historical benchmark counts. Use temporary/result workspaces
for derivatives. Mechanical file/dimension listing is fine; filename order is
not score order. Do not require user labels or ROI.

## 2. Visual inspection

Open every image. Identify TAB region, visible barlines/measures/numbers,
partial left/right regions, cursor/UI overlays and clean alternatives. Enlarge
explicit regions when needed; coordinate grids can help select precise pixels.
Inspect above/below the strings for stems/beams, ties, techniques, repeats and
opening annotations. Record visual evidence and uncertainty, not musical events.

## 3. Candidate extraction

Choose boxes visually; execute explicit pixel crops. Retain every useful
complete/partial candidate with source, bbox, identity evidence and boundary
state (complete, partial_left, partial_right, partial_both). Never infer crop
boundaries with morphology, projection, OCR or another application algorithm.

## 4. Cross-image reconciliation

Compare candidates visually. Decide which are the same logical measure, which
are distinct repeated passages, and which partials have complete alternatives.
Printed numbers help but are not required. Never substitute a later repetition
for an unavailable measure. Preserve ambiguous alternatives.

## 5. Global ordering

Keep concise agent-authored notes/ledger: each logical measure, supporting
sources, partials accounted for, ordering evidence, selected source and uncertainty.
This is working evidence, not an application manifest pipeline or required schema.
Verify every visible measure is represented once, overlaps reconcile, partials
are retained or linked to better sources, and the sequence is coherent. Check
numbering jumps; an unlabeled edge does not prove its missing contents.

If coverage is incomplete, finish resolvable work, show explicit gap/partial
labels and explain the additional source needed. Do not imply an incomplete
set yielded a complete song. Recheck new/changed inputs before declaring gaps.

## 6. Final source selection

Prefer complete, sharp, unobstructed, high-resolution views with minimal cursor
interference. Preserve notation and boundary context. Combining complementary
views requires visually established identity/alignment and review of the join.
Never invent notation to paint over an overlay.

## 7. Compose full score

Mechanically resize to your chosen scale, align staff bands and place crops in
your explicit order. Preserve aspect ratio and markings. Keep original color
crops unless a visually verified tonal change improves printing without losses.

Create a small helper only for repeatedly useful mechanical work. It consumes
explicit crops/order/scale/placements; it must not decide them. This repository's
tools/compose.py is mechanical. benchmark/decisions.json is one run's evidence,
never a template for another song's visual decisions.

## 8. A4 layout

Default to portrait with sensible margins and readable, consistent scale.
Choose row groups and page placements visually. Never split a measure; preserve
cross-boundary annotations/ties. Arithmetic executing selected placements is
allowed, automatic musical layout decisions are not.

## 9. Export

Produce result/full_score.png, result/page_001.png (and subsequent pages) and
result/full_score.pdf. Optionally retain measures/, inspection/, the decision
ledger and coverage report. PDF pages must have actual A4 dimensions.

## 10. Final visual QA

Open the full score at readable scale (sections for a long strip), every page
PNG and rendered pages of the actual PDF. Compare against all sources again:
omissions, duplicates, order, fragments, clipped markings, wrong crops, poor row
breaks, unreadable scale and overlays. Correct decisions and regenerate; do not
stop at the first render. File/hash/count/geometry checks supplement visual QA.

Report source count, reconstructed logical-measure count, complete/partial/gap
coverage, duplicate/omission findings, A4 page count, paths and remaining source
limitations. Do not ask for coordinates/order/duplicates/page breaks unless
the source is genuinely impossible to resolve.

## Later versions

V2 extends this same workflow: inspect video/file URL, choose timestamps, extract
with ffmpeg, inspect novelty/coverage, return for more frames and perform V1.
Fixed sampling is not the product. V3 visually transcribes the reconstructed
score into structured music, then calls independent alphaTab/MusicXML/Guitar
Pro MCP export tools. A future hosted runtime is a multimodal API agent with
controlled tools. None of those future stages is part of V1.
