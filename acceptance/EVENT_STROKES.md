# Event arpeggio, strum and pick-stroke support

The previous model noticed source arrows but recorded them only as unresolved
items. GP therefore received ordinary chords. This was a canonical-model and
adapter support omission, not a Guitar Pro format limitation.

Optional v1 event fields now preserve `brush` type/direction and independent
`pick_stroke`. Old canonical inputs remain valid. Up/down brush direction is
defined in TAB screen coordinates, independently of pick hand direction.
Pinned alphaTab 1.8.4 uses Down enums for the upward TAB arrow. Four re-imported
synthetic cases were rendered and opened to verify both arpeggio and straight
strum directions, plus staple/V pick symbols. These fixtures test mechanics.
Target playback spread defaults are recorded per event, never inserted into
canonical or treated as source measurements.

Validation: 34 Node adapter tests; 17 canonical validator tests; 12 verification
tests; 5 timing/report tests pass. Missing and reversed effects fail the semantic
comparator. Rest/malformed fields are rejected; short dotted tuplets preserve
rhythm and use capped playback spread.

Real local correction: `runs/silver-lining-strokes` preserves the old
`runs/silver-lining` version. All 53 affected source measure crops were reopened,
confirming 61 upward arpeggio arrows and 2 independent down-pick marks. All 33
affected re-imported render chunks were inspected. These marks now exist in the
editable GP and no longer appear as unsupported. There were no changes to
notes, durations, ties, slides, or metadata. 199 units / 947 events / 1230 notes
and all supported semantics pass full fresh import and exact assembly checks.

The previous all-note reread was explicitly reused; this revision is targeted,
not a new whole-song transcription. `verification/corrections.json` retains
all old/new values, original issue records, source hashes and old/new score/GP
hashes. 13,888 field observations pass. Three unknown slide endpoints and seven
remaining limitation groups (TH playback and engraving) still require the
existing review; they are unrelated to this fix. No external Guitar Pro desktop
acceptance is claimed. Music artifacts remain in ignored local run directories.
