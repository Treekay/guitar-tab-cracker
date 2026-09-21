import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch,MagicMock
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from acquisition.security import validate_url,audit_network,AcquisitionError,public_ip
from worker import classify,select_format,SafeRedirect,stream_video
from acquire import cleanup,validate_media

class AcquisitionTests(unittest.TestCase):
 def test_reject_private_schemes_hosts_credentials(self):
  for url in ['file:///C:/secret','http://localhost/a','http://127.0.0.1/a','http://10.1.2.3/a','http://169.254.169.254/latest','http://[::1]/','http://[::ffff:127.0.0.1]/','http://router.local/','http://user:pass@example.com/','https://example.com:22/','http://2130706433/','http://example.com\\@127.0.0.1/']:
   with self.subTest(url=url),self.assertRaises(AcquisitionError):validate_url(url,resolve=False)
 def test_dns_private_or_mixed_answers_blocked(self):
  with patch('acquisition.security.socket.getaddrinfo',return_value=[(2,1,6,'',('93.184.216.34',443)),(2,1,6,'',('10.0.0.1',443))]):
   with self.assertRaises(AcquisitionError):validate_url('https://example.com/')
 def test_connect_rechecks_dns_rebinding_and_ports(self):
  audit_network('socket.connect',(None,('93.184.216.34',443)))
  for address in [('127.0.0.1',443),('10.0.0.1',80),('example.com',443),('93.184.216.34',22)]:
   with self.assertRaises(AcquisitionError):audit_network('socket.connect',(None,address))
 def test_redirect_to_private_blocked_before_request(self):
  with self.assertRaises(AcquisitionError):SafeRedirect().redirect_request(None,None,302,'',{},'http://127.0.0.1/secret')
 def test_external_runtime_blocked(self):
  with self.assertRaises(AcquisitionError):audit_network('subprocess.Popen',('x',))
 def test_auth_drm_rate_errors_are_actionable(self):
  self.assertEqual(classify('The web client only works when logged-in'),'authentication_required')
  self.assertEqual(classify('This video is DRM protected'),'drm_or_protected')
  self.assertEqual(classify('HTTP Error 429'),'rate_limited')
  self.assertEqual(classify('HTTP Error 403'),'access_restricted')
  self.assertEqual(classify('timed out'),'network_error')
 def test_quality_preserved_without_extreme_resolution(self):
  def f(height):return {'height':height,'width':height*2,'protocol':'https','vcodec':'h264','url':'https://example.com/a'}
  self.assertEqual(select_format({'formats':[f(360),f(1080),f(2160)]})['height'],1080)
  self.assertEqual(select_format({'formats':[f(1440),f(2160)]})['height'],1440)
  with self.assertRaises(AcquisitionError):select_format({'formats':[dict(f(1080),has_drm=True)]})
 def test_html_does_not_become_media(self):
  response=MagicMock();response.__enter__.return_value=response;response.url='https://example.com/a';response.headers.get_content_type.return_value='text/html'
  with tempfile.TemporaryDirectory() as d,patch('worker.validate_url'),patch('worker.request.build_opener') as op:
   op.return_value.open.return_value=response
   self.assertIsNone(stream_video(response.url,Path(d)/'media',10,1,allow_html=True));self.assertFalse((Path(d)/'media').exists())
 def test_size_limit_checked_before_opening_output(self):
  response=MagicMock();response.__enter__.return_value=response;response.url='https://example.com/a';response.headers.get_content_type.return_value='video/mp4';response.headers.get.return_value='1000'
  with tempfile.TemporaryDirectory() as d,patch('worker.validate_url'),patch('worker.request.build_opener') as op:
   op.return_value.open.return_value=response
   with self.assertRaises(AcquisitionError):stream_video(response.url,Path(d)/'media',10,1)
   self.assertFalse((Path(d)/'media').exists())
 def test_probe_success_without_video_is_failure(self):
  with tempfile.TemporaryDirectory() as d,patch('acquire.subprocess.run') as run:
   p=Path(d)/'fake';p.write_bytes(b'not-video');run.return_value=MagicMock(returncode=0,stdout='{"streams":[]}',stderr='')
   with self.assertRaises(AcquisitionError):validate_media(p,'ffprobe','ffmpeg')
 def test_cleanup_never_deletes_original_or_escaped_path(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d)/'run';(r/'result/source').mkdir(parents=True);original=Path(d)/'original.mp4';original.write_bytes(b'original')
   record=r/'result/source/source.json';record.write_text(json.dumps({'source_type':'local','remote_download_files':[str(original)]}))
   cleanup(r,True);self.assertTrue(original.exists())
   record.write_text(json.dumps({'source_type':'url','remote_download_files':[str(original)]}))
   with self.assertRaises(ValueError):cleanup(r,True)
   self.assertTrue(original.exists())
if __name__=='__main__':unittest.main()
