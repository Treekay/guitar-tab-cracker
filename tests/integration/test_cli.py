import json
from pathlib import Path
from unittest.mock import patch

from PIL import Image
import pytest

from tabstitch.cli import main


def test_config_command(capsys) -> None:
    assert main(["config"]) == 0
    assert json.loads(capsys.readouterr().out)["workspace"]["root"] == "runs"


def test_build_produces_artifacts(tmp_path: Path, image_directory: Path, capsys) -> None:
    runs = tmp_path / "runs"
    config = tmp_path / "config.toml"
    config.write_text('[roi]\nenabled = true\nx = 0.1\ny = 0.25\nwidth = 0.8\nheight = 0.5\n')
    assert main(["build", str(image_directory), "--run-id", "sample", "--output", str(runs), "--config", str(config)]) == 0
    run = runs / "sample"
    manifest = json.loads((run / "manifest.json").read_text())
    assert manifest["schema_version"] == 1
    assert manifest["status"] == "images_ready"
    assert manifest["config"]["workspace"]["root"] == str(runs.resolve())
    assert len(manifest["inputs"]) == 4
    for entry in manifest["inputs"]:
        assert (run / entry["artifact_path"]).read_bytes() == Path(entry["source_path"]).read_bytes()
        bbox = entry["roi"]["pixel_bbox"]
        with Image.open(run / entry["roi"]["artifact_path"]) as crop:
            crop.load()
            assert crop.size == (bbox["right"] - bbox["left"], bbox["bottom"] - bbox["top"])
    assert not list((run / "crops").iterdir())
    assert manifest["measure_candidates"] == []
    with Image.open(run / manifest["outputs"][0]) as preview:
        preview.verify()
    summary = (run / "summary.md").read_text()
    assert "Image count (artifacts completed): 4" in summary
    assert "120 x 80" in summary
    assert "ROI: enabled" in summary
    assert "No measure detection" in summary
    assert "No measure detection" in capsys.readouterr().err


def test_inspect_with_preview(tmp_path: Path, image_directory: Path, capsys, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    preview = tmp_path / "preview.png"
    assert main(["inspect", str(image_directory), "--preview", str(preview)]) == 0
    captured = capsys.readouterr()
    summary = json.loads(captured.out)
    assert summary["input_directory"] == str(image_directory.resolve())
    assert summary["image_count"] == 4
    assert summary["images"][0]["width"] == 120
    assert summary["images"][0]["roi"]["pixel_bbox"] == {"left": 0, "top": 0, "right": 120, "bottom": 80}
    assert not (tmp_path / "runs").exists()
    with Image.open(preview) as image:
        image.load()
        assert image.width == 1280
        assert image.getbbox()


def test_existing_run_is_preserved(tmp_path: Path, image_directory: Path) -> None:
    args = ["build", str(image_directory), "--run-id", "sample", "--output", str(tmp_path / "runs")]
    assert main(args) == 0
    manifest = tmp_path / "runs/sample/manifest.json"
    before = manifest.read_bytes()
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2
    assert manifest.read_bytes() == before


def test_preview_cannot_overwrite_source(image_directory: Path) -> None:
    original = image_directory / "01.png"
    before = original.read_bytes()
    with pytest.raises(SystemExit) as error:
        main(["inspect", str(image_directory), "--preview", str(original)])
    assert error.value.code == 2
    assert original.read_bytes() == before


def test_corruption_fails_without_creating_run(tmp_path: Path, image_directory: Path, capsys) -> None:
    (image_directory / "broken.png").write_bytes(b"broken")
    with pytest.raises(SystemExit) as error:
        main(["build", str(image_directory), "--run-id", "broken", "--output", str(tmp_path / "runs")])
    assert error.value.code == 2
    assert "broken.png" in capsys.readouterr().err
    assert not (tmp_path / "runs").exists()


def test_io_failure_recorded_in_manifest(tmp_path: Path, image_directory: Path) -> None:
    with patch("tabstitch.images.pipeline.shutil.copyfile", side_effect=OSError("disk full")):
        with pytest.raises(SystemExit):
            main(["build", str(image_directory), "--run-id", "failed", "--output", str(tmp_path / "runs")])
    manifest = json.loads((tmp_path / "runs/failed/manifest.json").read_text())
    assert manifest["status"] == "failed"
    assert "disk full" in manifest["error"]


def test_build_full_roi_preserves_pixels_and_orientation_policy(tmp_path: Path, capsys) -> None:
    source = tmp_path / "input"
    source.mkdir()
    original_path = source / "portrait.jpg"
    with Image.new("RGB", (30, 60), "green") as image:
        exif = Image.Exif()
        exif[274] = 6
        image.save(original_path, exif=exif)
    assert main(["build", str(source), "--run-id", "full", "--output", str(tmp_path / "runs")]) == 0
    with Image.open(original_path) as original, Image.open(tmp_path / "runs/full/normalized/0001_roi.png") as crop:
        assert crop.size == original.size == (30, 60)
        assert crop.tobytes() == original.tobytes()
        assert crop.getexif().get(274) is None


def test_layout_is_unavailable(tmp_path: Path, capsys) -> None:
    manifest = tmp_path / "manifest.json"; manifest.write_text("{}")
    assert main(["layout", str(manifest)]) == 2
    assert "Task 9" in capsys.readouterr().err
