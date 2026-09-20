# V2 raw-video acceptance

PASS for one local horizontally scrolling guitar-tab video. V1 COMPLETE;
V2 COMPLETE; V3 NEXT (not started). No claim of universal video/URL reliability.

The user supplied only `雪之华 - 冈崎伦典 动态吉他谱.mp4` (209.95 s,
986 × 720, approximately 30 fps). No prepared screenshots, timestamps, crop
coordinates, duplicate labels or ordering were supplied.

Codex inspected 69 self-extracted frames: 6 survey, 37 adaptive, 13 additional
coverage/clean-source recovery and 13 independent second-pass inspections.
Printed identities 1–57, overlap, chronology, the opening annotation and the
terminal bar establish coverage; repeated passages remain separate occurrences.
Second-pass review improved source selections for measures 6, 18 and 48.

Primary output: [57 ordered measure images](../runs/v2-yukinohana/result/measures/)
and [metadata](../runs/v2-yukinohana/result/measures.json). Each image has one
logical core; selected boundary context preserves crossing markings and is
explicitly distinguished by core_bbox_in_output. Composition uses cores only.
Original RGB frames remain available; a visually checked max-channel grayscale
transform reduces adjacent yellow edges without reconstructing hidden notation.

Full score, 3 A4 landscape page PNGs and PDF passed visual review. All 57 crops
were opened through native-size contact sheets; the actual long score was
inspected in contiguous readable sections. Every page PNG and actual PDF render
was opened. PDF pages measure 297 × 210 mm; embedded pixel data equals the PNGs.
No known omitted/duplicated occurrences, unresolved partials or order errors.
Minor compression blur, pale seams and context fragments remain source artifacts.

- [Result/report](../runs/v2-yukinohana/result/report.md)
- [Coverage and inspected timestamps](../runs/v2-yukinohana/working/coverage.json)
- [Explicit decisions](../runs/v2-yukinohana/working/decisions.json)
- [Mechanical verification](../runs/v2-yukinohana/result/inspection/verification.json)

The local original's SHA-256 remains unchanged. No video copy was downloaded or
created, so download cleanup is not applicable. Source media is not committed.
Other video styles and URL/Xiazaitool acquisition remain unvalidated. V3 was not
started. Visual decisions remain agent-authored; no CV detector, OMR, matching,
scene-change detector or automatic musical layout was added.
