# Chord strokes (backward-compatible v1 extension)

Events may carry `brush: {"type": "arpeggio" | "strum", "direction": "up" | "down"}`
and independently `pick_stroke: "up" | "down"`. Omitted or null means no encoded
mark, preserving old v1 files. Brush requires at least two simultaneous notes;
neither mark is valid on a rest. Both can coexist on the same chord.

Brush direction is the **visible arrow on top-string-first TAB**: up points
toward string 1 (low strings to high strings), down toward string 6. Arpeggio
uses a wavy arrow; strum a straight arrow. Pick direction is the conventional
hand stroke: down is the squared staple symbol, up the V symbol. Do not conflate
these conventions or infer one mark from the other. Record visible marks on
the event, not merely in unresolved notes. No per-note ordering or timing is
required. Unclear direction remains an unresolved source item.

# Canonical written score, schema version 1

The schema is exporter independent: [score.schema.json](../schema/score.schema.json).
Codex visually transcribes source images. No code recognizes notation, reads
digits, chooses rhythms, or fills content to satisfy arithmetic. No image
normalization or OMR is involved in recognition. After canonical acceptance,
the separate [Guitar Pro adapter](GUITAR_PRO_MAPPING.md) exports and validates
editable notation without revisiting recognition.

## Semantics

- `sequence_index` is the accepted V2 **written** order, starting at 1. Printed
  numbers may be null. Repeated playback never duplicates written measures.
- String 1 is the top TAB line / highest string; string 6 is the bottom / lowest.
  `metadata.tuning`, if visibly known, contains six MIDI pitches in that order.
  Unknown tuning, capo, title, artist and tempo remain null. Do not fetch metadata.
- An event contains simultaneous notes on distinct strings, or a rest with no
  notes. Events have contiguous indices within a measure. Each voice progresses
  sequentially from its own measure start; event order must be supplied visually.
  Multiple voices are checked separately, not summed together.
- Durations are denominators of whole notes, 1 through 64 powers of two. Dots
  multiply by `1 + 1/2 + ...`; tuplet numerator:denominator means that many notes
  in the time of denominator notes. Unknown durations/frets may be null with
  explicit uncertainty and root unresolved entries. Never use zero as unknown.
- A rest, dead note, ghost indication, and parenthesized note are distinct.
  Parentheses alone do not automatically imply ghost-note technique.
- `relations` bind measure/event/string references. Ties link matching frets on
  the same string. A visible continuation without a reprinted fret retains the
  tied note and written duration with `display: tie_continuation`; it is not a
  new attack. A parenthesized tied destination still has `display: fret`.
- The normalized technique vocabulary includes hammer/pull, directional slides,
  legato/shift slides, bend/release, vibrato, tie/slur, ghost/dead, harmonics,
  accent, palm mute and let ring. Optional `technique_parameters` preserve
  visually supported amounts/text; unsupported specifics remain unknown.
  A slide direction plus a separate slur records both visible marks without
  guessing a more specific articulation. Score-wide printed text is an annotation.
- `barline` records visible line style separately from repeat flags. Repeat
  start belongs to the measure after the sign; repeat end to the measure before
  it. `repeat_regions` link their written indices and alternate-ending spans.
  Counts remain null without printed count evidence. A first/second-ending pair
  does not manufacture a printed repeat count. Pickups are explicitly marked;
  unnumbered does not automatically mean pickup.
- Measure signature/tempo values are changes; null inherits the preceding value.
  Root signature/tempo is the initial value. Unknown meter disables total comparison.
- `source.image` is relative to `score.json`; `core_bbox_in_image` is the V2
  core [left, top, right, bottom]. Adjacent context supports references, not
  additional events. All ambiguities are listed under `unresolved`.
- Open-ended relations use `to: null` with an explanation in `uncertainty` and
  `unresolved`. Exporters must handle these explicitly instead of guessing.
  Confidence is evidence quality, not a claim that arithmetic proves correctness.

## Execution

Install the deterministic validator dependency using the project's Python:

```text
python -m pip install -r tools/requirements-v3.txt
python -m unittest discover -s tools -p test_validate_score.py -v
```

For a V2 result, put manually authored records in `result/v3/measures/001.json`
through `NNN.json`, and root fields other than measures in `header.json`. Open
every source twice, checking events, strings, frets, rhythms, techniques and
boundaries. Set `audit.pass2` to `inspected` only after the actual second inspection.

```text
python tools/assemble_score.py RUN/result/v3 --manifest RUN/result/measures.json
python tools/validate_score.py RUN/result/v3/score.json --manifest RUN/result/measures.json
python tools/report_score.py RUN/result/v3 --selected 1 3 16 18 45
```

Assembly checks contiguous filenames and completed audit records, preserves all
musical fields unchanged, and validates before writing score.json. It copies
the canonical schema to `v3/schema/`. Validation errors fail the command;
rhythmic warnings do not change content and require a return to the image.
Both warnings and unresolved data must be read before acceptance. Audit flags
are operational records, not machine verification of visual reasoning.

For a deliberately limited sample, supply `--selected-indices` with the original
V2 indices to both assembly and validation. JSON sequence indices are local to
the sample, while printed numbers and source paths retain their identity. The
validator labels the scope `sample`; never claim this as complete-song acceptance.

## Accepted evidence and limits

Una Mattina: 45/45 units, 628 events, 692 note records, zero rests; two repeat
regions, two pairs of alternate endings, 14 ties and 7 descending slide marks.
One slide destination at the first-ending repeat bar remains unresolved. All
45 units total 4/4. The unnumbered introduction is a complete 4/4 unit (dotted
half harmonic, tied eighth, two sixteenths), despite the historical V2 ledger's
informal "pickup" description. V2 artifacts are unchanged.

Yuki no Hana: only printed 1, 16, 29 and 30 are sampled. The right-edge ties
from printed 30 into unsampled 31 are explicit open relations. Original V2
sample images already had a historical tonal transform; V3 adds none.

See [acceptance](../acceptance/V3_STRUCTURED_SCORE.md). V1 COMPLETE / V2 COMPLETE /
V1 COMPLETE / V2 COMPLETE / V3 STRUCTURED SCORE COMPLETE / V3 GUITAR PRO EXPORT COMPLETE / CORE PIPELINE COMPLETE.
Phase 1 evidence above remains separate from [export acceptance](../acceptance/V3_GUITAR_PRO.md).
Neither establishes general accuracy for unseen music.
