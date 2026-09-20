---
name: guitar-tab-product
description: Build and maintain the private guitar-tab reconstruction product. Use this skill for work on screenshot stitching, video-to-score reconstruction, measure segmentation/deduplication/ordering, A4 layout, AI visual transcription, structured score data, or Guitar Pro export. Follow the current V1→V2→V3 roadmap and do not prematurely implement later-version features.
---

# Guitar Tab Product Skill

This repository implements a private commercial guitar-tab conversion product.

Always read:

- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/EXECUTION_PLAN.md`

before making architectural or scope-changing decisions.

# Product roadmap

## V1
Multiple screenshots → measures → dedupe/order → full score image → A4 PNG/PDF.

## V2
Video → automatic frame capture → V1 pipeline → printable score.

## V3
Clean measure images → AI vision structured score JSON → validation → Guitar Pro-compatible output.

Never collapse these milestones into one uncontrolled implementation.

# Current scope rule

Before starting a task, determine the active version.

If the user has not explicitly advanced the project beyond the current milestone, do not implement future-version features.

During V1, do not add:

- video processing
- GPT/OpenAI runtime integration
- OMR
- score recognition
- Guitar Pro export
- billing
- auth
- web frontend
- MCP integration

During V2, do not start Guitar Pro recognition/export unless explicitly requested.

# Engineering principles

1. Preserve all source evidence.
2. Never silently drop measures.
3. Never silently merge uncertain duplicates.
4. Never silently invent score content.
5. Save intermediate artifacts.
6. Keep thresholds configurable.
7. Prefer deterministic algorithms for dedupe/order/layout.
8. Keep AI providers behind interfaces.
9. Keep score export separate from recognition.
10. Add regression tests before changing reconstruction heuristics.

# V1 expected pipeline

```text
input screenshots
  ↓
ROI
  ↓
barline detection
  ↓
measure crops
  ↓
fingerprints / similarity
  ↓
duplicate groups
  ↓
global sequence reconstruction
  ↓
best candidate selection
  ↓
full horizontal strip
  ↓
A4 row layout
  ↓
PNG + PDF
```

# V1 manifest requirements

Every measure candidate should retain:

- source image
- crop bbox
- complete/partial boundary type
- quality score
- hashes/fingerprints
- similarity relationships
- duplicate group
- selected/not selected
- final sequence position
- uncertainty

Do not make the rendered output the only source of truth.

# Measure boundary types

Allowed:

- `complete`
- `partial_left`
- `partial_right`
- `partial_both`

Do not treat an edge crop as complete without evidence.

# Duplicate matching

Use multiple signals.

Good candidates:

- perceptual hash
- normalized pixel similarity
- local feature similarity
- printed measure number
- screenshot progression
- partial/full overlap

Do not use one threshold as the sole identity decision.

When uncertain:

- retain both candidates
- mark ambiguity
- do not silently merge

# Ordering

Use evidence in descending priority:

1. reliable printed measure number
2. image/frame order
3. overlap relation
4. partial-to-complete continuation
5. visual similarity

If evidence conflicts, record it.

# Rendering

Full strip:

- consistent TAB height
- preserve aspect ratio
- no accidental cropping

A4 layout:

- portrait default
- configurable DPI and margins
- wrap only at measure boundaries
- never split a measure across rows
- preserve readability

# V2 additions

When V2 begins:

- use FFmpeg for video decode/probe
- sample only useful frames
- dedupe near-identical frames
- feed extracted measure candidates into the same V1 pipeline
- implement gap detection
- re-sample only suspicious time windows

Do not fork the V1 reconstruction code.

# V3 additions

When V3 begins:

AI vision is the primary planned recognition engine.

Use:

```text
clean measure image
→ multimodal model
→ strict canonical JSON
```

Do not use Codex CLI as the production runtime.

Codex may still be used during development and testing.

# V3 visual recognition rules

The model must:

- use only visible source evidence
- not infer clipped/hidden content
- preserve uncertainty
- output strict JSON
- identify string, fret, duration, rests, chords, parenthesized notes, and visible techniques
- allow unresolved events

String convention:

- `1 = top/highest TAB line`
- `6 = bottom/lowest TAB line`

# Canonical score architecture

Recognition and export must be separated:

```text
MeasureImage
  ↓
VisionTabProvider
  ↓
Canonical Measure JSON
  ↓
Score Validator
  ↓
Canonical Score
  ↓
Exporter
```

# Vision provider abstraction

Design toward:

```python
class VisionTabProvider:
    async def transcribe_measure(self, image, context):
        ...
```

Do not scatter provider-specific SDK calls through business logic.

# Guitar Pro export

Preferred path:

```text
canonical JSON
→ alphaTab Score
→ Gp7Exporter
→ .gp
```

Possible prototype/debug alternatives:

- Guitar Pro MCP
- MusicXML
- PyGuitarPro

Never implement the Guitar Pro binary format manually unless explicitly required.

# Product privacy

This is a private commercial implementation.

Do not add documentation intended to publicly disclose:

- prompts
- matching heuristics
- retry logic
- model routing
- confidence calculations
- cost controls
- proprietary benchmark data

Normal private repository documentation is fine.

# Commercial architecture

After V2, the expected first paid service is:

```text
upload video
→ async processing
→ reconstructed printable score
→ download
```

After V3:

```text
upload video
→ printable score
→ optional editable Guitar Pro output
```

Billing, accounts, subscriptions, and BYOK come only after the core conversion is validated unless explicitly requested earlier.

# Task discipline

For every implementation task:

1. State the exact milestone.
2. Inspect existing code before changing it.
3. Implement only the requested scope.
4. Add/update tests.
5. Run relevant tests.
6. Summarize:
   - files changed
   - behavior added
   - tests run
   - remaining limitations
7. Stop.

Do not autonomously continue into the next roadmap milestone.

# First task

If the repository is new, start with:

> V1 Task 1 — bootstrap repository, CLI skeleton, config, run workspace, tests, and documentation links.

Do not implement barline detection in Task 1 unless explicitly requested.
