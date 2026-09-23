import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from .test_companion import APITests,body
from .agent_runner import AgentRunResult,CodexRunner
from .conversion import output_path,stage,validate_completion,sha
from pipeline.timing import Timer


class FakeRunner:
    def readiness(self):return None
    def run_conversion(self,run,video,cancel,progress):
        self.called=(run,video);progress();return AgentRunResult(0)

class ConversionTests(APITests):
    def test_resume_preserves_attempt_and_does_not_download_again(self):
        from pipeline.timing import atomic
        run_id='extension-'+'d'*32;run=self.server.runs/run_id
        source=self.acquisition({},run,conversion=True)
        source['sha256']=sha(Path(source['local_path']))
        atomic(run/'result/source/source.json',source)
        atomic(run/'working/job_status.json',{'run_id':run_id,'status':'failed','stage':'failed',
            'failure_stage':'v2_reconstruction','reason':'agent_exit_failed','agent_exit_code':1,'end_time':1})
        with patch('local_companion.app.acquire') as download,patch('local_companion.app.validate_completion',return_value={}):
            self.server.resume_failed(run_id);self.server.executor.shutdown(wait=True)
            download.assert_not_called()
            status=self.server.get_status(run_id)
            self.assertEqual(status['status'],'completed')
            self.assertEqual(status['attempts'][0]['agent_exit_code'],1)
        with self.assertRaises(ValueError):self.server.resume_failed('../escape')
    def test_second_listener_cannot_share_companion_port(self):
        import socket
        with socket.socket() as second:
            second.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            with self.assertRaises(OSError):second.bind(('127.0.0.1',self.port))
    def setUp(self):
        super().setUp();self.server.runner=FakeRunner()
    def acquisition(self,data,run,*args,**kwargs):
        self.assertTrue(kwargs['conversion'])
        video=run/'working/acquisition/video.mp4';video.parent.mkdir(parents=True,exist_ok=True);video.write_bytes(b'fixture')
        return {'status':'success','local_path':str(video),'pipeline_handoff':{'conversion_started':False}}
    def test_automatic_runner_and_review_required_outputs(self):
        result={'delivery_status':'REVIEW_REQUIRED','gp_available':True,'report_available':True,'review_count':2,'files':['score.gp','final_report.md']}
        with patch('local_companion.app.acquire',side_effect=self.acquisition),patch('local_companion.app.validate_completion',return_value=result):
            code,job=self.req('/convert','POST',body());self.assertEqual(code,202)
            self.server.executor.shutdown(wait=True)
            code,status=self.req(job['status_url']);self.assertEqual(status['status'],'completed')
            self.assertEqual(status['agent_exit_code'],0);self.assertEqual(status['result'],result)
            self.assertGreaterEqual(status['elapsed_seconds'],0)
            self.assertEqual(self.req(f'/runs/{job["run_id"]}/outputs')[1],result)
            self.assertTrue(self.server.runner.called)
    def test_zero_exit_without_artifacts_is_failure(self):
        with patch('local_companion.app.acquire',side_effect=self.acquisition):
            _,job=self.req('/convert','POST',body());self.server.executor.shutdown(wait=True)
            _,status=self.req(job['status_url']);self.assertEqual(status['status'],'failed')
            self.assertEqual(status['failure_stage'],'finalizing')
            self.assertEqual(self.req(f'/runs/{job["run_id"]}/files/score.gp')[0],409)
    def test_runtime_setup_fails_before_download(self):
        self.server.runner.readiness=lambda:'agent_not_authenticated'
        with patch('local_companion.app.acquire') as download:
            self.assertEqual(self.req('/convert','POST',body())[0],503);download.assert_not_called()
    def test_busy_and_cancel_do_not_start_second_job(self):
        entered=threading.Event();release=threading.Event()
        def runner(run,video,cancel,progress):
            entered.set();release.wait(3);return AgentRunResult(-1,'conversion_cancelled')
        self.server.runner.run_conversion=runner
        with patch('local_companion.app.acquire',side_effect=self.acquisition):
            _,job=self.req('/convert','POST',body());self.assertTrue(entered.wait(2))
            self.assertEqual(self.req('/convert','POST',body())[0],409)
            self.assertEqual(self.req(f'/runs/{job["run_id"]}/cancel','POST')[0],202)
            release.set();self.server.executor.shutdown(wait=True)
            self.assertEqual(self.req(job['status_url'])[1]['reason'],'conversion_cancelled')

