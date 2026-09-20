"""Mechanical preservation tests; these do not replace visual notation review."""
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from export_visual_score import execute
from normalize_measures import normalize_selected_crop


class NormalizationContract(unittest.TestCase):
    def test_no_recipe_preserves_color_pixels(self):
        source = Image.new("RGB", (8, 6), (240, 225, 90))
        output, record = normalize_selected_crop(source, None, "plan.json")
        self.assertEqual(output.tobytes(), source.tobytes())
        self.assertEqual(record["status"], "source_preserved")
        self.assertTrue(record["source_faithful"])
        self.assertFalse(record["visually_reviewed"])

    def test_explicit_inversion_retains_faint_pixels_and_geometry(self):
        # A mechanical dark-background fixture, not validation of a second video style.
        source = Image.new("RGB", (3, 1))
        source.putdata([(0, 0, 0), (255, 255, 255), (90, 90, 90)])
        output, record = normalize_selected_crop(source, {
            "status": "partial", "operations": [{"op": "invert"}],
            "uncertainty": "Awaiting visual review",
        }, "plan.json")
        self.assertEqual([output.getpixel((x, 0)) for x in range(3)], [(255, 255, 255), (0, 0, 0), (165, 165, 165)])
        self.assertEqual(output.size, source.size)
        self.assertIsNone(record["source_faithful"])

    def test_explicit_levels_keep_intermediate_strokes(self):
        source = Image.new("RGB", (4, 1))
        source.putdata([(20, 20, 20), (100, 100, 100), (200, 200, 200), (245, 245, 245)])
        output, _ = normalize_selected_crop(source, {
            "status": "partial", "operations": [
                {"op": "grayscale", "mode": "max_rgb"},
                {"op": "levels", "black": 30, "white": 240, "gamma": 1.2},
            ],
        }, "plan.json")
        values = list(output.convert("L").tobytes())
        self.assertEqual(values[0], 0)
        self.assertEqual(values[-1], 255)
        self.assertTrue(0 < values[1] < values[2] < 255)

    def test_invalid_or_unreviewed_decisions_fail(self):
        source = Image.new("RGB", (8, 6), "white")
        for decision in (
            {"status": "normalized"},
            {"status": "normalized", "visually_reviewed": True, "source_faithful": False},
            {"status": "source_preserved", "operations": [{"op": "invert"}]},
            {"status": "partial", "operations": [{"op": "levels", "black": 240, "white": 30, "gamma": 1}]},
            {"status": "partial", "operations": [{"op": "threshold", "value": 100}]},
        ):
            with self.subTest(decision=decision), self.assertRaises(ValueError):
                normalize_selected_crop(source, decision, "plan.json")

    def test_external_preparation_requires_matching_geometry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = Image.new("RGB", (8, 6), "black")
            prepared = Image.new("RGB", source.size, "white")
            prepared.save(root / "prepared.png")
            decision = {"status": "partial", "prepared_image": "prepared.png", "method": "Explicit external transform"}
            output, record = normalize_selected_crop(source, decision, root / "plan.json")
            self.assertEqual(output.tobytes(), prepared.tobytes())
            self.assertEqual(record["prepared_image"], "prepared.png")
            Image.new("RGB", (9, 6)).save(root / "prepared.png")
            with self.assertRaisesRegex(ValueError, "geometry"):
                normalize_selected_crop(source, decision, root / "plan.json")

    def test_export_retains_raw_context_and_honors_measure_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frame = Image.new("RGB", (120, 40), (20, 40, 60))
            frame.paste((100, 80, 60), (60, 0, 120, 40))
            frame.save(root / "frame.png")
            plan = {"normalization": {"status": "partial", "operations": [{"op": "invert"}]},
                    "selection": [
                        {"sequence_index": 1, "source_frame": "frame.png", "box": [5, 0, 60, 40], "context_pixels": [5, 5]},
                        {"sequence_index": 2, "source_frame": "frame.png", "box": [60, 0, 120, 40],
                         "normalization": {"status": "source_preserved", "uncertainty": "Unsafe style"}},
                    ], "pages": [[[1, 2]]], "positions": [[40, 240]], "scale": 1,
                    "page_pixels": [800, 600], "page_points": [842, 595]}
            path = root / "plan.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            execute(path, root)
            records = json.loads((root / "measures.json").read_text())
            self.assertEqual([item["sequence_index"] for item in records], [1, 2])
            with Image.open(root / "full_score.png") as strip:
                offset = 0
                for item in records:
                    with Image.open(root / item["source_output"]) as raw, Image.open(root / item["output"]) as clean:
                        self.assertEqual(raw.tobytes(), frame.crop(item["source_crop_box"]).tobytes())
                        self.assertEqual(raw.size, clean.size)
                        if item["sequence_index"] == 2:
                            self.assertEqual(clean.tobytes(), raw.tobytes())
                            self.assertEqual(item["normalization"]["status"], "source_preserved")
                        else:
                            self.assertNotEqual(clean.tobytes(), raw.tobytes())
                        core = clean.crop(item["core_bbox_in_output"])
                        self.assertEqual(strip.crop((offset, 0, offset+core.width, core.height)).tobytes(), core.tobytes())
                        offset += core.width


if __name__ == "__main__":
    unittest.main()
