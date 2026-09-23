"""Mechanical stage tracking and delivery gate. Agent prose is never success."""
import hashlib
import json
from pathlib import Path
import subprocess
from .config import ROOT

FILES={'score.gp':'result/v3/export/score.gp','final_report.md':'result/final_report.md',
       'final_report.json':'result/final_report.json','timing.json':'result/timing.json',
       'verification_report.md':'result/v3/verification/verification_report.md','full_score.pdf':'result/full_score.pdf'}
STAGES={'acquisition':'acquisition','v2':'v2_reconstruction','v3':'v3_transcription',
        'guitar_pro':'gp_export','v4':'v4_verification'}
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def owned(run,relative):
    root=Path(run).resolve();path=(root/relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():raise ValueError('missing_or_unsafe_output')
    return path
def output_path(run,name):
    if name not in FILES:raise ValueError('output_not_allowed')
    return owned(run,FILES[name])
def stage(run,fallback='v2_reconstruction'):
    try:
        s=read(Path(run)/'working/timing_state.json')
        active=s.get('active',{})
        for key,value in STAGES.items():
            if key in active:return value
        spans=s.get('spans',[])
        if s.get('finished_at') or any(x['key']=='v4' for x in spans):return 'finalizing'
        parents=[x['key'] for x in spans if x['key'] in STAGES]
        if parents:return STAGES[parents[-1]] if parents[-1]!='acquisition' else fallback
    except (OSError,ValueError,KeyError):pass
    return fallback

def validate_completion(run):
    run=Path(run).resolve();base=run/'result/v3'
    for name in ['score.gp','final_report.json','final_report.md','timing.json']:
        if output_path(run,name).stat().st_size==0:raise ValueError('empty_required_output')
    report=read(output_path(run,'final_report.json'));timing=read(output_path(run,'timing.json'))
    statuses={'READY_FOR_DELIVERY','REVIEW_RECOMMENDED','REVIEW_REQUIRED'}
    if report.get('status') not in statuses:raise ValueError('invalid_delivery_status')
    if timing.get('status')!='finished' or timing.get('active_spans') or not isinstance(timing.get('total_wall_seconds'),(int,float)):
        raise ValueError('unfinished_timing')
    if not all(report.get('checks',{}).get(k) is True for k in ['acquisition','canonical_validation','gp_roundtrip','v4_completed']):
        raise ValueError('failed_delivery_gate')
    hashes={'canonical_sha256':sha(owned(run,'result/v3/score.json')),'gp_sha256':sha(output_path(run,'score.gp'))}
    for name in ['export/roundtrip_validation.json','verification/verification.json']:
        data=read(owned(run,'result/v3/'+name))
        if any(data.get(k)!=v for k,v in hashes.items()):raise ValueError('stale_score_evidence')
        if name.startswith('export'):
            if data.get('valid') is not True or data.get('unexpected_mismatches'):raise ValueError('roundtrip_failed')
        elif data.get('mechanical_valid') is not True or not data.get('source_sweep',{}).get('complete'):
            raise ValueError('verification_incomplete')
    for rel,value in report.get('evidence_hashes',{}).items():
        if not value or sha(owned(run,'result/'+rel))!=value:raise ValueError('stale_report')
    dossier=read(owned(run,'result/v3/verification/observations.json'))
    if not dossier.get('artifacts'):raise ValueError('missing_bound_evidence')
    for entry in dossier['artifacts']:
        if sha(owned(run,'result/v3/'+entry['path']))!=entry['sha256']:raise ValueError('stale_visual_evidence')
    # Fresh import, using the existing comparator, additionally rejects corrupt GP bytes.
    fresh=run/'working/companion_roundtrip.json'
    result=subprocess.run(['node',str(ROOT/'tools/verification/inspect_gp.mjs'),str(base/'score.json'),
        str(base/'export/score.gp'),str(base/'export/export_mapping.json'),str(fresh)],cwd=ROOT,
        capture_output=True,timeout=120,shell=False)
    if result.returncode or not read(fresh).get('valid'):raise ValueError('fresh_roundtrip_failed')
    names=[name for name in FILES if (run/FILES[name]).is_file()]
    for name in names:output_path(run,name)
    return {'delivery_status':report['status'],'gp_available':True,'report_available':True,
            'review_count':report.get('issue_counts',{}).get('USER_REVIEW_REQUIRED',0),'files':names}
