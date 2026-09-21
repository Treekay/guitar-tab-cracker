# V4 forensic verification: Una Mattina

The reported first-ending problem is **not a confirmed pipeline recognition or
export error**. The source itself has first/second endings. The human GP omits
them in the first repeat. Classification: **manual/reference ambiguity**. Keep
canonical source-faithful; do not delete correct marks to match the reference.

Analysis and reusable verification design are complete. The actual score remains
`USER_REVIEW_REQUIRED` for two slide-interpretation issue groups. No canonical
correction was justified. This distinction supersedes any reading of prior V3
PASS as proof of zero unresolved source/export interpretation.

## Inputs and evidence

- Accepted Una source: `runs/v2-una-mattina/result/measures/`, its frame/crop
  manifest, all 45 per-measure records, header and assembled score.
- Accepted GP: SHA-256 `62c9ed00dc851286971f1134e237e44f19c6cfa9897b21e9ee9991699bb3416b`.
- Canonical, unchanged: SHA-256 `d93d2d17d6990084107ad0973527309af165caa380c8cf4abe69831d8af99c28`.
- User-specified human file: `C:/Users/pc/OneDrive/Guitar/指弹/Una Mattina（触不可及）- Roxane Elfasci.gp`.
  Read-only working copy: SHA-256 `8c2f577a25accdcaeee5a61f168bae514a6970205d5eb7fd038f826c9321158d`.
  Imported successfully with alphaTab 1.8.4: one Steel Guitar track, 45 bars,
  tempo 68. Original file was not edited.
- [Live verification report](../runs/v2-una-mattina/result/v3/verification/verification_report.md),
  [structured results](../runs/v2-una-mattina/result/v3/verification/verification.json),
  [field/evidence ledger](../runs/v2-una-mattina/result/v3/verification/observations.json),
  [reference benchmark](../runs/v2-una-mattina/result/v3/verification/reference/benchmark.json).

Indices here are written sequence indices including the unnumbered opening;
sequence 3 is printed measure 2, sequence 5 is printed measure 4. The reference
and generated GP share a confirmed one-to-one written alignment. Opening,
repeat-boundary, cross-bar and final anchors were checked; matching event/rhythm
sequences across all 45 units supplement that alignment, not just matching counts.

## 1. Where did the first-ending discrepancy originate?

Trace backwards:

| Stage | Evidence |
|---|---|
| Generated rendering | first ending over sequence 3; second ending over 4 |
| Actual GP re-import | alternate-ending values [1] and [2] at those bars |
| Adapter / mapping | explicit bit masks 1 and 2 from canonical arrays; no automatic recognition |
| Assembled canonical | measures 3/4 contain [1]/[2]; first repeat region has corresponding ending records |
| Per-measure JSON | 003/004 already contain [1]/[2]; exact assembly comparison passes |
| V2 source crops | 003 shows `1.` bracket; 004 shows `2.` bracket |
| Original frames | t=0 shows the first ending and start of second; t=22 shows the second ending; not an artifact introduced by cropping |
| Human GP | repeat start/end retained, alternate endings absent from bars 3/4 |

The earliest observed divergence is in the manual/reference branch. No wrong
ending was found entering the generated pipeline. The available evidence cannot
tell whether the manual author intentionally used a different arrangement or
omitted the source markings. This is the single assigned causal class for the
reported issue, not a claim that every human-reference difference is an error.

## 2. Was canonical already wrong before export?

The disputed ending fields were present before export, but they are supported by
source. Presence before export establishes provenance, not wrongness. All 45
per-measure records plus header exactly equal the assembled canonical file.
There was no source-supported canonical correction in this investigation.

## 3. Did export introduce new musical-content errors?

Fresh validation and actual GP re-import match all supported projected canonical
semantics: 45 measures, 628 events and 692 notes, zero unexpected mismatches.
No new unintended note/rhythm/repeat corruption was found. That statement excludes
documented limitations and defaults and is not an independent desktop-GP test.

Known effects are material: all 692 notes receive let-ring flags, tempo defaults
to 120, instrument defaults to nylon guitar, and six directional slides use Shift.
The human GP uses no note let-ring flags, tempo 68, steel guitar and Legato slides.
Playback therefore need not sound identical despite matching fret/rhythm data.
The unresolved terminal slide is omitted by the exporter while the manual uses
targetless OutDown. This visible loss remains explicit; no destination is invented.

## Other observed differences and agreements

