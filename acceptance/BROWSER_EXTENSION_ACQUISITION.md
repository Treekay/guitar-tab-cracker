# Browser-extension acquisition MVP acceptance

**Implementation and secondary HTML5 integration validated. Primary Bilibili browser-session acceptance is pending.** Do not call the entire acceptance gate passed.

## Architecture and implementation

Chrome/Edge Manifest V3 extension → authenticated localhost companion → validated local video path → unchanged existing pipeline. The importable Python implementation is local_companion/; local-companion/ holds launch instructions and ignored installation config. No cloud/accounts, website-specific selectors, cookie store access, credential export, or anonymous scraping workarounds were added.

Direct HTTP media and finite unencrypted HLS VOD are implemented. HLS fetches every URI through the existing public-network guard and gives ffmpeg only a rewritten local manifest. DASH MPD, encrypted/keyed HLS, external audio renditions, advanced/live HLS and DRM are explicitly unsupported. Complete HTTP video tracks can pass independently of filename; fragments/audio-only resources cannot pass video validation.

The service listens only on 127.0.0.1:8787. Shared token plus extension ID are mandatory. Present Origin and Host must match; foreign web preflights are rejected. Real Chromium testing showed privileged extension fetch omits Origin, so absent Origin is supported only alongside both token and matching extension ID. No token is disclosed by a service endpoint.

## Real Chromium / HTML5 secondary test

The checked-in manifest loaded as MV3 in a separate test Chromium profile; service worker ID matched npfhoaohhbggabdgcigfgncilfgpkifo. A controlled HTML5 page at an intercepted example.org fixture URL loaded the real public MDN flower video. The exact content.js was evaluated against that browser DOM, and the real extension transport module sent its candidate through authenticated localhost HTTP. This is not an automated native-toolbar click or a claim that optional browser permission prompts were exercised. Popup routing/current-page handoff is additionally covered by a deterministic extension test.

Media: https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4
Validated size 1128375 bytes; duration 5.055 s; 960 × 540; SHA-256 `0cd83d944a6ca7822b4a8306cecc60a36e859b041f6702c6a1ad9ead78924451`.
Final integration acquisition wall time: 0.854868 s; download: 0.534718 s.

Existing ffprobe + first-frame ffmpeg validation passed. Existing V2 extract_frames.py decoded t=1 second from the first integration run; the frame was opened and showed the flower video. The final integration run produced the same media SHA-256. Both tiny run-owned test videos were removed after validation; source metadata, timing and first-run frame remain. Isolated browser test profiles were cleaned. No user browser profile was used.

## HLS mechanics

A deterministic 2-second color-video fixture produced two real HLS segments. The HLS planner rewrote local filenames, actual ffmpeg remuxed with network protocols disabled, and existing validation confirmed the 160 × 90 video. This verifies remux mechanics, not a real public HLS website or visual transcription. Private segment URLs, encrypted manifests and unsupported variants are rejected by tests.

## Primary Bilibili test

Target: https://www.bilibili.com/video/BV16BJL6cE6o

The user has been given a concrete unpacked extension folder, running companion and private local pairing page. They must open/play the authorized video normally, click the extension and send discovered candidates. No such payload has arrived yet. Metadata/download/media validation/frame review for this browser-session path therefore remain **unverified**. Earlier anonymous and Chrome cookie failures are separate evidence and do not substitute for this test. No Bilibili browser page was operated by the agent.

## Tests and reproducibility

47 tests passed: companion/security/HLS 12, extension discovery/popup boundary 5, existing acquisition 25, timing/report 5. Tests use synthetic secrets only. `git diff --check` passes.

Optional Chromium integration runner: `browser-extension/acceptance.cjs`. Supply `GTC_PLAYWRIGHT_MODULE` if Playwright is not installed locally and `GTC_CHROMIUM_EXECUTABLE` for an installed extension-capable Chromium; start the companion first. The runner uses an isolated profile, a controlled HTML5 fixture and real public media. It does not operate user video sites.

[Extension setup](../browser-extension/README.md) · [Companion setup](../local-companion/README.md) · [Safe measured evidence](BROWSER_EXTENSION_ACQUISITION.json).

Source/timing files retain redacted page/candidate URLs, source category, status, validated path and hash. Candidate query parameters and request context are not logged. Pairing files and run media are ignored by Git. Successful user acquisitions remain available for downstream V2; conversion is not automatically started by this acquisition MVP.
