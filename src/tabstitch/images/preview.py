"""Contact sheets for manual ROI verification, separate from score layout."""

from dataclasses import dataclass
import math
from pathlib import Path
import textwrap
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

from tabstitch.images.roi import PixelBBox, crop_pixels


@dataclass(frozen=True)
class PreviewItem:
    path: Path
    label: str
    bbox: PixelBBox


def write_contact_sheet(items: Sequence[PreviewItem], destination: Path) -> None:
    """Create a labelled PNG with aspect-preserving ROI thumbnails; refuse overwrite."""
    if not items:
        raise ValueError("preview requires at least one image")
    if destination.suffix.lower() != ".png":
        raise ValueError("preview output must have a .png extension")
    labels = [textwrap.wrap(item.label, width=65) or [""] for item in items]
    label_height = max(len(lines) for lines in labels) * 18
    cell_width, cell_height = 640, 196 + label_height
    columns = min(2, len(items))
    font = ImageFont.load_default(size=14)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.new("RGB", (columns * cell_width, math.ceil(len(items) / columns) * cell_height), "#e8e8e8") as sheet:
        draw = ImageDraw.Draw(sheet)
        for index, (item, lines) in enumerate(zip(items, labels)):
            x, y = (index % columns) * cell_width, (index // columns) * cell_height
            draw.multiline_text((x + 12, y + 8), "\n".join(lines), fill="black", font=font, spacing=4)
            with Image.open(item.path) as source, crop_pixels(source, item.bbox) as crop:
                crop.thumbnail((616, 172), Image.Resampling.LANCZOS)
                position = (x + (cell_width - crop.width) // 2, y + label_height + 16 + (172 - crop.height) // 2)
                sheet.paste(crop, position, crop if crop.mode == "RGBA" else None)
        with destination.open("xb") as stream:
            sheet.save(stream, format="PNG")
