# V1 existing-set reconstruction

**Final result: PASS on the supplied benchmark.** Ten original screenshots yield
26 complete logical measures in the printed order 1-26, a continuous full-score
PNG, and two A4 pages in PNG and PDF. No user segmentation, ordering, duplicate,
source-selection or layout guidance was requested. No musical transcription was
performed. This establishes coverage of the supplied score, not unseen music.

## Independence and input inventory

Only `benchmark/input/` images were used as visual evidence. Historical
`benchmark/decisions.json`, `benchmark/REPORT.md`, `benchmark/expected/`, prior
result images and old run outputs were not opened or used. Initial file discovery
listed historical filenames but did not read their contents. The generic
`tools/compose.py` was read and used unchanged. README and product documents were
read only after the independent reconstruction and visual inspection.

| Source | Pixels | Visible sequence and edge accounting |
| --- | --- | --- |
| 1.png | 1563 x 345 | 1-3 complete; 4 right partial, resolved by 2.png |
| 2.png | 1560 x 321 | 3 left partial; 4-5 complete; 6 right partial |
| 3.png | 1534 x 320 | 5 left partial; 6-8 complete; beginning boundary of 9 |
| 4.png | 1535 x 327 | 8 begins at the image edge; 9-11; beginning boundary of 12 |
| 5.png | 1567 x 313 | 10 left partial; 11-13 complete; 14 right partial |
| 6.png | 1530 x 410 | 13 left partial; 14-16 complete; beginning boundary of 17 |
| 7.png | 1560 x 319 | 16-18 complete; 19 right partial |
| 8.png | 1547 x 316 | 18 left partial; 19-21 complete; 22 right partial |
| 9.png | 1560 x 323 | 20 left partial; 21-23 complete; 24 right partial |
| 10.png | 1551 x 318 | 23 left partial; 24-26 complete, including final double bar |

Source SHA-256 values are in `execution-checks.json`. Original files were not
edited. Crops, candidates and explicit run decisions are retained here.

## Visual identity, ordering and source ledger

Printed measure labels establish the sequence. Repeated graphic shapes and the
same neighboring boundaries reconcile overlaps. Similar later passages remain
distinct logical measures; they were never substituted for earlier measures.
All edge fragments link to the corresponding complete measure below. There are
no remaining partial-only measures or numbering gaps.

| Measure | Selected source | Other supporting view / selection evidence |
| --- | --- | --- |
| 1 | 1 | Opening annotations and repeat retained; no alternative |
| 2 | 1 | Complete between labeled boundaries; no alternative |
| 3 | 1 + 2 | Same graphic sequence; cleaner partial from 2, cursor region from 1 |
| 4 | 2 | Partial in 1; complete overhead ending bracket retained in 2 |
| 5 | 2 | Left partial in 3 confirms overlap |
| 6 | 3 + 2 | Complete in 3; clean narrow strip from 2 replaces cursor |
| 7 | 3 | Complete; upper technique labels and curves retained |
| 8 | 3 | Edge view in 4 contains cursor; 3 is clean |
| 9 | 4 | Beginning boundary in 3; complete clean view in 4 |
| 10 | 4 | Left partial in 5 confirms overlap |
| 11 | 5 + 4 | Clean left strip from 4; rest from 5 to preserve alignment into 12 |
| 12 | 5 | Beginning boundary in 4; complete continuation in 5 |
| 13 | 5 | Left partial in 6 confirms overlap |
| 14 | 6 + 5 | Complete in 6; clean strip from partial 5 replaces cursor |
| 15 | 6 | Complete between neighboring labeled boundaries |
| 16 | 6 | Complete alternate in 7 has cursor; 6 is clean |
| 17 | 7 | Beginning boundary in 6; clean complete view in 7 |
| 18 | 7 | Left partial in 8 has cursor; 7 is clean |
| 19 | 8 | Right partial in 7 confirms overlap |
| 20 | 8 | Left partial in 9 has cursor; 8 is clean |
| 21 | 8 | Complete alternate in 9; retain original join with 20 |
| 22 | 9 | Right partial in 8 confirms overlap |
| 23 | 9 | Left partial in 10 has cursor; 9 is clean |
| 24 | 10 | Right partial in 9 confirms overlap |
| 25 | 10 | Complete; upper and lower technique curves retained |
| 26 | 10 | Complete terminal measure; final marking and double bar retained |

