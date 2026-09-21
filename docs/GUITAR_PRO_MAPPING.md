# Canonical → alphaTab mapping

Use a separate Node ESM adapter with pinned `@coderline/alphatab` 1.8.4.
Python recognition/validation and canonical schema remain unchanged. No target
enum or object is written into canonical JSON. The exporter calls Gp7Exporter;
the round trip calls ScoreLoader.loadScoreFromBytes on the saved GP bytes.
The planned mappings below are implemented and tested; see
[acceptance](../acceptance/V3_GUITAR_PRO.md). GP bar numbers are sequential written
indices; original printed labels remain in export_mapping.json.source_measure_order.

Verified primary references:

- [Gp7Exporter](https://www.alphatab.net/docs/reference/types/exporter/gp7exporter/)
- [Note model](https://www.alphatab.net/docs/reference/types/model/note/)
- [Node rendering](https://www.alphatab.net/docs/guides/nodejs)
- Installed 1.8.4 `alphaTab.d.ts`, `Note.getStringTuning`, `Note.finish`,
  `GpifWriter._writeNoteProperties`, `_writeMasterBarNode` and `Gp7Exporter`.

| Canonical | Adapter / alphaTab | Limits / defaults to record |
|---|---|---|
| title, artist | Score strings | null → empty strings, no invented attribution |
| tempo | MasterBar.tempoAutomations | null → 120 BPM technical playback default |
| time signature / changes | MasterBar numerator/denominator, inherited | unknown initial meter → 4/4 technical default |
| tuning | Staff.stringTuning.tunings, top-to-bottom | null → [64,59,55,50,45,40] technical tuning |
| capo | Staff.capo | null → 0 technical default |
| instrument | Track playback program | GM 24 nylon guitar technical default |
| measures | one MasterBar + Bar each, same written order | never expand repeats |
| voice | Voice per canonical voice | per-voice event sequence; no inferred onset |
| duration | explicit Whole/Half/Quarter/Eighth/Sixteenth/ThirtySecond/SixtyFourth | null duration fails export, never guess |
| dots / tuplets | Beat.dots / tupletNumerator,tupletDenominator | no rhythmic reinterpretation |
| rest / chord | empty Beat.notes / all simultaneous notes in one Beat | retain duration and simultaneity |
| string | `canonicalStringToAlphaTab(s) = 7-s` | alphaTab 1 is bottom/lowest; tuning array is top first |
| fret / dead | Note.fret / isDead | unknown non-dead fret fails export |
| ghost | isGhost | includes softer playback; never infer from parentheses |
| parentheses / tied display | preserve tie; target draws its own continuation glyph | GP writer has no independent non-ghost parenthesis/display flag; record visual loss, do not add ghost playback |
| tie | origin/destination links + isTieDestination | check endpoints after re-import, not IDs |
| hammer / pull | isHammerPullOrigin, explicit endpoint | verify next same-string target and fret direction; library encodes shared HOPO |
| slide up/down | Shift slide; Legato if same pair explicitly has slur | subtype-less slides require documented technical articulation choice |
| explicit shift/legato | SlideOutType.Shift/Legato | verify endpoint survives importer |
| unresolved relation | omit target-dependent relation, retain note | exact source relation and reason logged; no guessed endpoint |
| slur | paired slide → Legato; standalone note slur unsupported by GP writer | document unsupported standalone mapping |
| natural harmonic | HarmonicType.Natural, harmonicValue = touched fret | verify GP preserves fret and harmonic |
| artificial harmonic | unsupported without an unambiguous touched-position field | generic amount_semitones is not a touched fret; do not invent sounding pitch |
| bend/release | BendPoint values (quarter tones), explicit amount | missing amount → documented omission; curve timing is technical default |
| vibrato / accent | Slight / Normal | amount-less vocabulary uses documented standard subtype |
| palm mute / let ring | isPalmMute / isLetRing | expand explicit score-wide let-ring scope; retain printed text |
| normal/double/final | default GP bar / MasterBar.isDoubleBar / final implicit at end | custom independent bar-line styles not serialized by 1.8.4 writer |
| repeat start/end | MasterBar.isRepeatStart / repeatCount | null end count → 2 technical default, never source data |
| endings | alternateEndings bitmask, bit n-1 | preserve numbers per written bar and ranges |
| pickup | first MasterBar.isAnacrusis | GP writer supports first-bar anacrusis only |

Round-trip comparison will project imported notes back to canonical string order,
compare every measure/voice/event/note and relation endpoint, and check concrete
defaults. Expected defaults and specifically documented unsupported mappings
are distinct from unexpected mismatches. No blanket mismatch suppression.
Rendered QA uses the re-imported GP model; it never fixes canonical recognition.

The output GP carries editable model data. Rendered PNG/SVG files are separate
QA artifacts. Technical defaults affect playback/pitch spelling, not recognized
source metadata; all are recorded in export_mapping.json and export_report.md.
