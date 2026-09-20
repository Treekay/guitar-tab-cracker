"""Merge explicit per-measure JSON and header; validate without changing music."""
import argparse
import json
from pathlib import Path
from validate_score import validate, SCHEMA


def assemble(header, directory):
    score = dict(header)
    if 'measures' in score:
        raise ValueError('Header must not contain measures')
    files = sorted(directory.glob('*.json'))
    if not files or [p.name for p in files] != [f'{n:03}.json' for n in range(1,len(files)+1)]:
        raise ValueError('Per-measure files must be exactly 001.json ... NNN.json')
    score['measures'] = [json.loads(p.read_text(encoding='utf-8')) for p in files]
    if any(m['audit']['pass2']!='inspected' for m in score['measures']):
        raise ValueError('Second visual pass is not recorded for every measure')
    return score


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path,help='V3 output directory containing header.json and measures/')
    p.add_argument('--manifest',required=True,type=Path)
    p.add_argument('--selected-indices',type=int,nargs='+')
    a=p.parse_args(); root=a.directory.resolve()
    score=assemble(json.loads((root/'header.json').read_text(encoding='utf-8')),root/'measures')
    result=validate(score,root,json.loads(a.manifest.read_text(encoding='utf-8')),a.selected_indices)
    (root/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    if not result['valid']:
        raise ValueError(result['errors'])
    (root/'score.json').write_text(json.dumps(score,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (root/'schema').mkdir(exist_ok=True)
    (root/'schema/score.schema.json').write_bytes(SCHEMA.read_bytes())
    print(f"Assembled {len(score['measures'])} measures; {len(result['warnings'])} review warnings")


if __name__=='__main__': main()
