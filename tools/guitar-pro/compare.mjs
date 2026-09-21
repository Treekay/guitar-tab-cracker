import { alphaTab } from './adapter.mjs';
const M=alphaTab.model;
const address=r=>`${r.measure}/${r.event}/${r.string}`;
const normalizeRelations=relations=>relations.sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)));
const sortNotes=notes=>notes.sort((a,b)=>a.string-b.string);

// This expectation is read from canonical values, not from the constructed
// alphaTab model. Comparing only pre-export and post-export models would miss
// an adapter error common to both models.
export function canonicalSemantics(c) {
    let signature=c.metadata.time_signature??{numerator:4,denominator:4};
    let tempo=c.metadata.tempo_bpm??120;
    const refs=new Map();
    const measureData=c.measures.map((m,mi)=>{
        if(m.time_signature) signature=m.time_signature;
        if(m.tempo_bpm!==null) tempo=m.tempo_bpm;
        const voices=[...new Set(m.events.map(e=>e.voice))].sort((a,b)=>a-b).map(v=>({voice:v,
            events:m.events.filter(e=>e.voice===v).map((e,ei)=>{
                const notes=e.notes.map(n=>{
                    refs.set(`${mi+1}/${e.index}/${n.string}`,{measure:mi+1,voice:v,beat:ei+1,string:n.string});
                    const has=t=>n.techniques.includes(t);
                    const bendType=has('bend')?'bend':has('release_bend')?'release_bend':null;
                    const amount=n.technique_parameters?.find(p=>p.type===bendType)?.amount_semitones;
                    return {string:n.string,fret:n.fret,dead:n.dead||has('dead_note'),ghost:has('ghost'),
                        harmonic:has('natural_harmonic')?'Natural':'None',
                        harmonic_value:has('natural_harmonic')?n.fret:0,
                        accent:has('accent'),palm_mute:has('palm_mute'),
                        let_ring:has('let_ring')||c.annotations.some(a=>a.type==='let_ring'&&(a.scope==='score'?mi+1>=a.measure:mi+1===a.measure)),
                        vibrato:has('vibrato')?'Slight':'None',bend:amount==null?[]:(bendType==='bend'?[[0,0],[60,amount*2]]:[[0,amount*2],[60,0]])};
                });
                return {duration:e.duration,dots:e.dots,tuplet:e.tuplet,rest:e.rest,notes:sortNotes(notes)};
            })}));
        return {signature:{...signature},tempo,repeat_start:m.barline.repeat_start,repeat_end:m.barline.repeat_end,
            repeat_count:m.barline.repeat_end?(m.barline.repeat_count??2):0,endings:[...m.barline.ending_numbers].sort((a,b)=>a-b),
            pickup:m.pickup&&mi===0,barline_end:mi===c.measures.length-1?'final':m.barline.end,voices};
    });
    const relations=[];
    for(const r of c.relations) {
        if(!r.to)continue;
        const from=refs.get(address(r.from)),to=refs.get(address(r.to));
        const cn=c.measures[r.from.measure-1].events.find(e=>e.index===r.from.event).notes.find(n=>n.string===r.from.string);
        const tn=c.measures[r.to.measure-1].events.find(e=>e.index===r.to.event).notes.find(n=>n.string===r.to.string);
        if(['tie','hammer_on','pull_off'].includes(r.type)) relations.push({type:r.type,from,to});
        else if(['slide_up','slide_down','shift_slide','legato_slide'].includes(r.type)) {
            const legato=r.type==='legato_slide'||c.relations.some(s=>s.type==='slur'&&s.to&&address(s.from)===address(r.from)&&address(s.to)===address(r.to));
            relations.push({type:tn.fret>cn.fret?'slide_up':'slide_down',style:legato?'Legato':'Shift',from,to});
        }
    }
    return {metadata:{title:c.metadata.title??'',artist:c.metadata.artist??'',tuning:c.metadata.tuning??[64,59,55,50,45,40],
            capo:c.metadata.capo??0,tempo:measureData[0]?.tempo??c.metadata.tempo_bpm??120,program:24},
        measures:measureData,relations:normalizeRelations(relations),
        annotations:c.annotations.map(a=>({measure:a.measure,text:a.text})).sort((a,b)=>a.measure-b.measure)};
}

