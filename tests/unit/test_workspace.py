import json
from pathlib import Path
import pytest
from tabstitch.workspace import ARTIFACT_DIRECTORIES, RunWorkspace, WorkspaceError


def test_creates_inspectable_workspace(tmp_path: Path) -> None:
    source = tmp_path / "images"; source.mkdir()
    workspace = RunWorkspace.create(tmp_path / "runs", "demo-01", source, {"test": True})
    assert all((workspace.root / name).is_dir() for name in ARTIFACT_DIRECTORIES)
    manifest = json.loads((workspace.root / "manifest.json").read_text())
    assert manifest["run_id"] == "demo-01" and manifest["status"] == "initialized"
    assert manifest["source_directory"] == str(source.resolve())


@pytest.mark.parametrize("run_id", ["../escape", "nested/run", "", ".hidden"])
def test_rejects_unsafe_run_id(tmp_path: Path, run_id: str) -> None:
    source = tmp_path / "images"; source.mkdir()
    with pytest.raises(WorkspaceError):
        RunWorkspace.create(tmp_path / "runs", run_id, source, {})


def test_refuses_overwrite(tmp_path: Path) -> None:
    source = tmp_path / "images"; source.mkdir()
    RunWorkspace.create(tmp_path / "runs", "demo", source, {})
    with pytest.raises(WorkspaceError, match="already exists"):
        RunWorkspace.create(tmp_path / "runs", "demo", source, {})
