# Guitar Tab Video Conversion Service
## Product Requirements Document

Version: 1.0
Status: Approved direction after feasibility testing

---

# 1. Product vision

Build a private, server-side service that turns dynamic guitar-tab screenshots or videos into reusable guitar-tab outputs.

The product evolves in three versions:

- **V1 — Images to reconstructed printable score**
- **V2 — Video to reconstructed printable score**
- **V3 — Video to structured score and Guitar Pro output**

The first commercial milestone is reached at **V2**.  
V3 adds higher-value editable score output.

The implementation remains private. The service may later support users supplying their own AI API credentials, but the initial commercial product should be a hosted online service.

---

# 2. Core product promise

## V1

Input:

> Multiple overlapping screenshots from the same dynamic guitar tab.

Output:

> A reconstructed, de-duplicated, correctly ordered, printable full-score image/PDF.

V1 does **not** need to understand the musical meaning of the notes.

---

## V2

Input:

> A dynamic guitar-tab video.

Output:

> A reconstructed, de-duplicated, correctly ordered, printable full-score image/PDF.

The system automatically selects the necessary frames from the video and then applies the V1 reconstruction pipeline.

V2 is the first product that can be offered as an online paid conversion service.

---

## V3

Input:

> A dynamic guitar-tab video.

Output:

> The V2 printable score plus structured musical data and an editable Guitar Pro-compatible file.

V3 uses an AI vision model to read cleaned measure images into canonical score JSON, validates the result, and exports to a Guitar Pro-compatible format.

---

# 3. Product principles

1. **Do not require music recognition before it is necessary.**
   V1 and V2 work entirely from image segmentation, matching, ordering, and layout.

2. **Never silently drop a measure.**
   If the system cannot determine whether a segment is present, duplicated, or missing, it must surface the uncertainty.

3. **Never silently duplicate a measure.**
   Repeated measures across screenshots/frames must be reconciled.

4. **Preserve provenance.**
   Every reconstructed measure must remain traceable to source image/frame coordinates.

5. **Separate recognition from export.**
   In V3, image-to-structure and structure-to-Guitar-Pro are independent modules.

6. **Prefer deterministic code around AI.**
   AI should only do the visual interpretation that benefits from multimodal reasoning. Ordering, dedupe, validation, file generation, and layout should be deterministic whenever possible.

7. **Private implementation.**
   Do not publish internal prompts, matching heuristics, reconstruction logic, retry strategy, cost controls, or backend architecture.

---

# 4. Current technical validation

Direct multimodal visual reading has passed the initial feasibility gate.

Observed benchmark behavior:

- First manually checked sample: 44 readable notes across measures 26, 27 and visible measure 28 were correctly extracted at the string/fret level.
- Second multi-image benchmark: overlapping independently analyzed regions were highly consistent.
- The benchmark also showed useful uncertainty behavior: clipped or unreadable events were surfaced as unresolved instead of being guessed.

This is sufficient to proceed with product development.

The dedicated Guitar Tab OMR model is **not** the primary planned recognition engine.

---

# 5. Version 1 — Multi-image score reconstruction

## 5.1 Goal

Given a folder of guitar-tab screenshots from the same song:

1. locate the tablature area,
2. detect individual measure boundaries,
3. crop measures,
4. identify overlapping/duplicate measures,
5. reconstruct their global order,
6. build a continuous score strip,
7. re-layout the strip into normal multi-line A4 pages,
8. export PNG and PDF.

No note recognition is required.

---

## 5.2 Supported input

Required:

- PNG
- JPG/JPEG
- WebP

Expected image properties:

- horizontally rendered TAB
- one visible score system
- multiple measures per screenshot
- neighboring screenshots may overlap
- left and right edges may contain partial measures
- UI overlays may be present

---

## 5.3 V1 output

```text
runs/<run-id>/
  inputs/
  crops/
  normalized/
  matches/
  outputs/
    full_strip.png
    page_001.png
    page_002.png
    full_score.pdf
  manifest.json
  summary.md
```

---

## 5.4 Measure representation

Each detected measure candidate must retain:

```json
{
  "candidate_id": "img03-m02",
  "source_image": "03.png",
  "crop": {
    "x": 312,
    "y": 54,
    "width": 351,
    "height": 121
  },
  "boundary": "complete",
  "printed_measure_number": 8,
  "image_hash": "...",
  "perceptual_hash": "...",
  "quality_score": 0.94,
  "duplicate_group": "measure-8",
  "final_sequence_index": 8,
  "uncertainty": null
}
```

Boundary values:

- `complete`
- `partial_left`
- `partial_right`
- `partial_both`

---

## 5.5 V1 functional requirements

