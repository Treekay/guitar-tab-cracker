# Local companion

Start from the repository root with Python 3.11+:

```powershell
python -m local_companion
# This workstation, where default python can be 3.9:
F:/anaconda/python.exe -m local_companion
```

No server dependency installation is needed. ffmpeg and ffprobe default to this
repository's existing temporary runtime; otherwise pass `--ffmpeg PATH --ffprobe PATH`.
`start.ps1` is a foreground shortcut; close its terminal/Ctrl+C to stop. Do not
interrupt an active acquisition if you need its result.

Only `127.0.0.1:8787` is bound. The installation token lives in ignored
`local-companion/.local/config.json`. Open `.local/pairing.html` locally to copy it
into the extension. Never paste the token into chat or commit that directory.
`python -m local_companion --init` only creates pairing files. The allowlisted
extension ID is derived from the checked-in public manifest key, not a secret.
Requests require `X-GTC-Token` and `X-GTC-Extension-ID`. A present Origin must match this extension; Chromium can omit it on privileged extension requests. Foreign web origins/preflights,
Host headers, missing tokens and arbitrary paths/commands are rejected. No HTTP
endpoint reveals the token. This protects against unrelated web origins, not
malware already running as your OS user.

Endpoints: authenticated `GET /health`, `POST /acquire`, and
`GET /runs/<id>/status`. `/acquire` returns 202 and a generated run ID; polling
reports success only after existing ffprobe/ffmpeg first-frame validation and
SHA-256. One job runs at a time. Caller-supplied output paths or commands are
not accepted. `/convert` is intentionally not implemented: source recognition
still requires the existing visual-agent workflow, not a fabricated CLI.

Supported: complete HTTP(S) video resources, including complete video-only
tracks, and unencrypted finite HLS VOD with embedded audio or video only.
HLS master variants prefer up to 1080p. The guarded Python worker downloads
each manifest/segment and rewrites a local manifest using only generated filenames;
ffmpeg remuxes it with network protocols disabled. This prevents manifest URLs
from bypassing SSRF checks. Live/low-latency/byte-range HLS, external audio
renditions, any HLS key declaration, DASH MPD and DRM are rejected explicitly.
A `.m4s` URL may be a complete track or a fragment; only a complete validated
video can pass. Missing audio does not prevent visual score reconstruction.

SSRF protections reuse the existing isolated acquisition socket guard. Each
redirect, manifest and segment must resolve/connect to public HTTP(S) port
80/443. No backend page scraping, cookies or Authorization headers. Minimal
context is source-page origin Referer, matching Origin and User-Agent. Signed
URLs travel in memory over local IPC, never command-line arguments/input files.
All query values and fragments are removed from persisted candidate/page URLs.
Raw network/ffmpeg stderr is discarded. Download limit is 2 GiB per candidate,
650-second network deadline, 1 MiB per manifest, 2000 segments and at most five
candidates. Not every session-authorized URL is replayable outside its browser.

Successful source metadata and timing are under `runs/extension-<id>/result/`.
`pipeline_handoff.local_video_path` is the validated input for existing V2.
Acquisition-only timing ends at validation; do not call it full conversion latency.
Failed jobs clean their run-owned partial media. Successful jobs retain source
video for downstream work; after QA or an abandoned test use existing
`tools/acquisition/acquire.py ignored RUN --cleanup --abandoned` (omit
`--abandoned` only after conversion QA/report). This never deletes user originals.

Test: `python -m unittest local_companion.test_companion`.
Implementation is in the importable `local_companion/` package; this hyphenated
directory holds local launch/setup files.
