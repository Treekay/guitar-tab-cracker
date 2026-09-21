# Product hardening acceptance

Implementation and regression complete; score delivery status: **REVIEW_REQUIRED**.

## Scope

Real local-video regression, not a fresh blind transcription: freshly extracted 58 frames and exported 57 source crops, assembled canonical data, exported/re-imported/rendered GP, reviewed all 14 source rows and selected generated systems. Six representative full frames and all three actual PDF pages were viewed. Existing accepted timestamp/crop/transcription decisions and detailed V4 observations were reused explicitly after bound artifact hashes matched. No music was changed.

Input: local Yuki no Hana video, 209.955 seconds (container), 986 × 720. User original preserved.

57 measures, 610 events, 794 note records. Canonical validation and GP round-trip pass. 57 verified groups, 0 corrections, 1 user-review item, 18 known limitations, 0 unexpected mismatches. The m20 e8 string4 grace-slide remains unresolved; other known limitations include arpeggiation, staccato and engraving differences. These are item counts, not accuracy percentages.

## Measured timing

- acquisition: 0.159585 seconds
- v2: 105.501677 seconds
- v3: 18.896539 seconds
- guitar_pro: 4.899151 seconds
- v4: 367.456655 seconds
- Total: 498.845535 seconds

Top three: v4 (367.457 s), v2 (105.502 s), v3 (18.897 s).

Values above are generated from measured timing.json. Durations include agent/tool orchestration, pauses and review; no historical transcription latency was backfilled. Reused transcription and unexecuted correction steps remain null. Final-report serialization follows the end-of-QA timer finish.

## Real backend URL tests

### direct

- URL: https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4
- Provider: direct-http; status: success; reason: none
- Download seconds: 0.4583485000039218; acquisition wall seconds: 1.174535599995579
- Size: 1128375; metadata: {}
- Video: 960 × 540, 5.055 seconds, 30000/1001 fps, 1,128,375 bytes.
- Detail: Validated, hashed, and decoded.
- Cleanup: removed

### page

- URL: https://vimeo.com/76979871
- Provider: yt-dlp; status: failed; reason: authentication_required
- Download seconds: None; acquisition wall seconds: 2.4019826000003377
- Size: None; metadata: null
- Detail: ERROR: [vimeo] 76979871: The web client only works when logged-in. Use --cookies, --cookies-from-browser, --username and --password, --netrc-cmd, or --netrc (vimeo) to provide account credentials. See  https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp  for how to manually pass cookies
- Cleanup: removed

### youtube

- URL: https://www.youtube.com/watch?v=BaW_jenozKc
- Provider: yt-dlp; status: failed; reason: download_failed
- Download seconds: None; acquisition wall seconds: 2.2623186000055284
- Size: None; metadata: null
- Detail: ERROR: [youtube] BaW_jenozKc: This video is unavailable
- Cleanup: removed

Direct-media V2 acceptance: existing extract_frames.py probed and decoded a frame at 1 second; the frame was opened. This flower video tests transport/decoding only, not tablature reconstruction. Run-owned download was deleted after the acquisition test; source metadata and frame remain.

The Vimeo diagnostic was initially classified download_failed. The classifier was corrected to recognize logged-in; its retained diagnostic was reclassified offline with original_reason preserved, without another request. YouTube returned video unavailable. No successful public-page extraction is claimed. Both pages were tested through yt-dlp; authentication/DRM bypass and browser/manual download services were not used. URL test total session durations include intervening work; the acquisition spans above are the relevant measured URL latencies.

## Regression checks

77 tests passed: acquisition 11, timing/report 5, alphaTab adapter 26, canonical validator 16, V4 12, frame extraction 4, visual export 1, source-measure export 2. ReportLab suites used the bundled Python runtime; the default Python lacks ReportLab. Tests cover implementation mechanics, not source transcription accuracy.

## Local outputs

- [Final report](../runs/hardening-yuki-timed/result/final_report.md)
- [Timing](../runs/hardening-yuki-timed/result/timing.json)
- [Editable GP](../runs/hardening-yuki-timed/result/v3/export/score.gp)
- [Source PDF](../runs/hardening-yuki-timed/result/full_score.pdf)
- [Machine-readable acceptance snapshot](HARDENING_ACCEPTANCE.json)

Run artifacts are private/ignored. The committed snapshot preserves measured values and provenance, not raw media.
