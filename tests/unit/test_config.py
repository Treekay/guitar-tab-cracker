from pathlib import Path
import pytest
from tabstitch.config import ConfigError, load_config


def test_defaults() -> None:
    config = load_config()
    assert config.workspace.root == Path("runs")
    assert config.logging.level == "INFO"


def test_toml_overrides_defaults(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text('[workspace]\nroot = "artifacts"\n[logging]\nlevel = "debug"\n')
    config = load_config(path)
    assert config.workspace.root == Path("artifacts")
    assert config.logging.level == "DEBUG"


def test_unknown_setting_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"; path.write_text("[workspace]\nsecret = true\n")
    with pytest.raises(ConfigError, match="Unknown workspace setting"):
        load_config(path)
