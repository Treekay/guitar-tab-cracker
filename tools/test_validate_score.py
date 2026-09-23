"""Mechanical tests only; synthetic data is not visual acceptance evidence."""
import copy
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest
from validate_score import validate, duration
from assemble_score import assemble


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)/'v3';self.base.mkdir()
        (self.base.parent/'measures').mkdir();(self.base.parent/'measures/001.png').write_bytes(b'path-only-test')
        self.manifest=[dict(sequence_index=1,printed_measure_number=1,output='measures/001.png')]
        note=dict(string=1,fret=0,parenthesized=False,dead=False,techniques=[],confidence='high',uncertainty=None,display='fret')
        event=dict(index=1,voice=1,duration=1,dots=0,tuplet=None,rest=False,notes=[note],confidence='high',uncertainty=None)
        measure=dict(sequence_index=1,printed_measure_number=1,confidence='high',uncertainty=None,
          barline=dict(start='normal',end='final',repeat_start=False,repeat_end=False,repeat_count=None,ending_numbers=[]),
          time_signature=None,tempo_bpm=None,pickup=False,events=[event],source=dict(image='../measures/001.png',core_bbox_in_image=[0,0,1,1]),
          audit=dict(pass1='inspected',pass2='inspected'))
        self.score=dict(schema_version=1,string_convention='1=top/highest;6=bottom/lowest',
          metadata=dict(title=None,artist=None,tempo_bpm=None,time_signature=dict(numerator=4,denominator=4),capo=None,tuning=None),
          measures=[measure],relations=[],annotations=[],repeat_regions=[],unresolved=[])

    def check(self):return validate(self.score,self.base,self.manifest)
    def event(self):return self.score['measures'][0]['events'][0]
    def test_valid(self):self.assertTrue(self.check()['valid']);self.assertFalse(self.check()['warnings'])
    def test_event_strokes(self):
        self.event()['notes'].append(dict(self.event()['notes'][0],string=6))
        self.event().update(brush={'type':'arpeggio','direction':'up'},pick_stroke='down')
        self.assertTrue(self.check()['valid'])
        for value in [{'type':'unknown','direction':'up'},{'type':'strum','direction':'sideways'},{'type':'arpeggio'}]:
            self.event()['brush']=value;self.assertFalse(self.check()['valid'])
        self.event()['brush']={'type':'strum','direction':'down'}
        self.event()['notes'].pop();self.assertFalse(self.check()['valid'])
        self.event().update(brush=None,pick_stroke='up',notes=[],rest=True)
        self.assertFalse(self.check()['valid'])
        self.event()['pick_stroke']=None;self.assertTrue(self.check()['valid'])
    def test_dot_tuplet_exact(self):
        self.event().update(duration=8,dots=2,tuplet={'numerator':3,'denominator':2})
        self.assertEqual(duration(self.event()),Fraction(7,48))
    def test_warning_never_repairs(self):
        self.event()['duration']=2;before=copy.deepcopy(self.score)
        self.assertEqual(len(self.check()['warnings']),1);self.assertEqual(before,self.score)
    def test_pickup_and_signature_change(self):
        self.event()['duration']=4;self.score['measures'][0]['pickup']=True
        self.assertFalse(self.check()['warnings'])
        self.score['measures'][0].update(pickup=False,time_signature={'numerator':1,'denominator':4})
        self.assertFalse(self.check()['warnings'])
    def test_bad_schema_types(self):
        for key,value in [('duration',3),('dots',-1),('index',True)]:
            with self.subTest(key=key):
                original=self.event()[key];self.event()[key]=value
                self.assertFalse(self.check()['valid']);self.event()[key]=original
    def test_strings_frets(self):
        n=self.event()['notes'][0]
        for key,value in [('string',0),('string',7),('fret',-1)]:
            with self.subTest(key=key,value=value):
                original=n[key];n[key]=value;self.assertFalse(self.check()['valid']);n[key]=original
    def test_rest_and_duplicate_string(self):
        self.event()['rest']=True;self.assertFalse(self.check()['valid'])
        self.event()['rest']=False;self.event()['notes']*=2;self.assertFalse(self.check()['valid'])
    def test_coverage_and_indices(self):
        self.manifest*=2;self.assertFalse(self.check()['valid']);self.manifest=self.manifest[:1]
        self.event()['index']=2;self.assertFalse(self.check()['valid'])
    def test_source_identity(self):
        self.score['measures'][0]['source']['image']='../measures/missing.png'
        self.assertFalse(self.check()['valid'])
    def test_tie_reference(self):
        self.score['relations']=[dict(id='r1',type='tie',**{'from':dict(measure=1,event=1,string=1),'to':dict(measure=2,event=1,string=1)},confidence='high',uncertainty=None)]
        self.assertFalse(self.check()['valid'])
    def test_continuation_requires_tie(self):
        self.event()['notes'][0]['display']='tie_continuation';self.assertFalse(self.check()['valid'])
    def test_unpaired_repeat(self):
        self.score['measures'][0]['barline']['repeat_end']=True;self.assertFalse(self.check()['valid'])
    def test_ending_mismatch(self):
        self.score['measures'][0]['barline']['ending_numbers']=[2];self.assertFalse(self.check()['valid'])
    def test_unknown_duration(self):
        self.event()['duration']=None;self.assertFalse(self.check()['valid'])
        self.event()['uncertainty']='Beam obscured'
        self.score['unresolved']=[dict(measure=1,event=1,field='duration',issue='Beam obscured',candidates=[4,8],confidence='medium')]
        self.assertTrue(self.check()['valid']);self.assertTrue(self.check()['warnings'])
    def test_multiple_voices_separate(self):
        e=copy.deepcopy(self.event());e.update(index=2,voice=2);e['notes'][0]['string']=2
        self.score['measures'][0]['events'].append(e);self.assertFalse(self.check()['warnings'])
    def test_assembler_rejects_pending_audit(self):
        directory=self.base/'measures';directory.mkdir()
        self.score['measures'][0]['audit']['pass2']='pending'
        (directory/'001.json').write_text(json.dumps(self.score['measures'][0]),encoding='utf-8')
        header={k:v for k,v in self.score.items() if k!='measures'}
        with self.assertRaises(ValueError):assemble(header,directory)


if __name__=='__main__':unittest.main()
