// Injected only when the user opens/refreshes the popup. Never reads cookies.
(() => {
  const candidates = [], seen = new Set(); let blob = false, protectedMedia = false;
  const typeOf = (url, type = '') => {
    let path; try { path = new URL(url, location.href).pathname.toLowerCase(); } catch { return null; }
    if (path.endsWith('.m3u8') || /mpegurl/i.test(type)) return 'hls';
    if (path.endsWith('.mpd') || /dash\+xml/i.test(type)) return 'dash';
    if (/\.(mp4|webm|mkv|mov|m4v|flv)$/.test(path) || /^video\/(?!mp2t)/i.test(type)) return 'direct';
    if (path.endsWith('.m4s')) return 'unknown';
    return null;
  };
  const add = (value, source, type = '', knownMedia = false) => {
    if (!value) return;
    if (value.startsWith('blob:')) { blob = true; return; }
    try {
      const url = new URL(value, location.href);
      if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || seen.has(url.href)) return;
      const kind = typeOf(url.href, type);
      if (!knownMedia && !kind) return;
      seen.add(url.href); candidates.push({url: url.href, type: kind || 'unknown', content_type: type, source});
    } catch { /* Untrusted page attributes are not executable. */ }
  };
  for (const video of document.querySelectorAll('video')) {
    if (video.mediaKeys) protectedMedia = true;
    add(video.currentSrc, 'video.currentSrc', '', true);
    add(video.src, 'video.src', '', true);
    for (const source of video.querySelectorAll('source')) add(source.src, 'source', source.type, true);
  }
  for (const entry of performance.getEntriesByType('resource')) add(entry.name, 'performance');
  return {page_url: location.href, page_title: document.title.slice(0, 512), media_candidates: candidates.slice(0, 100),
    blob_detected: blob, protected: protectedMedia,
    request_context: {referer: location.href, origin: location.origin, user_agent: navigator.userAgent.slice(0, 512)}};
})();
