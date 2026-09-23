import {displayURL} from './discovery.js';
import {outputFile} from './transport.js';
const $ = id => document.getElementById(id);
const errors = {
  no_media_candidate: '未发现支持的媒体。请先播放视频，再检查候选。',
  blob_without_backing_media: '播放器使用 blob。请观察播放请求，继续播放后重新检查。',
  protected_or_drm: '受保护或加密的媒体暂不支持。', manifest_unsupported: '暂不支持这种清单格式，请选择直链或提供本地视频。',
  local_companion_unavailable: '本地服务未连接。请启动伴随服务。', local_authorization_failed: '配对未完成，请填写本地配对码。',
  busy: '已有转换任务正在运行，请稍后。', download_failed: '下载失败。可重播视频以更新媒体地址，或提供本地文件。',
  agent_runtime_missing: '未找到 Codex CLI，请完成本地服务的一次性设置。',
  agent_not_authenticated: 'Codex CLI 尚未登录。请在本机终端运行 codex login，完成一次性登录。',
  agent_runtime_unavailable: 'Codex CLI 暂不可用，请检查本地安装。',
  agent_exit_failed: '转换运行器异常退出，已保留本次文件和日志。',
  agent_upgrade_required: 'Codex CLI 版本过旧，无法使用当前模型。请更新或选择新版 CLI 后重试。',
  agent_timeout: '转换超过时限，已停止并保留本次文件。',
  outputs_not_ready: '结果尚未通过校验，暂不可下载。',
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
    $('send').disabled = jobRunning || page.protected || !page.media_candidates.length;
    $('status').textContent = page.protected ? errors.protected_or_drm : page.media_candidates.length ? `检测到 ${page.media_candidates.length} 个候选媒体` : errors[page.blob_detected ? 'blob_without_backing_media' : 'no_media_candidate'];
    $('candidates').replaceChildren(...page.media_candidates.map(c => { const item = document.createElement('li'); item.textContent = `${c.type} · ${c.source}\n${displayURL(c.url)}`; return item; }));
    $('candidates').hidden = !show;
  } catch (e) { failure(e); }
}
let polling, jobRunning=false, statusPending=false;
const stages={queued:'等待开始',acquisition:'正在获取视频',v2_reconstruction:'正在重建谱面',
  v3_transcription:'正在识别乐谱',gp_export:'正在生成 Guitar Pro',v4_verification:'正在检查结果',finalizing:'正在整理并校验文件'};
const elapsed=seconds=>`${Math.floor((seconds||0)/60)}分 ${Math.floor((seconds||0)%60)}秒`;
function showOutputs(r) {
  const labels={'score.gp':'下载 Guitar Pro','final_report.md':'下载转换报告','verification_report.md':'下载复核报告','full_score.pdf':'下载原谱 PDF','timing.json':'下载耗时记录'};
  $('outputs').replaceChildren();$('outputs').hidden=false;
  for (const [name,label] of Object.entries(labels)) {
    if (!r.result.files.includes(name)) continue;
    const button=document.createElement('button');button.textContent=label;
    button.onclick=async()=>{
      button.disabled=true;
      try {
        const blob=await outputFile(r.run_id,name),url=URL.createObjectURL(blob),a=document.createElement('a');
        a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);
      } catch(e){failure(e);} finally{button.disabled=false;}
    };
    $('outputs').append(button);
  }
}
async function status() {
  if(statusPending)return;statusPending=true;
  try {
    const r = await call('status');
    if (r.status === 'idle') return;
    jobRunning=r.status==='running';
    if (jobRunning) { $('send').disabled=true;$('outputs').hidden=true;$('result').textContent = `${stages[r.stage]||'正在转换'}…\n已用时 ${elapsed(r.elapsed_seconds)}\n关闭弹窗后仍会继续运行。`; return; }
    clearInterval(polling);
    if(r.status==='completed') {
      const review=r.result.delivery_status!=='READY_FOR_DELIVERY';
      $('result').textContent=`${review?'转换完成，建议查看复核报告':'转换完成'}${r.result.review_count?`（${r.result.review_count} 处需要确认）`:''}\n${r.result.delivery_status}\n耗时 ${elapsed(r.elapsed_seconds)}`;
      showOutputs(r);
    } else $('result').textContent=r.status==='success'?'旧任务仅完成了视频获取。请点击“转换为 Guitar Pro”开始完整转换。':`转换失败：${stages[r.failure_stage]||r.failure_stage||'获取视频'}\n${errors[r.reason]||r.message||'请查看本地运行记录。'}`;
    await inspect();
  } catch (e) { failure(e); }
  finally{statusPending=false;}
}
$('inspect').onclick = () => inspect(true);
$('send').onclick = async () => {
  $('send').disabled = true;
  try { await call('send');$('outputs').hidden=true;clearInterval(polling);polling = setInterval(status, 1500);await status(); }
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
  try { const h=await call('health'); $('setup').open = false; $('status').textContent = h.agent_setup_issue?(errors[h.agent_setup_issue]||'请完成运行器设置。'):'本地服务已连接。'; } catch (e) { failure(e); }
};
const saved = await chrome.storage.local.get('token'); $('setup').open = !saved.token;
await inspect();
if (saved.token) { polling = setInterval(status, 1500); await status(); }
