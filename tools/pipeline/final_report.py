"""Delivery summary of existing canonical/export/V4 evidence; no new recognition."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote

STATUSES=('VERIFIED','AUTO_CORRECTED','USER_REVIEW_REQUIRED','KNOWN_EXPORT_LIMITATION','UNEXPECTED_EXPORT_MISMATCH')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig')) if p.is_file() else None
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def rel(base,value):
    if not value:return None
    return (base/value).resolve().as_posix()

def normalize(raw,score,base):
    loc=raw.get('location',{});m=loc.get('measure')
    measure=next((x for x in (score or {}).get('measures',[]) if x['sequence_index']==m),None)
    field=loc.get('field') or loc.get('path') or raw.get('field') or raw.get('classification','unspecified')
    correction=raw.get('correction')
    return {'issue_id':raw['issue_id'],'status':raw['status'],
        'measure':{'sequence_index':m,'printed_number':measure.get('printed_measure_number') if measure else loc.get('printed_measure')},
        'event':loc.get('event'),'note':loc.get('note'),'string':loc.get('string'),'field':field,
        'current_value':raw.get('canonical_value',raw.get('current_value')),
        'exported_value':raw.get('exported_value'),'candidates':raw.get('candidates',[]),
        'reason':raw.get('notes',raw.get('reason','')),
        'source_image':rel(base,raw.get('source_image') or (measure or {}).get('source',{}).get('image')),
        'render_image':rel(base,raw.get('generated_image')),
        'v4_attempted_correction':raw.get('correction_attempted',raw['status']=='AUTO_CORRECTED'),
        'correction':correction,'impact':raw.get('impact','low' if raw['status']=='KNOWN_EXPORT_LIMITATION' else 'unknown'),
        'related_locations':[normalize({'issue_id':raw['issue_id']+f'-location-{i}', 'status':raw['status'],**x},score,base) for i,x in enumerate(raw.get('related_evidence',[]),1)],
        'evidence_origin':raw.get('evidence_origin','V4 verification')}

def delivery_status(checks,issues):
    if not all(checks.values()):return 'REVIEW_REQUIRED'
    if any(i['status']=='UNEXPECTED_EXPORT_MISMATCH' or (i['status']=='USER_REVIEW_REQUIRED' and i.get('impact')!='low') or i.get('impact') in ('high','core') for i in issues):return 'REVIEW_REQUIRED'
    if any(i['status'] in ('USER_REVIEW_REQUIRED','KNOWN_EXPORT_LIMITATION') for i in issues):return 'REVIEW_RECOMMENDED'
    return 'READY_FOR_DELIVERY'

def build(result):
    root=Path(result).resolve();base=root/'v3';score=read(base/'score.json');validation=read(base/'validation.json')
    rt=read(base/'export/roundtrip_validation.json');mapping=read(base/'export/export_mapping.json') or {}
    v4=read(base/'verification/verification.json') or {};timing=read(root/'timing.json');source=read(root/'source/source.json')
    raw=list(v4.get('issues',[]));checks={
        'acquisition':bool(source and source.get('status')=='success'),
        'canonical_validation':bool(validation and validation.get('valid') and not validation.get('warnings')),
        'gp_roundtrip':bool(rt and rt.get('valid') and not rt.get('unexpected_mismatches') and rt.get('canonical_sha256')==sha(base/'score.json') and rt.get('gp_sha256')==sha(base/'export/score.gp')),
        'v4_completed':bool(v4.get('mechanical_valid') and v4.get('source_sweep',{}).get('complete') and v4.get('canonical_sha256')==sha(base/'score.json') and v4.get('gp_sha256')==sha(base/'export/score.gp'))}
    # Final reporting only checks artifact freshness; it does not reread music.
    dossier=read(base/'verification/observations.json')
    if checks['v4_completed']:
        bound=(dossier or {}).get('artifacts',[])
        if not bound or any(sha(base/e['path'])!=e['sha256'] for e in bound):checks['v4_completed']=False
    for key,ok in checks.items():
        if not ok:
            raw.append({'issue_id':'gate-'+key,'status':'USER_REVIEW_REQUIRED','location':{'field':key},'impact':'high','canonical_value':False,'notes':'Required evidence is missing, stale or failed. '+(source.get('message','') if source and key=='acquisition' else '')})
    covered={(i.get('location',{}).get('measure'),i.get('location',{}).get('event'),i.get('location',{}).get('field')) for i in raw if i.get('status')!='VERIFIED'}
    for index,u in enumerate((score or {}).get('unresolved',[]),1):
        if (u.get('measure'),u.get('event'),u.get('field')) not in covered:
            raw.append({'issue_id':f'canonical-unresolved-{index}','status':'USER_REVIEW_REQUIRED','location':{k:u.get(k) for k in ('measure','event','field')},'canonical_value':u,'candidates':u.get('candidates',[]),'notes':u['issue'],'evidence_origin':'canonical unresolved inventory'})
    # Mapping omissions not already covered by an exact V4 location are visible.
    def locations(item):
        loc=item.get('location',{});yield loc
        for sub in item.get('related_evidence',[]):yield from locations(sub)
    known={(x.get('measure'),x.get('event'),x.get('string'),x.get('field')) for i in raw if i.get('status')=='KNOWN_EXPORT_LIMITATION' for x in locations(i)}
    for index,loss in enumerate(mapping.get('unsupported_or_partial',[])+mapping.get('unresolved_skipped',[]),1):
        field=loss.get('field','unknown');match=re.match(r'notes\.(\d+)/(\d+)/(\d+)\.(.+)',field)
        loc={'field':field}
        if match:loc=dict(zip(('measure','event','string'),map(int,match.groups()[:3])),field=match[4])
        if (loc.get('measure'),loc.get('event'),loc.get('string'),loc['field']) in known:continue
        # Some V4 relation issue groups cover loss records by canonical field.
        if any(i.get('canonical_value')==loss for i in raw):continue
        raw.append({'issue_id':f'export-limitation-{index}','status':'KNOWN_EXPORT_LIMITATION','location':loc,'canonical_value':loss.get('canonical'), 'notes':loss.get('reason',json.dumps(loss)),'evidence_origin':'export mapping'})
    for index,mismatch in enumerate((rt or {}).get('unexpected_mismatches',[]),1):
        path=mismatch.get('path','unknown');match=re.search(r'measures\[(\d+)\]',path);ev=re.search(r'events\[(\d+)\]',path)
        raw.append({'issue_id':f'export-mismatch-{index}','status':'UNEXPECTED_EXPORT_MISMATCH','location':{'measure':int(match[1])+1 if match else None,'event':int(ev[1])+1 if ev else None,'field':path},'canonical_value':mismatch.get('expected'),'exported_value':mismatch.get('actual'),'notes':mismatch.get('issue','Re-imported GP differs from canonical musical semantics'),'impact':'high','evidence_origin':'GP round-trip'})
    for item in raw:
        if item.get('status') not in STATUSES:raise ValueError('Unknown issue classification: '+str(item.get('status')))
    counts=Counter(i['status'] for i in raw)
    issues=[normalize(i,score,base) for i in raw if i['status']!='VERIFIED']
    # Fill generated system paths mechanically from alphaTab's layout metadata.
    layout=read(base/'export/rendered/score_render.json') or []
    def fill(item):
        m=item['measure']['sequence_index']
        if m and not item['render_image']:
            chunk=next((x for x in layout if x['first_master_bar']<=m-1<=x['last_master_bar']),None)
            if chunk:item['render_image']=(base/'export/rendered'/chunk['image']).as_posix()
        for sub in item['related_locations']:fill(sub)
    for issue in issues:fill(issue)
    totals={'measures':len(score['measures']),'events':sum(len(m['events']) for m in score['measures']),'notes':sum(len(e['notes']) for m in score['measures'] for e in m['events'])} if score else {'measures':None,'events':None,'notes':None}
    slowest=sorted([{'phase':k,'wall_seconds':v['wall_seconds']} for k,v in (timing or {}).get('phases',{}).items() if v['wall_seconds'] is not None],key=lambda x:x['wall_seconds'],reverse=True)[:3]
    result={'schema_version':1,'status':delivery_status(checks,issues),'counts':totals,'issue_counts':{s:counts[s] for s in STATUSES},'checks':checks,
        'accuracy_statement':'No independent ground-truth accuracy percentage is available. Confidence and exact GP round-trip are not source accuracy.',
        'evidence_reuse':(dossier or {}).get('evidence_reuse'),'issues':issues,'technical_defaults':mapping.get('technical_defaults',[]),'timing':timing,'slowest_phases':slowest,'source':source,
        'outputs':{'guitar_pro':(base/'export/score.gp').as_posix() if (base/'export/score.gp').is_file() else None,'source_pdf':(root/'full_score.pdf').as_posix() if (root/'full_score.pdf').is_file() else None,'verification_report':(base/'verification/verification_report.md').as_posix() if v4 else None},
        'evidence_hashes':{p:sha(root/p) for p in ['v3/score.json','v3/export/score.gp','v3/verification/verification.json','timing.json']}}
    root.mkdir(parents=True,exist_ok=True);write(root/'final_report.json',result)
    (root/'final_report.md').write_text(markdown(result,root),encoding='utf8');return result

def markdown(r,root):
    c=r['counts'];n=r['issue_counts'];t=r['timing'] or {}
    lines=['# Conversion result','',f"Status: **{r['status']}**",'',f"Measures: {c['measures']} · Events: {c['events']} · Notes: {c['notes']}",'',
           f"Verified issue groups: {n['VERIFIED']} · Auto-corrected: {n['AUTO_CORRECTED']} · Requires user review: {n['USER_REVIEW_REQUIRED']} · Known GP/export/preview limitations: {n['KNOWN_EXPORT_LIMITATION']} · Unexpected export mismatches: {n['UNEXPECTED_EXPORT_MISMATCH']}",'',r['accuracy_statement'],'','## Processing time','']
    for name,label in [('acquisition','Acquisition'),('v2','V2 reconstruction'),('v3','V3 transcription/assembly'),('guitar_pro','Guitar Pro export'),('v4','Verification')]:
        seconds=t.get('phases',{}).get(name,{}).get('wall_seconds');lines.append(f"- {label}: {seconds:.3f} s" if seconds is not None else f'- {label}: not measured/not executed')
    seconds=t.get('total_wall_seconds');lines+=([f'- Total: {seconds:.3f} s ({t.get("status")})'] if seconds is not None else ['- Total: unavailable; historical timings are not estimated'])
    lines+=['',f"Timing scope: {t.get('scope','unavailable')}. Unexecuted substeps remain null.",'']
    for stage in t.get('reused_stages',[]):lines.append(f"- Reused {stage['stage']}: {stage['source']}; no historical duration backfilled.")
    if r.get('evidence_reuse'):lines+=['','Verification evidence reuse: '+json.dumps(r['evidence_reuse'],ensure_ascii=False)]
    lines+=['','Slowest measured phases:','']+[f"{i}. {x['phase']}: {x['wall_seconds']:.3f} s" for i,x in enumerate(r['slowest_phases'],1)]
    def link(value,label):
        if not value:return label+': unavailable / not applicable'
        try:p=Path(value).relative_to(root).as_posix()
        except ValueError:p=Path(value).as_posix()
        return f'[{label}](<{p}>)'
    lines+=['','## Outputs','']+[f'- {link(v,k)}' for k,v in r['outputs'].items()]
    lines+=['','## Corrections, unresolved items and limitations','']
    for issue in r['issues']:
        loc=issue['measure'];at=f"measure {loc['sequence_index']} (printed {loc['printed_number']}), event {issue['event']}, string {issue['string']}"
        lines += [f"### {issue['issue_id']} — {issue['status']}",'',f"Location: {at}; field: `{issue['field']}`",'',issue['reason'],'',
                  'Current value: `'+json.dumps(issue['current_value'],ensure_ascii=False)+'`',
                  'Candidates: `'+json.dumps(issue['candidates'],ensure_ascii=False)+'`',
                  f"V4 correction attempted: {issue['v4_attempted_correction']}. Before/after: `"+json.dumps(issue['correction'],ensure_ascii=False)+'`','',
                  link(issue['source_image'],'Source')+' · '+link(issue['render_image'],'Generated comparison')]
        for x in issue['related_locations']:
            l=x['measure'];lines.append(f"- Also measure {l['sequence_index']} (printed {l['printed_number']}), event {x['event']}, string {x['string']}, {x['field']}: "+link(x['source_image'],'source')+' · '+link(x['render_image'],'generated'))
        lines.append('')
    lines+=['## Export defaults','','These are target requirements, not recognized source facts.','', '```json',json.dumps(r['technical_defaults'],indent=2,ensure_ascii=False),'```','']
    return '\n'.join(lines)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('result',type=Path);a=p.parse_args();r=build(a.result)
    print(json.dumps({k:r[k] for k in ['status','counts','issue_counts','slowest_phases']}))
