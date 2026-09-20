from PIL import Image
import pytest

from tabstitch.config import ConfigError, RoiConfig
from tabstitch.images.roi import PixelBBox, crop_pixels, pixel_bbox


@pytest.mark.parametrize("size", [(1200, 800), (80, 120), (1, 1)])
def test_disabled_and_full_image_roi(size: tuple[int, int]) -> None:
    for roi in (RoiConfig(), RoiConfig(True), RoiConfig(False, .1, .2, .3, .4)):
        assert pixel_bbox(*size, roi).as_tuple() == (0, 0, *size)


def test_partial_roi_example() -> None:
    assert pixel_bbox(1200, 800, RoiConfig(True, .1, .7, .8, .25)).as_tuple() == (120, 560, 1080, 760)


def test_rounding_preserves_edges_without_float_overflow() -> None:
    assert pixel_bbox(11, 7, RoiConfig(True, .1, .2, .2, .3)).as_tuple() == (1, 1, 4, 4)
    assert pixel_bbox(100, 100, RoiConfig(True, .1, .1, .2, .2)).as_tuple() == (10, 10, 30, 30)
    assert pixel_bbox(101, 99, RoiConfig(True, .9, .7, .1, .3)).as_tuple() == (90, 69, 101, 99)
    assert pixel_bbox(100, 100, RoiConfig(True, .5, .5, 1e-40, 1e-40)).as_tuple() == (50, 50, 51, 51)


@pytest.mark.parametrize("overrides", [
    {"x": -.1}, {"y": -.1}, {"width": 0}, {"height": 0},
    {"x": .2, "width": .9}, {"y": .2, "height": .9},
    {"width": -1}, {"height": -1}, {"x": float("nan")},
    {"height": float("inf")}, {"width": True}, {"x": "0.1"}, {"enabled": "yes"},
    {"x": 1, "width": 1e-40},
])
def test_invalid_roi_is_never_clamped_even_when_disabled(overrides: dict) -> None:
    with pytest.raises(ConfigError, match="roi"):
        RoiConfig(**overrides)


def test_bounds_for_small_portrait_and_landscape_images() -> None:
    for width, height in [(1, 1), (2, 3), (3, 2), (101, 99), (1200, 800)]:
        for x in (0, .1, .3, .9):
            bbox = pixel_bbox(width, height, RoiConfig(True, x, .1, .1, .9))
            assert 0 <= bbox.left < bbox.right <= width
            assert 0 <= bbox.top < bbox.bottom <= height


def test_actual_crop_pixels_and_alpha() -> None:
    with Image.new("RGBA", (10, 10), (1, 2, 3, 128)) as source:
        source.putpixel((2, 3), (255, 0, 0, 255))
        bbox = pixel_bbox(10, 10, RoiConfig(True, .2, .3, .3, .4))
        with crop_pixels(source, bbox) as crop:
            assert crop.size == (3, 4)
            assert crop.getpixel((0, 0)) == (255, 0, 0, 255)
            assert crop.getpixel((1, 1)) == (1, 2, 3, 128)


def test_out_of_bounds_crop_rejected() -> None:
    with Image.new("RGB", (10, 10)) as image:
        with pytest.raises(ValueError, match="within the image"):
            crop_pixels(image, PixelBBox(-1, 0, 10, 10))


def test_zero_image_dimension_rejected() -> None:
    with pytest.raises(ValueError, match="positive"):
        pixel_bbox(0, 10, RoiConfig())


def test_effective_roi_is_explicit() -> None:
    roi = RoiConfig(False, .1, .1, .2, .2)
    assert roi.normalized() == {"x": 0., "y": 0., "width": 1., "height": 1.}
