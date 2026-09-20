# Visual extraction benchmark

Each of the nine images was transcribed and given a separate second visual audit before the next image was opened. Transcription used the current image alone; no OMR/OCR, external recognizer, other image, or earlier benchmark score was consulted to fill its uncertainties.

| Image | Detected measure labels | Complete / partial | Events | Notes | Unresolved | Visually difficult areas |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 1.png | 1, 2, 3, 4 | 3 / 1 | 34 | 48 | 6 | Small slide-source rhythms; unreadable continuation near x=432. |
| 2.png | unnumbered, 4, 5, 6 | 2 / 2 | 35 | 39 | 5 | Grace rhythms; unreadable continuations in measures 4 and 6. |
| 3.png | unnumbered, 6, 7, 8, 9 | 3 / 2 | 31 | 36 | 5 | Clipped left glyph, bottom-clipped tuplet marking, and continuation notes. |
| 4.png | 8, 9, 10, 11, clipped label | 4 / 1 | 31 | 38 | 2 | Outgoing curves and clipped final measure label at the right edge. |
| 5.png | unnumbered, 11, 12, 13, 14 | 3 / 2 | 30 | 46 | 5 | Stemless tied chord, grace rhythms, X symbols, and clipped final fret. |
| 6.png | unnumbered, 16, 17, 18, 19 | 3 / 2 | 33 | 54 | 6 | Grace rhythms, X symbols, unreadable continuation, and right-edge slide. |
| 7.png | unnumbered, 19, 20, 21, 22 | 3 / 2 | 32 | 54 | 6 | Clipped slide endpoints, X symbols, and stemless/unreadable continuations. |
| 8.png | unnumbered, 21, 22, 23, 24 | 3 / 2 | 33 | 47 | 7 | Clipped left event, grace rhythms, and stemless/unreadable continuations. |
| 9.png | unnumbered, 24, 25, 26 | 3 / 1 | 34 | 41 | 3 | Grace rhythms and unreadable continuation after the angle-bracketed harmonic. |

Totals: **9 images, 27 complete measure instances, 293 events, 403 notes, 45 unresolved items**. There are 42 visible measure regions in total, including 15 partial regions.

Counting conventions:

- Counts are per-image instances; overlapping passages are not deduplicated.
- A visible opening boundary with only an empty edge fragment is counted as a partial measure, with zero events.
- Events include explicit small grace/slide-source frets, rests, and visible-stem placeholders whose fret content is unreadable.
- Notes include readable numbered frets and 16 explicit X dead notes. X symbols are stored in `unpitched_notes`, without assigning a fictitious fret. Unknown placeholder pitches are not counted.
- Base durations come from visible stems, beams, flags and dots. Unreadable grace values, stemless tied values and a cropped tuplet ratio remain explicit uncertainties.
- An unresolved entry may cover several events or a measure-label ambiguity, so it need not equal the number of low-confidence events.

Each image folder contains `score.json`, `review.md`, and view-only inspection crops. `validate_results.py` checks structural consistency and derives the JSON summary counts. Complete measures with a visible time signature were also checked for duration totals; no meter was borrowed from another image.

No ground truth was supplied, so recognition accuracy is not estimated. Confidence labels express the visual reading judgment and do not establish objective correctness.
