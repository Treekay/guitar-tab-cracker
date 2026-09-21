import test from 'node:test';
import assert from 'node:assert/strict';
import { adapt,alphaTab as a,canonicalStringToAlphaTab,durations } from './adapter.mjs';
import { compare } from './compare.mjs';

const note=(string=1,fret=7,extra={})=>({string,fret,dead:false,parenthesized:false,display:'fret',techniques:[],confidence:'high',uncertainty:null,...extra});
const event=(notes=[note()],duration=4,extra={})=>({index:1,voice:1,duration,dots:0,tuplet:null,rest:!notes.length,notes,confidence:'high',uncertainty:null,...extra});
function fixture(eventLists=[[event()]]) {
    return {schema_version:1,string_convention:'1=top/highest;6=bottom/lowest',
        metadata:{title:null,artist:null,tempo_bpm:null,tuning:null,capo:null,time_signature:{numerator:4,denominator:4}},
        measures:eventLists.map((events,mi)=>({sequence_index:mi+1,printed_measure_number:mi+1,
            time_signature:null,tempo_bpm:null,pickup:false,barline:{start:'normal',end:mi===eventLists.length-1?'final':'normal',
                repeat_start:false,repeat_end:false,repeat_count:null,ending_numbers:[]},events:events.map((e,i)=>({...e,index:i+1}))})),
        relations:[],annotations:[],unresolved:[]};
}
const relation=(type,from,to)=>({id:'r'+type,type,from,to,confidence:to?'high':'medium',uncertainty:to?null:'Target unknown'});
const ref=(measure,event,string=1)=>({measure,event,string});
function roundtrip(c) {
    const original=JSON.stringify(c),x=adapt(c),bytes=new a.exporter.Gp7Exporter().export(x.score,x.settings);
    const imported=a.importer.ScoreLoader.loadScoreFromBytes(bytes,new a.Settings());
    const validation=compare(c,imported,x.mapping);
    assert.equal(JSON.stringify(c),original,'Adapter must not mutate canonical');
    assert.equal(validation.valid,true,JSON.stringify(validation.unexpected_mismatches));
    return {...x,bytes,imported,validation};
}
const beats=r=>r.imported.tracks[0].staves[0].bars[0].voices[0].beats;

test('root source uncertainty survives export provenance without invented notes',()=>{
    const c=fixture();c.unresolved=[{measure:1,event:1,field:'grace_slide',
        issue:'Small unmetered onset cannot be encoded in schema v1',candidates:[],confidence:'medium'}];
    const r=roundtrip(c);
    assert.deepEqual(r.validation.source_unresolved,c.unresolved);
    assert.equal(beats(r).length,1);assert.equal(beats(r)[0].notes.length,1);
    r.mapping.canonical_unresolved[0].candidates.push('changed');
    assert.deepEqual(c.unresolved[0].candidates,[]);
});

test('first written measure tempo overrides metadata for initial playback',()=>{
    const c=fixture();c.metadata.tempo_bpm=80;c.measures[0].tempo_bpm=100;
    assert.equal(roundtrip(c).imported.tempo,100);
});

