# Guitar Tab Cracker - Product Requirements

Status: agent-first architecture reset. Active version: V1.

## Core model

Codex is the primary visual agent and executor. Users supply source material;
Codex makes all visual and workflow decisions and controls mechanical tools.
This is an agent workflow repository, not a traditional CV application.

No deterministic application algorithm decides staff/barlines, measure
boundaries, duplicates, global order, source selection or row breaks. Python,
Pillow, ImageMagick and PDF tools may crop, resize, place and export explicit
agent decisions. Helpers must accept decisions, not infer them.

## V1 - Images to printable score

Input: multiple guitar-tab images only.

Output: result/full_score.png, A4 portrait result/page_001.png and subsequent
pages, and result/full_score.pdf. Working crops, inspection images and a
concise coverage/evidence report may be retained.

Codex opens every image; visually identifies TAB regions, measures, visible
numbers, clipping and overlays; chooses exact crops; reconciles duplicates;
orders all measures; selects the best source for each; composes the full score;
decides A4 row/page breaks; exports; and visually corrects the result against
every source. The user supplies no ROI, coordinates, numbering, ordering,
duplicate information or page breaks. Ask for additional source only when
genuinely necessary, after completing all available independent work.

V1 is visual reconstruction, not musical transcription. Preserve visible
string/fret symbols, rhythm, techniques and chords as pixels, without parsing
them into musical data.

### Fidelity

- Preserve original bytes and crop provenance.
- Account for every visible measure and useful partial fragment. Filename order
  is not musical truth. Use visual overlap and visible numbers as evidence.
- Prefer complete, sharp, unobstructed sources. Include notation outside the
  strings: stems, beams, ties, techniques, repeats and opening annotations.
- Never silently merge distinct repeated passages, invent clipped content,
  remove notation or substitute a later repetition for missing material.
- Preserve unresolved identity/order/coverage explicitly. Show genuine source
  gaps in both printable output and report; placeholders are not reconstructed music.
- Visually verify tonal/scale changes and preserve original crops. Do not erase
  overlays by inventing obscured notation.

### Composition and acceptance

Codex chooses scale, alignment, row groups and placements. Preserve aspect
ratio, readable size and sensible margins. Never split a measure across rows;
retain cross-boundary annotation/tie context.

Open the full image at readable scale, every page PNG, and rendered pages of the
actual A4 PDF. Compare with all sources for omissions, duplicates, order,
clipping, incorrect crops and unreadable scale. Fix and re-export until QA
passes or the remaining source limitation is explicitly documented.

V1 is complete when representative sets work reliably without user crop/order/
duplicate instructions. One successful benchmark is evidence, not proof of
general reliability. Incomplete inputs cannot establish complete-song recovery.

## V2 - Agent-controlled video inspection

Input: a video file or downloadable video URL only. Output: the same printable
score. Extend the same skill: Codex accesses the video, chooses useful inspection
timestamps, extracts those frames using ffmpeg or similar tools, checks novelty
and coverage, returns for more frames as needed, and performs V1. Do not make
fixed frame sampling the product. Respect source access permissions. Not started.

## V3 - Visual transcription and export

Input: V2 reconstructed score. Output: structured music and a Guitar Pro-compatible
file. Codex/multimodal AI reads visible notation, preserving uncertainty, then
uses independent exporters such as Guitar Pro MCP, alphaTab or MusicXML. Do not
invent hidden music or implement Guitar Pro binary formats manually. Not started.

## Future hosted product (documentation only)

The hosted runtime replaces Codex reasoning with a multimodal GPT/API agent
using controlled file/image/video tools:

upload -> AI agent -> tool calls -> generated score -> download

V3 adds structured transcription and export tool calls. The core remains an
agent workflow. No hosted framework, API integration, billing, auth, UI or
deployment is required now. Private prompts/workflows and evidence remain private.
