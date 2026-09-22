# Guitar Tab Cracker — local Chromium extension

1. Start the [local companion](../local-companion/README.md).
2. In Chrome `chrome://extensions` or Edge `edge://extensions`, enable developer
   mode, choose **Load unpacked**, and select this `browser-extension/` directory.
3. Open `local-companion/.local/pairing.html` locally. Copy its installation token
   into **本地服务配对** in the extension popup and check the connection.
4. Open the authorized video normally and confirm it plays. Click the extension,
   inspect candidates if useful, then **发送视频到 Guitar Tab Cracker**.
5. If only a blob player is found, click **观察播放请求**, grant optional host access,
   replay/seek the video, then reopen the popup and inspect/send again. Observation
   lasts three minutes for that tab; navigation/closing the tab clears it.
6. Wait for the validated local path. The popup can be closed while the companion
   works; reopening polls the last run. Pass this path to the existing score
   conversion workflow. Acquisition does not automatically claim a GP exists.

Manifest V3; Chrome and Edge. The stable extension ID is in `extension-id.txt`.
The public manifest key stabilizes this ID; it is not a signing key or secret.
Only localhost host permission is mandatory. `activeTab`/`scripting` inspect the
current page on user action; optional HTTP(S) host access enables observation of
cross-origin media/CDN requests through `webRequest`. The browser may describe
this optional grant broadly as all-site access: the implementation only stores
media observations for the user-selected tab and time window. You can revoke it
in extension settings. No cookie permission, request Cookie/Authorization capture,
login automation, content upload or third-party downloader is implemented.

Discovery: video currentSrc/src → source elements → resource performance entries
→ manifest URLs → observed media responses. Blob URLs are never sent as normal
download candidates. Current-page DOM injection is top-frame only; inaccessible
cross-origin iframe media may require observing playback requests. EME mediaKeys
cause a protected-media result. Other encryption is rejected by the backend.
Session-authorized signed URLs are preferred; browser cookies are not transferred.
URLs that additionally require cookies or a browser fingerprint may fail.

The token is saved only in this extension's local storage, with content-script
access disabled. Short-lived observed media URLs use session storage; their query
values are hidden in the popup, and companion records redact all query values.
Do not publish local pairing/config files. The MVP is local only, with no accounts
or cloud mode. A future hosted handoff would need separately designed authorization.

Sources: [activeTab](https://developer.chrome.com/docs/extensions/develop/concepts/activeTab),
[scripting](https://developer.chrome.com/docs/extensions/reference/api/scripting),
[webRequest](https://developer.chrome.com/docs/extensions/reference/api/webRequest).
Tests: `node --test browser-extension/discovery.test.mjs`.

Optional real Chromium integration: start the companion, then run `node browser-extension/acceptance.cjs` with Playwright available. Set `GTC_PLAYWRIGHT_MODULE` and `GTC_CHROMIUM_EXECUTABLE` if needed. It uses a separate test profile and a controlled HTML5 page with real public media; it does not operate user video sites. See [acceptance scope](../acceptance/BROWSER_EXTENSION_ACQUISITION.md).
