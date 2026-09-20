# V3 structured-score phase 1 — PASS

V1 COMPLETE / V2 COMPLETE / V3 STRUCTURED SCORE PASS / V3 GUITAR PRO EXPORT NEXT.
No Guitar Pro, alphaTab, MusicXML export or full notation renderer was built.

## Primary acceptance: Una Mattina

Input: accepted `runs/v2-una-mattina/result/measures/001.png`–`045.png`, with
original V2 provenance and core boundaries. All 45 sources were opened for
transcription, independently reopened for event-by-event audit, and compared
globally against the three accepted full-score sections after score assembly.
Additional enlarged checks covered the opening harmonic, dots, tied blank
stems, repeats/endings, parentheses, slides, chords and final bar.

- 45/45 written units: unnumbered introduction, then printed 1–44. No expanded
  repeat playback, omitted unit or duplicated context event.
- 628 written events, 692 note records including tied continuations, zero rests.
- Repeat regions: sequence 2–3 (printed 1–2), endings sequence 3 / 4; sequence
  13–16 (printed 12–15), endings sequence 16 / 17. Printed counts are absent,
  so counts remain null.
- 14 tie relations, seven descending slide marks, natural harmonic, parenthesized
  tied note and score-wide `let ring throughout`.
- Opening meter 4/4; all 45 exact rhythmic totals equal one whole note.
  No rhythmic warnings. The unnumbered introduction is full 4/4, not a shortened
  pickup: dotted half harmonic, tied eighth, two sixteenths. This corrects the
  historical V2 ledger's informal pickup label without altering that evidence.
- One unresolved musical issue: sequence 16 / printed 15, event 14, descending
  stroke at the repeat bar has no explicit printed destination. Relation target
  is null, confidence medium; no playback jump target is guessed. The containing
  measure and root unresolved inventory disclose the same issue. No low-confidence
  records. Unknown title/artist, tuning, capo and tempo remain null.
- Source images and V2 artifacts were not changed. No video revisit, OCR/OMR,
  normalization or metadata web search was needed.

Private outputs:

- [Score](../runs/v2-una-mattina/result/v3/score.json)
- [45 per-measure records](../runs/v2-una-mattina/result/v3/measures/)
- [Validation](../runs/v2-una-mattina/result/v3/validation.json)
- [Source-linked human-readable report](../runs/v2-una-mattina/result/v3/TRANSCRIPTION_REPORT.md)
- [Operational inspection manifest](../runs/v2-una-mattina/result/v3/inspection/audit.json)

## Second-style sample: Yuki no Hana

Only original printed measures 1, 16, 29 and 30: four sample units, 42 events,
54 note records, zero rests. Each image was reopened for independent audit.
Covers chords, accent, hammer-on, pull-off, three eighth-note triplets, slide
directions with slurs, within-bar ties and a slide crossing 29–30. Printed 28
was viewed solely to establish that the edge vibrato belongs to prior context.

All four rhythmic totals pass. Three outgoing ties from printed 30 into
unsampled 31 remain explicit open relations with sample-boundary explanations;
they are not claims of unreadable source. The sample keeps source paths and
printed numbers; local sequence indices 1–4 are clearly sample-only. No full-song
acceptance is claimed. The existing historical V2 grayscale pixels are consumed
directly without further tonal processing. No schema change was needed.

- [Sample score](../runs/v2-yukinohana/result/v3/score.json)
- [Sample report](../runs/v2-yukinohana/result/v3/TRANSCRIPTION_REPORT.md)
- [Sample validation](../runs/v2-yukinohana/result/v3/validation.json)

## Deterministic verification

- 16 V3 unit tests pass using the default Python with jsonschema. They exercise
  exact dot/tuplet arithmetic, meter changes and pickups, separate voices,
  invalid schema values, rests, duplicate strings, source identity/coverage,
  references, tie continuations, repeats/endings, unresolved duration and audit
  gating. Fixtures test mechanics, never visual interpretation.
- Seven existing extraction/source/export tests pass using the project's bundled
  Python (including its five presentation variants). The default environment
  lacks pypdf/reportlab; the bundled environment lacks jsonschema, so the suites
  were run separately in their dependency-equipped environments.
- Both actual structured outputs pass schema and semantic validation. The primary
  score is revalidated after second-style sampling; per-measure records equal the
  assembled records. Schema copies equal the repository canonical schema.
- `git diff --check` passes. Generated run evidence stays local under the existing
  ignored `runs/` policy; reusable schema/tools/docs and this record are committed.

This passes the requested phase 1 gate with explicit ambiguity. It does not
establish accuracy on arbitrary notation or complete all of V3.
