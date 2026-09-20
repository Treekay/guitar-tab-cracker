"""Source-pixel and legacy-plan guards; visual decisions remain with the agent."""
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image
from export_visual_score import execute


class SourceMeasureContract(unittest.TestCase):
    def test_source_pixels_context_order_and_single_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frame = Image.new("RGB", (120, 40), (21, 47, 83))
            frame.paste((191, 207, 163), (60, 0, 120, 40))
            frame.putpixel((10, 10), (22, 48, 84))  # Faint color detail must survive.
            frame.save(root / "frame.png")
            plan = {"selection": [
                {"sequence_index": 1, "source_frame": "frame.png", "box": [5, 0, 60, 40], "context_pixels": [5, 5]},
                {"sequence_index": 2, "source_frame": "frame.png", "box": [60, 0, 120, 40]},
            ], "pages": [[[1, 2]]], "positions": [[40, 240]], "scale": 1,
                "page_pixels": [800, 600], "page_points": [842, 595]}
            path = root / "plan.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            execute(path, root)
            self.assertFalse((root / "source_measures").exists())
            records = json.loads((root / "measures.json").read_text())
            self.assertEqual([item["sequence_index"] for item in records], [1, 2])
            with Image.open(root / "full_score.png") as strip:
                offset = 0
                for item in records:
                    self.assertFalse({"normalization", "source_output", "tonal_transform"} & item.keys())
                    with Image.open(root / item["output"]) as tile:
                        self.assertEqual(tile.tobytes(), frame.crop(item["source_crop_box"]).tobytes())
                        core = tile.crop(item["core_bbox_in_output"])
                        self.assertEqual(strip.crop((offset, 0, offset+core.width, core.height)).tobytes(), core.tobytes())
                        offset += core.width

    def test_legacy_processing_fails_before_writing_outputs(self):
        for settings in (
            {"normalization": {}}, {"tone": "max_rgb_to_gray"},
            {"selection": [{"normalization": {"status": "source_preserved"}}]},
        ):
            with self.subTest(settings=settings), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = root / "plan.json"
                path.write_text(json.dumps({"selection": [], **settings}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    execute(path, root)
                self.assertFalse((root / "measures").exists())
                self.assertFalse((root / "source_measures").exists())


if __name__ == "__main__":
    unittest.main()
