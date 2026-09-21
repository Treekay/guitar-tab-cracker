"""Acquire one local/public video, validate it, preserve provenance and timing.

python tools/acquisition/acquire.py INPUT RUN --ffprobe PATH --ffmpeg PATH
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pipeline.timing import Timer,atomic
from acquisition.security import AcquisitionError,validate_url
from acquisition.auth import add_arguments,browser_sources,message

class LocalFileProvider:
    name='local-file'
    def acquire(self,source):
        p=Path(source).expanduser().resolve()
        if not p.is_file():raise AcquisitionError('invalid_media','Local video file does not exist')
        return {'status':'success','provider':self.name,'authentication_mode':None,'browser_source':None,'local_path':str(p),'download_seconds':0.0,'downloaded_size':0,'metadata':{}}

def validate_media(path,ffprobe,ffmpeg):
    path=Path(path).resolve()
    if not path.is_file() or path.stat().st_size==0:raise AcquisitionError('invalid_media','Missing or empty media')
    try:
        probe=subprocess.run([ffprobe,'-v','error','-protocol_whitelist','file,pipe','-select_streams','v:0',
             '-show_entries','format=duration:stream=index,width,height,duration,avg_frame_rate','-of','json',str(path)],capture_output=True,text=True,timeout=45,shell=False)
        if probe.returncode:raise AcquisitionError('ffmpeg_validation_failed',probe.stderr[-2000:])
        data=json.loads(probe.stdout);streams=data.get('streams',[])
        if not streams:raise AcquisitionError('invalid_media','No video stream')
        stream=streams[0];duration=float(data.get('format',{}).get('duration',stream.get('duration',0)))
        if not math.isfinite(duration) or not 0<duration<=86400 or not stream.get('width') or not stream.get('height'):
            raise AcquisitionError('invalid_media','Missing dimensions or implausible duration')
        decode=subprocess.run([ffmpeg,'-v','error','-nostdin','-protocol_whitelist','file,pipe','-i',str(path),'-map','0:v:0','-frames:v','1','-f','null','-'],capture_output=True,text=True,timeout=45,shell=False)
        if decode.returncode:raise AcquisitionError('ffmpeg_validation_failed',decode.stderr[-2000:])
    except (OSError,subprocess.TimeoutExpired,ValueError) as e:raise AcquisitionError('ffmpeg_validation_failed',str(e)) from e
    with path.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    return {'sha256':digest,'duration':duration,'duration_seconds':duration,'width':stream['width'],'height':stream['height'],'frame_rate':stream.get('avg_frame_rate'),'size_bytes':path.stat().st_size,'media_validation':'ffprobe video/duration/dimensions + ffmpeg first frame decode; local protocols only'}


def acquire_video(source,run_directory,ffprobe='ffprobe',ffmpeg='ffmpeg',max_bytes=2*1024**3,cookies_from_browser=None,auto_browser_cookies=False):
    browser_sources(cookies_from_browser,auto_browser_cookies)
    root=Path(run_directory).resolve();record=root/'result/source/source.json'
    if record.exists():raise ValueError('Source record exists; use a fresh run to preserve provenance')
    timer=Timer(root)
    if not timer.state.exists():timer.begin()
    source_type='url' if '://' in source else 'local'
    result={'authentication_mode':None if source_type=='local' else 'anonymous','browser_source':None,'source_type':source_type,'source_url':source if source_type=='url' else None,'supplied_local_path':source if source_type=='local' else None}
    started=time.monotonic();owned=[];attempt=None
    with timer.span('acquisition'):
        try:
            if source_type=='local':result.update(LocalFileProvider().acquire(source))
            else:
                validate_url(source,resolve=False)
                attempt=root/'working/acquisition'/uuid.uuid4().hex;attempt.mkdir(parents=True)
                log=attempt/'downloader.log'
                # Cookie databases copied by native yt-dlp live outside result/run
                # artifacts. Parent cleanup also runs after a killed worker.
                timed_out=False
                with tempfile.TemporaryDirectory(prefix='gtc-session-') as cookie_temp:
                    command=[sys.executable,str(Path(__file__).with_name('worker.py')),source,str(attempt),'--max-bytes',str(max_bytes),'--cookie-temp',cookie_temp]
                    if cookies_from_browser:command+=['--cookies-from-browser',cookies_from_browser]
                    if auto_browser_cookies:command+=['--auto-browser-cookies']
                    try:
                        completed=subprocess.run(command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=650,shell=False)
                    except subprocess.TimeoutExpired:timed_out=True
                result['cookie_temporary_cleanup']='completed'
                if timed_out:raise AcquisitionError('network_error','Download deadline exceeded')
                worker=attempt/'worker_result.json'
                if not worker.exists():raise AcquisitionError('download_failed','Acquisition worker failed; inspect '+str(log))
                result.update(json.loads(worker.read_text(encoding='utf8')))
                log.write_text(json.dumps({'status':result['status'],'reason':result.get('reason'),'attempts':result.get('attempts',[])},indent=2),encoding='utf8')
                if completed.returncode or result['status']!='success':raise AcquisitionError(result.get('reason','download_failed'),result.get('detail','Downloader failed'))
                path=Path(result['local_path']).resolve()
                if not path.is_relative_to(attempt.resolve()):raise AcquisitionError('invalid_media','Downloaded path escaped run storage')
            result.update(validate_media(result['local_path'],ffprobe,ffmpeg))
            result['status']='success'
        except AcquisitionError as e:
            result.update(status='failed',reason=e.reason,detail=message(e.reason),message=result.get('message',message(e.reason)))
        except (OSError,ValueError) as e:
            result.update(status='failed',reason='download_failed',detail=message('download_failed'),message=message('download_failed'))
        finally:
            if attempt:
                owned=[str(p.resolve()) for p in attempt.iterdir() if p.is_file() and p.name not in ('worker_result.json','downloader.log')]
            result.update(acquisition_wall_seconds=time.monotonic()-started,download_seconds=result.get('download_seconds'),
                remote_download_files=owned,temporary_directory=str(attempt) if attempt else None,
                cleanup={'status':'pending' if owned else 'not_applicable','removed_paths':[]})
            atomic(record,result)
    return result


def cleanup(run,abandoned=False):
    root=Path(run).resolve();record=root/'result/source/source.json';s=json.loads(record.read_text(encoding='utf8'))
    if s['source_type']=='local':return s
    if not abandoned and not (root/'result/final_report.json').is_file():raise ValueError('Finish conversion and final QA/report before cleanup, or explicitly abandon this run')
    allowed=(root/'working/acquisition').resolve();removed=[]
    for name in s.get('remote_download_files',[]):
        p=Path(name).resolve()
        if not p.is_relative_to(allowed) or p==allowed or p.suffix=='.json':raise ValueError('Unsafe cleanup path')
        if p.is_file():p.unlink();removed.append(str(p))
    s['cleanup']={'status':'removed','removed_paths':s.get('cleanup',{}).get('removed_paths',[])+removed,'reason':'abandoned/test run' if abandoned else 'conversion final QA complete'}
    atomic(record,s);return s

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('run');p.add_argument('--ffprobe',default='ffprobe');p.add_argument('--ffmpeg',default='ffmpeg');p.add_argument('--max-bytes',type=int,default=2*1024**3);p.add_argument('--cleanup',action='store_true');p.add_argument('--abandoned',action='store_true');add_arguments(p);a=p.parse_args()
    r=cleanup(a.run,a.abandoned) if a.cleanup else acquire_video(a.source,a.run,a.ffprobe,a.ffmpeg,a.max_bytes,a.cookies_from_browser,a.auto_browser_cookies)
    print(json.dumps(r,ensure_ascii=True));raise SystemExit(0 if r.get('status')=='success' else 1)
