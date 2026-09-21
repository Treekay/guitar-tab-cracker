"""Explicit monotonic wall-clock spans across agent/tool calls on one host/boot."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import hashlib
import subprocess
import time

PHASES=('acquisition','v2','v3','guitar_pro','v4')
FIELDS={
'acquisition':('download_seconds',),
'v2':('video_inventory_seconds','frame_survey_seconds','adaptive_frame_collection_seconds','coverage_recovery_seconds','measure_reconciliation_seconds','crop_export_seconds','final_qa_seconds'),
'v3':('transcription_seconds','canonical_assembly_seconds','deterministic_validation_seconds'),
'guitar_pro':('gp_adapter_seconds','gp_export_seconds','gp_roundtrip_validation_seconds','gp_render_seconds'),
'v4':('source_feature_sweep_seconds','targeted_review_seconds','auto_correction_seconds','final_verification_seconds')}

def utc():return datetime.now(timezone.utc).isoformat()
def atomic(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    os.replace(temp,path)

class Timer:
    def __init__(self,run):
        self.root=Path(run).resolve();self.state=self.root/'working/timing_state.json'
        self.output=self.root/'result/timing.json'
    @contextmanager
    def locked(self):
        self.state.parent.mkdir(parents=True,exist_ok=True)
        lock=self.state.with_suffix('.lock')
        try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
        except FileExistsError:raise ValueError('Timing writer active or interrupted lock; inspect before recovery')
        try:yield
        finally:os.close(fd);lock.unlink()
    def begin(self,scope='conversion'):
        with self.locked():
            if self.state.exists():raise ValueError('Timing session already exists; never overwrite or backfill')
            s={'started_at':utc(),'start_ns':time.monotonic_ns(),'host':platform.node(),
               'boot_estimate':time.time()-time.monotonic(),'scope':scope,'finished_at':None,
               'spans':[],'active':{},'reused_stages':[]}
            self.save(s)
    def load(self):
        s=json.loads(self.state.read_text(encoding='utf8'))
        if s['finished_at']:raise ValueError('Timing session finished')
        if s['host']!=platform.node() or time.monotonic_ns()<s['start_ns'] or abs(time.time()-time.monotonic()-s['boot_estimate'])>60:
            raise ValueError('Host/boot/clock continuity lost; do not fabricate elapsed time. Start a fresh run.')
        return s
    def save(self,s):
        now=s.get('finish_ns',time.monotonic_ns());phases={}
        for phase in PHASES:
            spans=[x for x in s['spans'] if x['key']==phase]
            active=s['active'].get(phase)
            total=sum(x['seconds'] for x in spans)+(max(0,now-active['start_ns'])/1e9 if active else 0)
            p={'wall_seconds':round(total,6) if spans or active else None}
            for field in FIELDS[phase]:
                subs=[x for x in s['spans'] if x['key']==phase+'.'+field]
                p[field]=round(sum(x['seconds'] for x in subs),6) if subs else None
            phases[phase]=p
        for metric in s.get('gp_measurements',[]):
            for field in FIELDS['guitar_pro']:
                value=metric.get(field)
                if value is not None:
                    phases['guitar_pro'][field]=(phases['guitar_pro'][field] or 0)+value
        out={'schema_version':1,'started_at':s['started_at'],'finished_at':s['finished_at'],
             'status':'finished' if s['finished_at'] else 'running','scope':s['scope'],
             'clock':'time.monotonic_ns; same host and boot; not CPU time',
             'total_wall_seconds':round((now-s['start_ns'])/1e9,6),'phases':phases,
             'active_spans':list(s['active']),'reused_stages':s['reused_stages'],
             'spans':s['spans'],'note':'Total includes orchestration/agent/wait time; phase spans may be revisited. Unexecuted substeps are null; totals are not sums of nested spans.'}
        atomic(self.state,s);atomic(self.output,out)
    def start(self,key):
        phase=key.split('.')[0]
        if phase not in PHASES or ('.' in key and key.split('.',1)[1] not in FIELDS[phase]):raise ValueError('Unknown phase/substep')
        with self.locked():
            s=self.load()
            if key in s['active']:raise ValueError('Span already active')
            if '.' in key:
                if phase not in s['active']:raise ValueError('Start parent phase first')
                if any(k.startswith(phase+'.') for k in s['active']):raise ValueError('Overlapping substeps are not allowed')
            elif any(k in PHASES for k in s['active']):raise ValueError('Stop current phase before starting another')
            s['active'][key]={'start_ns':time.monotonic_ns(),'started_at':utc()};self.save(s)
    def stop(self,key,outcome='completed'):
        with self.locked():
            s=self.load()
            if key not in s['active']:raise ValueError('Span not active')
            if any(k.startswith(key+'.') for k in s['active']):raise ValueError('Stop child spans first')
            a=s['active'].pop(key);s['spans'].append({'key':key,'started_at':a['started_at'],'finished_at':utc(),
                'seconds':(time.monotonic_ns()-a['start_ns'])/1e9,'outcome':outcome});self.save(s)
    def reuse(self,key,source):
        with self.locked():
            s=self.load();s['reused_stages'].append({'stage':key,'source':str(source),'timing':'not backfilled'});self.save(s)
    def finish(self):
        with self.locked():
            s=self.load()
            if s['active']:raise ValueError('Cannot finish with open spans')
            s.update(finished_at=utc(),finish_ns=time.monotonic_ns());self.save(s)
    def import_gp(self):
        """Import only instrument-produced metrics bound to this run's score."""
        with self.locked():
            s=self.load();p=self.root/'result/v3/export/timing.json'
            metric=json.loads(p.read_text(encoding='utf8'))
            score=self.root/'result/v3/score.json'
            if metric.get('canonical_sha256')!=hashlib.sha256(score.read_bytes()).hexdigest():raise ValueError('Stale GP timing')
            spans=[x for x in s['spans'] if x['key']=='guitar_pro']
            if not any(x['started_at']<=metric['started_at']<=metric['finished_at']<=x['finished_at'] for x in spans):raise ValueError('GP metrics were not recorded inside a measured phase')
            if any(x['started_at']==metric['started_at'] for x in s.get('gp_measurements',[])):raise ValueError('GP metrics already imported')
            s.setdefault('gp_measurements',[]).append(metric);self.save(s)
    @contextmanager
    def span(self,key):
        self.start(key)
        try:yield
        except BaseException:
            self.stop(key,'failed');raise
        else:self.stop(key)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path)
    sub=p.add_subparsers(dest='action',required=True)
    b=sub.add_parser('begin');b.add_argument('--scope',default='conversion')
    for a in ['start','stop']:sub.add_parser(a).add_argument('key')
    sub.add_parser('finish')
    sub.add_parser('import-gp')
    r=sub.add_parser('reuse');r.add_argument('key');r.add_argument('source')
    e=sub.add_parser('exec');e.add_argument('key');e.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args();t=Timer(a.run)
    if a.action=='begin':t.begin(a.scope)
    elif a.action=='start':t.start(a.key)
    elif a.action=='stop':t.stop(a.key)
    elif a.action=='finish':t.finish()
    elif a.action=='import-gp':t.import_gp()
    elif a.action=='reuse':t.reuse(a.key,a.source)
    else:
        cmd=a.command[1:] if a.command[:1]==['--'] else a.command
        if not cmd:raise ValueError('Missing command')
        with t.span(a.key):
            c=subprocess.run(cmd,shell=False)
            if c.returncode:raise SystemExit(c.returncode)
if __name__=='__main__':main()