### FR-V1-001 Input ingestion
- Read all supported images from a folder.
- Sort by filename only as an initial hint, not as final musical order.

### FR-V1-002 ROI
Support:
- manually configured normalized ROI
- auto-detection later

Manual ROI must be sufficient for MVP.

### FR-V1-003 Barline detection
Detect vertical measure boundaries.

The system must expose:
- detected x positions
- confidence
- source image

### FR-V1-004 Measure cropping
Save every measure candidate independently.

Do not destroy or overwrite original images.

### FR-V1-005 Printed number reading
Printed measure numbers may be used as a strong ordering signal.

This may use visual-model assistance later, but V1 must also work with geometric matching when printed numbers are absent.

### FR-V1-006 Similarity
Compare candidate crops using multiple signals, such as:
- perceptual hash
- normalized image similarity
- feature matching
- structural edge similarity
- optional AI visual similarity fallback

Do not deduplicate based on one weak similarity score.

### FR-V1-007 Duplicate grouping
Group different screenshots of the same logical measure.

Retain all source candidates.

### FR-V1-008 Candidate selection
For each logical measure group, choose the best visual candidate based on:
- completeness
- sharpness
- obstruction
- resolution
- similarity agreement

### FR-V1-009 Sequence reconstruction
Determine final order using:
1. printed measure numbers where reliable,
2. screenshot temporal/filename order,
3. overlap between neighboring images,
4. image similarity,
5. partial-to-complete continuation logic.

### FR-V1-010 Ambiguity
If order is uncertain, do not guess silently.

Record uncertainty in `manifest.json`.

### FR-V1-011 Horizontal strip
Build:

```text
full_strip.png
```

All selected measures must be placed in order with consistent scale.

### FR-V1-012 A4 layout
Create a multi-line printable layout.

Requirements:
- A4 portrait by default
- configurable page margins
- consistent TAB height
- line wrapping only between measures
- no measure split across rows
- readable resolution
- page numbering optional

### FR-V1-013 PDF export
Generate one printable PDF from the page images.

---

# 6. Version 1 acceptance criteria

V1 is complete when:

1. A folder of screenshots can be processed from a CLI.
2. Measure candidates are cropped correctly on representative samples.
3. Overlapping repeated measures are usually grouped correctly.
4. Partial measures are not treated as complete without evidence.
5. Final sequence is coherent.
6. No accepted measure silently disappears.
7. `full_strip.png` is readable and ordered.
8. A4 page PNGs are readable and ordered.
9. `full_score.pdf` opens successfully.
10. Re-running layout from `manifest.json` does not require redoing measure detection.

---

# 7. Version 2 — Video to reconstructed printable score

## 7.1 Goal

Input one video and automatically obtain enough screenshots to reconstruct the entire score with the V1 pipeline.

---

## 7.2 V2 pipeline

```text
video
  ↓
video probe
  ↓
TAB ROI
  ↓
frame sampling
  ↓
candidate-frame filtering
  ↓
measure detection/cropping
  ↓
measure identity + dedupe
  ↓
coverage / continuity analysis
  ↓
targeted re-sampling around gaps
  ↓
V1 reconstruction
  ↓
full score PNG/PDF
```

---

## 7.3 V2 requirements

### FR-V2-001 Video ingestion
Support MP4 first.

Read:
- duration
- FPS
- resolution

### FR-V2-002 TAB ROI
MVP supports manual ROI.

Auto-detection may be added after reliability is established.

### FR-V2-003 Initial sampling
Configurable default sampling frequency.

Do not process every source frame.

### FR-V2-004 Frame filtering
Avoid redundant work by detecting near-identical frames.

### FR-V2-005 Coverage
The system must determine whether all logical measures have been captured.

### FR-V2-006 Gap recovery
When a likely gap is detected:
- resample a local time window at a higher frequency,
- extract new candidates,
- retry sequence reconstruction.

### FR-V2-007 Evidence
Every final measure must retain one or more source timestamps.

### FR-V2-008 V1 compatibility
V2 must feed the same measure-manifest/reconstruction system used by V1.

Do not build a separate layout pipeline.

---

# 8. Version 2 acceptance criteria

V2 is complete when:

1. A representative video can be submitted.
2. The system automatically extracts a sufficient set of frames.
3. Measures are segmented and deduplicated.
4. Repeated scrolling content does not become repeated final measures.
5. Likely gaps are detected and re-sampled.
6. Final score image/PDF is coherent and printable.
7. Human intervention is limited to unresolved cases.
8. The conversion can run as a background job.

V2 marks the first commercial online-service milestone.

---

# 9. Version 3 — Structured recognition and Guitar Pro output

## 9.1 Goal

Convert cleaned measure images into structured musical data and then export an editable score.

---

## 9.2 Recognition engine

