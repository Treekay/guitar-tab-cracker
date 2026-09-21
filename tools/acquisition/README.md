# Backend acquisition

Python 3.11+, ffmpeg and ffprobe required. Install `python -m pip install -r tools/acquisition/requirements.txt` (yt-dlp 2026.8.19). The [upstream project](https://github.com/yt-dlp/yt-dlp) supplies public-page extractors.

```powershell
python tools/acquisition/acquire.py "SOURCE_PATH_OR_URL" runs/NEW_RUN --ffmpeg PATH_TO_FFMPEG --ffprobe PATH_TO_FFPROBE
```

Use only a successful `result/source/source.json` local_path for V2. Local originals are validated in place. Remote media streams into a unique `working/acquisition/` directory, with 2 GiB default limit (`--max-bytes`), 20-second socket timeout and 650-second worker deadline. ffprobe checks duration, dimensions and video stream; ffmpeg decodes the first frame, then SHA-256 is recorded. This is not a full-file decode test.

Provider order: local, direct HTTP (HTML dispatches to yt-dlp), anonymous public-page extraction, authorized browser-session fallback when enabled, actionable structured failure. yt-dlp selects a progressive HTTP video stream, preferring best available quality up to 1080p; if only larger sources exist it chooses the smallest available height. No forced resizing. HLS/DASH-only sources, live streams, playlists, DRM, JS challenge runtimes and external downloader subprocesses are not supported. An initial HTTP failure can stop discovery before extraction. Supported extractor names do not guarantee current site availability.

HTTP(S) ports 80/443 only. Reject credentials, internal hostnames and nonpublic DNS results; redirects are revalidated. An isolated Python worker audits DNS/socket connections to reject private rebinding targets and blocks subprocess escape. Proxies and yt-dlp plugins are disabled. This is a Python networking guard, not an OS network sandbox.

Failures retain reason codes, safe diagnostic messages and per-attempt timing. Raw exceptions, request headers and signed media URLs are not persisted. Ask for a local file. Do not use browser navigation or manual download websites.

After final QA/report: `python tools/acquisition/acquire.py ignored runs/NEW_RUN --cleanup`. Explicitly abandoned acquisition tests may add `--abandoned`. Cleanup deletes only recorded individual remote files within that run; it preserves metadata and local originals. Regenerate final_report after cleanup so metadata agrees.

Tests: `python -m unittest discover -s tools/acquisition -p 'test_*.py'`. Real provider results are in [hardening acceptance](../../acceptance/HARDENING_ACCEPTANCE.md).

## Optional local browser session

```powershell
python tools/acquisition/acquire.py URL runs/NEW_RUN --cookies-from-browser edge
python tools/acquisition/acquire.py URL runs/NEW_RUN --auto-browser-cookies
$env:GTC_BROWSER_COOKIE_SOURCES = 'edge,chrome,firefox'
```

Use Python 3.11+ explicitly if Windows `python` selects an older installation. `--cookies-from-browser` supports edge, chrome and firefox and directly tests that authorized session. Automatic mode first tries direct media and anonymous yt-dlp. It only reads browsers after authentication/session/access-challenge failures; timeout, invalid URL, rate-limit and DRM failures do not trigger cookie retries. Browser order is configurable, deduplicated, and defaults to Edge, Chrome, Firefox. No flags means no browser-cookie access. Local files remain independent of cookie options. No browser automation or cookie-file export is used; arbitrary profile/database paths and an explicit cookie-file option are not supported in this pass.

This uses [yt-dlp native browser-cookie integration](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp). The in-memory jar is restricted to cookie domains matching the supplied site before network extraction. Standard cookie domain/path/secure rules also apply during CDN streaming and redirects; unrelated browser sessions are discarded. Never send a copied Cookie header across redirects. SSRF checks and ffprobe/ffmpeg media validation are unchanged. Browser encryption or profile locks may prevent extraction; do not kill browsers or attempt encryption bypass. Close the browser yourself if requested, choose another authorized browser, or supply a local video.

`source.json` records authentication_mode (`anonymous`, `browser_cookies`, or null for local), browser_source, safe attempt status/reason/time, and normal media provenance. Cookie values are never logged or saved. Native temporary database copies use a parent-owned OS temp directory outside result/; normal exits and worker timeouts clean it. A force-killed parent or OS crash cannot guarantee cleanup; no persistent cookie cache/export is enabled. The worker's stdout/stderr are discarded; downloader.log contains only structured safe diagnostics. Original browser databases are never altered. Never commit cookie files.

This is a local desktop/development capability, not a remote-server browser-profile integration. Future options could include a browser extension, desktop helper, local companion or explicit session handoff; none is implemented. Test evidence: [browser-cookie acquisition](../../acceptance/BROWSER_COOKIE_ACQUISITION.md).
