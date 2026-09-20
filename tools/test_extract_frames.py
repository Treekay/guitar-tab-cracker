"""Mechanical contract checks only; these are not a video benchmark."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import extract_frames as helper


class ExtractionContract(unittest.TestCase):
    def test_invalid_batch_does_not_start_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "frames"
            for timestamps in ([1, 10], [float("nan")], [-1], [1, 1]):
                with self.subTest(timestamps=timestamps), patch.object(helper, "run") as run:
                    with self.assertRaises(ValueError):
                        helper.extract(Path("source"), timestamps, output,
                                       {"duration_seconds": 10}, "ffmpeg")
                    run.assert_not_called()
                    self.assertFalse(output.exists())

    def test_partial_failure_retains_provenance_without_claiming_completion(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            commands = []

            def execute(command):
                commands.append(command)
                if len(commands) == 2:
                    raise ValueError("decode failed")
                # Stub output validates orchestration, not video decoding.
                Path(command[-1]).write_bytes(b"stub frame")

            with patch.object(helper, "run", side_effect=execute):
                with self.assertRaisesRegex(ValueError, "decode failed"):
                    helper.extract(Path("source with spaces.mp4"), [2.5, 1], output,
                                   {"duration_seconds": 10}, "ffmpeg")
            record = json.loads(next(output.glob("extraction_*.json")).read_text())
            self.assertFalse(record["complete"])
            self.assertEqual(record["frames"], [{"requested_timestamp_seconds": 2.5,
                                                 "file": "t_2.500000000.png"}])
            self.assertEqual(commands[0][commands[0].index("-i") + 1], "source with spaces.mp4")
            with patch.object(helper, "run") as run:
                with self.assertRaisesRegex(ValueError, "overwritten"):
                    helper.extract(Path("source"), [2.5], output,
                                   {"duration_seconds": 10}, "ffmpeg")
                run.assert_not_called()

    def test_probe_preserves_metadata_and_source_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source"
            source.write_bytes(b"source identity fixture, not a video")
            response = {"streams": [{"index": 2, "width": 1920, "height": 1080,
                                     "avg_frame_rate": "30000/1001"}],
                        "format": {"duration": "12.5"}}
            with patch.object(helper, "run", return_value=subprocess.CompletedProcess(
                    [], 0, stdout=json.dumps(response))):
                metadata = helper.probe(source, "ffprobe")
            self.assertEqual(metadata["duration_seconds"], 12.5)
            self.assertAlmostEqual(metadata["approximate_fps"], 29.97002997)
            self.assertEqual(metadata["video_stream_index"], 2)
            self.assertEqual(len(metadata["sha256"]), 64)

    def test_missing_executable_has_actionable_error(self):
        with patch.object(subprocess, "run", side_effect=FileNotFoundError):
            with self.assertRaisesRegex(ValueError, "provide its explicit path"):
                helper.run(["missing-ffmpeg"])


if __name__ == "__main__":
    unittest.main()
