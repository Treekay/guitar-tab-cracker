// Explicit alignment only: identical counts or printed numbers do not prove identity.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {alphaTab} from '../guitar-pro/adapter.mjs';
import {importedSemantics} from '../guitar-pro/compare.mjs';
const [generated,manual,alignment,output]=process.argv.slice(2);
if(!output)throw new Error('Usage: node benchmark.mjs GENERATED_GP MANUAL_GP ALIGNMENT_JSON OUTPUT');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const a=JSON.parse(fs.readFileSync(alignment));
if(a.generated_sha256!==hash(generated)||a.manual_sha256!==hash(manual)||!a.independently_confirmed)
    throw new Error('Alignment must be independently confirmed and bound to both file hashes');
function read(p,track){
 const score=alphaTab.importer.ScoreLoader.loadScoreFromBytes(new Uint8Array(fs.readFileSync(p)),new alphaTab.Settings());
 if(!Number.isInteger(track)||!score.tracks[track]||score.tracks[track].staves.length!==1)throw new Error('Select one explicit guitar track with one staff');
 return importedSemantics({tracks:[score.tracks[track]],masterBars:score.masterBars,tempo:score.tempo,title:score.title,artist:score.artist});
}
const g=read(generated,a.generated_track),m=read(manual,a.manual_track);
const eventMetrics={rhythm:{matching:0,total:0},chord_grouping:{matching:0,total:0},string_fret_notes:{matching:0,total:0},note_techniques_excluding_let_ring:{matching:0,total:0}};
const rows=[],seenG=new Set(),seenM=new Set();
const events=x=>x.voices.map(v=>({voice:v.voice,events:v.events}));
const project=(bar,fn)=>events(bar).map(v=>({voice:v.voice,events:v.events.map(fn)}));
const eq=(x,y)=>JSON.stringify(x)===JSON.stringify(y);
const toGenerated=new Map(a.measures.map(p=>[p.manual,p.generated]));
const relations=(score,index,isManual)=>score.relations.filter(r=>r.from?.measure===index).map(r=>({
 ...r,from:{...r.from,measure:isManual?toGenerated.get(r.from.measure)??'unaligned':r.from.measure},
 to:r.to?{...r.to,measure:isManual?toGenerated.get(r.to.measure)??'unaligned':r.to.measure}:null
}));
for(const p of a.measures){
 if(seenG.has(p.generated)||seenM.has(p.manual))throw new Error('Alignment must be one-to-one written measures, not playback expansion');
 seenG.add(p.generated);seenM.add(p.manual);
 const x=g.measures[p.generated-1],y=m.measures[p.manual-1];if(!x||!y)throw new Error('Invalid alignment index');
 for(let vi=0;vi<x.voices.length;vi++)for(let ei=0;ei<x.voices[vi].events.length;ei++){
 const e=x.voices[vi].events[ei],f=y.voices[vi]?.events[ei];
 eventMetrics.rhythm.total++;eventMetrics.chord_grouping.total++;
 if(f&&eq([e.duration,e.dots,e.tuplet,e.rest],[f.duration,f.dots,f.tuplet,f.rest]))eventMetrics.rhythm.matching++;
 if(f&&e.notes.length===f.notes.length)eventMetrics.chord_grouping.matching++;
 for(let ni=0;ni<e.notes.length;ni++){
  const n=e.notes[ni],o=f?.notes[ni];eventMetrics.string_fret_notes.total++;eventMetrics.note_techniques_excluding_let_ring.total++;
  if(o&&n.string===o.string&&n.fret===o.fret)eventMetrics.string_fret_notes.matching++;
  const tech=({string,fret,let_ring,...rest})=>rest;
  if(o&&eq(tech(n),tech(o)))eventMetrics.note_techniques_excluding_let_ring.matching++;
 }
}
rows.push({...p,checks:{
 structure:eq(x.signature,y.signature)&&eq(x.voices.map(v=>[v.voice,v.events.length]),y.voices.map(v=>[v.voice,v.events.length])),
 string_fret:eq(project(x,e=>e.notes.map(n=>[n.string,n.fret])),project(y,e=>e.notes.map(n=>[n.string,n.fret]))),
 rhythm:eq(project(x,e=>[e.duration,e.dots,e.tuplet,e.rest]),project(y,e=>[e.duration,e.dots,e.tuplet,e.rest])),
 chord_grouping:eq(project(x,e=>e.notes.length),project(y,e=>e.notes.length)),
 repeats:eq([x.repeat_start,x.repeat_end,x.repeat_count],[y.repeat_start,y.repeat_end,y.repeat_count]),
 endings:eq(x.endings,y.endings),
 techniques:eq(project(x,e=>e.notes.map(({string,fret,...tech})=>tech)),project(y,e=>e.notes.map(({string,fret,...tech})=>tech)))&&eq(relations(g,p.generated,false),relations(m,p.manual,true))
 }});
}
const metrics={};for(const key of Object.keys(rows[0]?.checks??{}))metrics[key]={matching_aligned_measures:rows.filter(r=>r.checks[key]).length,aligned_measures:rows.length};
const genRelations=a.measures.flatMap(p=>relations(g,p.generated,false));
const manualRelations=a.measures.flatMap(p=>relations(m,p.manual,true));
const relationMetrics={};
for(const type of ['tie','slide_down','slide_up']){
 const x=genRelations.filter(r=>r.type===type),y=manualRelations.filter(r=>r.type===type);
 const endpoints=({style,...rest})=>rest;
 relationMetrics[type]={generated:x.length,manual:y.length,
   matching_endpoints:x.filter(r=>y.some(t=>eq(endpoints(r),endpoints(t)))).length,
   matching_including_style:x.filter(r=>y.some(t=>eq(r,t))).length};
}
fs.writeFileSync(output,JSON.stringify({generated_sha256:hash(generated),manual_sha256:hash(manual),
 generated_measures:g.measures.length,manual_measures:m.measures.length,metrics,eventMetrics,relationMetrics,rows,
 scope:'Exact agreement over explicitly aligned written measures; not source accuracy. Unaligned measures excluded.',
 limitations:'Tied beat segmentation, defaults, numbering and engraving may differ. No automatic truth transfer; inspect mismatches against source.'},null,2)+'\n');
