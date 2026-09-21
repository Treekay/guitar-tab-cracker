import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from http.cookiejar import Cookie, CookieJar
from urllib.request import Request
from unittest.mock import patch, MagicMock

sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from worker import acquire_remote, restrict_cookies, classify, stream_video
from worker import SafeRedirect
from acquisition.auth import browser_sources
from acquisition.security import AcquisitionError
from acquire import acquire_video

URL='https://www.bilibili.com/video/test'
SECRET='FAKE_COOKIE_DO_NOT_LOG'

def cookie(domain, value=SECRET, specified=True):
    return Cookie(0,'session',value,None,False,domain,specified,domain.startswith('.'), '/',True,True,None,True,None,None,{},False)

class BrowserCookieTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def test_anonymous_success_never_reads_browser(self):
        with patch('worker.DirectVideoUrlProvider.acquire',return_value=None), patch('worker.YtDlpProvider.acquire',return_value=({'download_seconds':1},{})) as provider:
            result=acquire_remote(URL,self.root,100,automatic=True)
        self.assertEqual(result['authentication_mode'],'anonymous')
        self.assertEqual(provider.call_args.args[-1],None)
        self.assertEqual(provider.call_count,1)

    def test_auth_failure_tries_configured_browsers_in_order(self):
        with patch('worker.DirectVideoUrlProvider.acquire',return_value=None),patch.dict(os.environ,{'GTC_BROWSER_COOKIE_SOURCES':'chrome,edge'}),patch('worker.YtDlpProvider.acquire',side_effect=[AcquisitionError('authentication_required',SECRET),AcquisitionError('cookies_unavailable',SECRET),({'download_seconds':1},{})]) as provider:
            result=acquire_remote(URL,self.root,100,automatic=True)
        self.assertEqual([c.args[-1] for c in provider.call_args_list],[None,'chrome','edge'])
        self.assertEqual(result['browser_source'],'edge')
        self.assertEqual(result['authentication_mode'],'browser_cookies')
        self.assertNotIn(SECRET,json.dumps(result))

    def test_explicit_browser_test_even_after_previous_network_failure(self):
        with patch('worker.DirectVideoUrlProvider.acquire') as direct,patch('worker.YtDlpProvider.acquire',return_value=({},{})) as provider:
            result=acquire_remote(URL,self.root,100,explicit='firefox')
        direct.assert_not_called();self.assertEqual(provider.call_args.args[-1],'firefox')
        self.assertEqual(result['status'],'success')

    def test_no_cookie_retry_on_unrelated_failures(self):
        for reason in ['network_error','unsupported_url','drm_or_protected','rate_limited','invalid_media']:
            with self.subTest(reason=reason),patch('worker.DirectVideoUrlProvider.acquire',return_value=None),patch('worker.YtDlpProvider.acquire',side_effect=AcquisitionError(reason,SECRET)) as provider:
                result=acquire_remote(URL,self.root,100,automatic=True)
                self.assertEqual(provider.call_count,1);self.assertNotIn(SECRET,json.dumps(result))

    def test_cookie_unavailable_is_actionable_and_secret_free(self):
        with patch('worker.YtDlpProvider.acquire',side_effect=RuntimeError('failed to load cookies '+SECRET)):
            result=acquire_remote(URL,self.root,100,explicit='edge')
        self.assertEqual(result['reason'],'cookies_unavailable');self.assertIn('local video',result['message'])
        self.assertNotIn(SECRET,json.dumps(result))

    def test_classify_browser_failures(self):
        for text,expected in [('could not find edge cookies database','browser_not_installed'),('Could not copy Chrome cookie database','browser_profile_locked'),('Failed to decrypt with DPAPI','cookies_unavailable'),('HTTP Error 412','session_required')]:
            self.assertEqual(classify(text),expected)

    def test_browser_names_not_untrusted_database_paths(self):
        for name in ['edge:../../secret','C:/cookies','edge --exec calc']:
            with self.assertRaises(ValueError):browser_sources(name)
        with patch.dict(os.environ,{'GTC_BROWSER_COOKIE_SOURCES':'firefox,edge,firefox'}):
            self.assertEqual(browser_sources(automatic=True),['firefox','edge'])
            self.assertEqual(browser_sources(),[])

    def test_cookie_scope_and_host_only_rules(self):
        jar=CookieJar();jar.set_cookie(cookie('.bilibili.com'));jar.set_cookie(cookie('.other.example'))
        jar.set_cookie(cookie('www.bilibili.com','HOST_ONLY',False))
        restrict_cookies(jar,URL)
        self.assertEqual(len(jar),2)
        for url,expected in [('https://api.bilibili.com/','session='+SECRET),('https://other.example/',None)]:
            req=Request(url);jar.add_cookie_header(req);self.assertEqual(req.get_header('Cookie'),expected)

    def test_stream_receives_cookie_jar_without_header_serialization(self):
        jar=CookieJar();jar.set_cookie(cookie('.bilibili.com'))
        response=MagicMock();response.__enter__.return_value=response;response.url=URL
        response.headers.get_content_type.return_value='video/mp4';response.headers.get.return_value='1';response.read.side_effect=[b'x',b'']
        with patch('worker.validate_url'),patch('worker.request.build_opener') as op:
            op.return_value.open.return_value=response
            result=stream_video(URL,self.root/'video',10,1,cookiejar=jar)
            self.assertTrue(any(getattr(x,'cookiejar',None) is jar for x in op.call_args.args))
        self.assertNotIn(SECRET,json.dumps(result))

    def test_redirect_does_not_forward_site_cookie_to_other_host(self):
        jar=CookieJar();jar.set_cookie(cookie('.bilibili.com'))
        req=Request(URL);jar.add_cookie_header(req)
        self.assertIn(SECRET,req.get_header('Cookie'))
        with patch('worker.validate_url'):
            redirected=SafeRedirect().redirect_request(req,None,302,'',{},'https://other.example/video')
        jar.add_cookie_header(redirected)
        self.assertIsNone(redirected.get_header('Cookie'))

    def test_direct_success_and_local_original_ignore_cookie_flags(self):
        with patch('worker.DirectVideoUrlProvider.acquire',return_value={}),patch('worker.YtDlpProvider.acquire') as provider:
            result=acquire_remote(URL,self.root,100,automatic=True)
        self.assertEqual(result['authentication_mode'],'anonymous');provider.assert_not_called()
        original=self.root/'original.mp4';original.write_bytes(b'fixture')
        from pipeline.timing import Timer
        Timer(self.root/'local').begin()
        with patch('acquire.validate_media',return_value={'sha256':'fixture'}),patch('acquire.subprocess.run') as provider:
            result=acquire_video(str(original),self.root/'local',cookies_from_browser='edge')
        self.assertIsNone(result['authentication_mode']);provider.assert_not_called()
        self.assertEqual(original.read_bytes(),b'fixture')

    def test_parent_safe_argv_no_raw_worker_logs_and_temp_cleanup(self):
        seen={}
        def run(command,**kwargs):
            seen.update(command=command,kwargs=kwargs)
            attempt=Path(command[3]);temp=Path(command[command.index('--cookie-temp')+1]);seen['temp']=temp
            (temp/'native-copy').write_text(SECRET)
            (attempt/'worker_result.json').write_text(json.dumps({'status':'failed','provider':'yt-dlp','authentication_mode':'browser_cookies','browser_source':'edge','reason':'cookies_unavailable','detail':'No readable site cookies','attempts':[]}))
            return MagicMock(returncode=1)
        from pipeline.timing import Timer
        Timer(self.root).begin()
        with patch('acquire.subprocess.run',side_effect=run):
            result=acquire_video(URL+'?x=a&y=b',self.root,cookies_from_browser='edge')
        self.assertEqual(seen['command'][2],URL+'?x=a&y=b');self.assertFalse(seen['kwargs']['shell'])
        self.assertFalse(seen['temp'].exists())
        self.assertEqual(result['cookie_temporary_cleanup'],'completed')
        for p in self.root.rglob('*'):
            if p.is_file():self.assertNotIn(SECRET,p.read_text(encoding='utf8'))

    def test_worker_timeout_cleans_native_cookie_material(self):
        import subprocess
        from pipeline.timing import Timer
        Timer(self.root).begin();seen={}
        def timeout(command,**kwargs):
            temp=Path(command[command.index('--cookie-temp')+1]);seen['temp']=temp
            (temp/'native-copy').write_text(SECRET)
            raise subprocess.TimeoutExpired(command,650,stderr=SECRET)
        with patch('acquire.subprocess.run',side_effect=timeout):
            result=acquire_video(URL,self.root,cookies_from_browser='chrome')
        self.assertEqual(result['reason'],'network_error')
        self.assertEqual(result['cookie_temporary_cleanup'],'completed')
        self.assertFalse(seen['temp'].exists());self.assertNotIn(SECRET,json.dumps(result))

    def test_private_url_rejected_before_browser_worker(self):
        from pipeline.timing import Timer
        Timer(self.root).begin()
        with patch('acquire.subprocess.run') as run:
            result=acquire_video('http://127.0.0.1/secret',self.root,cookies_from_browser='chrome')
        run.assert_not_called();self.assertEqual(result['reason'],'unsupported_url')

if __name__=='__main__':unittest.main()
