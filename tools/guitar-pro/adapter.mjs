import * as alphaTab from '@coderline/alphatab';

export { alphaTab };
const M = alphaTab.model;
export function canonicalStringToAlphaTab(string) {
    if (!Number.isInteger(string) || string < 1 || string > 6) throw new Error(`Invalid canonical string ${string}`);
    return 7 - string;
}
export const durations = Object.freeze({1:M.Duration.Whole,2:M.Duration.Half,4:M.Duration.Quarter,
    8:M.Duration.Eighth,16:M.Duration.Sixteenth,32:M.Duration.ThirtySecond,64:M.Duration.SixtyFourth});
const key = r => `${r.measure}/${r.event}/${r.string}`;
const pair = r => `${key(r.from)}>${r.to ? key(r.to) : '?'}`;
const requireValue = (condition, message) => { if (!condition) throw new Error(message); };

export function adapt(canonical) {
    requireValue(canonical.schema_version === 1, 'Unsupported canonical schema');
    requireValue(canonical.string_convention === '1=top/highest;6=bottom/lowest', 'Unknown string convention');
    const mapping = {exporter:'alphaTab Gp7Exporter', library_version:'1.8.4', canonical_schema_version:1,
        technical_defaults:[], unsupported_or_partial:[], unresolved_skipped:[],
        string_mapping:Object.fromEntries([1,2,3,4,5,6].map(s=>[s,canonicalStringToAlphaTab(s)])),
        note_display_policy:'Keep ghost articulation separate; tie-continuation/parenthesis engraving is target-controlled.',
        preserved_annotations:[],
        // Source uncertainties can describe marks outside schema v1, not only
        // relations with null endpoints. Carry them through without guessing.
        canonical_unresolved:structuredClone(canonical.unresolved ?? []),
        source_measure_order:canonical.measures.map(m=>({sequence_index:m.sequence_index,printed_measure_number:m.printed_measure_number})),
        measure_numbering:'GP numbers written units sequentially; original printed labels are retained here, not in GP bar numbers.'};
    const defaultValue = (field, value, fallback, reason='required technical default') => {
        if (value !== null && value !== undefined) return value;
        mapping.technical_defaults.push({field,canonical:null,export_value:fallback,reason});
        return fallback;
    };
    const loss = (field, reason, value) => mapping.unsupported_or_partial.push({field,reason,canonical:value});
    M.Score.resetIds();
    const settings = new alphaTab.Settings();
    const score = new M.Score();
    score.title=defaultValue('metadata.title',canonical.metadata.title,'');
    score.artist=defaultValue('metadata.artist',canonical.metadata.artist,'');
    const tuning=defaultValue('metadata.tuning',canonical.metadata.tuning,[64,59,55,50,45,40]);
    const capo=defaultValue('metadata.capo',canonical.metadata.capo,0);
    let tempo=defaultValue('metadata.tempo_bpm',canonical.metadata.tempo_bpm,120);
    let signature=defaultValue('metadata.time_signature',canonical.metadata.time_signature,{numerator:4,denominator:4});
    const track=new M.Track();score.addTrack(track);track.name='Guitar';track.shortName='Gtr.';
    track.playbackInfo.program=24;track.playbackInfo.primaryChannel=0;track.playbackInfo.secondaryChannel=1;
    mapping.technical_defaults.push({field:'instrument',canonical:null,export_value:'GM program 24 (nylon guitar)',reason:'GP playback requires an instrument; not recognized source data'},
        {field:'notation.key_signature',canonical:null,export_value:'no accidentals',reason:'canonical carries no key signature; technical pitch spelling default'},
        {field:'notation.display_transposition',canonical:null,export_value:0,reason:'technical display default'},
        {field:'playback.dynamics',canonical:null,export_value:'F',reason:'alphaTab default beat dynamic; source has no dynamics field'},
        {field:'track.label',canonical:null,export_value:'Guitar / Gtr.',reason:'technical instrument label, not source attribution'});
    const staff=new M.Staff();track.addStaff(staff);staff.stringTuning=new M.Tuning('',[...tuning],false);
    staff.capo=capo;staff.showTablature=true;staff.showStandardNotation=false;
    const noteMap=new Map(), beatMap=new Map(), canonicalNotes=new Map();
    const noteOrder=[];
    for (const [mi,cm] of canonical.measures.entries()) {
        requireValue(cm.sequence_index===mi+1,'Canonical measures must be contiguous');
        if(cm.time_signature) signature=cm.time_signature;
        if(cm.tempo_bpm!==null) tempo=cm.tempo_bpm;
        const master=new M.MasterBar();master.timeSignatureNumerator=signature.numerator;
        master.timeSignatureDenominator=signature.denominator;
        master.isRepeatStart=cm.barline.repeat_start;
        master.repeatCount=cm.barline.repeat_end ? defaultValue(`measures.${mi+1}.repeat_count`,cm.barline.repeat_count,2) : 0;
        master.alternateEndings=cm.barline.ending_numbers.reduce((bits,n)=>{
            requireValue(Number.isInteger(n)&&n>=1&&n<=M.MasterBar.MaxAlternateEndings,'Ending outside target bitmask');
            return bits | (1<<(n-1));
        },0);
        master.isDoubleBar=cm.barline.end==='double';
        master.isAnacrusis=cm.pickup && mi===0;
        if(cm.pickup && mi!==0) loss(`measures.${mi+1}.pickup`,'GP writer only supports score-initial anacrusis',true);
        if(cm.barline.start!=='normal') loss(`measures.${mi+1}.barline.start`,'GP writer does not serialize independent left bar styles',cm.barline.start);
        if(cm.barline.end==='final' && mi!==canonical.measures.length-1) throw new Error('Internal final bar unsupported; cannot silently remove a score boundary');
        if(mi===canonical.measures.length-1 && cm.barline.end!=='final') {
            mapping.technical_defaults.push({field:`measures.${mi+1}.barline.end`,canonical:cm.barline.end,export_value:'final',reason:'GP terminates the exported score/sample with an implicit final bar'});
        }
        if(mi===0 || cm.tempo_bpm!==null) {
            const auto=new M.Automation();auto.type=M.AutomationType.Tempo;auto.value=tempo;auto.ratioPosition=0;auto.isLinear=false;
            master.tempoAutomations.push(auto);
        }
        score.addMasterBar(master);
        const bar=new M.Bar();staff.addBar(bar);
        const maxVoice=Math.max(...cm.events.map(e=>e.voice));
        requireValue(maxVoice<=4,'GP supports at most four voices per staff');
        const voices=Array.from({length:maxVoice},()=>{const v=new M.Voice();bar.addVoice(v);return v;});
        for(const [ei,ce] of cm.events.entries()) {
            requireValue(ce.index===ei+1,'Canonical event indices must be contiguous');
            requireValue(durations[ce.duration]!==undefined,`Unknown duration at measure ${mi+1} event ${ei+1}`);
            const beat=new M.Beat();voices[ce.voice-1].addBeat(beat);beat.duration=durations[ce.duration];beat.dots=ce.dots;
            if(ce.tuplet){beat.tupletNumerator=ce.tuplet.numerator;beat.tupletDenominator=ce.tuplet.denominator;}
            requireValue(ce.rest ? ce.notes.length===0 : ce.notes.length>0,'Invalid rest/notes combination');
            if (ce.brush != null) {
                const {type,direction}=ce.brush;
                requireValue(!ce.rest && ce.notes.length>=2,'Brush requires a chord');
                requireValue(['arpeggio','strum'].includes(type)&&['up','down'].includes(direction),'Invalid brush type/direction');
                // Canonical direction is the arrow on top-string-first TAB.
                // alphaTab Down renders an UP arrow (low strings to high strings).
                beat.brushType=type==='arpeggio'
                    ? (direction==='up'?M.BrushType.ArpeggioDown:M.BrushType.ArpeggioUp)
                    : (direction==='up'?M.BrushType.BrushDown:M.BrushType.BrushUp);
                const ticks=3840/ce.duration*(2-2**(-ce.dots))*(ce.tuplet?ce.tuplet.denominator/ce.tuplet.numerator:1);
                beat.brushDuration=Math.max(1,Math.min(type==='arpeggio'?240:60,Math.floor(ticks/2)));
                mapping.technical_defaults.push({field:`events.${mi+1}/${ce.index}.brush_duration_ticks`,canonical:null,
                    export_value:beat.brushDuration,reason:'Playback-only spread default (960 ticks/quarter): arpeggio 240, strum 60, capped at half the written event; source specifies type/direction, not timing'});
            }
            if (ce.pick_stroke != null) {
                requireValue(!ce.rest&&['up','down'].includes(ce.pick_stroke),'Invalid pick stroke');
                beat.pickStroke=ce.pick_stroke==='up'?M.PickStroke.Up:M.PickStroke.Down;
            }
            beatMap.set(`${mi+1}/${ce.index}`,beat);
            const strings=new Set();
            for(const cn of ce.notes) {
                requireValue(!strings.has(cn.string),'Duplicate string within a chord');strings.add(cn.string);
                requireValue(Number.isInteger(cn.fret)&&cn.fret>=0,`Unknown fret at ${mi+1}/${ce.index}/${cn.string}; cannot invent a target pitch`);
                const note=new M.Note();note.string=canonicalStringToAlphaTab(cn.string);note.fret=cn.fret;
                note.isDead=cn.dead;beat.addNote(note);
                const ref={measure:mi+1,event:ce.index,string:cn.string};
                noteMap.set(key(ref),note);canonicalNotes.set(key(ref),cn);noteOrder.push({ref,note,voice:ce.voice});
                if(cn.parenthesized && !cn.techniques.includes('ghost')) loss(`notes.${key(ref)}.parenthesized`,
                    'alphaTab GP writer cannot encode parentheses independently of ghost dynamics. Tie remains; target controls courtesy parentheses.',true);
                if(cn.display==='tie_continuation') loss(`notes.${key(ref)}.display`,
                    'Tie semantics retained; blank-fret versus courtesy-fret display is target-controlled.',cn.display);
                for(const technique of cn.techniques) {
                    const field=`notes.${key(ref)}.techniques.${technique}`;
                    const parameters=(cn.technique_parameters??[]).find(p=>p.type===technique);
                    switch(technique) {
                    case 'dead_note':note.isDead=true;break;
                    case 'ghost':note.isGhost=true;break;
                    case 'natural_harmonic':note.harmonicType=M.HarmonicType.Natural;note.harmonicValue=cn.fret;break;
                    case 'artificial_harmonic':
                        loss(field,'Canonical parameters do not define artificial-harmonic touch position; preserve fret and do not invent sounding pitch',technique);
                        break;
                    case 'accent':note.accentuated=M.AccentuationType.Normal;break;
                    case 'palm_mute':note.isPalmMute=true;break;
                    case 'let_ring':note.isLetRing=true;break;
                    case 'vibrato':
                        note.vibrato=M.VibratoType.Slight;
                        mapping.technical_defaults.push({field,canonical:technique,export_value:'Slight',reason:'target requires vibrato subtype; source supplies none'});break;
                    case 'bend':case 'release_bend': {
                        const amount=parameters?.amount_semitones;
                        if(amount==null){loss(field,'Bend amount unknown; do not invent pitch change',technique);break;}
                        requireValue(amount>=0 && Number.isInteger(amount*2),'Target bend amounts require nonnegative half-semitone steps');
                        note.addBendPoint(new M.BendPoint(0,technique==='bend'?0:amount*2));
                        note.addBendPoint(new M.BendPoint(60,technique==='bend'?amount*2:0));
                        mapping.technical_defaults.push({field:field+'.curve',canonical:parameters,export_value:'linear over full note',reason:'target bend timing requires a curve; canonical gives only amount'});break;
                    }
                    default:
                        if(!canonical.relations.some(r=>r.type===technique && (key(r.from)===key(ref)||r.to && key(r.to)===key(ref))))
                            loss(field,'Endpoint-dependent technique lacks an explicit relation',technique);
                    }
                }
            }
        }
        // Empty extra voice slots are structural padding, not canonical events.
        for(const voice of voices) if(!voice.beats.length){const b=new M.Beat();b.isEmpty=true;voice.addBeat(b);}
    }
    for(const annotation of canonical.annotations) {
        const beat=staff.bars[annotation.measure-1]?.voices[0]?.beats[0];
        requireValue(!!beat,'Annotation has invalid source measure');
        beat.text=[beat.text,annotation.text].filter(Boolean).join('\n');
        mapping.preserved_annotations.push(annotation);
        if(annotation.type==='let_ring') for(const entry of noteOrder) {
            if(annotation.scope==='score' ? entry.ref.measure>=annotation.measure : entry.ref.measure===annotation.measure) entry.note.isLetRing=true;
        }
    }
    const slurPairs=new Set(canonical.relations.filter(r=>r.type==='slur'&&r.to).map(pair));
    const slidePairs=new Set(canonical.relations.filter(r=>['slide_up','slide_down','shift_slide','legato_slide'].includes(r.type)&&r.to).map(pair));
    const nextOnString=(ref)=> {
        const index=noteOrder.findIndex(n=>key(n.ref)===key(ref)), origin=noteOrder[index];
        return noteOrder.slice(index+1).find(n=>n.voice===origin.voice && n.ref.string===ref.string)?.ref;
    };
    for(const relation of canonical.relations) {
        const from=noteMap.get(key(relation.from)), to=relation.to?noteMap.get(key(relation.to)):null;
        requireValue(!!from && (!relation.to || !!to),`Invalid relation ${relation.id}`);
        if(!relation.to){mapping.unresolved_skipped.push({...relation,reason:'No canonical endpoint; target-dependent effect omitted without guessing'});continue;}
        const field=`relations.${relation.id}`;
        if(relation.type==='tie') {
            requireValue(from.string===to.string && from.fret===to.fret,'Tie string/fret mismatch');
            to.isTieDestination=true;to.tieOrigin=from;from.tieDestination=to;
        } else if(['hammer_on','pull_off','slide_up','slide_down','shift_slide','legato_slide'].includes(relation.type)) {
            requireValue(nextOnString(relation.from) && key(nextOnString(relation.from))===key(relation.to),
                `Target API cannot preserve non-next same-string endpoint ${relation.id}`);
            if(relation.type==='hammer_on'||relation.type==='pull_off') {
                requireValue(relation.type==='hammer_on'?to.fret>from.fret:to.fret<from.fret,'HOPO direction contradicts canonical frets');
                from.isHammerPullOrigin=true;from.hammerPullDestination=to;to.hammerPullOrigin=from;
            } else {
                if(relation.type==='slide_up'||relation.type==='slide_down') requireValue(relation.type==='slide_up'?to.fret>from.fret:to.fret<from.fret,'Slide direction contradicts canonical frets');
                const legato=relation.type==='legato_slide'||slurPairs.has(pair(relation));
                from.slideOutType=legato?M.SlideOutType.Legato:M.SlideOutType.Shift;from.slideTarget=to;to.slideOrigin=from;
                if(['slide_up','slide_down'].includes(relation.type)&&!legato)
                    mapping.technical_defaults.push({field,canonical:relation.type,export_value:'Shift (un-slurred connecting slide)',reason:'GP requires articulation subtype; direction/endpoints retained without adding a slur'});
            }
        } else if(relation.type==='slur'&&slidePairs.has(pair(relation))) {
            // The paired slide already carries the explicit slur through Legato.
        } else loss(field,'Standalone relation type is not serialized by this adapter; notes retained',relation);
    }
    score.finish(settings);
    return {score,settings,mapping};
}
