# Guitar Tab Cracker

Private Codex-first workflow. Invoke [$guitar-tab-cracker](.agents/skills/guitar-tab-cracker/SKILL.md).

- **V1 COMPLETE:** screenshots → ordered measures → reconstructed visual score.
- **V2 CORE COMPLETE:** video / accessible URL → ordered clean measure set → visual score.
- **V3 ACTIVE:** ordered clean measure set → structured music data → Guitar Pro.

Provide one local video or accessible URL and ask **Convert this guitar-tab
video.** Codex chooses inspection timestamps, extracts frames, revisits gaps,
reconciles observations, selects clean sources and visually verifies the output.
Users supply no screenshots, sampling rate, ROI, coordinates, numbering,
duplicate relationships, sequence order or page breaks.

The primary V2 artifact is `result/measures/001.png`, `002.png`, ... in global
order, accompanied by source timestamps and uncertainty in `measures.json`.
Other outputs: source metadata, useful frames, `full_score.png`, multi-line A4
`page_001.png` (and later pages), `full_score.pdf` and concise `report.md`.
Content coverage and clean crops take priority over publication polish.

**Raw-video acceptance passed:** one 209.95-second local video → 69 inspected
frames → 57 ordered complete logical measures → 3 visually checked A4 landscape
pages. Coverage includes adaptive recovery and an independent second video pass.
See [V2 acceptance](acceptance/V2_ACCEPTANCE.md) and
[outputs](runs/v2-yukinohana/result/). No known omissions or duplicate occurrences
remain in this run. The user-owned original video is unchanged.

Only this horizontally scrolling style has passed. A second video style and
URL/Xiazaitool acquisition remain unvalidated; this is not a claim of universal
robustness. These validation gaps do not block V3. V3 is now ACTIVE;
this handoff cleanup does not implement transcription or Guitar Pro export.
Do not further beautify raster scores unless V3 fails and raster output becomes
the primary final product.

Codex makes every visual decision. Helpers execute explicit timestamps, crops,
order, scales and placements; they never detect notation or infer layout.
No CV/OMR application, ROI configuration or fixed-sampling product is involved.
URLs must be accessible without bypassing login, DRM, paywalls or restrictions.
If direct access fails, use the user-selected fallback
[下载狗 / Xiazaitool](https://www.xiazaitool.com/): paste the public video URL,
parse it and download the available video. If that also fails or requires
unavailable access, request a local file. Genuine gaps stay explicit.
After reconstruction and final QA, delete only video copies downloaded for this
run (including partial downloads); retain measure images, score/PDF and source
metadata. Never delete a user-supplied local original.

## Tools and evidence

- `tools/extract_frames.py`: video metadata and explicit-timestamp extraction,
  using ffprobe/ffmpeg on PATH or supplied executable paths. Run `--help`.
- `tools/export_visual_score.py`: V2 explicit crop/context/order/page exporter,
  using Pillow and ReportLab; saves stable three-digit measures and provenance.
  Optional plan keys: `title`, `artist`, `font`, `show_header`, `debug`. Metadata
  is omitted when unknown. The default font is Pillow's bundled font; an explicit
  font path is resolved relative to the plan. Supply a font with suitable glyph
  coverage when needed. Normal pages show only supplied metadata and page numbers;
  engineering labels require `debug: true`. `show_header: false` hides the header.
- `tools/compose.py`: existing mechanical crop/place/export helper, using Pillow
  and ReportLab. Its existing V1 plan format is preserved; the V2 skill describes
  adapting explicit paths and exporting the stable measure set.
- `benchmark/input/`: preserved V1 screenshots.
- `benchmark/decisions.json`: one run's evidence, never another song's template.
- `acceptance/`: preserved V1 acceptance artifacts.

V1 acceptance: **10 screenshots → 26 logical measures → 2 A4 pages**, with
source comparison and actual PDF verification. Only the existing set was
validated; residual source overlays are documented. See
[V1 acceptance](acceptance/V1_ACCEPTANCE.md),
[printable score](acceptance/v1-existing/full_score.pdf) and
[benchmark report](benchmark/REPORT.md). Do not further polish V1 for V2.

Read [requirements](docs/PRODUCT_REQUIREMENTS.md) and
[execution plan](docs/EXECUTION_PLAN.md). Implementation and evidence remain
private. A future hosted runtime would use a multimodal agent with controlled
tools; no hosted application or musical transcription is implemented here.

The [V2 handoff regression](acceptance/V2_HARDENING.md) confirms unchanged
measure images, metadata and score order after generic PDF export.
