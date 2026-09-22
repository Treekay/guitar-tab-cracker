export function kind(url, contentType = '') {
  let path;
  try { path = new URL(url).pathname.toLowerCase(); } catch { return null; }
  if (/\.m3u8$/.test(path) || /mpegurl/i.test(contentType)) return 'hls';
  if (/\.mpd$/.test(path) || /dash\+xml/i.test(contentType)) return 'dash';
  if (/\.(mp4|webm|mkv|mov|m4v|flv)$/.test(path) || /^video\/(?!mp2t)/i.test(contentType)) return 'direct';
  if (/\.m4s$/.test(path)) return 'unknown'; // Can be a complete track or a fragment; backend validates.
  return null;
}

export function mergeCandidates(groups) {
  const seen = new Set(), result = [];
  for (const c of groups.flat()) {
    try {
      const u = new URL(c.url);
      if (!['http:', 'https:'].includes(u.protocol) || u.username || u.password || seen.has(c.url)) continue;
      if (c.url.length > 8192) continue;
      seen.add(c.url);
      result.push({url: c.url, type: c.type || 'unknown', content_type: c.content_type || '', source: c.source});
      if (result.length === 100) break;
    } catch { /* Ignore malformed page data. */ }
  }
  return result;
}

export function displayURL(url) {
  try { const u = new URL(url); return u.origin + u.pathname + (u.search ? '?[已隐藏参数]' : ''); }
  catch { return '无效地址'; }
}
