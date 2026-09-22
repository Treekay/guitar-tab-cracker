"""Isolated network worker: public destinations only, no child processes.

Input arrives on stdin and is never written to disk. HLS manifests are rewritten
from an allowlist to local filenames; ffmpeg never receives remote references.
"""
import json
from pathlib import Path
import re
import sys
import time
from urllib import request
from urllib.parse import urljoin
from .security import redacted
from acquisition.security import validate_url,install_network_guard,AcquisitionError
from acquisition.worker import SafeRedirect,stream_video

LIMIT=2*1024**3

class Unsupported(Exception):pass
class Protected(Exception):pass

class Fetcher:
    def __init__(self,headers):
        self.headers=headers;self.total=0;self.start=time.monotonic()
        self.opener=request.build_opener(request.ProxyHandler({}),SafeRedirect())
    def fetch(self,url,destination=None,manifest=False):
        validate_url(url);limit=1024**2 if manifest else LIMIT-self.total
        size=0;body=bytearray()
        with self.opener.open(request.Request(url,headers=self.headers),timeout=20) as response:
            validate_url(response.url);final=response.url
            length=response.headers.get('Content-Length')
            if length and (not length.isdigit() or int(length)>limit):raise Unsupported('size_limit')
            kind=response.headers.get_content_type()
            if kind in ('text/html','application/xhtml+xml'):raise Unsupported('not_media')
            file=destination.open('xb') if destination else None
            try:
                while True:
                    if time.monotonic()-self.start>600:raise Unsupported('deadline')
                    block=response.read(256*1024)
                    if not block:break
                    size+=len(block);self.total+=len(block)
                    if size>limit or self.total>LIMIT:raise Unsupported('size_limit')
                    if file:file.write(block)
                    else:body.extend(block)
            finally:
                if file:file.close()
            if not size or (length and size!=int(length)):raise Unsupported('truncated')
        return body.decode('utf-8-sig') if manifest else None,final

def playlist(text,base):
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    if not lines or lines[0]!='#EXTM3U':raise Unsupported('not_hls')
    if any(x.startswith(('#EXT-X-KEY:','#EXT-X-SESSION-KEY:')) for x in lines):raise Protected('encrypted_hls')
    if any(x.startswith(('#EXT-X-BYTERANGE:','#EXT-X-PART:','#EXT-X-PRELOAD-HINT:','#EXT-X-DEFINE:')) for x in lines):raise Unsupported('advanced_hls')
    if any(x.startswith('#EXT-X-MEDIA:') and 'URI=' in x for x in lines):raise Unsupported('separate_rendition')
    variants=[]
    for i,line in enumerate(lines):
        if line.startswith('#EXT-X-STREAM-INF:'):
            if i+1>=len(lines) or lines[i+1].startswith('#'):raise Unsupported('variant_uri')
            resolution=re.search(r'RESOLUTION=(\d+)x(\d+)',line)
            bandwidth=re.search(r'(?:^|,)BANDWIDTH=(\d+)',line.split(':',1)[1])
            variants.append((int(resolution[2]) if resolution else 0,int(bandwidth[1]) if bandwidth else 0,urljoin(base,lines[i+1])))
    if variants:
        preferred=[x for x in variants if x[0]<=1080]
        if not preferred:
            smallest=min(x[0] for x in variants);preferred=[x for x in variants if x[0]==smallest]
        return {'variant':max(preferred)[2]}
    if '#EXT-X-ENDLIST' not in lines:raise Unsupported('live_hls')
    output=['#EXTM3U'];downloads=[];pending=False;has_map=False
    for line in lines[1:]:
        if line.startswith('#EXT-X-MAP:'):
            match=re.fullmatch(r'#EXT-X-MAP:URI="([^"]+)"',line)
            if not match:raise Unsupported('map_attributes')
            name=f'init_{len(downloads):04}.mp4';downloads.append((urljoin(base,match[1]),name));has_map=True
            output.append(f'#EXT-X-MAP:URI="{name}"')
        elif line.startswith('#EXTINF:'):
            match=re.match(r'#EXTINF:(\d+(?:\.\d+)?)(?:,.*)?$',line)
            if not match or not 0<float(match[1])<=3600:raise Unsupported('duration')
            output.append('#EXTINF:'+match[1]+',');pending=True
        elif not line.startswith('#'):
            if not pending:raise Unsupported('segment_without_duration')
            name=f'segment_{len(downloads):04}'+('.m4s' if has_map else '.ts')
            downloads.append((urljoin(base,line),name));output.append(name);pending=False
        elif re.fullmatch(r'#EXT-X-(?:VERSION|TARGETDURATION|MEDIA-SEQUENCE|DISCONTINUITY-SEQUENCE):\d+',line) or line in ('#EXT-X-ENDLIST','#EXT-X-DISCONTINUITY','#EXT-X-INDEPENDENT-SEGMENTS','#EXT-X-PLAYLIST-TYPE:VOD'):
            output.append(line)
        # Drop everything else; never carry arbitrary URI-bearing tags to ffmpeg.
    if pending or not downloads or len(downloads)>2000:raise Unsupported('segment_count')
    return {'downloads':downloads,'local':'\n'.join(output)+'\n'}

def hls(url,directory,headers):
    fetch=Fetcher(headers)
    for _ in range(4):
        body,base=fetch.fetch(url,manifest=True);plan=playlist(body,base)
        if 'variant' in plan:url=plan['variant'];continue
        for address,name in plan['downloads']:fetch.fetch(address,directory/name)
        (directory/'local.m3u8').write_text(plan['local'],encoding='utf8')
        return {'input':'local.m3u8','downloaded_size':fetch.total,'segments':len(plan['downloads'])}
    raise Unsupported('nested_manifests')

def main():
    directory=Path(sys.argv[1]).resolve();started=time.monotonic()
    result={}
    try:
        install_network_guard()
        data=json.loads(sys.stdin.read(128*1024));c=data['candidate'];url=c['url'];validate_url(url)
        kind=c['type'];headers=data['headers']
        if kind=='dash':raise Unsupported('dash_manifest')
        if kind=='hls':result=hls(url,directory,headers)
        else:
            result=stream_video(url,directory/'video.download',LIMIT,20,headers=headers)
            result['input']='video.download'
        result.update(status='success')
    except Protected:result={'status':'failed','reason':'protected_or_drm'}
    except Unsupported:result={'status':'failed','reason':'manifest_unsupported'}
    except Exception:result={'status':'failed','reason':'download_failed'}
    result['download_seconds']=time.monotonic()-started
    (directory/'network_result.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    return 0 if result['status']=='success' else 1

if __name__=='__main__':raise SystemExit(main())