Complementary pieces use explicit translations checked against staff bands,
barlines and graphic positions. No matching algorithm, OCR, pixel inpainting,
notation synthesis or later-passage substitution was used. Background seams
remain visible because the original source appearance is retained.

## Layout and QA iterations

Page 1 rows: **1-3 / 4-6 / 7-8 / 9-12 / 13-14**.
Page 2 rows: **15-16 / 17-18 / 19-21 / 22-23 / 24-26**.

The page break is between 14 and 15. Tied graphic continuations 11-12 and 20-21
stay together in their original source alignment. All rows use uniform 1.55x
isotropic scaling; the roughly 102-pixel staff height becomes about 13.4 mm on
A4. Page images are 2480 x 3508 pixels at 300 dpi. The PDF uses actual
595.27559 x 841.88976-point A4 pages. Source colors are retained.

First-pass failures and corrections:

1. **Execution/tool failure:** ReportLab was missing in the initial tool
   environment. The sandbox blocked the download; an approved install enabled
   the existing compositor. Later the virtual environment disappeared during
   an external workspace change. The independent verification script completed
   with the available system Python. The generated exports were unaffected.
2. **Incorrect crop:** the first A4 render omitted closing barlines at nine
   nonterminal row ends. Those boundaries belong to the next tile in the
   continuous strip, but must also close the preceding reflowed row. Added
   explicitly selected original-source endcaps using the helper's existing
   support. No logical measure was added or duplicated.
3. **Bad source-candidate selection:** measure 3 initially used only the complete
   source 1, retaining unnecessary playback-track interference. Used the cleaner
   source 2 partial except its cursor-bearing strip, where source 1 remains.

The first page renders and decisions are saved as `inspection/first-pass-*`.
The corrected result was regenerated and visually inspected again. These were
execution-environment and agent-decision problems, not missing skill guidance:
the skill already requires boundary context, cleaner alternatives, complementary
views and iterative visual QA. No skill or helper modification was necessary.

Final visual inspection covered every original source again, both final page
PNGs, both Poppler-rendered PDF pages (`inspection/pdf-final-*.png`), and all ten
readable sections covering the entire full-score strip (`full-section-*.png`).
Enlarged source details and composite measure tiles were also inspected.

| Mandatory check | Final finding |
| --- | --- |
| Every visible logical measure represented | All 26, including edge-fragment identities |
| No duplicate logical measures | One occurrence per printed measure, 1-26 |
| Global order | Consecutive labels and neighboring visual overlap agree |
| Crops preserve notation | No additional important notation clipping found |
| Technique context | Upper labels, opening instructions, ending bracket, curves and lower marks retained |
| Cleaner source selection | Cleaner full or partial sources used; residual source limitations below |
| Page breaks | Between complete measures; tied continuations kept together |
| Readability | Both A4 PNGs and PDF renders readable at the chosen scale |
| Consistent scale | Same 1.55x factor and aligned staff bands throughout |
| PDF correspondence | Both embedded PDF images pixel-identical to the final page PNGs |

`inspection/verification.json` records supplementary mechanical checks, not a
substitute for visual judgment. `inspection/pdfinfo.txt` records PDF geometry.

## Remaining source limitations

- **Unresolved source ambiguity (occluded pixels only):** measure 1 has a cursor
  and playback track in its sole source. Measure 2 also has the playback track.
  Measure 3 retains narrow source-1 regions where source 2 is absent or has its
  own cursor. No entirely clean source exists for those regions. Visible marks
  are retained; pixels behind overlays cannot be authenticated or recovered.
- The opening TAB lettering touches the original image edge. No missing
  off-image pixels were invented. The opening instructions are preserved.
- No unresolved measure identity, ordering or visible-coverage gap remains.
- This is screen/PDF visual QA, not a physical printer proof.

## Reproduction and outputs

`reconstruct.py` stores this run's independently authored decisions and calls
the unchanged generic compositor. With Pillow and ReportLab available, run
`python acceptance/v1-existing/reconstruct.py`. It regenerates machine-local
source paths from the repository location. Then run
`python acceptance/v1-existing/verify.py` with Poppler's `pdfimages` and `pdfinfo`
available. Render the actual PDF with `pdftoppm` and repeat visual QA after any
decision change. These decisions are evidence for this input only, never a
template for a new song.

Final deliverables: `full_score.png`, `page_001.png`, `page_002.png`,
`full_score.pdf`, `measures/`, `inspection/`, and this report.
