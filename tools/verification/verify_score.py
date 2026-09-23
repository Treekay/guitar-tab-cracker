"""Read-only verification/report orchestration. Visual judgments are explicit input."""
import argparse
from collections import Counter
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
from compare_transcriptions import compare_observation, sha
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_score import validate
from assemble_score import assemble


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def write(p, value):
    Path(p).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


def risks(score):
    found = []
    for m in score['measures']:
        features = set()
        b = m['barline']
        if b['repeat_start'] or b['repeat_end']: features.add('repeat')
        if b['ending_numbers']: features.add('alternate_ending')
        if b['end'] in ('final','double'): features.add('bar_boundary')
        for e in m['events']:
            if e.get('brush'): features.add(e['brush']['type'])
            if e.get('pick_stroke'): features.add('pick_stroke')
            if e['dots']: features.add('dotted_rhythm')
            if e['tuplet']: features.add('tuplet')
            if len(e['notes']) > 1: features.add('chord')
            for n in e['notes']:
                if n['fret'] is not None and n['fret'] >= 10: features.add('multidigit_fret')
                if n['parenthesized']: features.add('parentheses_not_ghost')
                if n['display'] == 'tie_continuation': features.add('tie_continuation')
                features.update(n['techniques'])
        for r in score['relations']:
            if r['from']['measure'] == m['sequence_index']:
                features.add(r['type'])
                if not r['to']: features.add('unknown_endpoint')
                elif r['to']['measure'] != r['from']['measure']: features.add('cross_bar_relation')
        if features: found.append({'measure':m['sequence_index'], 'features':sorted(features)})
    return found


def check_source_sweep(score, entries, base):
    """Validate provenance/coverage of authored rereads, never infer from pixels."""
    if entries is None:
        return {'recorded':False,'complete':False,'measures':0}
    expected=[m['sequence_index'] for m in score['measures']]
    errors=[]
    if [e.get('measure') for e in entries] != expected:
        errors.append('Source sweep must cover each written measure once, in order')
    for entry in entries:
        evidence=entry.get('source_evidence',[])
        if (entry.get('method')!='independent_source_reread' or
            entry.get('all_events_reread') is not True or not entry.get('features') or
            not entry.get('events') or not evidence):
            errors.append(f"Incomplete authored reread: {entry.get('measure')}")
        for e in evidence:
            p=Path(base)/e['path']
            if not p.is_file() or sha(p)!=e['sha256']:
                errors.append(f"Stale source sweep evidence: {entry.get('measure')}")
    return {'recorded':True,'complete':not errors,'measures':len(entries),'errors':errors,
            'limit':'Coverage and evidence checks authenticate recorded agent judgments, not their musical correctness.'}


def untriaged_source_items(score, issues):
    """Do not let a passing GP round-trip conceal canonical unresolved data."""
    def location(item):
        return tuple(item.get(k) for k in ('measure','event','field'))
    covered={location(i.get('location',{})) for i in issues
             if i.get('status') in ('USER_REVIEW_REQUIRED','KNOWN_EXPORT_LIMITATION')}
    return [u for u in score.get('unresolved',[]) if location(u) not in covered]


