# Browser-session acquisition acceptance

Implementation available; **Bilibili acquisition is not resolved**. The user identified Chrome as the browser logged into Bilibili. Native Chrome extraction returned `browser_profile_locked`; authenticated metadata/download validation could not proceed. No full V2→GP run was started.

## Implementation

- Explicit `--cookies-from-browser edge|chrome|firefox` directly tests an authorized session.
- `--auto-browser-cookies` first tries anonymous acquisition, then configured browsers only after authentication/session/access-challenge errors.
- `GTC_BROWSER_COOKIE_SOURCES` configures order; no option means no cookie access.
- yt-dlp native browser integration, in-memory site-scoped cookies and domain-aware streaming; no manual cookie database parsing.
- SSRF, redirects, media limits, ffprobe/first-frame validation and SHA-256 remain required.
- Raw worker output and exception text are not logged; safe classifications and timings are retained. Native temporary cookie copies are outside result/ and cleaned by the parent. No cookie export is enabled.

## Real Bilibili tests

URL: https://www.bilibili.com/video/BV16BJL6cE6o

| Run | Mode/browser | Result | Acquisition seconds |
|---|---|---|---|
| bilibili-BV16BJL6cE6o | anonymous/none | network_error | 47.947891 |
| cookie-bilibili-anonymous | anonymous/none | unsupported_url | 23.600572 |
| cookie-bilibili-anonymous-stage | anonymous/none | unsupported_url | 21.534709 |
| cookie-bilibili-edge | browser_cookies/edge | cookies_unavailable | 1.590508 |
| cookie-bilibili-chrome | browser_cookies/chrome | browser_profile_locked | 1.488066 |

Original anonymous attempt: metadata read timed out. This pass repeated the anonymous test; it returned unsupported_url during metadata extraction. The stage-instrumented follow-up confirms the failure precedes format selection. Neither result is proof that cookies would fix the site. Auto mode therefore does not retry browsers for these unrelated failure classifications; explicit mode was used for the requested B comparison.

Edge was a preliminary default test before the user identified Chrome; it returned cookies_unavailable and did not establish a logged-in session. Chrome is the user-confirmed browser; its cookie database was locked or inaccessible. The user has been asked to save work and fully exit Chrome before a single retry. No browser was closed automatically and no decryption/access bypass was attempted.

For the Bilibili session test, downloaded size/duration/resolution/hash are unavailable; no media was produced and V2 acceptance is **not reached**. Parent-owned temporary cookie material was cleaned; no downloaded media requires cleanup. This is honest failure evidence, not a successful authenticated-download claim.

## Regressions

Direct URL: https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4

Anonymous direct HTTP success with auto mode enabled: 1128375 bytes, 5.055 seconds, 960 × 540; download 0.427841 s; acquisition 0.998024 s.
SHA-256: `0cd83d944a6ca7822b4a8306cecc60a36e859b041f6702c6a1ad9ead78924451`.
ffprobe and ffmpeg first-frame validation passed. Existing V2 extract_frames.py decoded t=1 second; the image was opened. Run-owned remote video was removed after testing; metadata/frame retained. No browser-cookie attempt ran.

Local original Yuki no Hana also validated with auto mode enabled: authentication_mode=null, no browser access, original SHA-256 unchanged. No downstream reconstruction changes.

25 acquisition tests and 5 timing/report regression tests pass. They cover anonymous/direct/local success, explicit and automatic session modes, ordered sources, missing cookies, non-session failures, cookie scope/redirect behavior, secret-free output, safe argv, temp cleanup, and existing SSRF checks. All cookie test values are synthetic.

## Local limitations and next step

Chrome being logged in does not guarantee yt-dlp can read its cookie database. Close Chrome yourself and retry, or provide a local video. Native encryption/OS restrictions may still prevent access; no bypass is implemented. Browser-session acquisition is for local desktop/development use, not arbitrary remote-server access to user browser profiles.

[Measured safe snapshot](BROWSER_COOKIE_ACQUISITION.json). Raw media and run artifacts remain ignored/private.
