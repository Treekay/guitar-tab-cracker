import copy
import tempfile
import unittest
from pathlib import Path
from compare_transcriptions import compare_observation, propose_patch, sha
from verify_score import risks, check_source_sweep, untriaged_source_items


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)
        (self.base/'source.txt').write_text('Explicit human observation fixture, not image recognition')
        self.score={'measures':[{'barline':{'ending_numbers':[1]},'events':[{'notes':[{'string':5}]}]}]}
        self.observation={'path':'/measures/0/barline/ending_numbers','observed_value':[],
          'clear':True,'method':'independent_source_reread',
          'evidence':[{'path':'source.txt','sha256':sha(self.base/'source.txt')}]}
    def tearDown(self): self.temp.cleanup()
    def test_source_sweep_requires_complete_current_evidence(self):
        score={'measures':[{'sequence_index':1},{'sequence_index':2}]}
        entries=[{'measure':i,'method':'independent_source_reread','all_events_reread':True,
                  'events':'4:1=7','features':'Explicit source observation',
                  'source_evidence':self.observation['evidence']} for i in (1,2)]
        self.assertTrue(check_source_sweep(score,entries,self.base)['complete'])
        self.assertFalse(check_source_sweep(score,entries[:1],self.base)['complete'])
        self.assertFalse(check_source_sweep(score,entries[::-1],self.base)['complete'])
        (self.base/'source.txt').write_text('changed')
        self.assertFalse(check_source_sweep(score,entries,self.base)['complete'])
    def test_unresolved_cannot_be_hidden_by_unrelated_or_verified_issue(self):
        u={'measure':1,'event':2,'field':'grace_slide','issue':'Unknown onset'}
        score={'unresolved':[u]}
        issue={'location':{'measure':1,'event':2,'field':'other'},'status':'KNOWN_EXPORT_LIMITATION'}
        self.assertEqual(untriaged_source_items(score,[issue]),[u])
        issue['location']['field']='grace_slide';issue['status']='VERIFIED'
        self.assertEqual(untriaged_source_items(score,[issue]),[u])
        issue['status']='USER_REVIEW_REQUIRED'
        self.assertEqual(untriaged_source_items(score,[issue]),[])
    def test_repeat_only_vs_false_ending_is_flagged(self):
        r=compare_observation(self.score,self.observation,self.base)
        self.assertTrue(r['discrepancy']);self.assertTrue(r['correctable_automatically'])
        self.assertEqual(r['status'],'USER_REVIEW_REQUIRED')
    def test_source_endings_override_no_ending_manual_reference(self):
        o=dict(self.observation,observed_value=[1]);r=compare_observation(self.score,o,self.base)
        self.assertEqual(r['status'],'VERIFIED');self.assertFalse(r['correctable_automatically'])
    def test_confirmed_reference_wrong_string_does_not_change_source_score(self):
        o=dict(self.observation,path='/measures/0/events/0/notes/0/string',observed_value=5)
        self.assertEqual(compare_observation(self.score,o,self.base)['status'],'VERIFIED')
        o['observed_value']=4;o['method']='manual_gp_reference'
        self.assertFalse(compare_observation(self.score,o,self.base)['correctable_automatically'])
    def test_stale_evidence_rejected(self):
        (self.base/'source.txt').write_text('changed')
        self.assertFalse(compare_observation(self.score,self.observation,self.base)['evidence_current'])
        with self.assertRaises(ValueError):propose_patch(self.score,self.observation,self.base)
    def test_ambiguous_observation_cannot_correct(self):
        self.observation['clear']=False
        with self.assertRaises(ValueError):propose_patch(self.score,self.observation,self.base)
    def test_minimal_patch_preserves_other_fields_and_original(self):
        old=copy.deepcopy(self.score);draft,log=propose_patch(self.score,self.observation,self.base)
        self.assertEqual(self.score,old);self.assertEqual(draft['measures'][0]['events'],old['measures'][0]['events'])
        self.assertEqual(draft['measures'][0]['barline']['ending_numbers'],[])
        self.assertNotEqual(log['status'],'AUTO_CORRECTED')
    def test_whole_measure_patch_rejected(self):
        self.observation.update(path='/measures/0',observed_value={})
        with self.assertRaises(ValueError):propose_patch(self.score,self.observation,self.base)
    def test_equal_but_not_independent_is_not_verified(self):
        self.observation.update(observed_value=[1],method='canonical_copy')
        self.assertEqual(compare_observation(self.score,self.observation,self.base)['status'],'USER_REVIEW_REQUIRED')
    def test_bool_and_integer_are_not_equal_json_fields(self):
        self.score['measures'][0]['barline']['repeat_start']=True
        self.observation.update(path='/measures/0/barline/repeat_start',observed_value=1)
        self.assertTrue(compare_observation(self.score,self.observation,self.base)['discrepancy'])
    def test_whole_note_list_replacement_rejected(self):
        self.observation.update(path='/measures/0/events/0/notes',observed_value=[])
        with self.assertRaises(ValueError):propose_patch(self.score,self.observation,self.base)


if __name__=='__main__':unittest.main()
