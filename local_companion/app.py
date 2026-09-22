import argparse
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
import uuid
from .config import ROOT,HOST,PORT,STATE,load
from .security import MAX_BODY,authorize,payload
from .media import acquire

class Companion(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,config,ffprobe,ffmpeg,port=PORT,runs=None):
        self.config=config;self.ffprobe=ffprobe;self.ffmpeg=ffmpeg
        self.runs=Path(runs or ROOT/'runs');self.jobs={};self.lock=threading.Lock();self.executor=ThreadPoolExecutor(max_workers=1)
        super().__init__((HOST,port),Handler)
    def submit(self,data):
        with self.lock:
            if any(x['status']=='running' for x in self.jobs.values()):return None
            run_id='extension-'+uuid.uuid4().hex
            self.jobs[run_id]={'run_id':run_id,'status':'running'}
            self.executor.submit(self.work,run_id,data)
            return run_id
    def work(self,run_id,data):
        try:
            result=acquire(data,self.runs/run_id,self.ffprobe,self.ffmpeg)
            status={'run_id':run_id,**result}
        except Exception:status={'run_id':run_id,'status':'failed','reason':'download_failed','message':'Local acquisition failed. Inspect the safe source record or provide a local file.'}
        with self.lock:
            self.jobs[run_id]=status
            while len(self.jobs)>100:self.jobs.pop(next(iter(self.jobs)))
    def server_close(self):
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
        if self.path=='/health':self.reply(200,{'status':'ok','service':'guitar-tab-cracker','acquisition_only':True});return
        match=re.fullmatch(r'/runs/(extension-[a-f0-9]{32})/status',self.path)
        if match:
            with self.server.lock:status=self.server.jobs.get(match[1])
            if status is None:
                record=self.server.runs/match[1]/'result/source/source.json'
                if record.is_file():status={'run_id':match[1],**json.loads(record.read_text(encoding='utf8'))}
            self.reply(200 if status else 404,status or {'reason':'run_not_found'});return
        self.reply(404,{'reason':'not_found'})
    def do_POST(self):
        if not self.authorized():return
        if self.path!='/acquire':self.reply(404,{'reason':'not_found','message':'Only media acquisition is implemented; conversion uses the existing workflow.'});return
        try:
            if self.headers.get('Transfer-Encoding') or self.headers.get_content_type()!='application/json':raise ValueError()
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=MAX_BODY:raise ValueError()
            raw=self.rfile.read(length)
            if len(raw)!=length:raise ValueError()
            data=payload(json.loads(raw))
        except Exception:self.reply(400,{'status':'failed','reason':'invalid_request','message':'Send a public page and media candidates with only minimal context.'});return
        run_id=self.server.submit(data)
        if not run_id:self.reply(409,{'status':'failed','reason':'busy','message':'One acquisition is already running. Wait for it to finish.'});return
        self.reply(202,{'run_id':run_id,'status':'running','status_url':f'/runs/{run_id}/status'})

def main():
    p=argparse.ArgumentParser();p.add_argument('--ffprobe',default=str(ROOT/'tmp/video-runtime/node_modules/ffprobe-static/bin/win32/x64/ffprobe.exe'))
    p.add_argument('--ffmpeg',default=str(ROOT/'tmp/video-runtime/node_modules/ffmpeg-static/ffmpeg.exe'));p.add_argument('--init',action='store_true');a=p.parse_args()
    config=load()
    # Pairing material is a local file, never an HTTP endpoint or console log.
    token=config['token']
    (STATE/'pairing.html').write_text('<!doctype html><meta charset="utf-8"><title>Guitar Tab Cracker pairing</title><h1>本地扩展配对</h1><p>将下方配对码复制到扩展弹窗中。不要发到聊天或提交到 Git。</p><input readonly style="width:38em" value="'+token+'"><p>服务地址：http://127.0.0.1:8787</p>',encoding='utf8')
    print('Pairing file: '+str(STATE/'pairing.html'))
    if a.init:return
    print('Guitar Tab Cracker companion listening on http://127.0.0.1:8787')
    server=Companion(config,a.ffprobe,a.ffmpeg)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