export function importedSemantics(score) {
    const staff=score.tracks[0]?.staves[0];
    if(!staff) return {error:'No guitar staff'};
    const ref=n=>({measure:n.beat.voice.bar.index+1,voice:n.beat.voice.index+1,beat:n.beat.index+1,string:7-n.string});
    let tempo=score.tempo;
    const relations=[],annotations=[];
    const measures=score.masterBars.map((m,mi)=>{
        if(m.tempoAutomations.length)tempo=m.tempoAutomations[0].value;
        const bar=staff.bars[mi];
        const voices=(bar?.voices??[]).filter(v=>v.beats.some(b=>!b.isEmpty)).map(v=>({voice:v.index+1,
            events:v.beats.filter(b=>!b.isEmpty).map(b=>{
                if(b.text)annotations.push({measure:mi+1,text:b.text});
                const notes=b.notes.map(n=>{
                    if(n.isTieDestination) relations.push({type:'tie',from:n.tieOrigin?ref(n.tieOrigin):null,to:ref(n)});
                    if(n.isHammerPullOrigin) relations.push({type:n.hammerPullDestination?.fret>n.fret?'hammer_on':'pull_off',from:ref(n),to:n.hammerPullDestination?ref(n.hammerPullDestination):null});
                    if([M.SlideOutType.Shift,M.SlideOutType.Legato].includes(n.slideOutType)) relations.push({type:n.slideTarget?.fret>n.fret?'slide_up':'slide_down',style:M.SlideOutType[n.slideOutType],from:ref(n),to:n.slideTarget?ref(n.slideTarget):null});
                    if(![M.SlideOutType.None,M.SlideOutType.Shift,M.SlideOutType.Legato].includes(n.slideOutType))relations.push({type:'unexpected_slide_out',from:ref(n),style:M.SlideOutType[n.slideOutType]});
                    return {string:7-n.string,fret:n.fret,dead:n.isDead,ghost:n.isGhost,harmonic:M.HarmonicType[n.harmonicType],harmonic_value:n.harmonicValue,
                        accent:n.accentuated===M.AccentuationType.Normal,palm_mute:n.isPalmMute,let_ring:n.isLetRing,
                        vibrato:M.VibratoType[n.vibrato],bend:n.bendPoints?.map(p=>[p.offset,p.value])??[]};
                });
                return {duration:b.duration,dots:b.dots,tuplet:b.hasTuplet?{numerator:b.tupletNumerator,denominator:b.tupletDenominator}:null,rest:b.isRest,notes:sortNotes(notes)};
            })}));
        const endings=[];for(let bit=0;bit<32;bit++)if((m.alternateEndings>>>bit)&1)endings.push(bit+1);
        return {signature:{numerator:m.timeSignatureNumerator,denominator:m.timeSignatureDenominator},tempo,
            repeat_start:m.isRepeatStart,repeat_end:m.isRepeatEnd,repeat_count:m.repeatCount,endings,pickup:m.isAnacrusis,
            barline_end:mi===score.masterBars.length-1?'final':m.isDoubleBar?'double':'normal',voices};
    });
    return {metadata:{title:score.title,artist:score.artist,tuning:staff.tuning,capo:staff.capo,tempo:score.tempo,program:score.tracks[0].playbackInfo.program},
        measures,relations:normalizeRelations(relations),annotations:annotations.sort((a,b)=>a.measure-b.measure)};
}

export function compare(canonical, imported, mapping) {
    const expected=canonicalSemantics(canonical),actual=importedSemantics(imported);
    const mismatches=[];let exact=0;
    function visit(a,b,path) {
        if(JSON.stringify(a)===JSON.stringify(b)){exact++;return;}
        if(Array.isArray(a)&&Array.isArray(b)) {
            if(a.length!==b.length)mismatches.push({path:path+'.length',expected:a.length,actual:b.length,classification:'UNEXPECTED_MISMATCH'});
            for(let i=0;i<Math.max(a.length,b.length);i++)visit(a[i],b[i],`${path}[${i}]`);
        } else if(a&&b&&typeof a==='object'&&typeof b==='object'&&!Array.isArray(a)&&!Array.isArray(b)) {
            for(const k of new Set([...Object.keys(a),...Object.keys(b)]))visit(a[k],b[k],path+'.'+k);
        } else mismatches.push({path,expected:a??null,actual:b??null,classification:'UNEXPECTED_MISMATCH'});
    }
    visit(expected,actual,'score');
    if(imported.tracks.length!==1||imported.tracks[0].staves.length!==1)mismatches.push({path:'score.tracks',classification:'UNEXPECTED_MISMATCH',issue:'Expected exactly one track and staff'});
    const count=(s,kind)=>s.measures.reduce((n,m)=>n+m.voices.reduce((n,v)=>n+v.events.reduce((n,e)=>n+(kind==='notes'?e.notes.length:1),0),0),0);
    return {valid:mismatches.length===0,canonical_measures:canonical.measures.length,roundtrip_measures:imported.masterBars.length,
        canonical_notes:count(expected,'notes'),roundtrip_notes:actual.measures?count(actual,'notes'):0,
        canonical_events:count(expected,'events'),roundtrip_events:actual.measures?count(actual,'events'):0,
        exact_matches:[{classification:'EXACT',checks:'All projected metadata, written measure/voice/event order, string/fret chords, durations/dots/tuplets/rests, repeats/endings, final bar, techniques and relation endpoints',passed:mismatches.length===0,matching_subtrees:exact}],
        expected_defaults:mapping.technical_defaults.map(d=>({classification:'EXPECTED_EXPORT_DEFAULT',...d})),
        known_losses:[...mapping.unsupported_or_partial,...mapping.unresolved_skipped].map(d=>({classification:'KNOWN_UNSUPPORTED_MAPPING',...d})),
        unexpected_mismatches:mismatches,comparison:{expected,actual}};
}
