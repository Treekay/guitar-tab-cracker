"""Compare explicit independent field observations, never infer from pixels."""
import copy
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def get(document, pointer):
    value = document
    for part in pointer.strip('/').split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def set_field(document, pointer, value):
    parts = pointer.rsplit('/', 1)
    parent = get(document, parts[0])
    leaf = parts[1].replace('~1', '/').replace('~0', '~')
    if isinstance(parent, list):
        parent[int(leaf)] = copy.deepcopy(value)
    else:
        if leaf not in parent:
            raise ValueError('Correction cannot introduce an unknown field')
        parent[leaf] = copy.deepcopy(value)


def compare_observation(score, observation, base):
    current = get(score, observation['path'])
    evidence = observation.get('evidence', [])
    bound = bool(evidence) and all(
        (Path(base) / e['path']).is_file() and sha(Path(base) / e['path']) == e['sha256']
        for e in evidence)
    independently_read = observation.get('method') == 'independent_source_reread'
    clear = observation.get('clear') is True
    equal = json.dumps(current,sort_keys=True) == json.dumps(observation['observed_value'],sort_keys=True)
    verified = bound and independently_read and clear and equal
    return dict(observation, canonical_value=current, evidence_current=bound,
                matches=equal, status='VERIFIED' if verified else 'USER_REVIEW_REQUIRED',
                correctable_automatically=bound and independently_read and clear and not equal,
                discrepancy=not equal)


def propose_patch(score, observation, base):
    result = compare_observation(score, observation, base)
    if not result['correctable_automatically']:
        raise ValueError('A clear, independently reread and hash-bound source discrepancy is required')
    pointer = observation['path']
    # Corrections are musical fields, not wholesale root/measure/event replacements.
    parts = pointer.strip('/').split('/')
    if len(parts) < 3 or (parts[0] == 'measures' and len(parts) < 4):
        raise ValueError('Whole-container replacement is forbidden')
    if isinstance(result['canonical_value'], dict) or isinstance(observation['observed_value'], dict):
        raise ValueError('Patch leaf fields, not structured objects')
    for value in [result['canonical_value'],observation['observed_value']]:
        if isinstance(value,list) and any(isinstance(item,(dict,list)) for item in value):
            raise ValueError('Patch individual fields, not lists of structured records')
    draft = copy.deepcopy(score)
    set_field(draft, pointer, observation['observed_value'])
    return draft, {'path':pointer, 'before':result['canonical_value'],
                   'after':observation['observed_value'], 'evidence':observation['evidence'],
                   'status':'USER_REVIEW_REQUIRED', 'correction_state':'PROPOSED_NOT_REVALIDATED'}
