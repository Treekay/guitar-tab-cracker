"""Execute an agent-authored crop/placement plan. No visual decisions are inferred.

Usage: python tools/compose.py benchmark/decisions.json benchmark/result
Requires Pillow and ReportLab in the tool environment, not an application install.
"""

import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def font(size):
    for name in ("C:/Windows/Fonts/arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def crop(source, box):
    left, top, right, bottom = box
    if not (0 <= left < right <= source.width and 0 <= top < bottom <= source.height):
        raise ValueError(f"Agent-selected crop is out of bounds: {box}")
    return source.crop(box).convert("RGB")


def execute(plan_path, destination):
    plan_path = Path(plan_path).resolve()
    destination = Path(destination).resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    source_root = plan_path.parent / "input"
    destination.mkdir(parents=True, exist_ok=True)
    measures_dir = destination / "measures"
    inspection_dir = destination / "inspection"
    measures_dir.mkdir(exist_ok=True)
    inspection_dir.mkdir(exist_ok=True)
    candidates_dir = inspection_dir / "candidates"
    candidates_dir.mkdir(exist_ok=True)
    source_hashes = {}
    # Inventory order and all boxes below are explicit decisions from the plan.
    for source in plan["inventory"]:
        path = source_root / source["file"]
        source_hashes[source["file"]] = hashlib.sha256(path.read_bytes()).hexdigest()
        with Image.open(path) as image:
            if list(image.size) != source["size"]:
                raise ValueError(f"Source changed dimensions: {path}")
            for candidate in source["candidates"]:
                with crop(image, candidate["box"]) as part:
                    part.save(candidates_dir / f"{path.stem}_m{candidate['measure']:02d}_{candidate['boundary']}.png")
    tiles = {}
    body_height = plan["tile_height"]
    staff_anchor = plan["staff_anchor"]
    for measure in plan["selected"]:
        tile = Image.new("RGB", (measure["width"], body_height), "#101313")
        for piece in measure["pieces"]:
            with Image.open(source_root / piece["file"]) as image, crop(image, piece["box"]) as part:
                x = piece["x"]
                y = staff_anchor - piece["source_staff_y"] + piece["box"][1]
                if x < 0 or y < 0 or x + part.width > tile.width or y + part.height > tile.height:
                    raise ValueError(f"Placement clips measure {measure['measure']}")
                tile.paste(part, (x, y))
        tile.save(measures_dir / f"m{measure['measure']:02d}.png")
        labelled = Image.new("RGB", (tile.width, body_height + 28), "white")
        ImageDraw.Draw(labelled).text((5, 4), f"{measure['measure']:02d}", fill="#38485a", font=font(16))
        labelled.paste(tile, (0, 28))
        tile.close()
        tiles[measure["measure"]] = labelled
    # Concatenation executes the exact declared order; no matching/reordering.
    sequence = plan["order"]
    if set(sequence) != set(tiles) or len(sequence) != len(set(sequence)):
        raise ValueError("Explicit order must reference each selected measure once")
    strip = Image.new("RGB", (sum(tiles[number].width for number in sequence), body_height + 28), "white")
    x = 0
    for number in sequence:
        strip.paste(tiles[number], (x, 0))
        x += tiles[number].width
    strip.save(destination / "full_score.png", dpi=(plan["dpi"], plan["dpi"]))
    strip.close()
    page_size = tuple(plan["page_size_pixels"])
    layout_order = [number for page in plan["pages"] for row in page["rows"] for number in row["measures"]]
    if layout_order != sequence:
        raise ValueError("Agent-selected page layout does not match explicit score order")
    pdf = canvas.Canvas(str(destination / "full_score.pdf"), pagesize=tuple(plan["page_size_points"]), pageCompression=1)
    pdf.setTitle(plan["title"])
    pdf.setAuthor("Codex visual reconstruction")
    for page_number, page_plan in enumerate(plan["pages"], start=1):
        page = Image.new("RGB", page_size, "white")
        draw = ImageDraw.Draw(page)
        draw.text((140, 90), plan["title"], fill="#182e43", font=font(46))
        draw.text((140, 152), page_plan["subtitle"], fill="#576777", font=font(25))
        draw.line((140, 205, page_size[0] - 140, 205), fill="#ccd4db", width=2)
        for row_index, row in enumerate(page_plan["rows"], start=1):
            cap = row.get("endcap")
            cap_width = cap["box"][2] - cap["box"][0] if cap else 0
            row_image = Image.new("RGB", (sum(tiles[number].width for number in row["measures"]) + cap_width, body_height + 28), "white")
            x = 0
            for number in row["measures"]:
                row_image.paste(tiles[number], (x, 0))
                x += tiles[number].width
            if cap:
                ImageDraw.Draw(row_image).rectangle((x, 28, row_image.width - 1, row_image.height - 1), fill="#101313")
                with Image.open(source_root / cap["file"]) as source, crop(source, cap["box"]) as part:
                    # Copy a visually selected existing boundary at a row ending.
                    # It is not a newly invented barline or an extra measure.
                    row_image.paste(part, (x, 28 + staff_anchor - cap["source_staff_y"] + cap["box"][1]))
            trim = row.get("trim_body_top", 0)
            if trim:
                if not 0 <= trim < body_height:
                    raise ValueError("Invalid explicit row trim")
                compact = Image.new("RGB", (row_image.width, row_image.height - trim), "white")
                compact.paste(row_image.crop((0, 0, row_image.width, 28)), (0, 0))
                compact.paste(row_image.crop((0, 28 + trim, row_image.width, row_image.height)), (0, 28))
                row_image.close()
                row_image = compact
            row_image.save(inspection_dir / f"page{page_number}_row{row_index}.png")
            scaled = row_image.resize((round(row_image.width * row["scale"]), round(row_image.height * row["scale"])), Image.Resampling.LANCZOS)
            px, py = row["position"]
            if px < 0 or py < 0 or px + scaled.width > page.width or py + scaled.height > page.height:
                raise ValueError("Explicit row placement exceeds the page; agent must choose new placement")
            page.paste(scaled, (px, py))
            scaled.close()
            row_image.close()
        draw.text((140, page.height - 160), plan["footer"], fill="#576777", font=font(24))
        draw.text((140, page.height - 115), f"A4 / 300 dpi     Page {page_number} of {len(plan['pages'])}", fill="#576777", font=font(24))
        page_path = destination / f"page_{page_number:03d}.png"
        page.save(page_path, dpi=(plan["dpi"], plan["dpi"]))
        pdf.drawImage(ImageReader(page), 0, 0, width=plan["page_size_points"][0], height=plan["page_size_points"][1])
        pdf.showPage()
        page.close()
    pdf.save()
    for tile in tiles.values():
        tile.close()
    # Mechanical audit only; this does not claim visual correctness.
    audit = {"source_sha256": source_hashes, "selected_measure_count": len(sequence), "pages": len(plan["pages"]), "order": sequence}
    (destination / "execution-checks.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(destination), "measures": len(sequence), "pages": len(plan["pages"])}))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python tools/compose.py decisions.json result-directory")
    execute(sys.argv[1], sys.argv[2])
