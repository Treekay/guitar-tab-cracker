# Guitar Tab Video Conversion Service
## Execution Plan

This plan implements the three-version product direction in controlled gates.

Do not start a later version until the current version is demonstrably working on representative samples.

---

# 1. Development strategy

Use a private repository.

Primary principles:

- local CLI first for core pipeline reliability,
- modular code compatible with future background workers,
- deterministic image pipeline before AI recognition,
- save intermediate artifacts,
- keep each phase independently testable,
- do not prematurely build billing/auth/UI.

---

# 2. V1 execution plan
## Multi-image screenshots → reconstructed A4 score

### Milestone V1.0 — Repository bootstrap

Deliver:

- Python project
- CLI entrypoint
- config system
- run workspace
- logging
- basic test setup
- example input folder

Suggested CLI:

```bash
tabstitch inspect input-images/
tabstitch build input-images/ --output runs/demo/
tabstitch layout runs/demo/manifest.json
```

Definition of done:

- CLI launches
- config loads
- run directory is deterministic and inspectable

---

### Milestone V1.1 — Image ingest and ROI

Implement:

- image loading
- dimension validation
- normalized ROI
- preview generation
- ROI crop output

Artifacts:

```text
runs/<id>/inputs/
runs/<id>/roi/
```

Tests:

- different image resolutions
- invalid ROI
- portrait/landscape guardrails

---

### Milestone V1.2 — TAB/barline detection

Implement:

- grayscale/edge preprocessing
- horizontal TAB-line detection
- vertical barline candidate detection
- boundary confidence
- debug overlay

Artifacts:

```text
debug/barlines_<image>.png
```

Tests:

- clear black barline
- faint barline
- UI overlay
- partial bar at image edge

---

### Milestone V1.3 — Measure cropping

Implement:

- crop between barline boundaries
- partial-left and partial-right handling
- crop normalization
- measure metadata
- quality metrics

Artifacts:

```text
crops/<source>-m01.png
```

Manifest fields:

- source image
- bbox
- boundary type
- quality score

Definition of done:

- representative screenshots produce visually correct measure crops

---

### Milestone V1.4 — Measure fingerprints

Implement multiple identity signals:

- cryptographic hash
- perceptual hash
- normalized pixel similarity
- local feature matching where useful

Do not make one threshold authoritative.

Build a comparison report.

Example:

```json
{
  "left": "img01-m03",
  "right": "img02-m01",
  "phash_similarity": 0.97,
  "pixel_similarity": 0.93,
  "feature_score": 0.91
}
```

---

### Milestone V1.5 — Duplicate grouping

Implement:

- candidate similarity graph
- duplicate clusters
- complete-vs-partial preference
- best-candidate selection

Important:

- never merge merely because two measures are visually similar,
- preserve all source candidates,
- expose uncertain clusters.

---

### Milestone V1.6 — Sequence reconstruction

Use evidence in this order:

1. reliable printed measure number
2. screenshot progression/order
3. adjacent overlap evidence
4. partial-to-complete continuation
5. duplicate-cluster relationships

Output:

```text
logical measure 1
logical measure 2
...
```

with uncertainty flags.

Add explicit detection for:

- duplicate sequence placement
- possible missing region
- conflicting order

---

### Milestone V1.7 — Full-strip composer

Implement:

- consistent height
- optional whitespace normalization
- gap/padding configuration
- preserve aspect ratio
- high-resolution output

Output:

```text
outputs/full_strip.png
```

---

### Milestone V1.8 — A4 layout

Implement:

- A4 portrait
- configurable DPI
- margins
- row width calculation
- wrap only between measures
- no crop splitting
- multiple pages

Output:

```text
outputs/page_001.png
outputs/page_002.png
...
outputs/full_score.pdf
```

---

### Milestone V1.9 — Manifest and report

Final `manifest.json` must contain:

- inputs
- ROI
- measure candidates
- similarity links
- duplicate groups
- chosen candidate per logical measure
- final order
- unresolved ambiguity
- output files

`summary.md` should give:

- images processed
- measure candidates
- logical measures
- duplicate groups
- unresolved order cases
- pages generated

---

### Milestone V1.10 — Regression tests

Create fixture sets for:

- clean overlap
- partial-left overlap
- partial-right overlap
- visually similar but different measures
- UI cursor overlap
- missing intermediate screenshot
- ambiguous barline

Do not rely only on one song.

---

# 3. V1 release gate

Proceed to V2 only when:

- segmentation is reliable,
- overlap dedupe works on representative input,
- order is stable,
- A4 output is usable,
- unresolved cases are visible instead of silently wrong.

---

# 4. V2 execution plan
## Video → automatic reconstructed score

### Milestone V2.1 — Video probe

Implement:

- FFmpeg integration
- metadata extraction
- duration/FPS/resolution
- frame timestamp system

---

### Milestone V2.2 — Video ROI

Initially reuse manual ROI.

Command example:

```bash
tabstitch video-preview input.mp4 --time 00:01:30
```

Later add automatic ROI detection.

---

### Milestone V2.3 — Initial frame sampling

Config:

```yaml
video:
  sample_fps: 2
```

Do not commit to the exact default until benchmarked.

Save only useful candidate frames.

---

### Milestone V2.4 — Frame dedupe

Avoid processing frames where the TAB region has not materially changed.

