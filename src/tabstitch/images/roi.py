"""Deterministic normalized ROI conversion and lossless PNG crop preparation."""

from dataclasses import dataclass
from fractions import Fraction
from math import ceil, floor

from PIL import Image

from tabstitch.config import RoiConfig


@dataclass(frozen=True)
class PixelBBox:
    """Half-open pixel bounds: right and bottom are exclusive."""

    left: int
    top: int
    right: int
    bottom: int

    def as_tuple(self) -> tuple[int, int, int, int]:
        return self.left, self.top, self.right, self.bottom


def pixel_bbox(width: int, height: int, roi: RoiConfig) -> PixelBBox:
    """Floor starts and ceil ends using exact decimal fractions; never clamp invalid ROI."""
    if width <= 0 or height <= 0:
        raise ValueError("image dimensions must be positive")
    effective = roi.effective()
    x, y, w, h = (Fraction(str(getattr(effective, name))) for name in ("x", "y", "width", "height"))
    return PixelBBox(
        floor(x * width),
        floor(y * height),
        ceil((x + w) * width),
        ceil((y + h) * height),
    )


def crop_pixels(image: Image.Image, bbox: PixelBBox) -> Image.Image:
    """Crop stored pixels to RGB/RGBA; preserve alpha, without rotation or rescaling."""
    if not (0 <= bbox.left < bbox.right <= image.width and 0 <= bbox.top < bbox.bottom <= image.height):
        raise ValueError("ROI pixel bounds must be non-empty and within the image")
    mode = "RGBA" if "A" in image.getbands() or "transparency" in image.info else "RGB"
    with image.crop(bbox.as_tuple()) as cropped:
        result = cropped.convert(mode)
    # EXIF orientation must not rotate a crop whose coordinates refer to raw pixels.
    result.info.clear()
    return result
