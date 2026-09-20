from pathlib import Path

from PIL import Image
import pytest

from tabstitch.images.preview import PreviewItem, write_contact_sheet
from tabstitch.images.roi import PixelBBox


def test_contact_sheet_displays_only_roi_pixels(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    with Image.new("RGB", (100, 50), "red") as image:
        image.paste("blue", (50, 0, 100, 50))
        image.save(source)
    preview = tmp_path / "preview.png"
    write_contact_sheet([PreviewItem(source, "0001 source.png", PixelBBox(50, 0, 100, 50))], preview)
    with Image.open(preview) as sheet:
        colors = sheet.getdata()
        assert (0, 0, 255) in colors
        assert (255, 0, 0) not in colors
        # Label pixels remain visible above the thumbnail.
        assert sheet.crop((0, 0, sheet.width, 30)).getextrema()[0][0] < 100


def test_preview_extension_is_explicit(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=".png extension"):
        write_contact_sheet([PreviewItem(tmp_path / "unused.png", "image", PixelBBox(0, 0, 1, 1))], tmp_path / "out.jpg")