| Finding | Source / canonical / generated | Manual | Outcome |
|---|---|---|---|
| First endings, seq 3/4 | source has 1./2.; preserved | no endings | reference ambiguity; keep source values |
| Later repeat, seq 13–17 | repeat and 1./2. | same | verified |
| Seq 5 event 14, fret 10 | fifth TAB line | fourth string | source supports generated; confirmed reference discrepancy |
| Let ring | one global instruction expanded to note flags and repeated target lines | no note flags | representation plus playback difference, not duplicated notes |
| Ties | 14 explicit endpoint pairs | same 14 | exact endpoint match, selected source checks |
| Parenthesized tied note seq 18 | source (2), non-ghost; courtesy (2) renders | same | target display limitation remains, no ghost substitution |
| Six resolved slides | descending, known endpoints; Shift technical subtype | Legato, same endpoints | user review of attack/legato intent |
| Seq 16 event 14 slide | endpoint null; exported relation omitted | targetless OutDown | user review; possible future safe representation, no pitch guess |
| Natural harmonic | string 5, touched fret 12, sustained rhythm | same; additional N.H. text | verified; text differs |
| Double master-bar flags seq 1/12 | double adjacent to repeat-start boundary | normal master-bar flag | boundary representation differs, no new rhythmic/note content |
| Final bar | final with last tied fret 12 | same | verified |
| Title / tempo / instrument | null source fields; recorded export defaults | title, 68 BPM, steel program | reference metadata is not automatically source truth |

The fifth-string finding was checked on enlarged 005.png and original t=18
frame. Fret 10 aligns with preceding fifth-line 8s, below fourth-line 7s.
This is the confirmed reference mistake used in a regression. The suspected
false-ending recognition mistake was **not** confirmed; its repeat-only fixture
is synthetic policy coverage and is not represented as an observed model failure.

## Initial reference agreement metrics

| Comparison | Agreement |
|---|---:|
| Aligned written measure structure | 45 / 45 |
| Event rhythm (duration, dots, tuplets, rests) | 628 / 628 |
| Chord/event note-count grouping | 628 / 628 |
| Note string and fret pairs | 691 / 692 |
| Repeat start/end/count per bar | 45 / 45 |
| Alternate endings per bar | 43 / 45 |
| Tie endpoint pairs | 14 / 14 |
| Resolved slide direction/endpoints | 6 / 6 |
| Resolved slide subtype including articulation | 0 / 6 |
| Note techniques excluding let-ring and relation techniques | 692 / 692 |

Aggregate technique agreement including let-ring is zero matching bars, because
every generated note has the global instruction expanded and the manual does not.
That number is not a notation recognition error rate. There is also one unmatched
manual OutDown. Metrics describe agreement over this specific alignment, not
accuracy against unquestionable ground truth or generalization to future music.

## 4. Which checks can remain mechanical?

Assembly equality, schema/coverage/reference/rhythm validation, deterministic
adapter regression and whole canonical-to-import semantic comparison run every
time. They do not require an AI to re-read every exported note. Reuse accepted V2
coverage/order; inspect only disputed original frames. GP writer/reader correlation,
projection blind spots and target-only engraving still require targeted review.
The [pipeline stage table](../docs/VERIFICATION_PIPELINE.md#stage-specific-effort)
classifies all eight stages without claiming they cannot fail.

## 5. Which features need stronger verification?

Repeat/endings and their full boundary scope; string-line placement of multidigit
frets; ties/parentheses versus ghost attacks; slide destination and articulation;
dense chord grouping, dots/tuplets and harmonic type; faint/cropped/overlaid marks;
global annotations versus playback defaults. Independent source sweeping must also
find omitted marks absent from canonical-derived risk flags. Use source-first
observations, then compare JSON fields. Expand review after discovered errors.

## 6. What can be auto-corrected?

Only precise fields contradicted by clear, independently reread source evidence,
with old-value/hash preconditions, dependent-field updates, canonical validation,
fresh GP round-trip and affected render audit. No such canonical correction was
justified here: **0 AUTO_CORRECTED**. Matching a manual file is not sufficient.
The proposal helper cannot label a draft as corrected or replace whole measures.

## 7. What requires user review?

Two issue groups: six Shift-versus-Legato slide interpretations (all exact
locations listed), and the sequence 16 event 14 terminal stroke/fall-off versus
unknown connecting destination. Review packets contain source, generated and
manual images, current values and candidates. Three known limitation groups
cover let-ring representation, target-controlled tie parentheses and metadata
defaults. Eight item groups are verified within their recorded scope.

## 8. What is the final standardized pipeline?

Bind accepted source → transcribe → deterministic validation and exact assembly
→ independent source feature sweep and high-risk field reread → minimal
source-supported correction or localized unresolved report → GP export → full
mechanical round-trip → targeted render audit → hash-bound scoped report.

Implemented under `tools/verification/`: field comparison/proposals, fresh GP
inspection, explicit-alignment manual benchmarking, risk inventory and real
issue packets/report generation. Ten deterministic verification tests cover
synthetic false endings, source-versus-reference precedence, the actual reference
wrong-string pattern, stale evidence, ambiguous corrections, minimal proposals,
whole-measure/note-list rejection, JSON type distinctions and false independence. They validate workflow mechanics,
not visual recognition. No video reconstruction, URL, UI or normalization work.
All 25 existing GP adapter tests and all 16 existing canonical-validator tests
also pass. Fresh read-only verification leaves canonical and accepted GP hashes unchanged.

V4 analysis/design and usable verification tooling pass. A literal claim that a
confirmed *generated-pipeline* mistake was converted into a regression is not
supported by this case: the confirmed error is in the reference, and the alleged
first-ending pipeline error is disproven by source evidence. This limitation is
explicit rather than manufacturing a failure to satisfy the original premise.
