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


def test_image_and_roi_config(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text('[image]\nsupported_extensions = [".png", ".webp"]\n[roi]\nenabled = true\nx = 0.1\nwidth = 0.8\n')
    config = load_config(path)
    assert config.image.supported_extensions == (".png", ".webp")
    assert config.roi.enabled
    assert config.roi.normalized()["width"] == .8
    assert config.as_dict()["image"]["supported_extensions"] == [".png", ".webp"]


@pytest.mark.parametrize("content", [
    '[roi]\nx = -0.1', '[roi]\nenabled = "true"', '[roi]\nwidth = nan',
    '[roi]\nwidht = 0.5', '[image]\nsupported_extensions = ".png"',
    '[image]\nsupported_extensions = []', '[image]\nsupported_extensions = [".gif"]',
    '[image]\nsupported_extensions = [".png", ".png"]',
])
def test_invalid_image_config(tmp_path: Path, content: str) -> None:
    path = tmp_path / "config.toml"
    path.write_text(content)
    with pytest.raises(ConfigError):
        load_config(path)
