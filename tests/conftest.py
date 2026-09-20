"""Generated screenshots shared by unit and integration tests."""

from pathlib import Path

from PIL import Image
import pytest


@pytest.fixture
def image_directory(tmp_path: Path) -> Path:
    directory = tmp_path / "images"
    directory.mkdir()
    for filename, size, mode, color in [
        ("02.JPG", (60, 100), "RGB", "blue"),
        ("01.png", (120, 80), "RGBA", (255, 0, 0, 128)),
        ("10.webp", (90, 30), "RGB", "green"),
        ("03.jpeg", (16, 16), "RGB", "white"),
    ]:
        with Image.new(mode, size, color) as image:
            image.save(directory / filename)
    (directory / "notes.txt").write_text("not an image", encoding="utf-8")
    (directory / "subfolder.png").mkdir()
    return directory
