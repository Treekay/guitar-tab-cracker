from pathlib import Path

from PIL import Image
import pytest

from tabstitch.config import ImageConfig
from tabstitch.images.ingest import ImageIngestError, discover_images, ingest_images, read_metadata


def test_filter_and_filename_order(image_directory: Path) -> None:
    assert [path.name for path in discover_images(image_directory, ImageConfig())] == [
        "01.png", "02.JPG", "03.jpeg", "10.webp",
    ]
    assert [path.name for path in discover_images(image_directory, ImageConfig((".png",)))] == ["01.png"]


def test_metadata_and_dimensions(image_directory: Path) -> None:
    images = ingest_images(image_directory, ImageConfig())
    assert [(image.source_index, image.width, image.height, image.format, image.mode) for image in images] == [
        (1, 120, 80, "PNG", "RGBA"), (2, 60, 100, "JPEG", "RGB"),
        (3, 16, 16, "JPEG", "RGB"), (4, 90, 30, "WEBP", "RGB"),
    ]
    assert all(image.source_path.is_absolute() for image in images)


def test_empty_directory_fails(tmp_path: Path) -> None:
    with pytest.raises(ImageIngestError, match="no supported images"):
        ingest_images(tmp_path, ImageConfig())


def test_missing_directory_fails(tmp_path: Path) -> None:
    with pytest.raises(ImageIngestError, match="directory does not exist"):
        ingest_images(tmp_path / "missing", ImageConfig())


def test_corrupt_supported_image_fails_entire_ingest(image_directory: Path) -> None:
    (image_directory / "broken.png").write_bytes(b"not a PNG")
    with pytest.raises(ImageIngestError, match="broken.png"):
        ingest_images(image_directory, ImageConfig())


def test_truncated_jpeg_fails_full_decode(image_directory: Path) -> None:
    path = image_directory / "02.JPG"
    path.write_bytes(path.read_bytes()[:-20])
    with pytest.raises(ImageIngestError, match="02.JPG"):
        read_metadata(path, 1)


def test_disguised_unsupported_format_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "fake.png"
    with Image.new("RGB", (10, 10)) as image:
        image.save(path, format="BMP")
    with pytest.raises(ImageIngestError, match="unsupported decoded format BMP"):
        read_metadata(path, 1)


def test_animated_input_rejected_without_silently_dropping_frames(tmp_path: Path) -> None:
    path = tmp_path / "animated.png"
    with Image.new("RGB", (10, 10), "red") as first, Image.new("RGB", (10, 10), "blue") as second:
        first.save(path, save_all=True, append_images=[second], duration=100)
    with pytest.raises(ImageIngestError, match="multi-frame"):
        read_metadata(path, 1)


def test_decompression_bomb_is_a_clear_ingest_error(image_directory: Path, monkeypatch) -> None:
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 5000)
    with pytest.raises(ImageIngestError, match="01.png"):
        ingest_images(image_directory, ImageConfig())
