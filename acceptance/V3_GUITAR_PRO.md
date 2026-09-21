# V3 Guitar Pro acceptance

V1 COMPLETE / V2 COMPLETE / V3 STRUCTURED SCORE COMPLETE / V3 GUITAR PRO EXPORT COMPLETE / CORE PIPELINE COMPLETE

Acceptance date: 2026-09-21. Node 22.22.1, alphaTab 1.8.4, resvg 2.6.2.
Canonical → deterministic adapter → Gp7Exporter → saved `.gp` → ScoreLoader → semantic comparison → visual review. No manual GP format implementation, canonical edit or retranscription.

| Input | Measures | Events | Notes | GP bytes | Unexpected mismatches |
|---|---:|---:|---:|---:|---:|
| v2-una-mattina | 45 | 628 | 692 | 22145 | 0 |
| v2-yukinohana | 4 | 42 | 54 | 4672 | 0 |

Both canonical files remain byte-identical to phase 1. Counts are measured from canonical and re-imported models, never fixture constants in the exporter. All supported semantic fields match; internal IDs are excluded.

## v2-una-mattina

- [Editable GP](../runs/v2-una-mattina/result/v3/export/score.gp), [round trip](../runs/v2-una-mattina/result/v3/export/roundtrip_validation.json), [report](../runs/v2-una-mattina/result/v3/export/export_report.md), [visual review](../runs/v2-una-mattina/result/v3/export/visual_review.md).
- Canonical SHA-256: `d93d2d17d6990084107ad0973527309af165caa380c8cf4abe69831d8af99c28`.
- GP SHA-256: `62c9ed00dc851286971f1134e237e44f19c6cfa9897b21e9ee9991699bb3416b`.
- 18 explicit technical-default records; 14 partial-mapping records; 1 unresolved relations omitted.

## v2-yukinohana

- [Editable GP](../runs/v2-yukinohana/result/v3/export/score.gp), [round trip](../runs/v2-yukinohana/result/v3/export/roundtrip_validation.json), [report](../runs/v2-yukinohana/result/v3/export/export_report.md), [visual review](../runs/v2-yukinohana/result/v3/export/visual_review.md).
- Canonical SHA-256: `3fafde16e0df36e6622a2b2dd035eb7dcc92377c05e21ba3246fd865e5a59ecd`.
- GP SHA-256: `fb0c589cefd1422e7ce87d056b589564f318fdb4c5c197a248884c6c31715ede`.
- 11 explicit technical-default records; 1 partial-mapping records; 3 unresolved relations omitted.

## Coverage and limits

Una: all 45 written units survive, including two repeat regions, first/second endings, 14 ties, six resolved descending slides and natural harmonic. The seventh slide has an unknown endpoint and is omitted. Source repeat counts null become technical count 2 without expanding bars. Visual checks cover sequence 1,3,4,12,13,16,17,18,19,45.

Yuki: only printed measures 1,16,29,30 (four-unit canonical sample) are exported. Chords, H/P, triplets, slides with slurs and cross-unit slide survive. Three ties leading outside the sample are omitted; no full-song claim. All four source crops were visually compared.

Parenthesized display is independent of ghost playback; target courtesy parentheses render Una (2) correctly, but arbitrary source parenthesis/blank-continuation engraving is not independently encoded. Explicit ghosts are supported. Standalone slurs and artificial harmonics lacking an unambiguous touched fret are documented partial mappings. Bends require an explicit amount; envelope timing is a technical default. Generic unsupported fields never authorize changing canonical music.

25 deterministic Node adapter tests pass, including all six string mappings, rhythm, relations, repeats/endings, defaults, unresolved handling and deliberate semantic corruption. All 16 existing Python structured-validator tests pass. These tests validate mechanics, not visual transcription.

The real files were re-imported and rendered through alphaTab; no Guitar Pro desktop application compatibility test is claimed. The pinned official Gp7Exporter produces editable GP7+ data. Optional PDF was not needed; system PNGs supply visual evidence. Runtime outputs remain local/ignored, and may be regenerated using [commands](../tools/guitar-pro/README.md).

Core input is ordered score images, independent of video. Full-image/PDF preparation is an extended input layer, not implemented here. URL acquisition remains deferred and does not block core completion.
