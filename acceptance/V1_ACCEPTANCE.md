# V1 final acceptance

**PASS — V1 COMPLETE — images → reconstructed printable score.**

Acceptance date: 2026-09-20. This verdict applies to the existing benchmark
under the requested acceptance criteria. V1 has only been validated on the
existing benchmark; general reliability on unseen sets is not established.

| Test | Input | Source images | Logical measures reconstructed | A4 pages | Result |
| --- | --- | ---: | ---: | ---: | --- |
| Existing benchmark | `benchmark/input/` | 10 | 26 complete, ordered 1-26 | 2 | PASS after visual corrections |
| Unseen set | No independent screenshot set found in the repository | 0 | — | — | NOT RUN |

The repository image inventory was checked initially and again after export.
Historical expected/result images and old run derivatives are not independent
unseen inputs. No unseen set was invented; `v1-unseen/` was not created.

## First-pass failures

| Classification | Finding | Fix | Final status |
| --- | --- | --- | --- |
| Execution/tool failure | Missing ReportLab; initial download blocked by sandbox | Approved dependency installation; existing compositor completed | Export complete |
| Incorrect crop | Closing barline missing at nine reflowed row ends | Explicit original-source endcaps through existing helper support | Corrected and reinspected |
| Bad source-candidate selection | Measure 3 retained avoidable playback-track interference | Combine cleaner partial source with cursor-free complementary strips | Corrected; unavoidable residual documented |

A later external workspace change removed the virtual environment and caused
verification-command failures. Verification completed using system Python. An
external commit also captured part of the acceptance work before the verdict;
this agent did not make that commit and did not rewrite it. The acceptance
commit is made only after the final result is established.

No missed measure, duplicate measure, incorrect global order, unreadable scaling
or bad page break was found. No product architecture, helper or skill change was
needed. The existing instructions already cover the two corrected visual
decision errors, so the conditional skill-rewrite/from-scratch-repeat rule was
not triggered. No V2 work was started.

## Final evidence and remaining items

- All 10 original images were opened initially and again after export. Prior
  recognition outputs and prepared answers were not read or used.
- All 26 logical measures are present exactly once. Partial views are accounted
  for by complete candidates or visually aligned complementary source pieces.
- Both generated page PNGs and both rendered pages of the actual PDF were
  opened and visually checked after correction. The full-score PNG was opened
  in ten readable sections covering its entire width.
- Opening annotations, technique markings, ending bracket, repeat boundaries,
  terminal bar and cross-boundary curves were retained. No important notation
  was newly clipped. The only page break is between measures 14 and 15.
- Both pages use the same scale. The PDF has actual A4 dimensions, and extracted
  PDF page images are pixel-identical to their exported PNG counterparts.
- **Unresolved source ambiguity:** overlays obscure some original pixels in
  measures 1-3. No fully clean alternate exists for those residual regions.
  They remain visible and documented; hidden pixels were not invented.
- No unresolved measure identity, global order or visible-coverage gaps remain.
- No user-provided ROI, coordinates, measure boundaries, ordering, duplicate
  relationships or page breaks were required. No musical data was transcribed.
- Unseen-set validation and physical printer testing remain unperformed.

See [reconstruction and QA report](v1-existing/report.md),
[printable PDF](v1-existing/full_score.pdf),
[page 1](v1-existing/page_001.png), [page 2](v1-existing/page_002.png),
[full score](v1-existing/full_score.png), and
[mechanical verification](v1-existing/inspection/verification.json).

**Final PASS is limited to this acceptance set, with the disclosed source
limitations. It does not claim successful reconstruction of unseen material.**
