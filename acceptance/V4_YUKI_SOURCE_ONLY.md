# Yuki no Hana: full-video source-only V4 rerun

Delivery: **REVIEW_REQUIRED**. The editable 57-measure GP exports and re-imports
successfully, but one unmetered slide onset remains outside canonical schema v1.
This is a complete-song run, not the earlier four-measure sample.

The user explicitly selected previously exposed Yuki no Hana instead of a new
video. Earlier context included a sample and count information. No previous
answer files, previous measure plans or human Guitar Pro reference were used in
this rerun. Therefore this does **not** satisfy the genuinely unseen-new-video
blind acceptance gate. No recall, missed-error or false-positive rate is claimed.

## Input and reconstruction

- Local user video: `雪之华 - 冈崎伦典 动态吉他谱.mp4`.
- SHA-256: `88f8a94fb8e51d5b787636101f55997131d8ef9828426808ea1ba6d18d261cfa`.
- Fresh probe: 209.933 seconds, 986×720, approximately 30 fps.
- 58 freshly extracted and inspected frames, including eight separate
  coverage/order audit frames. Printed sequence 1–57 and final bar observed.
- Direct source crops, ordered strip and three A4 landscape PDF pages. Actual
  PDF pages rendered and viewed; no OCR/OMR, recognition CV or normalization.
- Minor neighboring-label/highlight seams remain in the continuous presentation;
  individual measure crops retain context. Source musical content was preserved.

## Measured outputs

| Check | Result |
|---|---|
| Written measures | 57 → 57 |
| Metered events | 610 → 610 |
| Note records, including tied continuations | 794 → 794 |
| Rest events | 7 |
| Canonical validation | Pass, zero errors/warnings |
| Fresh GP semantic round-trip | Pass, zero unexpected mismatches |
| Independently authored source core-field comparisons | 7,546 |
| Explicit additional cross-bar endpoint comparisons | 15 |
| Source measures reopened for second pass | 57 |
| Re-imported GP musical systems visually inspected | 19 |
| Verified measure review groups | 57 |
| Applied musical auto-corrections | 0 |
| User-review-required issue groups | 1 |
| Known representation/preview limitation groups | 18 |
| GP size | 27,970 bytes |

The second pass was performed by the same Codex agent from reopened source
images, with separately authored event tokens and source feature notes. It is
not an independent human/model review. The validator compares musical semantics,
not alphaTab object IDs. A passing round-trip only demonstrates preservation of
the representable canonical projection.

The source sweep inspected H/P, slides, ties, parentheses, accents, vibrato,
chords, dots, triplets, rests and final-bar structure. Canonical relations are
18 hammer-ons, 11 pull-offs, 42 ties, 11 directional slides and eight paired
slurs. No source repeats, alternate endings, harmonic labels or bend marks were
observed; these features were not copied from another song.

## Localized limitations

1. **USER_REVIEW_REQUIRED:** measure 20, event 8, string 4. A small fret 2 precedes
   fret 4 with a slide/slur and no separately observed rhythmic stem. The main
   fret 4 and metered rhythm survive. Schema v1 cannot express the unmetered
   onset; no duration or additional ordinary attack was invented.
2. Fourteen upward arpeggio arrows at 2/11, 4/3, 5/1, 9/1, 15/5, 19/1, 21/5,
   24/2, 40/1, 43/2, 43/6, 51/1, 55/7, 56/8. Chords/rhythm survive; rolling is
   not expressible through current canonical event fields. This is a canonical
   representation boundary, not evidence that alphaTab cannot support arpeggios.
3. Measure 31/event 12/string 1 staccato is absent from schema v1. The note and
   duration survive; the shortened articulation does not.
4. Two grouped engraving limitations enumerate all affected parenthesized and
   blank-continuation notes. Untied parentheses are not changed into ghost
   dynamics; target engraving controls courtesy tie parentheses.
5. One grouped TAB-preview limitation: accent data survives GP re-import but the
   TAB-only preview does not draw the source accent glyphs.

The 18 known groups are 14 arpeggio locations + staccato + two engraving groups
+ one accent-preview group. Each has source/generated review images and exact
locations. Fourteen explicit format defaults include unknown-metadata playback
defaults and required slide/vibrato subtypes. They are not written back into
canonical source facts. Guitar Pro desktop opening was not tested.

A progress-message suspicion concerning measure 34 was retracted: frozen
first-pass data already placed both fret-1 notes on string 2. No correction was
applied and it is not counted as a detected error. First-pass musical data and
final data are identical; only completed pass2 audit flags changed.

## Artifacts and freeze

All musical artifacts remain local under ignored `runs/v4-yuki-source-only/`:

- `result/full_score.pdf` and `result/measures/`.
- `result/v3/score.json`, per-measure JSON and validation.
- `result/v3/export/score.gp`, mapping, round-trip, previews and visual review.
- `result/v3/verification/observations.json`, source sweep, verification report,
  correction log, localized review packets and `freeze_manifest.json`.
- `working/first-pass/`: preserved provisional score, GP and render.

Final canonical SHA-256:
`41860c0a2023c27b4a49a8fde89c4eb8c0c1d7c62b496c88623e535ab21cb713`.

Final GP SHA-256:
`b5c91db6df391ad8d937a70f7564b4f131681eba9d611919560c4943a93484b9`.

The source-only report was frozen before any optional reference comparison.
No manual reference was opened and no post-blind benchmark was performed.

## Reusable findings

Root canonical unresolved items were previously absent from export provenance.
The adapter now carries them unchanged, and the round-trip/report expose them
separately from target-format losses. The verifier now requires explicit triage
of root uncertainties and validates authored all-measure source-sweep coverage.
Added regression tests cover retained uncertainty without invented notes,
missing/stale/reordered source evidence, and unresolved items hidden behind
unrelated or unjustified VERIFIED issues. All 26 adapter and 12 verification
tests pass. These tests validate mechanics, not transcription reliability.
