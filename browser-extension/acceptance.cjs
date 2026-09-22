// Optional real Chromium + localhost integration. No user browser profile used.
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.GTC_PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
(async () => {
  const tmp = path.join(root, 'tmp'); fs.mkdirSync(tmp, {recursive: true});
  const profile = fs.mkdtempSync(path.join(tmp, 'gtc-extension-test-'));
  const context = await chromium.launchPersistentContext(profile, {
    ...(process.env.GTC_CHROMIUM_EXECUTABLE ? {executablePath: process.env.GTC_CHROMIUM_EXECUTABLE} : {}),
    headless: true, args: ['--disable-extensions-except=' + __dirname, '--load-extension=' + __dirname]
  });
  try {
    const worker = context.serviceWorkers()[0] || await context.waitForEvent('serviceworker', {timeout: 15000});
    const config = JSON.parse(fs.readFileSync(path.join(root, 'local-companion/.local/config.json'), 'utf8'));
    if (new URL(worker.url()).host !== config.extension_id) throw new Error('extension_id_mismatch');
    const page = await context.newPage();
    await page.route('https://example.org/gtc-html5-fixture', route => route.fulfill({contentType: 'text/html',
      body: '<!doctype html><title>HTML5 public-media fixture</title><video controls src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"></video>'}));
    await page.goto('https://example.org/gtc-html5-fixture');
    await page.waitForFunction(() => document.querySelector('video').readyState >= 1, null, {timeout: 20000});
    // Evaluate the exact content script in the controlled page. This is not a
    // claim that an automated toolbar click exercised activeTab permission UI.
    const payload = await page.evaluate(fs.readFileSync(path.join(__dirname, 'content.js'), 'utf8'));
    await worker.evaluate(token => chrome.storage.local.set({token}), config.token);
    const popup = await context.newPage();
    await popup.goto('chrome-extension://' + config.extension_id + '/popup.html');
    const health = await popup.evaluate(async () => (await import('./transport.js')).api('/health'));
    const submitted = await popup.evaluate(async body => (await import('./transport.js')).api('/acquire', body), payload);
    let result = submitted;
    for (let i = 0; i < 60 && result.status === 'running'; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      result = await popup.evaluate(async id => (await import('./transport.js')).api(`/runs/${id}/status`), submitted.run_id);
    }
    const evidence = {extension_id: config.extension_id, manifest_version: 3, health: health.status,
      candidate_count: payload.media_candidates.length, run_id: submitted.run_id, status: result.status,
      scope: 'Controlled HTML5 browser fixture; exact content.js evaluated; actual extension transport; toolbar permission UX not automated'};
    fs.writeFileSync(path.join(tmp, 'extension-html5-run.json'), JSON.stringify(evidence, null, 2));
    console.log(JSON.stringify(evidence));
    if (result.status !== 'success') process.exitCode = 1;
  } finally {
    await context.close();
    const resolved = path.resolve(profile), allowed = path.resolve(tmp) + path.sep;
    if (!resolved.startsWith(allowed)) throw new Error('unsafe_test_profile_cleanup');
    fs.rmSync(resolved, {recursive: true, force: true});
  }
})().catch(() => { console.error('Controlled integration failed. See safe companion status; no tokens or raw diagnostics emitted.'); process.exitCode = 1; });
