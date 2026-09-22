import {displayURL} from './discovery.js';
const $ = id => document.getElementById(id);
const errors = {
  no_media_candidate: '未发现支持的媒体。请先播放视频，再检查候选。',
  blob_without_backing_media: '播放器使用 blob。请观察播放请求，继续播放后重新检查。',
  protected_or_drm: '受保护或加密的媒体暂不支持。', manifest_unsupported: '暂不支持这种清单格式，请选择直链或提供本地视频。',
  local_companion_unavailable: '本地服务未连接。请启动伴随服务。', local_authorization_failed: '配对未完成，请填写本地配对码。',
  busy: '已有视频正在获取，请稍后。', download_failed: '下载失败。可重播视频以更新媒体地址，或提供本地文件。',
  media_validation_failed: '资源不是完整可解码的视频，可能只是片段或音轨。'
};
async function call(action) {
  const result = await chrome.runtime.sendMessage({action});
  if (!result?.ok) throw new Error(result?.reason || 'local_companion_unavailable');
  return result.value;
}
function failure(e) { $('status').textContent = errors[e.message] || '操作未完成，请重新检查页面和本地服务。'; }
async function inspect(show = false) {
  try {
    const page = await call('discover'); $('title').textContent = page.page_title;
    $('send').disabled = page.protected || !page.media_candidates.length;
    $('status').textContent = page.protected ? errors.protected_or_drm : page.media_candidates.length ? `检测到 ${page.media_candidates.length} 个候选媒体` : errors[page.blob_detected ? 'blob_without_backing_media' : 'no_media_candidate'];
    $('candidates').replaceChildren(...page.media_candidates.map(c => { const item = document.createElement('li'); item.textContent = `${c.type} · ${c.source}\n${displayURL(c.url)}`; return item; }));
    $('candidates').hidden = !show;
  } catch (e) { failure(e); }
}
let polling;
async function status() {
  try {
    const r = await call('status');
    if (r.status === 'idle') return;
    if (r.status === 'running') { $('result').textContent = '已发送，本地服务正在下载并验证…'; return; }
    clearInterval(polling);
    $('result').textContent = r.status === 'success' ? `获取成功\n${r.width} × ${r.height} · ${r.duration_seconds.toFixed(2)} 秒\n本地视频：${r.local_path}\n可交给现有读谱流程；尚未开始转换。` : (errors[r.reason] || '获取失败，请查看本地记录。');
  } catch (e) { clearInterval(polling); failure(e); }
}
$('inspect').onclick = () => inspect(true);
$('send').onclick = async () => {
  $('send').disabled = true;
  try { await call('send'); await status(); clearInterval(polling); polling = setInterval(status, 1500); }
  catch (e) { failure(e); $('send').disabled = false; }
};
$('observe').onclick = async () => {
  try {
    const granted = await chrome.permissions.request({origins: ['http://*/*', 'https://*/*']});
    if (!granted) { $('status').textContent = '未授权观察请求；仍可检查页面已有媒体。'; return; }
    await call('observe'); $('status').textContent = '正在观察当前标签页。请继续播放或拖动进度，再打开扩展检查。';
  } catch (e) { failure(e); }
};
$('save').onclick = async () => {
  const token = $('token').value.trim();
  if (token.length < 32) { $('status').textContent = '请粘贴完整配对码。'; return; }
  await chrome.storage.local.set({token}); $('token').value = '';
  try { await call('health'); $('setup').open = false; $('status').textContent = '本地服务已连接。'; } catch (e) { failure(e); }
};
const saved = await chrome.storage.local.get('token'); $('setup').open = !saved.token;
await inspect();
if (saved.token) { await status(); polling = setInterval(status, 1500); }
