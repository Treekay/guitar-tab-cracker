import json
from pathlib import Path
import tempfile
import time
import unittest
from timing import Timer
from final_report import delivery_status,build,normalize

class TimingReportTests(unittest.TestCase):
 def test_nested_revisited_wall_spans_and_unexecuted_null(self):
  with tempfile.TemporaryDirectory() as d:
   t=Timer(d);t.begin()
   with t.span('v2'):
    with t.span('v2.frame_survey_seconds'):time.sleep(.012)
   with t.span('v2'):
    with t.span('v2.frame_survey_seconds'):time.sleep(.012)
   t.finish();r=json.loads(t.output.read_text())
   self.assertGreaterEqual(r['phases']['v2']['frame_survey_seconds'],.024)
   self.assertGreaterEqual(r['total_wall_seconds'],r['phases']['v2']['wall_seconds'])
   self.assertIsNone(r['phases']['v3']['transcription_seconds'])
   with self.assertRaises(ValueError):t.start('v3')
 def test_failure_duration_and_open_span_gate(self):
  with tempfile.TemporaryDirectory() as d:
   t=Timer(d);t.begin();t.start('v2')
   with self.assertRaises(ValueError):t.finish()
   with self.assertRaises(ValueError):t.start('v3')
   t.stop('v2')
   with self.assertRaises(RuntimeError):
    with t.span('v3'):raise RuntimeError('test')
   t.finish();r=json.loads(t.output.read_text());self.assertEqual(r['spans'][-1]['outcome'],'failed')
 def test_status_never_equates_limitations_with_ready(self):
  good={'canonical':True,'gp':True,'v4':True}
  self.assertEqual(delivery_status(good,[]),'READY_FOR_DELIVERY')
  self.assertEqual(delivery_status(good,[{'status':'KNOWN_EXPORT_LIMITATION','impact':'low'}]),'REVIEW_RECOMMENDED')
  self.assertEqual(delivery_status(good,[{'status':'USER_REVIEW_REQUIRED','impact':'unknown'}]),'REVIEW_REQUIRED')
  self.assertEqual(delivery_status(good,[{'status':'UNEXPECTED_EXPORT_MISMATCH'}]),'REVIEW_REQUIRED')
  self.assertEqual(delivery_status({'gp':False},[]),'REVIEW_REQUIRED')
 def test_missing_evidence_report_is_explicit_and_not_success(self):
  with tempfile.TemporaryDirectory() as d:
   r=build(d);self.assertEqual(r['status'],'REVIEW_REQUIRED');self.assertEqual(len(r['issues']),4)
   self.assertIsNone(r['timing']);self.assertIsNone(r['counts']['notes'])
   self.assertIn('not measured', (Path(d)/'final_report.md').read_text(encoding='utf8'))
 def test_corrections_and_related_locations_remain_visible(self):
  s={'measures':[{'sequence_index':2,'printed_measure_number':7,'source':{'image':'../measures/002.png'}}]}
  raw={'issue_id':'fix','status':'AUTO_CORRECTED','location':{'measure':2,'event':3,'string':4,'field':'fret'},'canonical_value':5,'correction':{'before':4,'after':5},'notes':'Source-supported fix'}
  n=normalize(raw,s,Path('/run/v3'));self.assertEqual(n['measure']['printed_number'],7);self.assertTrue(n['v4_attempted_correction']);self.assertEqual(n['correction']['before'],4)
if __name__=='__main__':unittest.main()
