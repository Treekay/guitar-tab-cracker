const BASE = 'http://127.0.0.1:8787';
export async function api(path, payload) {
  const {token} = await chrome.storage.local.get('token');
  if (!token) throw new Error('local_authorization_failed');
  let response;
  try {
    response = await fetch(BASE + path, {method: payload ? 'POST' : 'GET', credentials: 'omit', cache: 'no-store',
      headers: {'X-GTC-Token': token, 'X-GTC-Extension-ID': chrome.runtime.id, ...(payload ? {'Content-Type': 'application/json'} : {})},
      body: payload ? JSON.stringify(payload) : undefined, signal: AbortSignal.timeout(10000)});
  } catch { throw new Error('local_companion_unavailable'); }
  if (response.status === 403) throw new Error('local_authorization_failed');
  const value = await response.json();
  if (!response.ok) throw new Error(value.reason || 'download_failed');
  return value;
}

