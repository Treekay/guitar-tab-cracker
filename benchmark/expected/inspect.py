"""Create view-only crops of one benchmark image at a time."""
import argparse
from pathlib import Path
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument("image")
p.add_argument("--top", type=int, default=0)
p.add_argument("--bottom", type=int)
p.add_argument("--parts", type=int, default=2)
p.add_argument("--scale", type=int, default=2)
a = p.parse_args()
src = Path(a.image).resolve()
im = Image.open(src)
out = Path(__file__).resolve().parent / src.stem / "inspection"
out.mkdir(parents=True, exist_ok=True)
print(f"{src.name}: {im.size}")
for i in range(a.parts):
    left = max(0, i * im.width // a.parts - 15)
    right = min(im.width, (i + 1) * im.width // a.parts + 15)
    crop = im.crop((left, a.top, right, a.bottom or im.height))
    dest = out / f"part-{i+1}.png"
    crop.resize((crop.width*a.scale, crop.height*a.scale), Image.Resampling.NEAREST).save(dest)
    print(dest)