Primary planned engine:

> Multimodal AI vision API with strict structured output.

The current development benchmark uses Codex visual reasoning.

Production should call a hosted multimodal model API directly rather than using Codex CLI as a runtime dependency.

---

## 9.3 Canonical score format

Example:

```json
{
  "schema_version": 1,
  "metadata": {
    "title": null,
    "tempo_bpm": null,
    "time_signature": null,
    "capo": 0,
    "tuning": null
  },
  "measures": [
    {
      "sequence_index": 26,
      "printed_number": 26,
      "status": "accepted",
      "events": [
        {
          "index": 1,
          "duration": 16,
          "dots": 0,
          "tuplet": null,
          "rest": false,
          "notes": [
            {
              "string": 6,
              "fret": 2,
              "parenthesized": false,
              "techniques": []
            }
          ]
        }
      ],
      "sources": [
        {
          "image": "measure_026.png"
        }
      ]
    }
  ],
  "unresolved": []
}
```

String convention:

- 1 = top/highest guitar TAB line
- 6 = bottom/lowest TAB line

---

## 9.4 V3 recognition rules

The vision model must:

- use the image as the only musical source of truth,
- avoid filling clipped content,
- preserve uncertainty,
- output strict JSON,
- identify:
  - event order
  - string
  - fret
  - duration
  - rests
  - simultaneous notes
  - parenthesized notes
  - visible techniques
  - uncertainty

A second-pass audit or low-confidence retry should be supported.

---

# 10. Structured validation

Deterministic validation should check:

- strings 1–6
- non-negative fret
- no impossible duplicate string within an event
- valid duration values
- measure rhythmic total when meter is known
- sequence continuity
- source evidence
- unresolved items
- duplicate measure IDs

Validation must not invent corrected musical content.

---

# 11. Guitar Pro export strategy

Preferred production path:

```text
canonical JSON
  ↓
alphaTab Score
  ↓
Gp7Exporter
  ↓
.gp
```

Alternative prototype paths:

- Guitar Pro MCP
- PyGuitarPro / `.gp5`
- MusicXML intermediate export

The exporter is a separate module and must not be coupled to recognition.

---

# 12. Commercial product direction

## Phase A — Paid hosted score reconstruction

After V2:

User flow:

```text
upload video
→ processing
→ download reconstructed score image/PDF
```

This is the first market-validation product.

---

## Phase B — Guitar Pro premium output

After V3:

```text
upload video
→ processing
→ download PDF + .gp
```

---

## Phase C — Mature product

Only after demand is proven:

- improved UI
- subscriptions
- credits
- batch conversion
- user history
- job retry/review
- optional BYOK
- desktop application
- public API
- model selection
- advanced correction UI

---

# 13. Business privacy requirements

Do not expose publicly:

- prompts
- internal schemas
- frame-selection heuristics
- dedupe heuristics
- matching thresholds
- retry strategy
- confidence logic
- model-routing strategy
- internal cost model
- backend source code

Public product messaging should focus on:

> Dynamic guitar-tab video → printable score / editable Guitar Pro file.

---

# 14. SaaS architecture target

```text
Frontend
   ↓
API
   ↓
Job Service
   ↓
Queue
   ↓
Worker
   ├─ Video Processor
   ├─ Measure Detector
   ├─ Measure Matcher
   ├─ Sheet Builder
   ├─ Vision Provider       (V3)
   ├─ Score Validator       (V3)
   └─ Guitar Pro Exporter   (V3)
   ↓
Object Storage
   ↓
Download
```

Early development may remain local CLI-first, but boundaries should remain compatible with asynchronous jobs.

---

# 15. Suggested repository structure

```text
guitar-tab-service/
  README.md
  docs/
    PRODUCT_REQUIREMENTS.md
    EXECUTION_PLAN.md

  backend/
    app/
      api/
      jobs/
      config/

  worker/
    tabservice/
      ingest/
      video/
      detection/
      measures/
      matching/
      sequence/
      layout/
      vision/
      score/
      export/
      reporting/

  frontend/
    # not required during first V1 implementation

  tests/
    fixtures/
    unit/
    integration/
    e2e/

  runs/
    .gitkeep
```

---

# 16. Explicit non-goals during V1

Do not implement:

- GPT score recognition
- OMR
- Guitar Pro output
- billing
- user accounts
- production web frontend
- video input
- public API
- desktop app
- MCP integration

Keep V1 focused on robust screenshot reconstruction.

---

# 17. Definition of success

The broader product is technically successful when:

```text
video
→ complete reconstructed score
→ printable PDF
→ structured score
→ editable Guitar Pro file
```

with low manual intervention and visible handling of uncertainty.

Commercial success is evaluated separately through real paid usage after V2.
