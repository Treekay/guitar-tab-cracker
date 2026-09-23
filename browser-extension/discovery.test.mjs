import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {kind,mergeCandidates,displayURL} from './discovery.js';
test('direct, manifest and complete-track candidates classified without site selectors',()=>{
 assert.equal(kind('https://cdn.example/v.mp4?token=1'),'direct');
 assert.equal(kind('https://cdn.example/manifest','application/vnd.apple.mpegurl'),'hls');
 assert.equal(kind('https://cdn.example/v.mpd'),'dash');
 assert.equal(kind('https://cdn.example/v.m4s'),'unknown');
});
test('blob, credentials and duplicate candidates cannot become normal URLs',()=>{
 const c=url=>({url,source:'performance',type:'direct'});
 const found=mergeCandidates([[c('blob:https://example.com/x'),c('https://u:p@example.com/a'),c('https://cdn.example/v.mp4')],[c('https://cdn.example/v.mp4')]]);
 assert.equal(found.length,1);assert.ok(!displayURL('https://cdn.example/v.mp4?token=secret').includes('secret'));
});
test('content discovery traces blob backing resources and preserves order',()=>{
 const code=fs.readFileSync(new URL('./content.js',import.meta.url),'utf8');
 const video={currentSrc:'blob:https://example.com/x',src:'',mediaKeys:null,querySelectorAll:()=>[{src:'https://cdn.example/fallback.mp4',type:'video/mp4'}]};
 const result=vm.runInNewContext(code,{URL,location:{href:'https://example.com/video',origin:'https://example.com'},document:{title:'A score',querySelectorAll:()=>[video]},navigator:{userAgent:'test'},performance:{getEntriesByType:()=>[{name:'https://cdn.example/master.m3u8'},{name:'https://cdn.example/a.js'}]}});
 assert.equal(result.blob_detected,true);assert.equal(result.media_candidates.length,2);
 assert.equal(result.media_candidates[0].source,'source');assert.equal(result.media_candidates[1].type,'hls');
});
test('MV3 permissions omit cookies and external messaging',()=>{
 const manifest=JSON.parse(fs.readFileSync(new URL('./manifest.json',import.meta.url),'utf8'));
 assert.equal(manifest.manifest_version,3);assert.ok(!manifest.permissions.includes('cookies'));
 assert.ok(!manifest.externally_connectable);assert.deepEqual(manifest.host_permissions,['http://127.0.0.1:8787/*']);
});
test('only own popup can initiate handoff and payload is freshly discovered',async()=>{
 const source=fs.readFileSync(new URL('./background.js',import.meta.url),'utf8').replace(/^import .*;$/gm,'');
 let listener, sent;
 const store={};const page={page_url:'https://example.com/video',media_candidates:[{url:'https://cdn.example/video.mp4',type:'direct',source:'video.currentSrc'}]};
 const storage={setAccessLevel:()=>{},get:async key=>({[key]:store[key]}),set:async value=>Object.assign(store,value),remove:()=>{}};
 const chrome={storage:{local:storage,session:storage},webRequest:{onHeadersReceived:{addListener:()=>{}}},tabs:{query:async()=>[{id:1,url:page.page_url}],onRemoved:{addListener:()=>{}},onUpdated:{addListener:()=>{}}},scripting:{executeScript:async()=>[{result:structuredClone(page)}]},runtime:{id:'extension-id',getURL:file=>'chrome-extension://extension-id/'+file,onMessage:{addListener:fn=>listener=fn}}};
 vm.runInNewContext(source,{chrome,kind,mergeCandidates,api:async(path,body)=>{sent={path,body};return {run_id:'extension-test'}},Date,Error});
 const sender={id:'extension-id',url:'chrome-extension://extension-id/popup.html'};
 assert.equal(listener({action:'send'},{...sender,tab:{id:1}},()=>{}),false);
 assert.equal(listener({action:'send'},{...sender,url:'https://evil.example'},()=>{}),false);
 const result=await new Promise(resolve=>listener({action:'send',body:{url:'https://evil.example'}},sender,resolve));
 assert.equal(result.ok,true);assert.equal(sent.path,'/convert');assert.equal(sent.body.page_url,page.page_url);
});
