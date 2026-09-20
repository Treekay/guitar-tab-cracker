# Guitar Tab Cracker

Private Codex-first workflow. Give Codex screenshots and ask: **Convert these
screenshots into a complete printable guitar tab.** Codex inspects every source,
chooses crops, reconciles overlap, orders measures, selects sources, composes
the score, chooses A4 page breaks, exports and visually checks the output.

Invoke [$guitar-tab-cracker](.agents/skills/guitar-tab-cracker/SKILL.md).
There is no application installation, tabstitch CLI, ROI config or CV pipeline.
Mechanical tools only execute explicit visual decisions made by the agent.

- V1 (active): images -> full score PNG, A4 page PNGs and PDF.
- V2 (not started): video/file URL -> agent-selected frames -> the same V1 workflow.
- V3 (not started): reconstructed score -> visual transcription -> structured data and Guitar Pro-compatible export.

Users do not supply ROI, coordinates, order, duplicates or page breaks. Genuine
source gaps stay visible; missing content is never invented.

```text
.agents/skills/guitar-tab-cracker/SKILL.md  autonomous workflow
docs/                                    requirements and short plan
benchmark/input/                         preserved screenshots
benchmark/expected/                      historical evidence, not a V1 dependency
benchmark/decisions.json                  explicit visual decisions for this run
benchmark/REPORT.md                      coverage and final visual QA
benchmark/result/                        full score, A4 PNGs, PDF
tools/compose.py                         mechanical crop/place/export helper
```

The helper uses Pillow and ReportLab from the available tool environment; no
Python application bootstrap is needed. It accepts explicit rectangles, order,
scale and page placements, and does not infer any of them.

The fresh benchmark uses all **10 currently supplied screenshots**, including
the added middle image that covers measures 14-16. Earlier benchmark records
covered nine images; these remain historical evidence, not V1 crop/order input.
See [benchmark report](benchmark/REPORT.md) and [final output](benchmark/result/).

The obsolete application/tests are removed from tracked source. Earlier
committed versions remain in Git history. Local uncommitted code is recoverable
in ignored tmp/retired-application/. The local tool environment is preserved.

Read [requirements](docs/PRODUCT_REQUIREMENTS.md) and
[execution plan](docs/EXECUTION_PLAN.md). A future hosted runtime will be a
multimodal API agent with controlled tools. Keep implementation evidence private.
