"""Mechanical export checks and readable strip sections; no recognition."""
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageChops

HERE=Path(__file__).resolve().parent
plan=json.loads((HERE/'decisions.json').read_text())
audit=json.loads((HERE/'execution-checks.json').read_text())
for name,digest in audit['source_sha256'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest
widths={m['measure']:m['width'] for m in plan['selected']}
strip=Image.open(HERE/'full_score.png')
x=0
for i,row in enumerate([r for p in plan['pages'] for r in p['rows']],1):
    width=sum(widths[n] for n in row['measures'])
    strip.crop((x,0,x+width,strip.height)).save(HERE/'inspection'/f'full-section-{i:02d}.png')
    x+=width
assert x==strip.width
subprocess.run(['pdfimages','-png',str(HERE/'full_score.pdf'),str(HERE/'inspection'/'pdf-embedded')],check=True)
embedded=sorted((HERE/'inspection').glob('pdf-embedded-*.png'))
pages=sorted(HERE.glob('page_*.png'))
assert len(embedded)==len(pages)==2
for png,pdf in zip(pages,embedded):
    a,b=Image.open(png).convert('RGB'),Image.open(pdf).convert('RGB')
    assert a.size==b.size==(2480,3508)
    assert ImageChops.difference(a,b).getbbox() is None
info=subprocess.check_output(['pdfinfo','-isodates',str(HERE/'full_score.pdf')]).decode(errors='replace')
info='\n'.join(line.rstrip() for line in info.splitlines())+'\n'
(HERE/'inspection'/'pdfinfo.txt').write_text(info,encoding='utf-8',newline='\n')
assert '595.276 x 841.89 pts (A4)' in info
results=dict(source_files_unchanged=10,measure_tiles=len(list((HERE/'measures').glob('m*.png'))),full_score_pixels=list(strip.size),strip_section_count=10,strip_sections_cover_all_pixels=True,page_count=2,page_pixels=[2480,3508],pdf_size_points=plan['page_size_points'],pdf_embedded_images_equal_page_pngs=True,scale_values=sorted({r['scale'] for p in plan['pages'] for r in p['rows']}),visual_verdict='Recorded separately in report.md; mechanical checks do not establish visual correctness.')
(HERE/'inspection'/'verification.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,indent=2))
