"""Isolated public-network worker; controlled parent handles media validation."""
import argparse
import json
from pathlib import Path
import socket
import time
import sys
import tempfile
from http.cookiejar import DefaultCookiePolicy
from urllib.parse import urlsplit
from urllib import request,error
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from acquisition.security import AcquisitionError,validate_url,install_network_guard
from acquisition.auth import classify,exception_reason,message,browser_sources,add_arguments,SESSION_ERRORS,COOKIE_ERRORS

class SafeRedirect(request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        validate_url(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def stream_video(url,dest,max_bytes,timeout,headers=None,allow_html=False,cookiejar=None):
    validate_url(url)
    handlers=[request.ProxyHandler({}),SafeRedirect()]
    if cookiejar is not None:handlers.append(request.HTTPCookieProcessor(cookiejar))
    opener=request.build_opener(*handlers)
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
        return {'download_seconds':time.monotonic()-started,'downloaded_size':size,'content_type':kind}

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
    def __init__(self):self.cookie_failure=None
    def debug(self,msg):pass
    def warning(self,msg):self.record(msg)
    def error(self,msg):self.record(msg)
    def record(self,msg):
        reason=classify(msg)
        if reason in COOKIE_ERRORS:self.cookie_failure=reason


def restrict_cookies(jar,url):
    host=urlsplit(url).hostname.lower().rstrip('.')
    for cookie in list(jar):
        domain=cookie.domain.lstrip('.').lower()
        if not domain or not (host==domain or host.endswith('.'+domain)) or cookie.is_expired():
            jar.clear(cookie.domain,cookie.path,cookie.name)
    jar.set_policy(DefaultCookiePolicy(strict_ns_domain=DefaultCookiePolicy.DomainStrictNonDomain))
    return jar

def extract_page(url,browser=None):
    import yt_dlp
    from yt_dlp.globals import plugin_dirs
    from yt_dlp.networking._urllib import UrllibRH
    plugin_dirs.value=[]
    class PublicYoutubeDL(yt_dlp.YoutubeDL):
        def urlopen(self,req):
            validate_url(req if isinstance(req,str) else req.url)
            return super().urlopen(req)
        def save_cookies(self):pass  # Never serialize browser sessions.
    logger=QuietLog()
    opts={'quiet':True,'no_warnings':True,'logger':logger,'proxy':'','socket_timeout':20,
          'retries':1,'extractor_retries':1,'noplaylist':True,'cachedir':False,
          'geo_bypass':False,'usenetrc':False,'cookiefile':None,'cookiesfrombrowser':(browser,) if browser else None,
          'js_runtimes':{},'remote_components':set(),'enable_file_urls':False}
    with PublicYoutubeDL(opts) as ydl:
        try:
            jar=restrict_cookies(ydl.cookiejar,url)
        except Exception as exc:
            reason=logger.cookie_failure or exception_reason(exc)
            raise AcquisitionError(reason if reason in COOKIE_ERRORS else 'cookies_unavailable','Browser session unavailable') from None
        if browser and not any(jar):
            raise AcquisitionError(logger.cookie_failure or 'cookies_unavailable','No readable cookies for the requested site')
        # Pin one Python network stack: every connection passes the socket guard.
        ydl._request_director=ydl.build_request_director([UrllibRH])
        try:info=ydl.extract_info(url,download=False)
        except Exception as exc:
            failure=AcquisitionError(exception_reason(exc),'Metadata extraction failed')
            failure.failure_stage='metadata_extraction'
            raise failure from None
        if not info:raise AcquisitionError('download_failed','No video metadata returned')
        try:f=select_format(info)
        except AcquisitionError as exc:
            exc.metadata_read=True
            exc.failure_stage='format_selection'
            raise
        headers={k:v for k,v in f.get('http_headers',info.get('http_headers',{})).items() if k.lower() in ('user-agent','referer','origin','accept')}
        return f['url'],headers,{k:info.get(k) for k in ('id','title','extractor','duration','webpage_url')}, {k:f.get(k) for k in ('format_id','width','height','fps','vcodec','acodec','protocol')},jar

class DirectVideoUrlProvider:
    name='direct-http'
    def acquire(self,url,dest,max_bytes):
        return stream_video(url,dest,max_bytes,20,allow_html=True)

class YtDlpProvider:
    name='yt-dlp'
    def acquire(self,url,dest,max_bytes,browser=None):
        media,headers,metadata,fmt,jar=extract_page(url,browser)
        try:
            downloaded=stream_video(media,dest,max_bytes,20,headers=headers,cookiejar=jar)
            metadata['selected_format']=fmt
            metadata['metadata_read']=True
            return downloaded,metadata
        finally:jar.clear()


def acquire_remote(url,directory,max_bytes,explicit=None,automatic=False):
    browsers=browser_sources(explicit,automatic)
    attempts=[]
    def attempt(provider,browser=None):
        dest=directory/f'video_{len(attempts):02}.download';start=time.monotonic()
        item={'provider':provider,'authentication_mode':'browser_cookies' if browser else 'anonymous','browser_source':browser}
        try:
            if provider=='direct-http':
                downloaded=DirectVideoUrlProvider().acquire(url,dest,max_bytes);metadata={}
                if downloaded is None:
                    item['status']='not_direct_media';return None
            else:downloaded,metadata=YtDlpProvider().acquire(url,dest,max_bytes,browser)
            item['status']='success'
            return {**item,'local_path':str(dest),'metadata':metadata,**downloaded}
        except Exception as exc:
            reason=exception_reason(exc);item.update(status='failed',reason=reason,detail=message(reason))
            if getattr(exc,'failure_stage',None):item['failure_stage']=exc.failure_stage
            if getattr(exc,'metadata_read',False):item['metadata_read']=True
            return dict(item)
        finally:
            item['wall_seconds']=time.monotonic()-start;attempts.append(item)
    # Explicit browser mode is an authorized session test, even after a previous
    # network failure. Automatic mode never reads cookies for network errors.
    if explicit:
        result=attempt('yt-dlp',explicit)
    else:
        direct=attempt('direct-http')
        if direct and (direct['status']=='success' or direct['reason'] not in SESSION_ERRORS):
            result=direct
        else:
            result=attempt('yt-dlp')
            if automatic and result['status']=='failed' and result['reason'] in SESSION_ERRORS:
                for browser in browsers:
                    result=attempt('yt-dlp',browser)
                    if result['status']=='success' or result['reason'] not in SESSION_ERRORS|COOKIE_ERRORS:break
    result['attempts']=attempts
    if result['status']=='failed':
        result['message']=message(result['reason'])
        if any(x['authentication_mode']=='browser_cookies' for x in attempts):
            result['message']+=' Could not acquire this video with the configured local browser session. Verify that you are logged in and can access it, or provide a local video file.'
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('directory',type=Path);p.add_argument('--max-bytes',type=int,default=2*1024**3);p.add_argument('--cookie-temp',type=Path);add_arguments(p);a=p.parse_args()
    started=time.monotonic()
    # Parent owns this OS-temp directory and cleans it even on worker timeout.
    if a.cookie_temp:tempfile.tempdir=str(a.cookie_temp.resolve())
    try:
        install_network_guard();validate_url(a.url)
        result=acquire_remote(a.url,a.directory,a.max_bytes,a.cookies_from_browser,a.auto_browser_cookies)
    except Exception as exc:
        reason=exception_reason(exc)
        result={'status':'failed','provider':'yt-dlp' if a.cookies_from_browser else 'direct-http','authentication_mode':'browser_cookies' if a.cookies_from_browser else 'anonymous','browser_source':a.cookies_from_browser,'reason':reason,'detail':message(reason),'message':message(reason)}
    result['provider_wall_seconds']=time.monotonic()-started
    (a.directory/'worker_result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    return 0 if result['status']=='success' else 1
if __name__=='__main__':raise SystemExit(main())
