import json
from pathlib import Path
from tabstitch.cli import main


def test_config_command(capsys) -> None:
    assert main(["config"]) == 0
    assert json.loads(capsys.readouterr().out)["workspace"]["root"] == "runs"


def test_build_initializes_run(tmp_path: Path, capsys) -> None:
    source = tmp_path / "images"; source.mkdir(); runs = tmp_path / "runs"
    assert main(["build", str(source), "--run-id", "sample", "--output", str(runs)]) == 0
    assert (runs / "sample" / "manifest.json").is_file()
    assert "not implemented" in capsys.readouterr().err


def test_inspect_is_scaffold(tmp_path: Path, capsys) -> None:
    source = tmp_path / "images"; source.mkdir()
    assert main(["inspect", str(source)]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["input_directory"] == str(source.resolve())
    assert "Task 2" in captured.err


def test_layout_is_unavailable(tmp_path: Path, capsys) -> None:
    manifest = tmp_path / "manifest.json"; manifest.write_text("{}")
    assert main(["layout", str(manifest)]) == 2
    assert "Task 9" in capsys.readouterr().err