test('all six strings: reversed note index but unchanged top-first tuning',()=>{
    assert.deepEqual([1,2,3,4,5,6].map(canonicalStringToAlphaTab),[6,5,4,3,2,1]);
    const r=roundtrip(fixture([[event([1,2,3,4,5,6].map(s=>note(s,s)))]]));
    const actual=beats(r)[0].notes;
    assert.deepEqual(actual.map(n=>n.string),[6,5,4,3,2,1]);
    assert.deepEqual(actual.map(n=>n.stringTuning),[64,59,55,50,45,40]);
    assert.throws(()=>canonicalStringToAlphaTab(0));assert.throws(()=>canonicalStringToAlphaTab(7));
});
test('single note and all seven denominator durations',()=>{
    const r=roundtrip(fixture([Object.keys(durations).map(d=>event([note()],Number(d)))]));
    assert.deepEqual(beats(r).map(b=>b.duration),[1,2,4,8,16,32,64]);
});
test('simultaneous chord is one event',()=>{
    const r=roundtrip(fixture([[event([note(1,12),note(3,9),note(6,0)])]]));
    assert.equal(beats(r).length,1);assert.equal(beats(r)[0].notes.length,3);
});
test('rest retains duration and no notes',()=>{
    const r=roundtrip(fixture([[event([],8)]]));assert.equal(beats(r)[0].isRest,true);
});
test('single and double dots survive',()=>roundtrip(fixture([[event([note()],8,{dots:1}),event([note()],16,{dots:2})]])));
test('three explicit eighth triplets retain 3:2',()=>roundtrip(fixture([[1,2,3].map(()=>event([note()],8,{tuplet:{numerator:3,denominator:2}}))])));
test('tied blank continuation is not a new attack, across bar boundary',()=>{
    const c=fixture([[event([note()])],[event([note(1,7,{display:'tie_continuation'})])]]);
    c.relations=[relation('tie',ref(1,1),ref(2,1))];const r=roundtrip(c);
    const n=r.imported.tracks[0].staves[0].bars[1].voices[0].beats[0].notes[0];
    assert.equal(n.isTieDestination,true);assert.equal(n.tieOrigin.fret,7);
});
test('hammer-on and pull-off preserve endpoints',()=>{
    const c=fixture([[event([note(1,2)]),event([note(1,3)]),event([note(1,0)])]]);
    c.relations=[relation('hammer_on',ref(1,1),ref(1,2)),relation('pull_off',ref(1,2),ref(1,3))];roundtrip(c);
});
test('cross-bar slide and paired slur become a legato slide',()=>{
    const c=fixture([[event([note(2,2)])],[event([note(2,4)])]]);
    c.relations=[relation('slide_up',ref(1,1,2),ref(2,1,2)),relation('slur',ref(1,1,2),ref(2,1,2))];
    const r=roundtrip(c);assert.equal(beats(r)[0].notes[0].slideOutType,a.model.SlideOutType.Legato);
});
test('direction-only slide documents technical articulation subtype',()=>{
    const c=fixture([[event([note(1,7)]),event([note(1,5)])]]);c.relations=[relation('slide_down',ref(1,1),ref(1,2))];
    const r=roundtrip(c);assert.ok(r.mapping.technical_defaults.some(d=>d.field==='relations.rslide_down'));
});
test('repeats and first/second ending bitmasks survive without expanding bars',()=>{
    const c=fixture([[event()],[event()],[event()]]);
    c.measures[0].barline.repeat_start=true;c.measures[1].barline.repeat_end=true;
    c.measures[1].barline.ending_numbers=[1];c.measures[2].barline.ending_numbers=[2,3];
    const r=roundtrip(c);assert.equal(r.imported.masterBars.length,3);assert.equal(r.imported.masterBars[1].repeatCount,2);
    assert.equal(r.imported.masterBars[2].alternateEndings,6);
});
test('null metadata defaults are explicit and do not change input',()=>{
    const r=roundtrip(fixture());assert.equal(r.imported.tempo,120);
    for(const field of ['metadata.title','metadata.artist','metadata.tempo_bpm','metadata.capo','metadata.tuning'])
        assert.ok(r.mapping.technical_defaults.some(d=>d.field===field&&d.canonical===null));
});
test('explicit metadata, tuning, capo and tempo/meter changes survive',()=>{
    const c=fixture([[event()],[event()]]);Object.assign(c.metadata,{title:'Test',artist:'Author',tempo_bpm:80,capo:2,tuning:[64,59,55,50,45,38]});
    c.measures[1].tempo_bpm=96;c.measures[1].time_signature={numerator:3,denominator:4};roundtrip(c);
});
test('unresolved destination is omitted, never guessed from next note',()=>{
    const c=fixture([[event([note(1,7)]),event([note(1,5)])]]);c.relations=[relation('slide_down',ref(1,1),null)];
    const r=roundtrip(c);assert.equal(r.mapping.unresolved_skipped.length,1);assert.equal(beats(r)[0].notes[0].slideOutType,a.model.SlideOutType.None);
});
test('natural harmonic retains touched fret and tie',()=>{
    const n=note(5,12,{techniques:['natural_harmonic']});const c=fixture([[event([n],2,{dots:1}),event([{...n,display:'tie_continuation'}],8)]]);
    c.relations=[relation('tie',ref(1,1,5),ref(1,2,5))];roundtrip(c);
});
test('parentheses never silently become ghost articulation',()=>{
    const r=roundtrip(fixture([[event([note(3,2,{parenthesized:true})])]]));
    assert.equal(beats(r)[0].notes[0].isGhost,false);assert.ok(r.mapping.unsupported_or_partial.some(l=>l.field.endsWith('parenthesized')));
});
test('explicit ghost/dead, accent, palm mute, let ring, vibrato',()=>{
    roundtrip(fixture([[event([note(1,7,{techniques:['ghost','accent','palm_mute','let_ring','vibrato']})]),event([note(2,0,{dead:true})])]]));
});
test('explicit bend and release amounts, no pitch guessed for missing amount',()=>{
    for(const type of ['bend','release_bend'])roundtrip(fixture([[event([note(1,7,{techniques:[type],technique_parameters:[{type,amount_semitones:2,text:null}]})])]]));
    const r=roundtrip(fixture([[event([note(1,7,{techniques:['bend','artificial_harmonic']})])]]));
    assert.equal(r.mapping.unsupported_or_partial.length,2);
});
test('standalone slur loss is documented and not changed to hammer-on',()=>{
    const c=fixture([[event([note(1,5)]),event([note(2,7)])]]);c.relations=[relation('slur',ref(1,1),ref(1,2,2))];
    const r=roundtrip(c);assert.equal(r.mapping.unsupported_or_partial.length,1);assert.equal(beats(r)[0].notes[0].isHammerPullOrigin,false);
});
test('pickup, double bar and final bar survive',()=>{
    const c=fixture([[event()],[event()]]);c.measures[0].pickup=true;c.measures[0].barline.end='double';roundtrip(c);
});
test('separate voices, same-beat chords and rests survive',()=>roundtrip(fixture([[event([note(1,7)]),event([note(2,4),note(4,2)],4,{voice:2}),event([],4,{voice:2})]])));
test('unknown duration/fret and invalid endpoints fail rather than fabricate',()=>{
    assert.throws(()=>adapt(fixture([[event([note()],null)]])),/Unknown duration/);
    assert.throws(()=>adapt(fixture([[event([note(1,null)])]])),/Unknown fret/);
    const c=fixture();c.relations=[relation('tie',ref(1,1),ref(2,1))];assert.throws(()=>adapt(c),/Invalid relation/);
});
test('canonical comparison detects corruption beyond counts',()=>{
    const c=fixture(),r=roundtrip(c);beats(r)[0].notes[0].fret++;
    assert.equal(compare(c,r.imported,r.mapping).valid,false);
    beats(r)[0].notes[0].fret--;beats(r)[0].notes[0].string=1;
    assert.equal(compare(c,r.imported,r.mapping).valid,false);
});
test('repeated exports have identical musical semantics',()=>{
    const c=fixture();assert.deepEqual(roundtrip(c).validation.comparison.actual,roundtrip(c).validation.comparison.actual);
});
