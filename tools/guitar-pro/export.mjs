import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { adapt,alphaTab } from './adapter.mjs';
import { compare } from './compare.mjs';
import { renderImported } from './render.mjs';

const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const writeJson=(p,data)=>fs.writeFileSync(p,JSON.stringify(data,null,2)+'\n');

export function exportScore(input,output,{render=false,sample=[],python='python'}={}) {
    input=path.resolve(input);output=path.resolve(output);
    if(path.dirname(input)===output)throw new Error('Use a dedicated export directory');
    const before=fs.readFileSync(input),canonical=JSON.parse(before);
    fs.mkdirSync(output,{recursive:true});
    const validator=fileURLToPath(new URL('../validate_score.py',import.meta.url));
    const args=[validator,input,'--manifest',path.resolve(path.dirname(input),'../measures.json'),
        '--output',path.join(output,'canonical_validation.json')];
    if(sample.length)args.push('--selected-indices',...sample.map(String));
    const check=spawnSync(python,args,{encoding:'utf8'});
    if(check.status!==0)throw new Error(`Canonical validation failed: ${check.stderr}\n${check.stdout}`);
    const validation=JSON.parse(fs.readFileSync(path.join(output,'canonical_validation.json')));
    if(validation.warnings.length)throw new Error('Canonical has review warnings; export does not repair them');
    const {score,settings,mapping}=adapt(canonical);
    mapping.canonical_sha256=hash(before);mapping.source_scope=sample.length?'sample':'complete';
    mapping.canonical_source=path.relative(output,input).replaceAll('\\','/');
    writeJson(path.join(output,'export_mapping.json'),mapping);
    const bytes=new alphaTab.exporter.Gp7Exporter().export(score,settings);
    const gp=path.join(output,'score.gp');fs.writeFileSync(gp,bytes);
    const saved=fs.readFileSync(gp);
    const imported=alphaTab.importer.ScoreLoader.loadScoreFromBytes(new Uint8Array(saved),new alphaTab.Settings());
    const roundtrip=compare(canonical,imported,mapping);
    roundtrip.canonical_sha256=hash(before);roundtrip.gp_sha256=hash(saved);roundtrip.gp_bytes=saved.length;
    roundtrip.canonical_unchanged=hash(fs.readFileSync(input))===hash(before);
    if(!roundtrip.canonical_unchanged)roundtrip.valid=false;
    const {comparison,...summary}=roundtrip;
    writeJson(path.join(output,'semantic_comparison.json'),comparison);
    writeJson(path.join(output,'roundtrip_validation.json'),summary);
    let renders=[];
    if(roundtrip.valid&&render)renders=renderImported(imported,path.join(output,'rendered'));
    const report=['# Guitar Pro export report','',
        `Exporter: alphaTab 1.8.4 Gp7Exporter. Scope: ${mapping.source_scope}.`,
        `Structural round trip: ${roundtrip.valid?'PASS':'FAIL'}. GP bytes: ${saved.length}.`,
        `Written measures: ${roundtrip.canonical_measures} → ${roundtrip.roundtrip_measures}; events: ${roundtrip.canonical_events} → ${roundtrip.roundtrip_events}; notes: ${roundtrip.canonical_notes} → ${roundtrip.roundtrip_notes}.`,
        `Canonical SHA-256: ${hash(before)}. Unchanged: ${roundtrip.canonical_unchanged}.`,'',
        'This is editable Guitar Pro 7+ model data. Playback defaults below are not recognized source metadata.',
        'Only alphaTab export/import is used; no manual GP archive modification or note-by-note MCP.','',
        '## Technical defaults','', '```json',JSON.stringify(mapping.technical_defaults,null,2),'```','',
        '## Unsupported or partial mappings','', '```json',JSON.stringify(mapping.unsupported_or_partial,null,2),'```','',
        '## Unresolved relations skipped','', '```json',JSON.stringify(mapping.unresolved_skipped,null,2),'```','',
        '## Canonical unresolved source data','',
        'These items remain unresolved even when the representable musical structure round-trips exactly. Export is not source acceptance.',
        '', '```json',JSON.stringify(mapping.canonical_unresolved,null,2),'```','',
        '## Unexpected mismatches','', '```json',JSON.stringify(roundtrip.unexpected_mismatches,null,2),'```','',
        '## Visual validation','',
        renders.length?`${renders.length} SVG/PNG chunks rendered from the re-imported GP. Human visual review is recorded separately in visual_review.md; rendering alone is not acceptance.`:'Render not requested. Visual acceptance remains pending.',
        '', 'Sources: [Gp7Exporter](https://www.alphatab.net/docs/reference/types/exporter/gp7exporter/), [Note](https://www.alphatab.net/docs/reference/types/model/note/), [Node rendering](https://www.alphatab.net/docs/guides/nodejs).',''];
    fs.writeFileSync(path.join(output,'export_report.md'),report.join('\n'));
    if(!roundtrip.valid)throw new Error('Unexpected semantic mismatch; see roundtrip_validation.json');
    return {gp,summary,renders};
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
    const args=process.argv.slice(2),input=args.shift();
    if(!input||input==='--help'){
        console.log('node tools/guitar-pro/export.mjs SCORE_JSON [--output DIR] [--render] [--sample 1,16,29,30] [--python PYTHON]');
        process.exit(input==='--help'?0:1);
    }
    const options={};let output=path.join(path.dirname(input),'export');
    while(args.length){const flag=args.shift();if(flag==='--render')options.render=true;
        else if(flag==='--output')output=args.shift();else if(flag==='--sample')options.sample=args.shift().split(',').map(Number);
        else if(flag==='--python')options.python=args.shift();else throw new Error(`Unknown argument ${flag}`);}
    const result=exportScore(input,output,options);
    console.log(JSON.stringify({file:result.gp,valid:result.summary.valid,measures:result.summary.roundtrip_measures,notes:result.summary.roundtrip_notes,render_chunks:result.renders.length}));
}
