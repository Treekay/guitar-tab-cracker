"""Isolated public-network worker; controlled parent handles media validation."""
import argparse
import json
from pathlib import Path
import socket
import time
import sys
from urllib import request,error
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from acquisition.security import AcquisitionError,validate_url,install_network_guard

class SafeRedirect(request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        validate_url(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def classify(message):
    m=message.lower()
    if any(x in m for x in ['drm','protected content']):return 'drm_or_protected'
    if any(x in m for x in ['429','too many requests','rate limit']):return 'rate_limited'
    if any(x in m for x in ['sign in','login','log in','logged-in','authentication','private video','members-only','premium','http error 401','paywall']):return 'authentication_required'
    if 'http error 403' in m:return 'access_restricted'
    if any(x in m for x in ['timed out','timeout','connection','dns','name resolution','network','certificate']):return 'network_error'
    if any(x in m for x in ['unsupported url','no suitable','no video formats','not a valid url']):return 'unsupported_url'
    return 'download_failed'

def stream_video(url,dest,max_bytes,timeout,headers=None,allow_html=False):
    validate_url(url)
    opener=request.build_opener(request.ProxyHandler({}),SafeRedirect())
    req=request.Request(url,headers={'User-Agent':'guitar-tab-cracker/0.1',**(headers or {})})
    started=time.monotonic()
    with opener.open(req,timeout=timeout) as response:
        validate_url(response.url)
        kind=response.headers.get_content_type()
        if kind in ('text/html','application/xhtml+xml'):
            if allow_html:return None
            raise AcquisitionError('invalid_media','Media endpoint returned HTML, not video')
        length=response.headers.get('Content-Length')
        if length and (not length.isdigit() or int(length)>max_bytes):raise AcquisitionError('download_failed','Declared media size exceeds limit')
        if not (kind.startswith('video/') or kind in ('application/octet-stream','binary/octet-stream','application/mp4','application/webm','application/x-matroska')):
            if allow_html:return None
            raise AcquisitionError('invalid_media','Endpoint did not return a supported media content type: '+kind)
        size=0
        with dest.open('xb') as output:
            while True:
                if time.monotonic()-started>600:raise AcquisitionError('network_error','Download deadline exceeded')
                block=response.read(256*1024)
                if not block:break
                size+=len(block)
                if size>max_bytes:raise AcquisitionError('download_failed','Streaming media size exceeds limit')
                output.write(block)
        if not size or (length and size!=int(length)):raise AcquisitionError('invalid_media','Empty or truncated download')
        return {'download_seconds':time.monotonic()-started,'downloaded_size':size,'content_type':kind,'resolved_url':response.url}

def select_format(info,max_height=1080):
    if info.get('is_live') or info.get('_type') in ('playlist','multi_video'):
        raise AcquisitionError('unsupported_url','Live streams and playlists are not supported; provide one completed video')
    formats=info.get('formats') or [info]
    usable=[f for f in formats if f.get('protocol') in ('http','https') and f.get('vcodec') not in (None,'none') and not f.get('has_drm') and f.get('url') and f.get('height')]
    if not usable:
        if any(f.get('has_drm') for f in formats):raise AcquisitionError('drm_or_protected','Protected video is not supported')
        raise AcquisitionError('unsupported_url','No suitable public progressive HTTP video. Upload the local video file.')
    preferred=[f for f in usable if f['height']<=max_height]
    if not preferred:
        smallest=min(f['height'] for f in usable);preferred=[f for f in usable if f['height']==smallest]
    return max(preferred,key=lambda f:(f['height'],f.get('width') or 0,f.get('tbr') or 0))

class QuietLog:
    def debug(self,msg):pass
    def warning(self,msg):pass
    def error(self,msg):pass

def extract_page(url):
    import yt_dlp
    from yt_dlp.globals import plugin_dirs
    from yt_dlp.networking._urllib import UrllibRH
    plugin_dirs.value=[]
    class PublicYoutubeDL(yt_dlp.YoutubeDL):
        def urlopen(self,req):
            validate_url(req if isinstance(req,str) else req.url)
            return super().urlopen(req)
    opts={'quiet':True,'no_warnings':True,'logger':QuietLog(),'proxy':'','socket_timeout':20,
          'retries':1,'extractor_retries':1,'noplaylist':True,'cachedir':False,
          'geo_bypass':False,'usenetrc':False,'cookiefile':None,'cookiesfrombrowser':None,
          'js_runtimes':{},'remote_components':set(),'enable_file_urls':False}
    with PublicYoutubeDL(opts) as ydl:
        # Pin one Python network stack: every connection passes the socket guard.
        ydl._request_director=ydl.build_request_director([UrllibRH])
        info=ydl.extract_info(url,download=False)
        if not info:raise AcquisitionError('download_failed','No video metadata returned')
        f=select_format(info)
        headers={k:v for k,v in f.get('http_headers',info.get('http_headers',{})).items() if k.lower() in ('user-agent','referer','origin','accept')}
        return f['url'],headers,{k:info.get(k) for k in ('id','title','extractor','duration','webpage_url')}, {k:f.get(k) for k in ('format_id','width','height','fps','vcodec','acodec','protocol')}

class DirectVideoUrlProvider:
    name='direct-http'
    def acquire(self,url,dest,max_bytes):
        return stream_video(url,dest,max_bytes,20,allow_html=True)

class YtDlpProvider:
    name='yt-dlp'
    def acquire(self,url,dest,max_bytes):
        media,headers,metadata,fmt=extract_page(url)
        downloaded=stream_video(media,dest,max_bytes,20,headers=headers)
        metadata['selected_format']=fmt
        return downloaded,metadata

def main():
    p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('directory',type=Path);p.add_argument('--max-bytes',type=int,default=2*1024**3);a=p.parse_args()
    provider='direct-http';started=time.monotonic();dest=a.directory/'video.download'
    result={}
    try:
        install_network_guard();validate_url(a.url)
        downloaded=DirectVideoUrlProvider().acquire(a.url,dest,a.max_bytes)
        metadata={}
        if downloaded is None:
            provider='yt-dlp';downloaded,metadata=YtDlpProvider().acquire(a.url,dest,a.max_bytes)
        result={'status':'success','provider':provider,'local_path':str(dest),'metadata':metadata,**downloaded}
    except AcquisitionError as e:result={'status':'failed','provider':provider,'reason':e.reason,'detail':str(e)}
    except (error.URLError,error.HTTPError,socket.timeout,OSError) as e:
        result={'status':'failed','provider':provider,'reason':classify(str(e)),'detail':str(e)[:2000]}
    except Exception as e:result={'status':'failed','provider':provider,'reason':classify(str(e)),'detail':str(e)[:2000]}
    result['provider_wall_seconds']=time.monotonic()-started
    if result['status']=='failed':result['message']='Public-video acquisition failed. Please provide the local video file; no authentication or access bypass is attempted.'
    (a.directory/'worker_result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('resolved_url','metadata')},ensure_ascii=True))
    return 0 if result['status']=='success' else 1
if __name__=='__main__':raise SystemExit(main())
