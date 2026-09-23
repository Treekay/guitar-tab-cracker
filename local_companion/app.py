import argparse
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import re
import socket
import threading
import uuid
import time
from datetime import datetime,timezone
from .agent_runner import CodexRunner
from .conversion import stage,validate_completion,output_path,FILES,read,sha,owned
from .config import ROOT,HOST,PORT,STATE,load
from .security import MAX_BODY,authorize,payload
from .media import acquire
from pipeline.timing import atomic

class Companion(ThreadingHTTPServer):
    daemon_threads=True
    allow_reuse_address=False
    def server_bind(self):
        if hasattr(socket,'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        super().server_bind()
    def __init__(self,config,ffprobe,ffmpeg,port=PORT,runs=None,runner=None):
        self.config=config;self.ffprobe=ffprobe;self.ffmpeg=ffmpeg
        self.runs=Path(runs or ROOT/'runs');self.jobs={};self.lock=threading.Lock();self.executor=ThreadPoolExecutor(max_workers=1)
        self.runner=runner or CodexRunner(secrets=(config['token'],));self.cancellations={}
        super().__init__((HOST,port),Handler)
    def submit(self,data,convert=False):
        with self.lock:
            if any(x['status']=='running' for x in self.jobs.values()):return None
            run_id='extension-'+uuid.uuid4().hex
            self.jobs[run_id]={'run_id':run_id,'status':'running','stage':'queued','conversion':convert,
                'started_at':datetime.now(timezone.utc).isoformat(),'start_time':time.time(),'message':'Waiting to start','result':None}
            self.cancellations[run_id]=threading.Event()
            atomic(self.runs/run_id/'working/job_status.json',self.jobs[run_id])
            self.executor.submit(self.work,run_id,data,convert)
            return run_id
    def update(self,run_id,**values):
        with self.lock:
            self.jobs[run_id].update(values)
            atomic(self.runs/run_id/'working/job_status.json',self.jobs[run_id])
    def get_status(self,run_id):
        with self.lock:status=dict(self.jobs[run_id]) if run_id in self.jobs else None
        if status is None:
            record=self.runs/run_id/'working/job_status.json'
            if record.is_file():
                status=read(record)
                if status['status']=='running':
                    status.update(status='failed',failure_stage=status['stage'],stage='failed',reason='companion_interrupted',message='Companion restarted during the job; retained artifacts require inspection.')
            else:
                record=self.runs/run_id/'result/source/source.json'
                if record.is_file():status={'run_id':run_id,**read(record)}
        if status:
            status['elapsed_seconds']=round(max(0,status.get('end_time',time.time())-status.get('start_time',time.time())),1)
            status.pop('start_time',None);status.pop('end_time',None)
        return status
    def cancel(self,run_id):
        with self.lock:
            if run_id not in self.jobs or self.jobs[run_id]['status']!='running':return False
            self.cancellations[run_id].set();return True
    def resume_failed(self,run_id):
        """Explicit local recovery only; no HTTP caller may supply a video path."""
        if not re.fullmatch(r'extension-[a-f0-9]{32}',run_id):raise ValueError('invalid_run_id')
        run=self.runs/run_id
        status=read(owned(run,'working/job_status.json'))
        result=read(owned(run,'result/source/source.json'))
        video=Path(result['local_path']).resolve()
        if (status['status']!='failed' or status.get('failure_stage')!='v2_reconstruction'
                or result['status']!='success' or not video.is_relative_to((run/'working/acquisition').resolve())
                or sha(video)!=result.get('sha256')):
            raise ValueError('run_not_resumable')
        with self.lock:
            if any(x['status']=='running' for x in self.jobs.values()):raise ValueError('busy')
            history=status.setdefault('attempts',[])
            history.append({k:status.get(k) for k in ('agent_exit_code','reason','end_time')})
            for key in ('end_time','reason','failure_stage','agent_exit_code'):status.pop(key,None)
            status.update(status='running',stage='v2_reconstruction',message='Retrying with retained validated video')
            self.jobs[run_id]=status;self.cancellations[run_id]=threading.Event()
            atomic(run/'working/job_status.json',status)
            self.executor.submit(self.work,run_id,None,True,result)
    def work(self,run_id,data,convert=False,acquired=None):
        run=self.runs/run_id
        try:
            if acquired is None:
                self.update(run_id,stage='acquisition',message='Downloading and validating video')
                result=acquire(data,run,self.ffprobe,self.ffmpeg,**({'conversion':True} if convert else {}))
            else:result=acquired
            if result['status']!='success':
                self.update(run_id,**result,stage='failed',failure_stage='acquisition');return
            if not convert:self.update(run_id,**result,stage='completed');return
            if self.cancellations[run_id].is_set():raise ValueError('conversion_cancelled')
            result['pipeline_handoff'].update(conversion_started=True)
            atomic(run/'result/source/source.json',result)
            self.update(run_id,stage='v2_reconstruction',message='Agent is starting the existing visual workflow')
            def progress():
                current=stage(run,self.jobs[run_id]['stage'])
                if current!=self.jobs[run_id]['stage']:self.update(run_id,stage=current,message=current)
            outcome=self.runner.run_conversion(run,result['local_path'],self.cancellations[run_id],progress)
            self.update(run_id,agent_exit_code=outcome.exit_code)
            if outcome.reason or outcome.exit_code:raise ValueError(outcome.reason or 'agent_exit_failed')
            self.update(run_id,stage='finalizing',message='Checking current files and re-importing Guitar Pro')
            outputs=validate_completion(run)
            self.update(run_id,status='completed',stage='completed',message='Conversion complete',result=outputs)
        except Exception as error:
            # Do not send raw subprocess errors, prompts or secrets to the popup.
            reason=str(error) if isinstance(error,ValueError) and re.fullmatch('[a-z_]+',str(error)) else 'conversion_failed' if convert else 'download_failed'
            current=self.jobs[run_id]['stage']
            self.update(run_id,status='failed',failure_stage=current,stage='failed',reason=reason,message=f'Failed during {current}. Run artifacts retained.')
        finally:self.update(run_id,end_time=time.time())
    def server_close(self):
        for cancel in self.cancellations.values():cancel.set()
        super().server_close();self.executor.shutdown(wait=True)

class Handler(BaseHTTPRequestHandler):
    def setup(self):super().setup();self.connection.settimeout(10)
    def log_message(self,*args):pass
    def reply(self,code,value):
        body=json.dumps(value,ensure_ascii=True).encode()
        self.send_response(code)
        if self.headers.get('Origin')=='chrome-extension://'+self.server.config['extension_id']:
            self.send_header('Access-Control-Allow-Origin',self.headers['Origin']);self.send_header('Vary','Origin')
        self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
    def authorized(self,preflight=False):
        c=self.server.config
        ok=authorize(self.headers,c['token'],c['extension_id'],self.server.server_port,preflight)
        if not ok:self.reply(403,{'status':'failed','reason':'local_authorization_failed','message':'Pair the installed extension with this companion.'})
        return ok
    def do_OPTIONS(self):
        if not self.authorized(True):return
        if self.headers.get('Access-Control-Request-Method') not in ('GET','POST'):
            self.reply(403,{'reason':'local_authorization_failed'});return
        names={x.strip().lower() for x in self.headers.get('Access-Control-Request-Headers','').split(',') if x.strip()}
        if names-{'content-type','x-gtc-token','x-gtc-extension-id'}:self.reply(403,{'reason':'local_authorization_failed'});return
        self.send_response(204);self.send_header('Access-Control-Allow-Origin',self.headers['Origin'])
        self.send_header('Access-Control-Allow-Headers','Content-Type, X-GTC-Token, X-GTC-Extension-ID');self.send_header('Access-Control-Allow-Methods','GET, POST')
        self.send_header('Access-Control-Allow-Private-Network','true');self.send_header('Content-Length','0');self.end_headers()
    def do_GET(self):
        if not self.authorized():return
        if self.path=='/health':self.reply(200,{'status':'ok','service':'guitar-tab-cracker','acquisition_only':False,'agent_backend':'codex-exec','agent_setup_issue':self.server.runner.readiness()});return
        files=re.fullmatch(r'/runs/(extension-[a-f0-9]{32})/(outputs|files/([A-Za-z0-9_.-]+))',self.path)
        if files:
            status=self.server.get_status(files[1])
            if not status or status['status']!='completed':self.reply(409,{'reason':'outputs_not_ready'});return
            if files[2]=='outputs':self.reply(200,status['result']);return
            try:path=output_path(self.server.runs/files[1],files[3])
            except ValueError:self.reply(404,{'reason':'output_not_found'});return
            # Fixed filenames only; token stays in headers, never download URLs.
            self.send_response(200)
            if self.headers.get('Origin')=='chrome-extension://'+self.server.config['extension_id']:
                self.send_header('Access-Control-Allow-Origin',self.headers['Origin'])
            self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Disposition',f'attachment; filename="{files[3]}"')
            self.send_header('Content-Length',str(path.stat().st_size));self.send_header('Cache-Control','no-store');self.end_headers()
            with path.open('rb') as stream:
                while chunk:=stream.read(65536):self.wfile.write(chunk)
            return
        match=re.fullmatch(r'/runs/(extension-[a-f0-9]{32})/status',self.path)
        if match:
            status=self.server.get_status(match[1])
            self.reply(200 if status else 404,status or {'reason':'run_not_found'});return
        self.reply(404,{'reason':'not_found'})
    def do_POST(self):
        if not self.authorized():return
        cancel=re.fullmatch(r'/runs/(extension-[a-f0-9]{32})/cancel',self.path)
        if cancel:
            ok=self.server.cancel(cancel[1]);self.reply(202 if ok else 409,{'status':'cancelling' if ok else 'not_running'});return
        if self.path not in ('/acquire','/convert'):self.reply(404,{'reason':'not_found'});return
        try:
            if self.headers.get('Transfer-Encoding') or self.headers.get_content_type()!='application/json':raise ValueError()
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=MAX_BODY:raise ValueError()
            raw=self.rfile.read(length)
            if len(raw)!=length:raise ValueError()
            data=payload(json.loads(raw))
        except Exception:self.reply(400,{'status':'failed','reason':'invalid_request','message':'Send a public page and media candidates with only minimal context.'});return
        convert=self.path=='/convert'
        if convert:
            reason=self.server.runner.readiness()
            if reason:self.reply(503,{'status':'failed','reason':reason,'message':'One-time local Codex CLI setup/login is required.'});return
        run_id=self.server.submit(data,convert)
        if not run_id:self.reply(409,{'status':'failed','reason':'busy','message':'One job is already running. Wait for it to finish.'});return
        self.reply(202,{'run_id':run_id,'status':'running','status_url':f'/runs/{run_id}/status'})

def main():
    p=argparse.ArgumentParser();p.add_argument('--ffprobe',default=str(ROOT/'tmp/video-runtime/node_modules/ffprobe-static/bin/win32/x64/ffprobe.exe'))
    p.add_argument('--ffmpeg',default=str(ROOT/'tmp/video-runtime/node_modules/ffmpeg-static/ffmpeg.exe'));p.add_argument('--init',action='store_true')
    p.add_argument('--codex-path',help='Installed Codex executable or official npm codex.cmd shim')
    p.add_argument('--agent-timeout',type=int,default=4*3600,help='Conversion runtime deadline in seconds')
    p.add_argument('--resume-run',help='Explicitly retry a failed V2 startup using its hash-verified retained video')
    a=p.parse_args()
    config=load()
    if a.codex_path:
        config['codex_path']=a.codex_path
        atomic(STATE/'config.json',config)
    # Pairing material is a local file, never an HTTP endpoint or console log.
    token=config['token']
    (STATE/'pairing.html').write_text('<!doctype html><meta charset="utf-8"><title>Guitar Tab Cracker pairing</title><h1>本地扩展配对</h1><p>将下方配对码复制到扩展弹窗中。不要发到聊天或提交到 Git。</p><input readonly style="width:38em" value="'+token+'"><p>服务地址：http://127.0.0.1:8787</p>',encoding='utf8')
    print('Pairing file: '+str(STATE/'pairing.html'))
    if a.init:return
    print('Guitar Tab Cracker companion listening on http://127.0.0.1:8787')
    server=Companion(config,a.ffprobe,a.ffmpeg,runner=CodexRunner(config.get('codex_path'),a.agent_timeout,secrets=(token,)))
    if a.resume_run:server.resume_failed(a.resume_run)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
