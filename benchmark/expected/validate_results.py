"""Validate this benchmark's finalized files and print counts; no recognition."""
import json
from fractions import Fraction
from pathlib import Path

root = Path(__file__).resolve().parent
inputs = sorted(p for p in (root.parent / 'benchmark-input').iterdir()
                if p.is_file() and p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'})
assert len({p.stem for p in inputs}) == len(inputs), 'Duplicate input stems'
rows = []
for image in inputs:
    directory = root / image.stem
    score = json.loads((directory / 'score.json').read_text(encoding='utf-8'))
    assert (directory / 'review.md').is_file()
    assert score['schema_version'] == 1
    assert (directory / score['source']['image']).resolve() == image.resolve()
    assert score['source']['string_numbering'] == '1=top/highest, 6=bottom/lowest'
    events = []
    for measure in score['measures']:
        assert measure['boundary'] in {'complete', 'partial_left', 'partial_right', 'partial_both'}
        assert measure['confidence'] in {'high', 'medium', 'low'}
        assert measure['printed_number'] is None or isinstance(measure['printed_number'], int)
        assert [e['index'] for e in measure['events']] == list(range(1, len(measure['events']) + 1))
        for event in measure['events']:
            assert event['duration'] in {None, 1, 2, 4, 8, 16, 32, 64}
            assert event['confidence'] in {'high', 'medium', 'low'}
            assert isinstance(event['rest'], bool)
            assert isinstance(event['dots'], int) and event['dots'] >= 0
            notes = event['notes']
            dead = event.get('unpitched_notes', [])
            strings = [n['string'] for n in notes + dead]
            assert all(1 <= s <= 6 for s in strings)
            assert len(strings) == len(set(strings)), 'Duplicate string in event'
            assert not event['rest'] or not (notes or dead)
            for note in notes:
                assert type(note['fret']) is int and note['fret'] >= 0
                assert isinstance(note['parenthesized'], bool)
                assert isinstance(note['techniques'], list)
                assert note['confidence'] in {'high', 'medium', 'low'}
            for note in dead:
                assert note['symbol'] == 'X' and 'dead-note' in note['techniques']
            if event['confidence'] != 'high' or event['duration'] is None:
                assert event['uncertainty']
                assert any(u['measure'] == measure['printed_number'] and
                           (u['event_index'] == event['index'] or
                            event['index'] in u.get('event_indexes', []))
                           for u in score['unresolved']), 'Untracked uncertainty'
        ts = score['source'].get('time_signature')
        if ts and measure['boundary'] == 'complete':
            timed = [e for e in measure['events'] if not e.get('grace')]
            if all(e['duration'] is not None and e['tuplet'] is None for e in timed):
                length = sum((Fraction(1, e['duration']) *
                              sum((Fraction(1, 2**i) for i in range(e['dots']+1)), Fraction())
                              for e in timed), Fraction())
                assert length == Fraction(ts['numerator'], ts['denominator']), (image.name, measure['printed_number'], str(length))
        events.extend(measure['events'])
    rows.append({
        'image': image.name,
        'measures_detected': len(score['measures']),
        'complete_measures': sum(m['boundary'] == 'complete' for m in score['measures']),
        'partial_measures': sum(m['boundary'] != 'complete' for m in score['measures']),
        'events': len(events),
        'notes': sum(len(e['notes']) + len(e.get('unpitched_notes', [])) for e in events),
        'rests': sum(e['rest'] for e in events),
        'high_confidence_events': sum(e['confidence'] == 'high' for e in events),
        'medium_confidence_events': sum(e['confidence'] == 'medium' for e in events),
        'low_confidence_events': sum(e['confidence'] == 'low' for e in events),
        'unresolved_count': len(score['unresolved']),
    })
summary = {'images': rows, 'totals': {'images': len(rows), **{
    key: sum(r[key] for r in rows)
    for key in ['complete_measures', 'events', 'notes', 'unresolved_count']}}}
print(json.dumps(summary, indent=2))
