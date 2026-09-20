"""Presentation regression checks using pixel fixtures, not video reconstruction."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image, ImageFont
from pypdf import PdfReader

from export_visual_score import execute


class PresentationContract(unittest.TestCase):
    def test_metadata_and_fonts_do_not_change_measure_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Exercise an explicitly supplied portable font without committing one.
            (root / "explicit.ttf").write_bytes(ImageFont.load_default(size=38).font_bytes)
            baseline = None
            for name, settings, title in (
                ("unknown", {}, ""),
                ("metadata", {"title": "Study", "artist": "Example"}, "Study / Example"),
                ("font", {"title": "Study", "font": "explicit.ttf"}, "Study"),
                ("hidden", {"show_header": False}, ""),
                ("debug", {"debug": True}, ""),
            ):
                with self.subTest(name=name):
                    out = root / name
                    out.mkdir()
                    frame = Image.new("RGB", (120, 40), "black")
                    frame.paste("white", (60, 0, 120, 40))
                    frame.save(out / "frame.png")
                    plan = {"selection": [
                        {"sequence_index": 1, "source_frame": "frame.png", "box": [0, 0, 60, 40]},
                        {"sequence_index": 2, "source_frame": "frame.png", "box": [60, 0, 120, 40]},
                    ], "tone": "none", "pages": [[[1, 2]]], "positions": [[40, 240]],
                        "scale": 1, "page_pixels": [800, 600], "page_points": [842, 595], **settings}
                    path = root / "plan.json"
                    path.write_text(json.dumps(plan), encoding="utf-8")
                    execute(path, out)
                    reader = PdfReader(out / "full_score.pdf")
                    self.assertEqual(len(reader.pages), 1)
                    self.assertEqual(reader.metadata.title or "", title)
                    names = ["measures/001.png", "measures/002.png", "measures.json", "full_score.png"]
                    hashes = {name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in names}
                    if baseline is None:
                        baseline = hashes
                    self.assertEqual(hashes, baseline)
                    with Image.open(out / "page_001.png") as page:
                        # Unknown metadata leaves the title band empty, not fabricated.
                        if name in ("unknown", "hidden", "debug"):
                            self.assertEqual(page.crop((0, 0, 800, 110)).getextrema(), ((255, 255),)*3)
                        if name == "hidden":
                            self.assertEqual(page.crop((0, 0, 800, 200)).getextrema(), ((255, 255),)*3)


if __name__ == "__main__":
    unittest.main()
