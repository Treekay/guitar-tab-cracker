import {kind, mergeCandidates} from './discovery.js';
import {api} from './transport.js';
chrome.storage.local.setAccessLevel({accessLevel: 'TRUSTED_CONTEXTS'});
chrome.storage.session.setAccessLevel({accessLevel: 'TRUSTED_CONTEXTS'});
const key = tabId => `observed-${tabId}`;

chrome.webRequest.onHeadersReceived.addListener(async details => {
  if (details.tabId < 0) return;
  const name = key(details.tabId), saved = (await chrome.storage.session.get(name))[name];
  if (!saved || saved.expires < Date.now()) return;
  // Read only Content-Type; never collect Cookie, Authorization, or request headers.
  const type = details.responseHeaders?.find(h => h.name.toLowerCase() === 'content-type')?.value || '';
  const mediaType = kind(details.url, type);
  if (!mediaType) return;
  saved.candidates = mergeCandidates([saved.candidates, [{url: details.url, type: mediaType, content_type: type, source: 'network'}]]);
  await chrome.storage.session.set({[name]: saved});
}, {urls: ['http://*/*', 'https://*/*']}, ['responseHeaders']);
chrome.tabs.onRemoved.addListener(tabId => chrome.storage.session.remove(key(tabId)));
chrome.tabs.onUpdated.addListener((tabId, change) => {
  if (change.url) chrome.storage.session.remove(key(tabId));
});


async function current() {
  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  if (!tab?.id || !/^https?:\/\//.test(tab.url || '')) throw new Error('no_media_candidate');
  return tab;
}

async function discover() {
  const tab = await current();
  const result = await chrome.scripting.executeScript({target: {tabId: tab.id}, files: ['content.js']});
  const page = result[0]?.result;
  if (!page) throw new Error('no_media_candidate');
  const observed = (await chrome.storage.session.get(key(tab.id)))[key(tab.id)];
  page.media_candidates = mergeCandidates([page.media_candidates, observed && observed.expires > Date.now() && observed.page === page.page_url ? observed.candidates : []]);
  return page;
}

chrome.runtime.onMessage.addListener((message, sender, respond) => {
  // The privileged API can only be invoked by this extension's own popup.
  if (sender.id !== chrome.runtime.id || sender.tab || sender.url !== chrome.runtime.getURL('popup.html')) return false;
  (async () => {
    if (message.action === 'discover') return discover();
    if (message.action === 'observe') {
      const tab = await current();
      await chrome.storage.session.set({[key(tab.id)]: {page: tab.url, expires: Date.now() + 180000, candidates: []}});
      return {status: 'observing'};
    }
    if (message.action === 'send') {
      const page = await discover();
      if (page.protected) throw new Error('protected_or_drm');
      if (!page.media_candidates.length) throw new Error(page.blob_detected ? 'blob_without_backing_media' : 'no_media_candidate');
      const result = await api('/acquire', page);
      await chrome.storage.local.set({lastRun: result.run_id});
      return result;
    }
    if (message.action === 'health') return api('/health');
    if (message.action === 'status') {
      const {lastRun} = await chrome.storage.local.get('lastRun');
      return lastRun && /^extension-[a-f0-9]{32}$/.test(lastRun) ? api(`/runs/${lastRun}/status`) : {status: 'idle'};
    }
    throw new Error('invalid_request');
  })().then(value => respond({ok: true, value})).catch(error => respond({ok: false, reason: error.message}));
  return true;
});
