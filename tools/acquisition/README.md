# Backend acquisition

Python 3.11+, ffmpeg and ffprobe required. Install `python -m pip install -r tools/acquisition/requirements.txt` (yt-dlp 2026.8.19). The [upstream project](https://github.com/yt-dlp/yt-dlp) supplies public-page extractors.

```powershell
python tools/acquisition/acquire.py "SOURCE_PATH_OR_URL" runs/NEW_RUN --ffmpeg PATH_TO_FFMPEG --ffprobe PATH_TO_FFPROBE
```

Use only a successful `result/source/source.json` local_path for V2. Local originals are validated in place. Remote media streams into a unique `working/acquisition/` directory, with 2 GiB default limit (`--max-bytes`), 20-second socket timeout and 650-second worker deadline. ffprobe checks duration, dimensions and video stream; ffmpeg decodes the first frame, then SHA-256 is recorded. This is not a full-file decode test.

Provider order: local, direct HTTP (HTML dispatches to yt-dlp), public-page extraction, actionable structured failure. yt-dlp selects a progressive HTTP video stream, preferring best available quality up to 1080p; if only larger sources exist it chooses the smallest available height. No forced resizing. HLS/DASH-only sources, live streams, playlists, cookies/login, DRM, JS challenge runtimes and external downloader subprocesses are not supported. An initial HTTP failure can stop discovery before extraction. Supported extractor names do not guarantee current site availability.

HTTP(S) ports 80/443 only. Reject credentials, internal hostnames and nonpublic DNS results; redirects are revalidated. An isolated Python worker audits DNS/socket connections to reject private rebinding targets and blocks subprocess escape. Proxies and yt-dlp plugins are disabled. This is a Python networking guard, not an OS network sandbox.

Failures retain reason codes and downloader diagnostics, without repeated authentication experiments. Ask for a local file. Do not use browser navigation or manual download websites.

After final QA/report: `python tools/acquisition/acquire.py ignored runs/NEW_RUN --cleanup`. Explicitly abandoned acquisition tests may add `--abandoned`. Cleanup deletes only recorded individual remote files within that run; it preserves metadata and local originals. Regenerate final_report after cleanup so metadata agrees.

Tests: `python -m unittest discover -s tools/acquisition -p 'test_*.py'`. Real provider results are in [hardening acceptance](../../acceptance/HARDENING_ACCEPTANCE.md).
