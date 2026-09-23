import http.client
import json
from pathlib import Path
import tempfile
import threading
import subprocess
import shutil
import unittest
from unittest.mock import patch
from .app import Companion
from .security import payload,redacted
from .network import playlist,Unsupported,Protected,Fetcher,hls
from .config import ROOT
from acquisition.acquire import validate_media

TOKEN='test-installation-token-not-a-real-secret-12345'
ID='a'*32
URL='https://example.com/watch?v=1'

def body():return {'page_url':URL,'page_title':'Test','media_candidates':[{'url':'https://cdn.example.com/video.mp4?token=SECRET','type':'direct','source':'video.currentSrc'}],'request_context':{'referer':URL,'user_agent':'test'}}

class SecurityTests(unittest.TestCase):
    def test_no_cookies_authorization_paths_or_commands(self):
        for context in [{'Cookie':'secret'},{'Authorization':'secret'},{'command':'calc'}]:
            b=body();b['request_context']=context
            with self.assertRaises(ValueError):payload(b)
        b=body();b['output_path']='C:/escape'
        with self.assertRaises(ValueError):payload(b)
    def test_private_urls_and_header_injection_rejected(self):
        for url in ['http://127.0.0.1/x','http://10.0.0.1/x','file:///secret']:
            b=body();b['media_candidates'][0]['url']=url
            with self.assertRaises(Exception):payload(b)
        b=body();b['request_context']['user_agent']='good\r\nCookie: bad'
        with self.assertRaises(ValueError):payload(b)
    def test_blob_not_forwarded_and_query_redacted(self):
        b=body();b['media_candidates'][0]['url']='blob:https://example.com/opaque'
        self.assertEqual(payload(b)['media_candidates'],[]);self.assertTrue(payload(b)['blob_detected'])
        self.assertEqual(redacted('https://example.com/a?token=SECRET#x'),'https://example.com/a?REDACTED')
        self.assertNotIn('?v=',payload(body())['headers']['Referer'])
    def test_hls_local_allowlist_and_relative_resolution(self):
        plan=playlist('#EXTM3U\n#EXT-X-TARGETDURATION:3\n#EXTINF:3,\na.ts?secret=x\n#EXT-X-ENDLIST','https://cdn.example.com/sub/list.m3u8')
        self.assertEqual(plan['downloads'][0][0],'https://cdn.example.com/sub/a.ts?secret=x')
        self.assertNotIn('secret',plan['local']);self.assertNotIn('http',plan['local'])
    def test_encrypted_live_byterange_external_audio_rejected(self):
        for extra,exc in [('#EXT-X-KEY:METHOD=AES-128,URI="key"',Protected),('#EXT-X-BYTERANGE:100@0',Unsupported),('#EXT-X-MEDIA:TYPE=AUDIO,URI="a.m3u8"',Unsupported)]:
            with self.assertRaises(exc):playlist('#EXTM3U\n'+extra+'\n#EXTINF:1,\na.ts\n#EXT-X-ENDLIST','https://example.com/')
        with self.assertRaises(Unsupported):playlist('#EXTM3U\n#EXTINF:1,\na.ts','https://example.com/')
    def test_hls_master_selects_reasonable_resolution(self):
        plan=playlist('#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=100,RESOLUTION=640x360\nlow.m3u8\n#EXT-X-STREAM-INF:BANDWIDTH=500,RESOLUTION=1920x1080\nmid.m3u8\n#EXT-X-STREAM-INF:BANDWIDTH=900,RESOLUTION=3840x2160\nhigh.m3u8','https://example.com/root/')
        self.assertEqual(plan['variant'],'https://example.com/root/mid.m3u8')
    def test_private_segment_is_blocked_before_open(self):
        fetch=Fetcher({})
        with patch.object(fetch.opener,'open') as open_request:
            with self.assertRaises(Exception):fetch.fetch('http://169.254.169.254/secret')
            open_request.assert_not_called()

class APITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.server=Companion({'token':TOKEN,'extension_id':ID},'ffprobe','ffmpeg',port=0,runs=self.tmp.name)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.port=self.server.server_port
    def tearDown(self):self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
    def req(self,path='/health',method='GET',data=None,headers=None):
        h={'Origin':'chrome-extension://'+ID,'X-GTC-Token':TOKEN,'X-GTC-Extension-ID':ID,'Content-Type':'application/json'}
        if headers:h.update(headers)
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=3)
        conn.request(method,path,json.dumps(data) if data is not None else None,headers=h)
        result=conn.getresponse();raw=result.read();conn.close();return result.status,json.loads(raw) if raw else None
    def test_token_origin_host_and_health(self):
        self.assertEqual(self.req()[0],200)
        for h in [{'X-GTC-Token':''},{'X-GTC-Extension-ID':'b'*32},{'Origin':'https://evil.example'},{'Host':'evil.example'},{'Origin':''}]:self.assertEqual(self.req(headers=h)[0],403)
    def test_no_arbitrary_command_or_path_endpoints(self):
        self.assertEqual(self.req('/convert','POST',{'command':'calc'})[0],400)
        self.assertEqual(self.req('/runs/../../secret/status')[0],404)
        self.assertEqual(self.req('/acquire','POST',{'command':'calc'})[0],400)
    def test_preflight_does_not_disclose_authentication(self):
        h={'X-GTC-Token':'','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'Content-Type,X-GTC-Token'}
        self.assertEqual(self.req('/acquire','OPTIONS',headers=h)[0],204)
        h['Origin']='https://evil.example';self.assertEqual(self.req('/acquire','OPTIONS',headers=h)[0],403)
    def test_submit_and_poll_reuses_media_boundary(self):
        with patch('local_companion.app.acquire',return_value={'status':'success','local_path':'validated.mp4','sha256':'test'}):
            code,result=self.req('/acquire','POST',body());self.assertEqual(code,202)
            self.server.executor.shutdown(wait=True)
            code,status=self.req(result['status_url']);self.assertEqual(code,200);self.assertEqual(status['status'],'success')

class FFmpegHLSTest(unittest.TestCase):
    def test_sanitized_vod_remux_and_existing_validation(self):
        ffmpeg=ROOT/'tmp/video-runtime/node_modules/ffmpeg-static/ffmpeg.exe'
        ffprobe=ROOT/'tmp/video-runtime/node_modules/ffprobe-static/bin/win32/x64/ffprobe.exe'
        if not ffmpeg.exists() or not ffprobe.exists():self.skipTest('Local ffmpeg fixture runtime not installed')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);fixture=root/'fixture';out=root/'download';fixture.mkdir();out.mkdir()
            subprocess.run([str(ffmpeg),'-v','error','-f','lavfi','-i','color=c=blue:s=160x90:r=10','-t','2','-c:v','libx264','-g','10','-hls_time','1','-hls_playlist_type','vod','-hls_segment_filename',str(fixture/'s%02d.ts'),str(fixture/'input.m3u8')],check=True,capture_output=True)
            def fetch(instance,url,destination=None,manifest=False):
                name=url.rsplit('/',1)[-1]
                if manifest:return (fixture/name).read_text(),url
                shutil.copyfile(fixture/name,destination);return None,url
            with patch.object(Fetcher,'fetch',fetch):result=hls('https://example.com/input.m3u8',out,{})
            self.assertEqual(result['segments'],2)
            subprocess.run([str(ffmpeg),'-v','error','-protocol_whitelist','file,pipe','-allowed_extensions','ALL','-i',str(out/'local.m3u8'),'-c','copy',str(out/'video.mp4')],check=True,capture_output=True)
            media=validate_media(out/'video.mp4',str(ffprobe),str(ffmpeg))
            self.assertEqual((media['width'],media['height']),(160,90));self.assertGreater(media['duration_seconds'],1)

if __name__=='__main__':unittest.main()
