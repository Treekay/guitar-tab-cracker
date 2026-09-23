"""Readable QA report from explicit structured data, with source-image links."""
import argparse
import json
from pathlib import Path


def report(root, selected):
    s=json.loads((root/'score.json').read_text(encoding='utf-8'))
    v=json.loads((root/'validation.json').read_text(encoding='utf-8'))
    techniques=set(r['type'] for r in s['relations'])
    techniques.update(a['type'] for a in s['annotations'])
    for m in s['measures']:
        for e in m['events']:
            for n in e['notes']: techniques.update(n['techniques'])
    lines=['# Structured transcription report','',
           f"Scope: {v['scope']}. Measures: {v['measure_count']}; events: {v['event_count']}; note records: {v['note_count']}; rests: {v['rest_count']}.",
           'Note records include written tied continuations; they are not a count of attacks.','',
           f"Validation: {'PASS' if v['valid'] else 'FAIL'}. Rhythmic warnings: {len(v['warnings'])}.",
           'Both visual passes recorded for every selected measure. Mechanical checks do not establish visual correctness.','',
           'Techniques: '+', '.join(sorted(techniques))+'.','',
           '## Repeat structures and alternate endings','',
           '```json',json.dumps(s['repeat_regions'],indent=2),'```','',
           'Repeat counts remain null unless a count is printed. Metadata is null when not visible in the images.','',
           '## Rhythmic warnings','', '```json',json.dumps(v['warnings'],indent=2),'```','',
           '## Medium / low confidence and unresolved items','']
    confidence_counts={'medium':0,'low':0}
    def scan(obj,path=''):
        if isinstance(obj,dict):
            if obj.get('confidence') in ('medium','low'):
                confidence_counts[obj['confidence']]+=1
                lines.append(f"- {path}: {obj['confidence']}; {obj.get('uncertainty') or obj.get('issue')}")
            for k,val in obj.items(): scan(val,path+'/'+k)
        elif isinstance(obj,list):
            for i,val in enumerate(obj):scan(val,path+'/'+str(i))
    scan(s)
    lines+=['',f"Medium-confidence records: {confidence_counts['medium']}; low-confidence records: {confidence_counts['low']}. Counts include parent summaries and unresolved records, not just distinct musical issues.",
            '', 'Complete unresolved inventory:','', '```json',json.dumps(s['unresolved'],indent=2),'```','',
            '## Source measures','']
    for m in s['measures']:
        seq=m['sequence_index']
        lines.append(f"- {seq:03} (printed {m['printed_measure_number']}): [source]({m['source']['image']}) · [JSON](measures/{seq:03}.json)")
    lines+=['','## Selected difficult measures','',
            'String 1 is the top/highest string. Durations are denominators; dots and tuplets are explicit.','']
    for m in s['measures']:
        seq=m['sequence_index']
        if seq not in selected:continue
        status=[x for x in v['warnings'] if x.get('measure')==seq]
        lines += [f'### Unit {seq:03} / printed {m["printed_measure_number"]}','',
                  f"![Source {seq}]({m['source']['image']})",'',
                  f'[Structured JSON](measures/{seq:03}.json). Validation: '+('review warnings' if status else 'no structural/rhythmic warnings')+'.','',
                  '| Event | Duration | Notes (string:fret) | Marks |','|---|---|---|---|']
        for e in m['events']:
            notes='rest' if e['rest'] else ', '.join(f"{n['string']}:{'('+str(n['fret'])+')' if n['parenthesized'] else n['fret']}" for n in e['notes'])
            marks=[n['display'] for n in e['notes'] if n['display']!='fret']
            marks += [t for n in e['notes'] for t in n['techniques']]
            if e['tuplet']:marks.append('tuplet '+str(e['tuplet']))
            if e.get('brush'):marks.append(e['brush']['type']+' arrow '+e['brush']['direction'])
            if e.get('pick_stroke'):marks.append('pick stroke '+e['pick_stroke'])
            lines.append(f"| {e['index']} | {e['duration']}{'.'*e['dots']} | {notes} | {', '.join(marks)} |")
        relations=[r for r in s['relations'] if r['from']['measure']==seq or (r['to'] and r['to']['measure']==seq)]
        if relations:lines+=['','Relations:','', '```json',json.dumps(relations,indent=2),'```']
        lines+=['']
    (root/'TRANSCRIPTION_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path);p.add_argument('--selected',type=int,nargs='+',required=True)
    a=p.parse_args();report(a.directory,a.selected)
