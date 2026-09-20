"""Acceptance-run visual decisions, authored from source screenshots only.

This is run evidence, not a detector or a reusable set of song answers.
The existing compositor executes the explicit boxes and placements below.
"""
import json
from pathlib import Path
import sys
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from compose import execute

STAFF = {1:155, 2:137, 3:149, 4:142, 5:135, 6:226, 7:139, 8:139, 9:137, 10:139}
VERTICAL = {1:(50,311), 2:(0,307), 3:(90,315), 4:(100,310), 5:(95,305), 6:(185,390), 7:(100,309), 8:(100,309), 9:(95,308), 10:(100,309)}
# Number, left edge, right edge, boundary state: all chosen by visual inspection.
VISIBLE = {
 1:[(1,0,489,'complete'),(2,489,993,'complete'),(3,993,1331,'complete'),(4,1331,1560,'partial_right')],
 2:[(3,0,310,'partial_left'),(4,310,799,'complete'),(5,799,1336,'complete'),(6,1336,1560,'partial_right')],
 3:[(5,0,266,'partial_left'),(6,266,489,'complete'),(7,489,1019,'complete'),(8,1019,1504,'complete'),(9,1504,1534,'partial_right')],
 4:[(8,0,476,'partial_left'),(9,476,906,'complete'),(10,906,1188,'complete'),(11,1188,1520,'complete'),(12,1520,1535,'partial_right')],
 5:[(10,0,178,'partial_left'),(11,178,508,'complete'),(12,508,671,'complete'),(13,671,1160,'complete'),(14,1160,1560,'partial_right')],
 6:[(13,0,107,'partial_left'),(14,107,617,'complete'),(15,617,1022,'complete'),(16,1022,1486,'complete'),(17,1486,1530,'partial_right')],
 7:[(16,17,482,'complete'),(17,482,971,'complete'),(18,971,1481,'complete'),(19,1481,1560,'partial_right')],
 8:[(18,0,448,'partial_left'),(19,448,853,'complete'),(20,853,1317,'complete'),(21,1317,1480,'complete'),(22,1480,1547,'partial_right')],
 9:[(20,0,287,'partial_left'),(21,287,450,'complete'),(22,450,853,'complete'),(23,853,1356,'complete'),(24,1356,1560,'partial_right')],
 10:[(23,0,327,'partial_left'),(24,327,666,'complete'),(25,666,1198,'complete'),(26,1198,1541,'complete')],
}
PICKS = [(1,1),(2,1),(3,1),(4,2),(5,2),(6,3),(7,3),(8,3),(9,4),(10,4),(11,5),(12,5),(13,5),(14,6),(15,6),(16,6),(17,7),(18,7),(19,8),(20,8),(21,8),(22,9),(23,9),(24,10),(25,10),(26,10)]

def filename(n):
    return str(ROOT / 'benchmark' / 'input' / f'{n}.png')

def piece(n, box, x=0):
    return dict(file=filename(n), box=box, x=x, source_staff_y=STAFF[n])

inventory = []
selected = []
for n, candidates in VISIBLE.items():
    top, bottom = VERTICAL[n]
    inventory.append(dict(file=filename(n), size=list(Image.open(filename(n)).size), candidates=[dict(measure=m, box=[l,top,r,bottom], boundary=b) for m,l,r,b in candidates]))
for m,n in PICKS:
    _,left,right,_ = next(c for c in VISIBLE[n] if c[0] == m)
    top,bottom = VERTICAL[n]
    if m in (2,3): top=120
    if m == 5: top=95
    selected.append(dict(measure=m,width=right-left,pieces=[piece(n,[left,top,right,bottom])]))

# Same-measure complementary source views. Translation was established visually
# from both barlines, staff bands and identical graphic shapes, without reading events.
# Replace cursor-bearing areas only with actual source pixels.
selected[2]['pieces'] = [piece(1,[993,120,1331,311]),piece(2,[0,102,247,293],28),piece(2,[263,102,310,293],291)]
selected[5]['pieces'] = [piece(3,[266,90,489,315]),piece(2,[1464,78,1478,303],128)]
selected[10]['pieces'] = [piece(5,[178,95,508,305]),piece(4,[1218,102,1258,312],30)]
selected[13]['pieces'] = [piece(6,[107,185,617,390]),piece(5,[1365,94,1383,299],205)]

GROUPS = [[[1,2,3],[4,5,6],[7,8],[9,10,11,12],[13,14]], [[15,16],[17,18],[19,20,21],[22,23],[24,25,26]]]
POSITIONS = [[270,900,1530,2070,2610],[350,900,1450,2000,2550]]
pages=[]
for pi,groups in enumerate(GROUPS):
    rows=[]
    for ri,group in enumerate(groups):
        row=dict(measures=group,scale=1.55,position=[140,POSITIONS[pi][ri]],trim_body_top=0 if pi==0 and ri<2 else 90)
        if group[-1] != 26:
            end_m=selected[group[-1]-1]
            n=dict(PICKS)[group[-1]]
            right=end_m['pieces'][0]['box'][2]
            row['endcap']=piece(n,[right,STAFF[n],right+15,VERTICAL[n][1]])
        rows.append(row)
    pages.append(dict(subtitle=f'Source-faithful visual reconstruction | Measures {groups[0][0]}-{groups[-1][-1]}',rows=rows))
plan=dict(inventory=inventory,selected=selected,order=list(range(1,27)),tile_height=330,staff_anchor=155,dpi=300,page_size_pixels=[2480,3508],page_size_points=[595.2755905511812,841.8897637795276],title='Reconstructed guitar score',footer='Original source appearance retained. Opening measure contains an unavoidable source overlay.',pages=pages)
plan_path=HERE/'decisions.json'
plan_path.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
execute(plan_path,HERE)
