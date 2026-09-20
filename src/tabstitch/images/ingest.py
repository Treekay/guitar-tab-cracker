"""Discover and validate static screenshots, keeping only metadata between images."""

from dataclasses import dataclass
from pathlib import Path
import warnings

from PIL import Image

from tabstitch.config import ImageConfig


class ImageIngestError(ValueError):
    """A supported source cannot be safely ingested; it must not be skipped."""


@dataclass(frozen=True)
class SourceImage:
    source_path: Path
    filename: str
    width: int
    height: int
    format: str
    mode: str
    source_index: int


def discover_images(directory: Path, config: ImageConfig) -> list[Path]:
    """Non-recursive discovery; sort by case-sensitive Unicode filename, not music order."""
    directory = directory.resolve()
    if not directory.is_dir():
        raise ImageIngestError(f"input directory does not exist: {directory}")
    paths = sorted(
        (path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in config.supported_extensions),
        key=lambda path: path.name,
    )
    if not paths:
        raise ImageIngestError(f"no supported images in: {directory}")
    return paths


def read_metadata(path: Path, index: int) -> SourceImage:
    """Verify structure and fully decode one static PNG/JPEG/WebP, then close it."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as image:
                if image.format not in {"PNG", "JPEG", "WEBP"}:
                    raise ImageIngestError(f"unsupported decoded format {image.format}")
                if getattr(image, "n_frames", 1) != 1:
                    raise ImageIngestError("animated/multi-frame images are not supported")
                if image.width <= 0 or image.height <= 0:
                    raise ImageIngestError("invalid image dimensions")
                metadata = SourceImage(path.resolve(), path.name, image.width, image.height, image.format, image.mode, index)
                image.verify()
            # verify() alone may accept a truncated pixel stream; require a full decode.
            with Image.open(path) as image:
                image.load()
        return metadata
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ImageIngestError(f"cannot ingest image {path}: {exc}") from exc


def ingest_images(directory: Path, config: ImageConfig) -> list[SourceImage]:
    """Fail the entire operation on a broken supported image; retain no full pixel buffers."""
    return [read_metadata(path, index) for index, path in enumerate(discover_images(directory, config), start=1)]
