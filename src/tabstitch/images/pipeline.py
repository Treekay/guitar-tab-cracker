"""Coordinate Task 2 artifacts and reports without any measure detection."""

from dataclasses import asdict
import json
from pathlib import Path
import shutil
from typing import Any

from PIL import Image

from tabstitch.config import AppConfig
from tabstitch.images.ingest import SourceImage, ingest_images
from tabstitch.images.preview import PreviewItem, write_contact_sheet
from tabstitch.images.roi import crop_pixels, pixel_bbox
from tabstitch.workspace import RunWorkspace


def _entry(image: SourceImage, config: AppConfig) -> dict[str, Any]:
    return {
        "index": image.source_index,
        "source_path": str(image.source_path),
        "source_filename": image.filename,
        "width": image.width,
        "height": image.height,
        "format": image.format,
        "mode": image.mode,
        "roi": {
            "normalized": config.roi.normalized(),
            "pixel_bbox": asdict(pixel_bbox(image.width, image.height, config.roi)),
        },
    }


def inspect_directory(source: Path, config: AppConfig, preview: Path | None = None) -> dict[str, Any]:
    """Validate all inputs and optionally save a contact sheet, without creating a run."""
    images = ingest_images(source, config.image)
    if preview is not None:
        write_contact_sheet([
            PreviewItem(image.source_path, f"{image.source_index:04d}  {image.filename}", pixel_bbox(image.width, image.height, config.roi))
            for image in images
        ], preview)
    return {
        "input_directory": str(source.resolve()),
        "image_count": len(images),
        "images": [_entry(image, config) for image in images],
        "roi": {"enabled": config.roi.enabled, "normalized": config.roi.normalized()},
        "preview": str(preview.resolve()) if preview is not None else None,
    }


def build_run(source: Path, run_id: str, config: AppConfig) -> RunWorkspace:
    """Validate first, copy original bytes, save PNG ROIs and report an explicit run state."""
    images = ingest_images(source, config.image)
    workspace = RunWorkspace.create(config.workspace.root, run_id, source, config.as_dict())
    manifest_path = workspace.root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["status"] = "ingesting"
    manifest["roi"] = {"enabled": config.roi.enabled, "normalized": config.roi.normalized()}
    preview_items = []
    try:
        for image in images:
            # Numeric names avoid collisions and excessive source filename lengths.
            artifact = f"inputs/{image.source_index:04d}_original{image.source_path.suffix.lower()}"
            roi_artifact = f"normalized/{image.source_index:04d}_roi.png"
            shutil.copyfile(image.source_path, workspace.root / artifact)
            bbox = pixel_bbox(image.width, image.height, config.roi)
            with Image.open(workspace.root / artifact) as original, crop_pixels(original, bbox) as crop:
                crop.save(workspace.root / roi_artifact, format="PNG")
            entry = _entry(image, config)
            entry["artifact_path"] = artifact
            entry["roi"]["artifact_path"] = roi_artifact
            manifest["inputs"].append(entry)
            preview_items.append(PreviewItem(
                workspace.root / artifact, f"{image.source_index:04d}  {image.filename}", bbox,
            ))
        preview_artifact = "outputs/preview_contact_sheet.png"
        write_contact_sheet(preview_items, workspace.root / preview_artifact)
        manifest["outputs"] = [preview_artifact]
        manifest["status"] = "images_ready"
        _write_summary(workspace, manifest)
    except (OSError, ValueError, SyntaxError) as exc:
        manifest["status"] = "failed"
        manifest["error"] = str(exc)
        _write_summary(workspace, manifest)
        raise
    finally:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return workspace


def _write_summary(workspace: RunWorkspace, manifest: dict[str, Any]) -> None:
    lines = [
        f"# Run {manifest['run_id']}", "",
        f"Status: {manifest['status']}",
        f"Image count (artifacts completed): {len(manifest['inputs'])}",
        f"Source directory: {manifest['source_directory']}",
        f"ROI: {'enabled' if manifest['roi']['enabled'] else 'disabled (full image)'}",
        f"Effective normalized ROI: {json.dumps(manifest['roi']['normalized'])}", "",
        "No measure detection has been performed. Filename order is only input order.", "",
    ]
    for entry in manifest["inputs"]:
        lines.append(
            f"- {entry['index']:04d} {entry['source_filename']}: {entry['width']} x {entry['height']}; "
            f"source: {entry['artifact_path']}; ROI: {entry['roi']['artifact_path']}"
        )
    lines.extend(["", f"Preview: {', '.join(manifest['outputs']) or 'not generated'}"])
    if "error" in manifest:
        lines.extend(["", f"Error: {manifest['error']}"])
    (workspace.root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
