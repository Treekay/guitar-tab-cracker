# Structured verification and correction

The source images are authoritative for source-faithful transcription. A human
GP is a comparison reference, not automatic ground truth. Una Mattina demonstrates
why: source images show first-region endings missing from the human GP, and a
source fifth-string fret 10 is on the fourth string in that reference. Neither
discrepancy justifies changing the generated canonical score.

The V4 layer is separate from recognition, canonical schema and GP export. It
uses explicit visual observations and deterministic comparisons. It does not
detect notation, identify pixels, redesign V2 or silently rewrite music.

## Standard workflow

1. **Bind evidence.** Hash accepted source images/manifest, per-measure records,
   header, canonical file, adapter mapping, GP and reviewed rendering. Reuse
   accepted V2 coverage/order; investigate only a disputed crop or boundary.
2. **Transcribe.** Record written events and unknowns, including high-risk marks.
   Do not assume that repeated-looking bars are interchangeable.
3. **Validate and verify assembly.** Check schema, exact rational rhythm, voice
   totals, note uniqueness, relation endpoints, coverage, repeat consistency and
   exact equality of header + per-measure records to assembled canonical.
4. **Independent source feature sweep.** Reopen every source image looking for
   omitted structural marks and suspicious notes, without using existing JSON as
   the answer. This is a feature sweep, not a second complete transcription of
   every clear note. Canonical-derived risk flags alone cannot detect a mark that
   recognition omitted. Record source-first observations before comparison.
5. **Targeted independent rereading.** Compare explicit fields for flagged features,
   ambiguous digits, dense groups and every cross-boundary relation. Review both
   neighboring images and the repeat playback boundary when relevant. Require
   original frame evidence only if the accepted crop cannot answer the question.
6. **Resolve or report.** Apply minimal source-supported corrections with a log;
   leave ambiguous values unresolved. A different reference interpretation alone
   is not correction authority. Selective review expands to the whole measure or
   adjacent passage after a confirmed ordinary-note error or repeated uncertainty.
7. **Export and mechanically validate.** Export through the deterministic adapter,
   reload actual saved GP bytes and compare against canonical semantics. Keep this
   full automatic comparison on every export; never replace it with spot checks.
8. **Targeted render audit.** Inspect changed features and format-limited notation:
   repeat/endings, ties/parentheses, slide articulation/fall-offs, harmonics and
   final boundaries. Inspect unfamiliar tuning/string mapping and a chord on
   first use or relevant adapter changes. Do not re-read every exported note when
   the full semantic comparison passed and no projection blind spot is suspected.
9. **Deliver scoped status.** Include remaining exact locations and source/generated
   snippets. Hash-bind review and invalidate it when relevant inputs change.

For untested notation styles, insufficient evidence, or a changed recognition
procedure, retain full independent note rereading until enough diverse evidence
supports reducing it. One successful fixture does not calibrate accuracy.
Existing `audit.pass2` labels alone are not evidence of field coverage. The V4
observation ledger states what was actually independently reviewed; do not mark
an uninspected image or unreviewed field as verified.

## Stage-specific effort

| Stage | Primary classification | Routine verification | When to expand |
|---|---|---|---|
| A: V2 source selection/cropping | probabilistic / visual reasoning | reuse accepted coverage and crop provenance; mechanically bind bytes/order | changed input, clipped mark, boundary identity dispute; targeted original frames, not full reconstruction |
| B: image → canonical | probabilistic / visual reasoning | source feature sweep plus independent high-risk field reread | new style, faint/corrupt evidence, ordinary-note mismatch; broader passage or full reread |
| C: canonical assembly | deterministic / mechanically verifiable | exact header/per-measure equality, order/coverage and schema | changed assembler or inconsistent redundant repeat/ending fields |
| D: deterministic validator | deterministic / mechanically verifiable | run every time; negative regression tests | new schema/notation/known blind spot; it cannot establish visual truth |
| E: canonical → alphaTab | deterministic / mechanically verifiable | full independent canonical-to-import projection plus targeted tests | new mapping/voice/tuning or unsupported target semantics |
| F: Gp7Exporter | target-format-limited | pinned library, re-import actual saved bytes | library upgrade, new feature, external application disagreement |
| G: GP re-import comparison | deterministic / mechanically verifiable | full automatic comparison; inspect losses/defaults separately | projection changes, features it cannot express, correlated writer/reader bug |
| H: rendered output | target-format-limited | targeted difficult/changed structures; readable source comparison | new renderer/font/notation settings or visual/semantic disagreement |

Actual Guitar Pro desktop compatibility remains **insufficiently validated** by
alphaTab self-round-trip alone. Its writer and reader may share assumptions.
The independently authored GP helps find differences but still uses alphaTab for
this benchmark import. Do not claim a stage cannot fail or skip automatic checks.

## Risk policy grounded in project evidence

