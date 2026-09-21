# Verification layer

Python uses the existing `jsonschema` validator. Node dependencies are the pinned
root package dependencies (`npm ci`). No OCR or automatic image interpretation.

```sh
python -m unittest discover -s tools/verification -p test_verification.py
python tools/verification/verify_score.py runs/v2-una-mattina/result/v3/score.json runs/v2-una-mattina/result/v3/verification/observations.json --output runs/v2-una-mattina/result/v3/verification
node tools/verification/benchmark.mjs GENERATED_GP MANUAL_GP ALIGNMENT_JSON OUTPUT_JSON
```

`verify_score.py` revalidates canonical, checks exact assembly, re-imports the
current GP without rewriting it, compares independent observations and builds
the user report. It requires header/per-measure files and the V2 manifest beside
the accepted canonical directory. Sample dossiers supply `selected_indices`.
Unresolved musical interpretation produces `USER_REVIEW_REQUIRED` in JSON while
allowing report creation; a mechanical failure also gives a nonzero exit code.
Failed independent field observations automatically become localized review
items. Their cause remains pending localization until the source-to-output trace
is adjudicated; the tool does not invent an earliest fault stage.

A dossier contains `canonical_sha256`, `gp_sha256`, `artifacts` (relative path and
SHA-256), `observations`, and `issues`. A field observation has:

```json
{
  "observation_id": "ending-check",
  "path": "/measures/0/barline/ending_numbers",
  "observed_value": [],
  "feature": "alternate_ending",
  "method": "independent_source_reread",
  "clear": true,
  "evidence": [{"path": "../measures/001.png", "sha256": "ACTUAL_HASH"}],
  "notes": "Repeat visible; no ending bracket in the complete source context."
}
```

This is a format example, not a finding about Una Mattina. A human/visual agent
must actually read the source before writing the observation. A hash binds bytes,
not truth or independence. Supplied issue judgments remain authored evidence;
the tool cannot infer their correctness from source pixels. Never fabricate a
review receipt from an existing canonical value.

`compare_transcriptions.py` compares leaf values and proposes source-supported
patches on an in-memory copy. A proposal is not `AUTO_CORRECTED`. The correction
transaction, including reassembly, validation, export and affected visual review,
is specified in [the pipeline](../../docs/VERIFICATION_PIPELINE.md).

`inspect_gp.mjs` uses the existing independent canonical projection and normal
ScoreLoader. `benchmark.mjs` compares explicit aligned written measures; its
alignment input supplies both file hashes, `independently_confirmed: true`,
zero-based `generated_track`/`manual_track`, and `measures` entries with one-based
`generated`/`manual` indices. Review identity/anchors before confirming alignment.
For differing event segmentation, exact metrics may be unsuitable; mismatches
must be adjudicated, not treated as automatically wrong source data.

Risk inventory is canonical-derived and only schedules candidates. An independent
source feature sweep must still look for omitted marks. The read-only report
rejects stale bound evidence and does not modify accepted files. Artifacts and
manual reference copies stay under ignored `runs/`; reusable logic and acceptance
analysis are committed. No manual score values or song indices are in the logic.
