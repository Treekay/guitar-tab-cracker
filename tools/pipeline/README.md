# Explicit wall-clock timing and delivery reports

Begin before acquisition. Timer durations use monotonic_ns, not CPU time or reconstructed log timestamps. State persists under working/; measured output is result/timing.json. Resume requires the same host/boot and clock continuity; do not overwrite an old run. Total includes pauses and orchestration gaps; phase spans include agent reading/review time. This is user-facing elapsed time, not pure compute time.

```powershell
python tools/pipeline/timing.py runs/NEW_RUN begin --scope "full conversion"
python tools/acquisition/acquire.py SOURCE runs/NEW_RUN
python tools/pipeline/timing.py runs/NEW_RUN start v2
python tools/pipeline/timing.py runs/NEW_RUN start v2.frame_survey_seconds
# Extract and actually inspect selected frames here.
python tools/pipeline/timing.py runs/NEW_RUN stop v2.frame_survey_seconds
# Bracket all other executed steps; complete V2 QA before stopping.
python tools/pipeline/timing.py runs/NEW_RUN stop v2
```

Acquisition automatically brackets its phase (and initializes a timer if missing). Its source record also records download-only/provider durations. Other commands can use `timing.py RUN exec PHASE_OR_SUBSTEP -- COMMAND ARGS...`; errors close the span as failed. Start a parent before timing its children. Revisited phases accumulate. Only one parent and one child run at a time.

Keys:
- v2: video_inventory_seconds, frame_survey_seconds, adaptive_frame_collection_seconds, coverage_recovery_seconds, measure_reconciliation_seconds, crop_export_seconds, final_qa_seconds.
- v3: transcription_seconds, canonical_assembly_seconds, deterministic_validation_seconds.
- guitar_pro: gp_adapter_seconds, gp_export_seconds, gp_roundtrip_validation_seconds, gp_render_seconds.
- v4: source_feature_sweep_seconds, targeted_review_seconds, auto_correction_seconds, final_verification_seconds.

Time V3 visual transcription as well as assembly. For GP, wrap the actual Node export command in `exec guitar_pro`, then `import-gp`; this imports the exporter's performance.now durations only if its canonical hash and run interval match. Export timing is separate from musical provenance. Optional unexecuted steps stay null. `reuse KEY SOURCE` records reused work without filling in historical seconds.

After V4 final verification, stop all open spans and `timing.py RUN finish`. Then `python tools/pipeline/final_report.py RUN/result`. Reports reuse V4 evidence and check current hashes; they do not perform new recognition. Status is conservative on missing/stale evidence. Review-required issues retain exact sequence/printed/event/string/field locations, values, source/render paths and correction history. VERIFIED groups are counted, not printed individually. Known low-impact limitations recommend review; unresolved musical content or unexpected mismatches require review. No accuracy percentage is inferred.

Tests: `python -m unittest discover -s tools/pipeline -p 'test_*.py'`. Tests validate mechanics, not visual recognition. See [measured regression](../../acceptance/HARDENING_ACCEPTANCE.md) for explicit reused evidence and latency scope.