def run(score_path, dossier_path, output):
    score_path=Path(score_path).resolve(); base=score_path.parent
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    score=read(score_path); dossier=read(dossier_path)
    if dossier['canonical_sha256'] != sha(score_path): raise ValueError('Stale canonical evidence')
    gp=base/'export/score.gp'
    if dossier['gp_sha256'] != sha(gp): raise ValueError('Stale GP/render evidence')
    for e in dossier['artifacts']:
        if sha(base/e['path']) != e['sha256']: raise ValueError('Stale artifact: '+e['path'])
    canonical_validation=validate(score,base,read(base.parent/'measures.json'),dossier.get('selected_indices'))
    write(output/'canonical_validation.json',canonical_validation)
    rebuilt=assemble(read(base/'header.json'),base/'measures')
    assembly_matches=rebuilt==score
    command=['node',str(Path(__file__).with_name('inspect_gp.mjs')),str(score_path),str(gp),
             str(base/'export/export_mapping.json'),str(output/'fresh_roundtrip.json')]
    completed=subprocess.run(command,capture_output=True,text=True)
    if completed.returncode not in (0,1) or not (output/'fresh_roundtrip.json').exists():
        raise ValueError('GP import failed: '+completed.stderr)
    roundtrip=read(output/'fresh_roundtrip.json')
    if completed.returncode and roundtrip['valid']: raise ValueError('Importer failed without a mismatch report')
    observations=[compare_observation(score,o,base) for o in dossier['observations']]
    sweep=check_source_sweep(score,dossier.get('source_sweep'),base)
    issues=list(dossier['issues'])
    for index,u in enumerate(untriaged_source_items(score,issues),1):
        issues.append({'issue_id':f'untriaged-source-{index:03}',
          'location':{k:u.get(k) for k in ('measure','event','field')},
          'status':'USER_REVIEW_REQUIRED','earliest_fault_stage':'canonical unresolved inventory',
          'classification':'untriaged source uncertainty','correctable_automatically':False,
          'canonical_value':u,'exported_value':None,'manual_reference_value':None,
          'candidates':u.get('candidates',[]),'notes':u['issue']})
    for index,observation in enumerate(observations,1):
        if observation['status']=='VERIFIED': continue
        parts=observation['path'].strip('/').split('/')
        measure=int(parts[1])+1 if parts[0]=='measures' else None
        event=int(parts[parts.index('events')+1])+1 if 'events' in parts else None
        issues.append({'issue_id':f'field-review-{index:03}',
          'location':{'measure':measure,'event':event,'path':observation['path']},
          'source_evidence':observation.get('evidence',[]),
          'canonical_value':observation['canonical_value'],
          'exported_value':None,'manual_reference_value':None,
          'earliest_fault_stage':'pending localization','classification':'unlocalized discrepancy',
          'status':'USER_REVIEW_REQUIRED','correctable_automatically':observation['correctable_automatically'],
          'source_image':observation['evidence'][0]['path'] if observation.get('evidence') else None,
          'candidates':[observation['observed_value']],
          'notes':'Independent field check failed or its evidence is stale/ambiguous. Trace the exact field before any correction; no patch has been applied.'})
    allowed={'VERIFIED','AUTO_CORRECTED','USER_REVIEW_REQUIRED','KNOWN_EXPORT_LIMITATION'}
    for issue in issues:
        if not re.fullmatch(r'[A-Za-z0-9_-]+',issue['issue_id']): raise ValueError('Unsafe issue identifier')
        if issue['status'] not in allowed: raise ValueError('Invalid verification status')
        if issue['status']=='AUTO_CORRECTED':
            raise ValueError('Read-only review cannot assert AUTO_CORRECTED; requires separate revalidated correction receipt')
    status_counts=Counter(i['status'] for i in issues)
    mechanical=canonical_validation['valid'] and not canonical_validation['warnings'] and assembly_matches and roundtrip['valid']
    result={'schema_version':1,'canonical_sha256':sha(score_path),'gp_sha256':sha(gp),
      'scope':('Recorded all-measure source reread plus field comparison and deterministic checks' if sweep['complete'] else 'Targeted forensic verification plus full deterministic checks; not a fresh all-note visual audit'),
      'source_sweep':sweep,
      'status':'VERIFIED' if mechanical and not status_counts['USER_REVIEW_REQUIRED'] and all(o['status']=='VERIFIED' for o in observations) and (not sweep['recorded'] or sweep['complete']) else 'USER_REVIEW_REQUIRED',
      'mechanical_valid':mechanical,'assembly_matches':assembly_matches,
      'totals':{'measures':len(score['measures']),'events':sum(len(m['events']) for m in score['measures']),
                'notes':sum(len(e['notes']) for m in score['measures'] for e in m['events'])},
      'item_counts':{s:status_counts[s] for s in sorted(allowed)},
      'verified_observation_fields':sum(o['status']=='VERIFIED' for o in observations),
      'observations':observations,'issues':issues,'risk_inventory':risks(score),
      'risk_inventory_limit':'Canonical-derived flags cannot find omitted marks; mandatory independent source feature sweep remains required.',
      'benchmark':dossier.get('benchmark'), 'auto_corrections':[]}
    result['delivery_status']='READY_FOR_DELIVERY' if result['status']=='VERIFIED' and sweep['complete'] else 'REVIEW_REQUIRED'
    rows=['# Verification report', '', 'Status: '+result['status'],
          'Scope: '+result['scope'], 'Mechanical checks: '+('PASS' if mechanical else 'FAIL'),
          'Totals: '+str(result['totals']), 'Item counts: '+str(result['item_counts']),
          'Delivery status: '+result['delivery_status'],
          'This verifier is read-only; it has not changed canonical data.', '',
          '## Items requiring user review', '']
    for issue in issues:
        item=output/'review'/issue['issue_id'];item.mkdir(parents=True,exist_ok=True)
        for label in ['source','generated','manual']:
            relative=issue.get(label+'_image')
            if relative:
                src=(base/relative).resolve(); dest=item/(label+src.suffix)
                if src!=dest:shutil.copyfile(src,dest)
                issue[label+'_review_file']=str(dest.relative_to(output)).replace('\\','/')
        for number,related in enumerate(issue.get('related_evidence',[]),1):
            for label in ['source','generated','manual']:
                if label+'_image' in related:
                    src=base/related[label+'_image'];dest=item/f'{label}_{number:03}{src.suffix}'
                    shutil.copyfile(src,dest)
                    related[label+'_review_file']=dest.relative_to(output).as_posix()
        write(item/'issue.json',issue)
        if issue['status']=='USER_REVIEW_REQUIRED':
            rows.extend(['### '+issue['issue_id'],json.dumps(issue['location'],ensure_ascii=False),
                         issue['notes'],'Candidates: '+json.dumps(issue.get('candidates',[]),ensure_ascii=False)])
            for label in ['source','generated','manual']:
                if label+'_review_file' in issue:rows.append('['+label+']('+issue[label+'_review_file']+')')
            for related in issue.get('related_evidence',[]):
                rows.append('Related location: '+json.dumps(related['location']))
                for label in ['source','generated','manual']:
                    if label+'_review_file' in related: rows.append('['+label+']('+related[label+'_review_file']+')')
            rows.append('')
    rows+=['## All findings','','| ID | Location | Status | Earliest stage | Finding |','|---|---|---|---|---|']
    rows += ['| '+ ' | '.join([i['issue_id'],str(i['location']),i['status'],i['earliest_fault_stage'],i['notes'].replace('|','/')])+' |' for i in issues]
    rows+=['','VERIFIED applies to the recorded item/field, not every uninspected feature in that measure.',
           'Benchmark agreement is not source correctness. Read verification.json for evidence hashes, exact values, observations and risk inventory.', '']
    write(output/'verification.json',result)
    (output/'verification_report.md').write_text('\n'.join(rows),encoding='utf-8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('score');p.add_argument('dossier');p.add_argument('--output',required=True)
    a=p.parse_args();r=run(a.score,a.dossier,a.output)
    print(json.dumps({k:r[k] for k in ['status','mechanical_valid','totals','item_counts']}))
    if not r['mechanical_valid']:sys.exit(1)
