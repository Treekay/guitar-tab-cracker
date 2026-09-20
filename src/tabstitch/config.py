"""Typed configuration loading for the local V1 CLI."""

from dataclasses import asdict, dataclass
from pathlib import Path
import tomllib
from typing import Any, Mapping


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class WorkspaceConfig:
    root: Path = Path("runs")


@dataclass(frozen=True)
class LoggingConfig:
    level: str = "INFO"


@dataclass(frozen=True)
class AppConfig:
    workspace: WorkspaceConfig = WorkspaceConfig()
    logging: LoggingConfig = LoggingConfig()

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["workspace"]["root"] = str(self.workspace.root)
        return data


def load_config(path: Path | None = None) -> AppConfig:
    raw: Mapping[str, Any] = {}
    if path is not None:
        try:
            with path.open("rb") as stream:
                raw = tomllib.load(stream)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ConfigError(f"Cannot load config {path}: {exc}") from exc
    unknown = set(raw) - {"workspace", "logging"}
    if unknown:
        raise ConfigError(f"Unknown config section(s): {', '.join(sorted(unknown))}")
    workspace = _section(raw, "workspace", {"root"})
    logging = _section(raw, "logging", {"level"})
    root, level = workspace.get("root", "runs"), logging.get("level", "INFO")
    if not isinstance(root, str) or not root.strip():
        raise ConfigError("workspace.root must be a non-empty string")
    levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if not isinstance(level, str) or level.upper() not in levels:
        raise ConfigError(f"logging.level must be one of: {', '.join(sorted(levels))}")
    return AppConfig(WorkspaceConfig(Path(root)), LoggingConfig(level.upper()))


def _section(raw: Mapping[str, Any], name: str, allowed: set[str]) -> Mapping[str, Any]:
    value = raw.get(name, {})
    if not isinstance(value, dict):
        raise ConfigError(f"{name} must be a TOML table")
    unknown = set(value) - allowed
    if unknown:
        raise ConfigError(f"Unknown {name} setting(s): {', '.join(sorted(unknown))}")
    return value
