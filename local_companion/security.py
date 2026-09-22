"""Strict extension-only localhost API contract; no caller paths/commands."""
import hmac
import re
import sys
from urllib.parse import urlsplit,urlunsplit
from .config import ROOT
sys.path.insert(0,str(ROOT/'tools'))
from acquisition.security import validate_url,AcquisitionError

MAX_BODY=128*1024
SOURCES={'video.currentSrc','video.src','source','performance','network'}
TYPES={'direct','hls','dash','unknown'}

def redacted(url):
    u=urlsplit(url)
    return urlunsplit((u.scheme,u.netloc,u.path,'REDACTED' if u.query else '', ''))

def authorize(headers,token,extension_id,port,preflight=False):
    origin='chrome-extension://'+extension_id
    if headers.get('Host')!=f'127.0.0.1:{port}':return False
    supplied_origin=headers.get('Origin')
    if preflight:return supplied_origin==origin
    # Chromium can omit Origin on privileged extension GET requests. A token
    # plus explicit extension ID is required then; a present foreign Origin
    # is always rejected, including browser preflights.
    if headers.get('X-GTC-Extension-ID')!=extension_id:return False
    if supplied_origin is not None and supplied_origin!=origin:return False
    supplied=headers.get('X-GTC-Token','')
    return preflight or (isinstance(supplied,str) and hmac.compare_digest(supplied.encode(),token.encode()))

def text(value,limit):
    if not isinstance(value,str) or len(value)>limit or any(ord(c)<32 for c in value):raise ValueError('Invalid text')
    return value

def payload(value):
    if not isinstance(value,dict) or set(value)-{'page_url','page_title','media_candidates','request_context','blob_detected','protected'}:raise ValueError('Unsupported fields')
    page=text(value.get('page_url'),8192);validate_url(page,resolve=False)
    title=text(value.get('page_title',''),512)
    context=value.get('request_context',{})
    if not isinstance(context,dict) or set(context)-{'referer','origin','user_agent'}:raise ValueError('Only minimal request context is accepted')
    headers={}
    if context.get('referer'):
        referer=text(context['referer'],8192)
        if referer!=page:raise ValueError('Referer must be the supplied page')
        # A page query can contain credentials; origin is sufficient for this MVP.
        headers['Referer']=urlunsplit((*urlsplit(page)[:2],'/','',''))
    origin=urlunsplit((*urlsplit(page)[:2],'','',''))
    if context.get('origin'):
        if context['origin']!=origin:raise ValueError('Origin must match the supplied page')
        headers['Origin']=origin
    if context.get('user_agent'):headers['User-Agent']=text(context['user_agent'],512)
    candidates=value.get('media_candidates',[])
    if not isinstance(candidates,list) or len(candidates)>100:raise ValueError('At most 100 candidates')
    accepted=[];seen=set();blob=value.get('blob_detected',False)
    if not isinstance(blob,bool) or not isinstance(value.get('protected',False),bool):raise ValueError('Invalid flags')
    for c in candidates:
        if not isinstance(c,dict) or set(c)-{'url','type','source','content_type'}:raise ValueError('Invalid candidate')
        url=text(c.get('url'),8192)
        if url.startswith('blob:'):blob=True;continue
        validate_url(url,resolve=False)
        kind=c.get('type','unknown');source=c.get('source','performance')
        if kind not in TYPES or source not in SOURCES:raise ValueError('Invalid candidate classification')
        content_type=text(c.get('content_type',''),128)
        if url not in seen:
            seen.add(url);accepted.append({'url':url,'type':kind,'source':source,'content_type':content_type})
    return {'page_url':page,'page_title':title,'media_candidates':accepted,'headers':headers,'blob_detected':blob,'protected':value.get('protected',False)}
