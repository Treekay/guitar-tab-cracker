"""Creation of deterministic, inspectable run workspaces."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
ARTIFACT_DIRECTORIES = ("inputs", "crops", "normalized", "matches", "outputs")


class WorkspaceError(ValueError):
    pass


@dataclass(frozen=True)
class RunWorkspace:
    root: Path

    @classmethod
    def create(cls, workspace_root: Path, run_id: str, source: Path, config: dict[str, Any]) -> "RunWorkspace":
        if not RUN_ID_PATTERN.fullmatch(run_id):
            raise WorkspaceError("run ID must start with an alphanumeric character and contain only letters, digits, '.', '_' or '-'")
        root = workspace_root.resolve() / run_id
        if root.exists():
            raise WorkspaceError(f"run already exists: {root}")
        root.mkdir(parents=True)
        for name in ARTIFACT_DIRECTORIES:
            (root / name).mkdir()
        manifest = {
            "schema_version": 1, "run_id": run_id, "status": "initialized",
            "source_directory": str(source.resolve()),
            "created_at": datetime.now(timezone.utc).isoformat(), "config": config,
            "inputs": [], "measure_candidates": [], "outputs": [], "uncertainties": [],
        }
        (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        (root / "summary.md").write_text(f"# Run {run_id}\n\nStatus: initialized\n\nNo image processing was performed during V1 Task 1.\n", encoding="utf-8")
        return cls(root)