class GateTests(unittest.TestCase):
    def test_npm_shim_uses_node_without_command_shell(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);entry=root/'node_modules/@openai/codex/bin/codex.js'
            entry.parent.mkdir(parents=True);entry.write_text('// test entry')
            runner=CodexRunner(str(root/'codex.cmd'))
            with patch('local_companion.agent_runner.shutil.which',return_value='node.exe'):
                self.assertEqual(runner.launcher(),['node.exe',str(entry)])
    def test_owned_process_scope_closes_running_process(self):
        import subprocess,sys
        from .process_scope import ProcessScope
        import os
        if os.name!='nt':self.skipTest('Windows Job Object lifecycle')
        child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'])
        try:
            scope=ProcessScope(child);scope.close()
            child.wait(timeout=5)
            self.assertIsNotNone(child.poll())
        finally:
            if child.poll() is None:child.kill();child.wait()
    def test_completion_gate_requires_fresh_evidence_not_just_report_prose(self):
        with tempfile.TemporaryDirectory() as d:
            run=Path(d)
            def put(p,value):
                path=run/p;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value),encoding='utf-8');return path
            gp=put('result/v3/export/score.gp','unit-test placeholder, not a real GP')
            score=put('result/v3/score.json',{})
            hashes={'canonical_sha256':sha(score),'gp_sha256':sha(gp)}
            put('result/v3/export/roundtrip_validation.json',dict(hashes,valid=True,unexpected_mismatches=[]))
            put('result/v3/verification/verification.json',dict(hashes,mechanical_valid=True,source_sweep={'complete':True}))
            put('result/v3/verification/observations.json',{'artifacts':[{'path':'score.json','sha256':sha(score)}]})
            put('result/final_report.md','fixture report')
            put('result/timing.json',{'status':'finished','active_spans':[],'total_wall_seconds':3})
            report={'status':'REVIEW_REQUIRED','checks':dict.fromkeys(['acquisition','canonical_validation','gp_roundtrip','v4_completed'],True),'evidence_hashes':{'v3/score.json':sha(score)},'issue_counts':{'USER_REVIEW_REQUIRED':2}}
            put('result/final_report.json',report)
            def imported(*args,**kwargs):
                put('working/companion_roundtrip.json',{'valid':True})
                from types import SimpleNamespace
                return SimpleNamespace(returncode=0)
            with patch('local_companion.conversion.subprocess.run',side_effect=imported):
                self.assertEqual(validate_completion(run)['review_count'],2)
                gp.write_text('changed GP')
                with self.assertRaisesRegex(ValueError,'stale_score_evidence'):validate_completion(run)
            report['checks']['v4_completed']=False;put('result/final_report.json',report)
            with self.assertRaisesRegex(ValueError,'failed_delivery_gate'):validate_completion(run)
    def test_allowlist_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run=root/'run';run.mkdir()
            for name in ['../secret','C:/secret','logs','score.gp/../secret']:
                with self.assertRaises(ValueError):output_path(run,name)
            (root/'secret').write_text('private')
            gp=run/'result/v3/export/score.gp';gp.parent.mkdir(parents=True)
            try:gp.symlink_to(root/'secret')
            except OSError:return # Windows without symlink privilege
            with self.assertRaises(ValueError):output_path(run,'score.gp')
    def test_stages_use_actual_timer(self):
        with tempfile.TemporaryDirectory() as d:
            timer=Timer(d);timer.begin();timer.start('v3')
            self.assertEqual(stage(d),'v3_transcription');timer.stop('v3');timer.start('v4')
            self.assertEqual(stage(d),'v4_verification');timer.stop('v4');timer.finish()
            self.assertEqual(stage(d),'finalizing')
    def test_prompt_and_no_shell_cli(self):
        runner=CodexRunner('C:/Program Files/Codex/codex.exe')
        self.assertEqual(runner.command()[0],'C:/Program Files/Codex/codex.exe')
        self.assertIn('workspace-write',runner.command());self.assertEqual(runner.command()[-1],'-')
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox',runner.command())
        self.assertIn('ALREADY',runner.prompt('run','video'));self.assertIn('$guitar-tab-cracker',runner.prompt('run','video'))
    def test_redacts_logs(self):
        runner=CodexRunner('codex',secrets=['PAIRING_SECRET'])
        value=runner.redact('PAIRING_SECRET https://cdn.example/video?token=SECRET sk-secretvalue')
        self.assertNotIn('PAIRING_SECRET',value);self.assertNotIn('token=SECRET',value);self.assertNotIn('sk-secretvalue',value)
