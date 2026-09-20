"""Export an agent-authored selection/context/placement plan; infer nothing.

Usage: python tools/export_visual_score.py decisions.json result-directory
Frame paths are relative to result-directory. Requires Pillow and ReportLab.
Optional plan fields: title, artist, font (path relative to the plan),
show_header (default true), debug (default false). Unknown metadata is omitted.
Without font, Pillow's bundled default font is used; supply a font for scripts
outside its glyph coverage. No font files are bundled by this project.
Source RGB crops are retained in source_measures/. Explicit normalization may
be specified song-wide or overridden per selection; absent a decision, preserve
source pixels. Legacy tone plans remain supported as unreviewed partial output.
"""
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from normalize_measures import normalize_selected_crop


def presentation(plan, plan_path):
    values = []
    for key in ("title", "artist"):
        value = plan.get(key)
        if value is not None:
            if not isinstance(value, str):
                raise ValueError(f"{key} must be text or null")
            if value.strip():
                values.append(value.strip())
    font_path = plan.get("font")
    if font_path:
        path = Path(font_path)
        if not path.is_absolute():
            path = Path(plan_path).resolve().parent / path
        fonts = [ImageFont.truetype(str(path), size) for size in (38, 25)]
    else:
        fonts = [ImageFont.load_default(size=size) for size in (38, 25)]
    return " / ".join(values), fonts


def execute(plan_path, root):
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    heading, (font, small) = presentation(plan, plan_path)
    root = Path(root)
    (root / "measures").mkdir(exist_ok=True)
    (root / "source_measures").mkdir(exist_ok=True)
    (root / "inspection").mkdir(exist_ok=True)
    records, cores, contextual = [], {}, {}
    for item in plan["selection"]:
        n = item["sequence_index"]
        left, top, right, bottom = item["box"]
        before, after = item.get("context_pixels", [0, 0])
        with Image.open(root / item["source_frame"]) as source:
            if not (0 <= left-before < right+after <= source.width and 0 <= top < bottom <= source.height):
                raise ValueError(f"Invalid explicit crop/context for {n}")
            tile = source.crop((left-before, top, right+after, bottom)).convert("RGB")
        source_output = f"source_measures/{n:03d}.png"
        tile.save(root / source_output)
        decision = item.get("normalization", plan.get("normalization"))
        if "normalization" not in item and "normalization" not in plan:
            if plan.get("tone", "none") == "max_rgb_to_gray":
                decision = {"status": "partial", "confidence": "unknown",
                            "source_faithful": None, "uncertainty": "Legacy tone; normalization review not recorded.",
                            "operations": [{"op": "grayscale", "mode": "max_rgb"}]}
            elif plan.get("tone", "none") != "none":
                raise ValueError("Unknown explicit tonal transform")
        tile, normalization = normalize_selected_crop(tile, decision, plan_path)
        output = f"measures/{n:03d}.png"
        tile.save(root / output)
        contextual[n] = tile
        cores[n] = tile.crop((before, 0, before+right-left, bottom-top))
        records.append({**item, "source_output": source_output, "output": output,
                        "normalization": normalization, "boundary_state": "complete",
                        "source_crop_box": [left-before, top, right+after, bottom],
                        "core_bbox_in_output": [before, 0, before+right-left, bottom-top],
                        "tonal_transform": "explicit_normalization" if "normalization" in item or "normalization" in plan else plan.get("tone", "none"),
                        "context_note": "Extra pixels preserve a crossing annotation; they are not another logical occurrence." if before or after else None})
    sequence = [item["sequence_index"] for item in records]
    if sequence != list(range(1, len(records)+1)):
        raise ValueError("Expected explicit contiguous sequence indices")
    if [n for page in plan["pages"] for row in page for n in row] != sequence:
        raise ValueError("Explicit page order differs from selected sequence")
    (root / "measures.json").write_text(json.dumps(records, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    strip = Image.new("RGB", (sum(cores[n].width for n in sequence), max(cores[n].height for n in sequence)), "white")
    x = 0
    for n in sequence:
        strip.paste(cores[n], (x, 0)); x += cores[n].width
    strip.save(root / "full_score.png")
    pdf = canvas.Canvas(str(root / "full_score.pdf"), pagesize=tuple(plan["page_points"]))
    pdf.setTitle(heading)
    row_index = 0
    for page_index, rows in enumerate(plan["pages"], 1):
        if len(rows) > len(plan["positions"]):
            raise ValueError("Missing explicit row positions")
        page = Image.new("RGB", tuple(plan["page_pixels"]), "white")
        draw = ImageDraw.Draw(page)
        if plan.get("show_header", True):
            if heading:
                draw.text((160, 70), heading, font=font, fill="#202020")
            label = f"{page_index} / {len(plan['pages'])}"
            if plan.get("debug", False):
                label = f"Source-faithful visual reconstruction | Measures {rows[0][0]}-{rows[-1][-1]} | {label}"
            draw.text((160, 124), label, font=small, fill="#555555")
        for row, position in zip(rows, plan["positions"]):
            row_index += 1
            end_context = plan.get("row_end_context", {}).get(str(row_index), {})
            extra = end_context.get("width", 0)
            width = sum(cores[n].width for n in row)
            row_image = Image.new("RGB", (width+extra, strip.height), "white")
            x = 0
            for n in row:
                row_image.paste(cores[n], (x, 0)); x += cores[n].width
            if extra:
                last = records[row[-1]-1]
                start = last["core_bbox_in_output"][2]
                band_height = end_context["height"]
                if start+extra > contextual[row[-1]].width or not 0 < band_height <= strip.height:
                    raise ValueError("Explicit annotation context is out of bounds")
                row_image.paste(contextual[row[-1]].crop((start, 0, start+extra, band_height)), (width, 0))
            row_image.save(root / "inspection" / f"final_row_{row_index:02d}.png")
            scaled = row_image.resize((round(row_image.width*plan["scale"]), round(row_image.height*plan["scale"])), Image.Resampling.LANCZOS)
            px, py = position
            if px < 0 or py < 0 or px+scaled.width > page.width or py+scaled.height > page.height:
                raise ValueError("Explicit row placement exceeds page")
            page.paste(scaled, (px, py))
        page.save(root / f"page_{page_index:03d}.png", dpi=(300, 300))
        pdf.drawImage(ImageReader(page), 0, 0, width=plan["page_points"][0], height=plan["page_points"][1])
        pdf.showPage()
    pdf.save()
    print(json.dumps({"measures": len(records), "pages": len(plan["pages"]), "full_score_size": strip.size}))


if __name__ == "__main__":
    execute(sys.argv[1], sys.argv[2])
