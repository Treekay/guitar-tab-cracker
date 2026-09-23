"""Validate explicit transcription data; never inspect pixels or repair music.

Requires jsonschema. Durations are exact fractions of a whole note. Each voice
is sequential; ties retain written durations and do not introduce attacks.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).resolve().parents[1] / 'schema/score.schema.json'


def duration(event):
    if event['duration'] is None:
        return None
    value = Fraction(1, event['duration']) * sum((Fraction(1, 2**d) for d in range(event['dots']+1)), Fraction())
    if event['tuplet']:
        value *= Fraction(event['tuplet']['denominator'], event['tuplet']['numerator'])
    return value


def validate(score, base, manifest, selected=None):
    errors, warnings, rhythms = [], [], []
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    for error in Draft202012Validator(schema).iter_errors(score):
        errors.append({'path': '/'.join(map(str, error.absolute_path)), 'issue': error.message})
    if errors:
        return {'valid': False, 'errors': errors, 'warnings': [], 'rhythmic_totals': []}
    measures = score['measures']
    expected = manifest if selected is None else [m for m in manifest if m['sequence_index'] in selected]
    if selected is not None and (len(set(selected)) != len(selected) or len(expected) != len(selected)):
        errors.append({'issue': 'Sample indices are duplicated or absent from V2 manifest'})
    if [m['sequence_index'] for m in measures] != list(range(1,len(measures)+1)):
        errors.append({'issue':'Measure indices are not contiguous from 1'})
    if len(measures) != len(expected):
        errors.append({'issue':'V2/V3 measure counts differ'})
    seen = set()
    refs = {}
    for m, original in zip(measures,expected):
        path = (base/m['source']['image']).resolve()
        # Manifest paths are relative to the V2 result, the parent of v3.
        if path != (base.parent/original['output']).resolve():
            errors.append({'measure':m['sequence_index'],'issue':'Source order/path differs from V2 manifest'})
        if not path.is_file():
            errors.append({'measure':m['sequence_index'],'issue':'Source image missing'})
        if path in seen:
            errors.append({'measure':m['sequence_index'],'issue':'Duplicate source image'})
        seen.add(path)
        if m['printed_measure_number'] != original['printed_measure_number']:
            errors.append({'measure':m['sequence_index'],'issue':'Printed number differs from V2 provenance'})
        if 'core_bbox_in_output' in original and m['source']['core_bbox_in_image'] != original['core_bbox_in_output']:
            errors.append({'measure':m['sequence_index'],'issue':'Core boundary differs from V2 provenance'})
    sig = score['metadata']['time_signature']
    for m in measures:
        seq=m['sequence_index']
        if m['time_signature'] is not None:
            sig=m['time_signature']
        if [e['index'] for e in m['events']] != list(range(1,len(m['events'])+1)):
            errors.append({'measure':seq,'issue':'Event indices are not contiguous from 1'})
        voices={}
        for e in m['events']:
            if e.get('brush') is not None and (e['rest'] or len(e['notes']) < 2):
                errors.append({'measure':seq,'event':e['index'],'issue':'Brush requires a chord with at least two notes'})
            if e.get('pick_stroke') is not None and e['rest']:
                errors.append({'measure':seq,'event':e['index'],'issue':'Pick stroke cannot be applied to a rest'})
            strings=[n['string'] for n in e['notes']]
            if len(strings) != len(set(strings)):
                errors.append({'measure':seq,'event':e['index'],'issue':'Duplicate string in simultaneous event'})
            if e['rest'] == bool(e['notes']):
                errors.append({'measure':seq,'event':e['index'],'issue':'Rest must have no notes; non-rest must have notes'})
            for n in e['notes']:
                refs[(seq,e['index'],n['string'])]=n
                if n['fret'] is None and not n['dead'] and not n['uncertainty']:
                    errors.append({'measure':seq,'event':e['index'],'issue':'Unknown fret requires uncertainty'})
            d=duration(e)
            voices.setdefault(e['voice'],[]).append(d)
            if d is None and not e['uncertainty']:
                errors.append({'measure':seq,'event':e['index'],'issue':'Unknown duration requires uncertainty'})
        for voice,values in voices.items():
            total=None if None in values else sum(values,Fraction())
            target=Fraction(sig['numerator'],sig['denominator']) if sig else None
            rhythms.append({'measure':seq,'voice':voice,'total':str(total) if total is not None else None,
                            'expected':str(target) if target is not None else None,'pickup':m['pickup']})
            if total is None or (target is not None and total != target and not (m['pickup'] and total < target)):
                warnings.append({'measure':seq,'voice':voice,'issue':'Review rhythmic total against source; never auto-repair','total':str(total),'expected':str(target)})
    relation_ids=set()
    incoming=set()
    def key(ref):
        return (ref['measure'],ref['event'],ref['string'])
    for r in score['relations']:
        if r['id'] in relation_ids:
            errors.append({'issue':'Duplicate relation id','relation':r['id']})
        relation_ids.add(r['id'])
        a,b=key(r['from']),key(r['to']) if r['to'] else None
        if a not in refs or (b is not None and b not in refs):
            errors.append({'issue':'Invalid note reference','relation':r['id']})
            continue
        if b is None:
            if not r['uncertainty']:
                errors.append({'issue':'Open relation needs uncertainty','relation':r['id']})
            continue
        if r['type']=='tie':
            incoming.add(b)
            if a>=b or a[2]!=b[2] or refs[a]['fret']!=refs[b]['fret']:
                errors.append({'issue':'Tie must link same string/fret forward in written order','relation':r['id']})
    for ref,n in refs.items():
        if n['display']=='tie_continuation' and ref not in incoming:
            errors.append({'issue':'Continuation without incoming tie','reference':list(ref)})
    byseq={m['sequence_index']:m for m in measures}
    for a in score['annotations']:
        if a['measure'] not in byseq:
            errors.append({'issue':'Annotation references absent measure'})
    for u in score['unresolved']:
        m=byseq.get(u['measure'])
        if u['measure'] is not None and (m is None or (u['event'] is not None and u['event'] not in [e['index'] for e in m['events']])):
            errors.append({'issue':'Unresolved item references absent measure/event'})
    starts,ends=set(),set()
    ending_map={}
    for r in score['repeat_regions']:
        a,b=r['start_measure'],r['end_measure']
        if a not in byseq or b not in byseq or a>b:
            errors.append({'issue':'Invalid repeat span'})
            continue
        if a in starts or b in ends:
            errors.append({'issue':'Duplicate repeat span'})
        starts.add(a); ends.add(b)
        if not byseq[a]['barline']['repeat_start'] or not byseq[b]['barline']['repeat_end']:
            errors.append({'issue':'Repeat region and barline flags disagree'})
        if r['count'] != byseq[b]['barline']['repeat_count']:
            errors.append({'issue':'Repeat counts disagree'})
        numbers=set()
        for ending in r['endings']:
            x,y=ending['start_measure'],ending['end_measure']
            if x<a or x>y or y not in byseq:
                errors.append({'issue':'Invalid alternate-ending span'})
            if numbers.intersection(ending['numbers']):
                errors.append({'issue':'Duplicate alternate-ending number'})
            numbers.update(ending['numbers'])
            for s in range(x,y+1):
                if s in ending_map:
                    errors.append({'issue':'Overlapping alternate endings'})
                ending_map[s]=ending['numbers']
    for m in measures:
        s,b=m['sequence_index'],m['barline']
        if b['repeat_start'] != (s in starts) or b['repeat_end'] != (s in ends):
            errors.append({'measure':s,'issue':'Unpaired repeat barline'})
        if b['repeat_count'] is not None and not b['repeat_end']:
            errors.append({'measure':s,'issue':'Repeat count without repeat end'})
        if b['ending_numbers'] != ending_map.get(s,[]):
            errors.append({'measure':s,'issue':'Ending numbers disagree with regions'})
        if b['end']=='final' and s != len(measures):
            warnings.append({'measure':s,'issue':'Final bar before last written unit; review'})
        if m['audit']['pass2']!='inspected':
            warnings.append({'measure':s,'issue':'Second visual pass pending'})
    # Every explicit uncertainty is included in the issue inventory, independently
    # of manually authored root unresolved records.
    uncertainties=[]
    def walk(obj,path=''):
        if isinstance(obj,dict):
            if obj.get('uncertainty'):
                uncertainties.append({'path':path,'issue':obj['uncertainty']})
                if not any(u['issue']==obj['uncertainty'] for u in score['unresolved']):
                    errors.append({'path':path,'issue':'Uncertainty absent from root unresolved inventory'})
            if obj.get('confidence') in ('medium','low') and not (obj.get('uncertainty') or obj.get('issue')):
                errors.append({'path':path,'issue':'Medium/low confidence requires uncertainty'})
            for k,v in obj.items(): walk(v,path+'/'+k)
        elif isinstance(obj,list):
            for i,v in enumerate(obj): walk(v,path+'/'+str(i))
    walk(score)
    return dict(valid=not errors,errors=errors,warnings=warnings,rhythmic_totals=rhythms,
                scope='complete' if selected is None else 'sample',measure_count=len(measures),
                event_count=sum(len(m['events']) for m in measures),
                note_count=len(refs),rest_count=sum(e['rest'] for m in measures for e in m['events']),
                uncertainties=uncertainties,unresolved=score['unresolved'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('score',type=Path)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--selected-indices',type=int,nargs='+',help='Explicit sample only; never complete acceptance')
    args=parser.parse_args()
    result=validate(json.loads(args.score.read_text(encoding='utf-8')),args.score.resolve().parent,
                    json.loads(args.manifest.read_text(encoding='utf-8')),args.selected_indices)
    output=args.output or args.score.with_name('validation.json')
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rhythmic_totals','uncertainties','unresolved')}))
    raise SystemExit(0 if result['valid'] else 1)


if __name__=='__main__': main()