| Feature | Evidence and required independent check |
|---|---|
| Repeats and endings | Una source/reference disagreement: verify existence, number, start/end extent and repeat region together; require positive source evidence before deletion |
| String position and multidigit fret | Una reference fifth/fourth-string mismatch: count all six lines and align the digit with neighboring established strings; compare fret and string separately |
| Ties versus attacks / parentheses / ghosts | Una 17→18 and final tied notes: inspect both endpoints and rhythmic continuations; parentheses are not automatically ghost dynamics |
| Slides / slurs / fall-offs | Una six Shift/Legato disagreements and unresolved ending stroke; Yuki explicit slurred slides: independently establish direction, endpoint, attack subtype and scope; direction alone cannot determine articulation |
| Chords and voices | Both accepted fixtures: verify simultaneous grouping and string uniqueness, especially dense stacks and beams |
| Dots / tuplets / rests | Una dotted patterns and Yuki triplets: read stems/flags/beams, not horizontal spacing; a correct total can still hide swapped durations |
| Harmonics | Una opening <12>: verify touched fret, string, notation type and tie; artificial-harmonic sounding pitch needs additional evidence |
| Faint marks, overlays, crop edges | Translucent Una and V2 context extents: verify marks across core/context, use alternate existing frame when needed; never infer disappearance from a clipped crop |
| Global text versus playback | Let ring throughout and null tempo: distinguish source text, adapter expansion, target engraving and playback assumptions |

The current fixture contains no ordinary-note error in generated output confirmed
by this analysis. That does not establish a safe universal one-pass rule. Clear
ordinary notes may use one transcription plus the source sweep/validator on
calibrated input styles; ambiguous or flagged fields always get independent rereading.

## Error localization and status

Trace render → imported model → mapping → canonical → per-measure/header → crop
→ original frame. Compare each boundary separately. Assign one causal class to
each actual discrepancy: V2 source preparation error, V3 visual recognition error,
V3 canonical assembly/modeling error, exporter mapping error,
target-format/rendering artifact, or manual/reference ambiguity. Split issues
with different causes. Verified matches use `no observed fault`, not an invented
fault. A manual-reference mismatch must first be adjudicated against source.

| Status | Required evidence |
|---|---|
| VERIFIED | required checks passed for the explicitly named item/field and current hashes; not an entire uninspected measure |
| AUTO_CORRECTED | logged source-supported minimal patch, canonical revalidation, fresh GP round-trip, and affected visual audit all passed |
| USER_REVIEW_REQUIRED | source is ambiguous, evidence stale, a mismatch remains, or a meaningful playback interpretation is unresolved |
| KNOWN_EXPORT_LIMITATION | canonical is known but target representation/adapter cannot preserve it exactly; document audible as well as visual effects |

Technical defaults remain `EXPECTED_EXPORT_DEFAULT` in export provenance. A
default is not recognized metadata. Unknown slide articulation can be both a
documented export default and a user-facing unresolved interpretation. Never
collapse that into an exact source match.

## Correction transaction

1. Identify a JSON pointer, old value, issue and affected source/neighbor images.
2. Independently reread those images; record observed value and evidence hashes.
3. If ambiguous, stop that correction and report candidates without choosing one.
4. Propose leaf-field replacements with old-value preconditions. Never replace a
   whole measure. Update all dependent fields explicitly: for endings, both the
   affected measure flags and header `repeat_regions`; for string changes, every
   affected relation endpoint. No inferred repair of related fields.
5. Preserve accepted files; validate a candidate assembled from patched header
   and per-measure records. Schema/rhythm/coverage/reference warnings block promotion.
6. Export that candidate in a separate revision using its correct source manifest;
   re-import and compare. Do not reuse validation from the old hash.
7. Reopen affected rendered structures against source, record new GP/render hashes.
8. Promote the explicit field patches into working canonical inputs only after all
   checks pass; retain before/after hashes and the prior accepted artifact. Mark
   `AUTO_CORRECTED` only now. Invalidate previous field reviews touched by the patch.

`propose_patch` implements source-bound leaf proposals without writing live data.
The current verifier is intentionally read-only and rejects an unsupported
`AUTO_CORRECTED` assertion. Promotion/export is orchestrated by Codex with existing
tools; this release does not provide an unattended multi-file transaction engine.
No correction was justified for the present canonical score.

## Report and reference contract

`result/v3/verification/` contains `observations.json`, `verification.json`,
`verification_report.md`, fresh validator/round-trip results, and per-issue
`review/<issue_id>/{source.png,generated.png,manual.png,issue.json}` when available.
Images can be whole relevant measure/system crops; locations specify sequence,
printed number and event so the user need not search the full score. Include all
affected locations for a multi-occurrence issue. Missing candidates stay `[]`.

Each issue records source evidence, canonical/exported/reference values, causal
stage, classification, status, correctability and notes. Counts refer to issues
or verified fields, never imply every note was visually inspected. Track total
measures/events/notes separately. The report does not include chain-of-thought.

Manual benchmarking requires a read-only file copy, explicit guitar track and a
hash-bound, independently confirmed written-measure alignment. Neither equal
counts nor printed labels alone establish alignment. Report numerator/denominator,
unaligned scope, event grouping, string/fret, rhythm, repeat/endings and techniques
separately. Tied-note segmentation or different voices may prevent exact event
comparison: report mismatches, do not silently normalize them away. Reference
values never enter generic rules. See [tool usage](../tools/verification/README.md)
and [current analysis](../acceptance/V4_VERIFICATION_ANALYSIS.md).
