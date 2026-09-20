# V1 Task 3 benchmark review (private)

Reviewed all nine full-resolution debug overlays against the visible screenshot
geometry. Source: `tests/fixtures/vision-benchmark/input/`; no source fixtures were
modified. Run: `runs/task3-benchmark/`. Detection uses full-image normalized ROI.
Coordinates below are ROI pixels. Annotation tolerance is 6 pixels (staff tests
use 2 pixels). Double/repeat bars count as a single logical boundary.

| Image | Staff y positions | Accepted count | Accepted x positions | Uncertain count | Cursor candidate x |
| --- | --- | ---: | --- | ---: | ---: |
| 1.png | 155,175,196,216,236,257 | 4 | 78,501,1004,1342 | 34 | 414 |
| 2.png | 137,157,178,198,218,239 | 3 | 322,809,1348 | 26 | 259 |
| 3.png | 149,169,190,210,230,251 | 4 | 278,501,1030,1516 | 29 | 401 |
| 4.png | 142,162,183,203,223,244 | 5 | 2,488,918,1200,1531 | 25 | 385 |
| 5.png | 135,155,176,196,216,237 | 4 | 190,520,683,1172 | 28 | 229 |
| 6.png | 139,159,180,200,220,241 | 4 | 30,494,983,1493 | 37 | 352 |
| 7.png | 139,159,180,200,220,241 | 4 | 460,865,1329,1492 | 38 | 322 |
| 8.png | 137,157,178,198,218,239 | 4 | 299,462,865,1368 | 32 | 208 |
| 9.png | 139,159,180,200,220,241 | 4 | 339,678,1210,1529 | 27 | 290 |

Result: 9/9 staff groups, 36 accepted logical boundaries, 276 uncertain vertical
candidates retained with feature values/reasons. No obvious accepted false
positives or missed visible boundaries were found in the final manual review.
This is a small, related screenshot set, not a general accuracy estimate.

## Visual findings

- All nine playback cursors remain uncertain rather than accepted. In image 2,
  the candidate center shifts from the visible cursor near x=256 to x=259 because
  adjacent vertical evidence is clustered; this is recorded, not exact cursor localization.
- Image 1 x=78, image 2 x=809, and image 9 x=1529 are double/repeat/end boundaries.
- Image 4 x=2 and x=1531 have visible near-edge line evidence. Other image edges
  are not automatically treated as boundaries.
- Early trials falsely accepted near-full-height decorative/arrow marks. Endpoint
  support and outside-staff extension regressions now keep them uncertain:
  especially image 3 x=536/764/1066/1331 and image 6 x=64, image 7 x=899.
- Staff-intersecting rhythmic stems and digit-like marks remain in the uncertain
  evidence instead of accepted barlines. No note/fret meanings are inferred.

## All retained uncertain x positions

These are geometrically suspicious candidates, not claimed missing barlines.
Very short marks below the candidate coverage floor are not emitted. Individual
confidence/features/reasons are in the generated manifest, and all candidates
are drawn in orange in `debug/0001_detection.png` through `0009_detection.png`.

- 1.png: 8,47,160,206,230,250,322,353,374,395,414,578,624,677,696,745,777,810,842,875,907,954,1082,1119,1139,1160,1209,1247,1285,1377,1436,1484,1519,1558
- 2.png: 61,98,118,139,189,226,259,356,415,463,497,532,566,600,633,668,849,908,989,1038,1071,1105,1139,1173,1207,1241
- 3.png: 2,36,70,104,137,171,401,536,556,596,635,667,700,764,784,840,879,1066,1086,1121,1155,1190,1225,1274,1306,1331,1352,1412,1462
- 4.png: 38,59,93,128,163,197,246,303,324,385,434,523,613,644,676,708,740,816,849,951,984,1017,1050,1445,1465
- 5.png: 6,39,229,434,455,562,760,810,859,908,958,978,1018,1047,1068,1118,1250,1270,1314,1337,1357,1402,1433,1452,1473,1495,1527,1557
- 6.png: 64,85,144,191,224,258,293,312,332,352,373,571,591,639,665,686,732,782,802,837,863,884,931,1060,1081,1125,1148,1167,1213,1244,1264,1284,1306,1337,1369,1398,1443
- 7.png: 28,48,92,115,135,180,211,230,251,272,305,322,336,365,411,538,558,596,615,636,671,690,711,746,785,822,899,920,979,1026,1059,1093,1128,1146,1167,1188,1208,1371
- 8.png: 29,64,98,117,138,158,178,208,341,539,583,605,625,694,725,778,798,942,988,1040,1060,1108,1141,1174,1206,1239,1271,1317,1445,1483,1502,1524
- 9.png: 11,31,80,112,145,176,210,242,290,416,454,473,494,544,582,619,712,770,852,899,933,967,1002,1035,1069,1103,1381

## Scope and limitations

No measure cropping, duplicate matching, ordering, layout, video, AI/OMR, or
Guitar Pro work. Staff and barline confidence values are explainable heuristic
scores, not calibrated probabilities. Tilt, perspective, low contrast,
occlusion, cropped staff context, or a UI line geometrically indistinguishable
from a barline need additional review. Normalized artifacts and original copies
are unchanged by detection or reruns; `measure_candidates` remains empty.
