"""Execute explicit visual normalization decisions; never choose a method.

Profiles belong in a run's plan, not in this helper. A prepared image allows
other agent-controlled tools/masks/multi-frame workflows without a fixed recipe.
No method, parameters or visual-fidelity claims are inferred from pixel data.
"""
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageOps


def normalize_selected_crop(source, decision, plan_path):
    decision = decision or {}
    status = decision.get("status", "source_preserved")
    if status not in ("normalized", "partial", "source_preserved"):
        raise ValueError("Unknown normalization status")
    confidence = decision.get("confidence", "unknown")
    if confidence not in ("high", "medium", "low", "unknown"):
        raise ValueError("Unknown normalization confidence")
    operations = decision.get("operations", [])
    prepared = decision.get("prepared_image")
    if prepared and operations:
        raise ValueError("Choose explicit operations or a prepared image, not both")
    if status == "source_preserved" and (operations or prepared):
        raise ValueError("source_preserved copies original pixels; use partial for minimal processing")
    if status == "normalized" and not (
        decision.get("visually_reviewed") is True and decision.get("source_faithful") is True
    ):
        raise ValueError("normalized requires an explicit source-vs-output visual review")
    tile = source.convert("RGB")
    if prepared:
        path = Path(prepared)
        if not path.is_absolute():
            path = Path(plan_path).resolve().parent / path
        with Image.open(path) as image:
            if image.size != tile.size:
                raise ValueError("Prepared image must preserve crop geometry and core coordinates")
            tile = image.convert("RGB")
    for operation in operations:
        name = operation["op"]
        if name == "grayscale":
            mode = operation["mode"]
            if mode == "luma":
                tile = tile.convert("L")
            elif mode in ("max_rgb", "min_rgb"):
                r, g, b = tile.convert("RGB").split()
                combine = ImageChops.lighter if mode == "max_rgb" else ImageChops.darker
                tile = combine(combine(r, g), b)
            else:
                raise ValueError("Unknown explicit grayscale mode")
        elif name == "invert":
            tile = ImageOps.invert(tile)
        elif name == "levels":
            black, white, gamma = (float(operation[key]) for key in ("black", "white", "gamma"))
            if not (0 <= black < white <= 255 and math.isfinite(gamma) and gamma > 0):
                raise ValueError("Invalid explicit levels")
            lut = [round(255 * max(0, min(1, (v-black)/(white-black)))**gamma) for v in range(256)]
            tile = tile.point(lut * len(tile.getbands()))
        elif name == "threshold":
            threshold = float(operation["value"])
            if tile.mode != "L" or not 0 <= threshold <= 255:
                raise ValueError("Threshold requires explicit grayscale and a value in 0..255")
            tile = tile.point([0 if v < threshold else 255 for v in range(256)])
        else:
            raise ValueError(f"Unknown normalization operation: {name}")
    record = {
        "status": status,
        "confidence": confidence,
        "source_faithful": decision.get("source_faithful"),
        "uncertainty": decision.get("uncertainty"),
        "visually_reviewed": decision.get("visually_reviewed", False),
        "operations": operations,
    }
    if status == "source_preserved":
        record.update(confidence="high", source_faithful=True,
                      uncertainty=decision.get("uncertainty", "Source retained; no safe normalization selected."))
    if prepared:
        record["prepared_image"] = str(prepared)
        record["method"] = decision.get("method", "Externally prepared, agent-selected transformation")
    return tile.convert("RGB"), record