Signals:

- perceptual difference
- edge-map difference
- barline shift
- playhead-only change

---

### Milestone V2.5 — Feed frame measures into V1

Every useful frame becomes another source of measure candidates.

Reuse V1:

- crop
- matching
- grouping
- ordering
- layout

No duplicate implementation.

---

### Milestone V2.6 — Coverage analyzer

Determine whether the reconstructed measure sequence is likely complete.

Signals:

- printed measure-number gaps
- temporal gaps
- incomplete partial edges with no continuation
- failed overlap between neighboring candidate sets

---

### Milestone V2.7 — Targeted recovery

For suspicious time ranges:

- resample at higher FPS
- re-run extraction only in those windows
- add candidates
- rebuild sequence

---

### Milestone V2.8 — Job-compatible worker

Refactor long-running conversion so it can execute as:

```text
queued job
→ progress events
→ final artifacts
```

No billing required yet.

---

### Milestone V2.9 — Minimal online service

First commercial prototype:

Frontend:
- upload video
- processing state
- download result

Backend:
- upload
- create job
- job status
- artifact download

Worker:
- V2 conversion pipeline

Outputs:
- PDF
- page images
- optional full strip

Use private deployment.

---

# 5. V2 release gate

V2 is ready for paid validation when:

- upload-to-PDF works reliably,
- average manual correction burden is low enough,
- conversion failures are explainable,
- processing cost/time is measurable,
- sample users can understand the result without technical assistance.

At this point, begin testing actual willingness to pay.

---

# 6. V3 execution plan
## Structured transcription and Guitar Pro

### Milestone V3.1 — Canonical schema

Define versioned JSON schema for:

- metadata
- measures
- events
- notes
- duration
- rest
- techniques
- uncertainty
- source evidence

Lock schema before exporter work.

---

### Milestone V3.2 — Vision provider abstraction

Interface concept:

```python
class VisionTabProvider:
    async def transcribe_measure(self, image, context) -> MeasureResult:
        ...
```

Initial provider:

```text
OpenAIVisionProvider
```

Keep provider details outside score logic.

---

### Milestone V3.3 — Structured API output

Use strict schema output.

One request should preferably process:
- one measure,
- or a very small number of measures,
to reduce omission risk.

Store:
- model
- prompt version
- token usage
- latency
- raw structured output
- retry count

---

### Milestone V3.4 — Recognition confidence / audit

Support:

- first-pass recognition
- deterministic validation
- second-pass visual audit
- targeted retry only on suspicious measures

Do not re-run the entire score for one uncertain measure.

---

### Milestone V3.5 — Score validation

Implement:

- valid string/fret range
- event order
- duplicate string checks
- duration checks
- known-meter total
- continuity
- unresolved reporting

---

### Milestone V3.6 — Exporter spike

Evaluate in this order:

1. alphaTab `Gp7Exporter`
2. Guitar Pro MCP as a prototype/debug path
3. MusicXML fallback
4. PyGuitarPro only if `.gp5` is acceptable

Do not implement Guitar Pro binary format manually.

---

### Milestone V3.7 — JSON to `.gp`

Build deterministic exporter.

Verify:

- score opens
- measures preserved
- strings/frets preserved
- chords preserved
- rests preserved
- durations preserved
- supported techniques preserved

Add round-trip structural test if exporter/library permits.

---

### Milestone V3.8 — Premium output

Online product options:

```text
Basic:
PDF / reconstructed score image

Premium:
PDF + editable Guitar Pro file
```

Do not finalize pricing until real model/API cost data exists.

---

# 7. Commercial execution

## Stage 1
Private paid beta after V2.

Sell:
- score reconstruction result

Do not market internal implementation.

## Stage 2
Add V3 premium export.

## Stage 3
After demand is proven:
- credits/subscriptions
- persistent accounts
- conversion history
- correction UI
- optional BYOK
- desktop product
- API product

---

# 8. Data to record from the beginning

For every job:

- input duration
- number of sampled frames
- number of kept frames
- measure candidates
- duplicate groups
- unresolved cases
- processing time
- output size

From V3 onward also record:

- AI model
- images sent
- input/output tokens
- API cost
- retries
- measure-level correction/failure type

This data will drive future pricing and optimization.

---

# 9. Codex task order

Do not ask Codex to "build the whole product".

Use bounded tasks.

## V1 tasks

1. Bootstrap repo and CLI
2. ROI and image inspection
3. Barline detector
4. Measure cropper
5. Similarity benchmark tool
6. Duplicate grouping
7. Sequence reconstruction
8. Full-strip renderer
9. A4 PNG/PDF renderer
10. Manifest/report
11. Fixture/regression suite
12. End-to-end V1 command

## V2 tasks

13. FFmpeg video probe
14. Frame sampler
15. Frame dedupe
16. V1 integration
17. Coverage/gap analyzer
18. Targeted re-sampling
19. Background-job refactor
20. Minimal upload/status/download web service

## V3 tasks

21. Canonical score schema
22. Vision provider interface
23. OpenAI structured transcription
24. Measure validation/retry
25. Guitar Pro exporter spike
26. Deterministic `.gp` exporter
27. Premium output integration

---

# 10. Immediate next action

Start only:

> V1 Task 1 — repository and CLI bootstrap.

Then review before Task 2.
