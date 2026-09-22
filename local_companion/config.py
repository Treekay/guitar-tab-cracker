import json
from pathlib import Path
import secrets

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'local-companion/.local'
HOST='127.0.0.1'
PORT=8787

def load():
    STATE.mkdir(parents=True,exist_ok=True)
    path=STATE/'config.json'
    if path.exists():
        data=json.loads(path.read_text(encoding='utf8'))
    else:
        data={'token':secrets.token_urlsafe(32),'extension_id':(ROOT/'browser-extension/extension-id.txt').read_text().strip()}
        with path.open('x',encoding='utf8') as f:json.dump(data,f)
    if len(data['token'])<32:raise ValueError('Installation token must have at least 32 characters')
    return data
