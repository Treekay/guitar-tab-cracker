"""Typed configuration loading for the local V1 CLI."""

from dataclasses import asdict, dataclass
from fractions import Fraction
import math
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


SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


@dataclass(frozen=True)
class ImageConfig:
    supported_extensions: tuple[str, ...] = SUPPORTED_EXTENSIONS

    def __post_init__(self) -> None:
        extensions = self.supported_extensions
        if (
            not isinstance(extensions, tuple)
            or not extensions
            or any(ext not in SUPPORTED_EXTENSIONS for ext in extensions)
            or len(set(extensions)) != len(extensions)
        ):
            raise ConfigError("image.supported_extensions must be a non-empty, unique list of supported extensions")


@dataclass(frozen=True)
class RoiConfig:
    """Normalized rectangle in stored source pixel coordinates, without EXIF rotation."""

    enabled: bool = False
    x: float = 0.0
    y: float = 0.0
    width: float = 1.0
    height: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise ConfigError("roi.enabled must be a boolean")
        for name in ("x", "y", "width", "height"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ConfigError(f"roi.{name} must be a finite number")
            if not 0 <= value <= 1 or (name in {"width", "height"} and value == 0):
                raise ConfigError(f"roi.{name} is outside its normalized range")
        if Fraction(str(self.x)) + Fraction(str(self.width)) > 1:
            raise ConfigError("roi.x + roi.width must be <= 1")
        if Fraction(str(self.y)) + Fraction(str(self.height)) > 1:
            raise ConfigError("roi.y + roi.height must be <= 1")

    def effective(self) -> "RoiConfig":
        """Return the full-image rectangle when ROI is disabled."""
        return self if self.enabled else RoiConfig()

    def normalized(self) -> dict[str, float]:
        effective = self.effective()
        return {name: float(getattr(effective, name)) for name in ("x", "y", "width", "height")}


@dataclass(frozen=True)
class AppConfig:
    workspace: WorkspaceConfig = WorkspaceConfig()
    logging: LoggingConfig = LoggingConfig()
    image: ImageConfig = ImageConfig()
    roi: RoiConfig = RoiConfig()

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["workspace"]["root"] = str(self.workspace.root)
        data["image"]["supported_extensions"] = list(self.image.supported_extensions)
        return data


def load_config(path: Path | None = None) -> AppConfig:
    raw: Mapping[str, Any] = {}
    if path is not None:
        try:
            with path.open("rb") as stream:
                raw = tomllib.load(stream)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ConfigError(f"Cannot load config {path}: {exc}") from exc
    unknown = set(raw) - {"workspace", "logging", "image", "roi"}
    if unknown:
        raise ConfigError(f"Unknown config section(s): {', '.join(sorted(unknown))}")
    workspace = _section(raw, "workspace", {"root"})
    logging = _section(raw, "logging", {"level"})
    image = _section(raw, "image", {"supported_extensions"})
    roi = _section(raw, "roi", {"enabled", "x", "y", "width", "height"})
    extensions = image.get("supported_extensions", list(SUPPORTED_EXTENSIONS))
    if not isinstance(extensions, list) or not all(isinstance(ext, str) for ext in extensions):
        raise ConfigError("image.supported_extensions must be a list of strings")
    root, level = workspace.get("root", "runs"), logging.get("level", "INFO")
    if not isinstance(root, str) or not root.strip():
        raise ConfigError("workspace.root must be a non-empty string")
    levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if not isinstance(level, str) or level.upper() not in levels:
        raise ConfigError(f"logging.level must be one of: {', '.join(sorted(levels))}")
    return AppConfig(
        workspace=WorkspaceConfig(Path(root)),
        logging=LoggingConfig(level.upper()),
        image=ImageConfig(tuple(extensions)),
        roi=RoiConfig(**roi),
    )


def _section(raw: Mapping[str, Any], name: str, allowed: set[str]) -> Mapping[str, Any]:
    value = raw.get(name, {})
    if not isinstance(value, dict):
        raise ConfigError(f"{name} must be a TOML table")
    unknown = set(value) - allowed
    if unknown:
        raise ConfigError(f"Unknown {name} setting(s): {', '.join(sorted(unknown))}")
    return value
