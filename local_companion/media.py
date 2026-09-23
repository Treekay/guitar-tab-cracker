"""Runs acquisition workers and existing ffprobe/ffmpeg validation."""
import json
from pathlib import Path
import subprocess
import sys
import time
from .config import ROOT
from .security import redacted
from acquisition.acquire import validate_media
from pipeline.timing import Timer,atomic

MESSAGES={
 'no_media_candidate':'No supported media was found. Play the video and inspect again.',
 'blob_without_backing_media':'The player uses a blob URL. Observe playback requests, replay the video, then inspect again.',
 'manifest_unsupported':'This manifest is not supported. Use a complete direct video resource or a local file.',
 'protected_or_drm':'Protected or encrypted media is unsupported. No protection bypass was attempted.',
 'download_failed':'The media request failed. Refresh/replay the video to obtain a fresh URL, or provide a local file.',
 'media_validation_failed':'The resource is not a complete decodable video. It may be only one segment or an audio track.',
}

def ordered(candidates):
    priority={'video.currentSrc':0,'video.src':1,'source':2,'performance':3,'network':4}
    kind={'direct':0,'hls':1,'unknown':2,'dash':3}
    return sorted(candidates,key=lambda c:(kind[c['type']],priority[c['source']]))[:5]

def acquire(data,run,ffprobe,ffmpeg,*,conversion=False):
    run=Path(run).resolve();timer=Timer(run);timer.begin('One-click acquisition and complete conversion' if conversion else 'Browser extension acquisition only; downstream conversion not started')
    record={'provider':'browser-extension','source_type':'browser_session','authentication_mode':'browser_authorized_url',
            'page_url':redacted(data['page_url']),'source_url':redacted(data['page_url']),'page_title':data['page_title'],
            'status':'failed','attempts':[],'local_path':None,'remote_download_files':[],
            'cleanup':{'status':'not_applicable','removed_paths':[]}}
    start=time.monotonic()
    try:
        with timer.span('acquisition'):
            if data['protected']:record['reason']='protected_or_drm'
            elif not data['media_candidates']:record['reason']='blob_without_backing_media' if data['blob_detected'] else 'no_media_candidate'
            else:
                for index,c in enumerate(ordered(data['media_candidates'])):
                    directory=run/'working/acquisition'/f'candidate_{index:02}';directory.mkdir(parents=True)
                    attempt={'type':c['type'],'url':redacted(c['url']),'source':c['source'],'status':'failed'}
                    t=time.monotonic()
                    try:
                        payload=json.dumps({'candidate':c,'headers':data['headers']})
                        subprocess.run([sys.executable,'-m','local_companion.network',str(directory)],cwd=ROOT,input=payload,text=True,
                                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=650,shell=False)
                        result=json.loads((directory/'network_result.json').read_text(encoding='utf8'))
                        if result['status']!='success':attempt['reason']=result['reason'];continue
                        source=directory/result['input']
                        if source.parent!=directory or source.name not in ('video.download','local.m3u8'):raise ValueError('Invalid worker output')
                        if source.name=='video.download':
                            # Do not let a mislabeled downloaded playlist make
                            # ffprobe follow local file references. HLS must use
                            # the explicit sanitized-manifest path below.
                            with source.open('rb') as f:head=f.read(32)
                            container=(head[4:8] in (b'ftyp',b'styp',b'moov',b'mdat') or head.startswith((b'\x1aE\xdf\xa3',b'FLV',b'RIFF',b'OggS')) or head[:1]==b'G')
                            if not container:attempt['reason']='media_validation_failed';continue
                        if source.name=='local.m3u8':
                            # Only generated local filenames reach ffmpeg. No remote
                            # protocols or cookie/header forwarding are enabled.
                            output=directory/'video.mp4'
                            done=subprocess.run([ffmpeg,'-v','error','-nostdin','-protocol_whitelist','file,pipe',
                                '-allowed_extensions','ALL','-i',str(source),'-map','0:v:0','-map','0:a?',
                                '-c','copy','-movflags','+faststart','-n',str(output)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=180,shell=False)
                            if done.returncode:attempt['reason']='media_validation_failed';continue
                            source=output
                        try:validation=validate_media(source,ffprobe,ffmpeg)
                        except Exception:attempt['reason']='media_validation_failed';continue
                        record.update(validation,status='success',local_path=str(source),selected_candidate=attempt.copy(),download_seconds=result['download_seconds'])
                        attempt['status']='success';record['selected_candidate']['status']='success';break
                    except Exception:attempt['reason']='download_failed'
                    finally:
                        attempt['wall_seconds']=time.monotonic()-t;record['attempts'].append(attempt)
                if record['status']!='success':record['reason']=record['attempts'][-1].get('reason','download_failed')
    except Exception:record.update(status='failed',reason='download_failed')
    finally:
        record['acquisition_wall_seconds']=time.monotonic()-start
        owned=[str(p.resolve()) for p in (run/'working/acquisition').rglob('*') if p.is_file() and p.name!='network_result.json']
        record['remote_download_files']=owned
        if record['status']=='failed':
            # Nothing can be handed off; discard run-owned partial media.
            allowed=(run/'working/acquisition').resolve()
            for name in owned:
                p=Path(name).resolve()
                if not p.is_relative_to(allowed):raise ValueError('Unsafe cleanup')
                p.unlink()
            record['cleanup']={'status':'removed' if owned else 'not_applicable','removed_paths':owned}
            record['message']=MESSAGES.get(record.get('reason'),MESSAGES['download_failed'])
        else:
            record['cleanup']={'status':'pending','removed_paths':[]}
            record['pipeline_handoff']={'ready':True,'local_video_path':record['local_path'],'conversion_started':False}
        atomic(run/'result/source/source.json',record)
        if not conversion or record['status']!='success':timer.finish()
    return record
