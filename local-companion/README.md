# Local companion

Start from the repository root with Python 3.11+:

```powershell
python -m local_companion
# This workstation, where default python can be 3.9:
F:/anaconda/python.exe -m local_companion
```

One-time agent setup: install/use a Codex CLI supporting `codex exec`, and run
`codex login` followed by `codex login status` in your local terminal. The companion
uses that CLI's existing authentication; do not paste keys/tokens into chat.
If multiple installations exist, explicitly select the working one:

```powershell
F:/anaconda/python.exe -m local_companion --codex-path "C:/path/to/codex.cmd"
# Or use the startup shortcut with the same explicit installation:
./local-companion/start.ps1 -CodexPath "C:/path/to/codex.cmd"
```

Official npm `codex.cmd` resolves to its sibling package's JS entry using Node,
without shell interpolation. A direct codex.exe also works. No second agent
backend is installed. [Codex non-interactive execution](https://developers.openai.com/codex/noninteractive/)
is invoked with workspace-write sandbox and non-interactive approval policy;
no sandbox bypass is used. A runtime policy/auth failure stays a concrete failure.

The explicit `--codex-path` is saved in the ignored local installation config and
reused on subsequent starts. Login success alone does not establish model
compatibility: `agent_upgrade_required` means the selected CLI must be upgraded
or replaced with an installed version that supports the configured model.
For an explicitly inspected failure at V2 startup, `--resume-run extension-<id>`
retries that run's retained video only after checking its recorded SHA-256.
It retains the failed attempt in job status; elapsed time includes recovery.
This is a repair retry, not a clean one-click acceptance run.

Start companion → open/play video → click **转换为 Guitar Pro** → wait → download
GP/report in the popup. One click creates one run and automatically executes
the existing skill's V2/V3/GP/V4 workflow. No manual Codex prompt is needed.

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

Endpoints: authenticated `GET /health`, `POST /convert` (acquire + agent),
`POST /acquire` (legacy acquisition only), `GET /runs/<id>/status`,
`GET /runs/<id>/outputs`, `GET /runs/<id>/files/<allowed-name>`, and
`POST /runs/<id>/cancel`. One job runs at a time; a second returns busy.
Caller-supplied paths/commands are never accepted. Stage comes from existing
timing state, without made-up percentages. On agent exit the companion requires
nonempty outputs, completed timing, fresh report/V4 hashes, and a fresh GP import.
Review-required musical issues can complete; missing/failed evidence cannot.

Allowed downloads are score.gp, final_report.md/.json, timing.json,
verification_report.md and optional full_score.pdf, strictly within that run.
Each request needs the existing token headers; tokens never appear in URLs.
Logs stay local at working/logs/agent.stdout.log and agent.stderr.log, with known
pairing secrets, API-key patterns and URL query values redacted. They are not
download endpoints. Status persists in working/job_status.json.

Popup close does not cancel. Authenticated cancel stops the owned agent process
tree; during acquisition it waits for the existing bounded acquisition worker,
then prevents conversion. Ctrl+C of the companion requests cancellation. On
Windows a kill-on-close Job Object also contains descendants if the companion
crashes. Interrupted persisted runs become failed on restart; they are not
silently retried. Default agent deadline is four hours (`--agent-timeout` seconds).
Artifacts are retained on conversion failure; success uses existing post-QA cleanup.

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

Tests: `python -m unittest local_companion.test_companion local_companion.test_conversion`.
Implementation is in the importable `local_companion/` package; this hyphenated
directory holds local launch/setup files.
