# Normalization experiment — retired

White-background/black-notation conversion is no longer a V2 stage or V3
prerequisite. New V2 runs export source-faithful selected crops to measures/,
without a duplicate source_measures/ folder, method comparisons or normalization
status fields. V3 handles the actual visual source style directly.

Normalization is only an optional future presentation enhancement, requiring
separate scope. It must not consume time in the current reconstruction workflow.

Historical plans, source_measures/, normalized outputs and review records in
accepted runs remain unchanged. The former helper is available in Git history
(commit 9128b9a); it is removed from the active pipeline. To reuse an old plan
for a NEW source-faithful export, remove plan-level and per-selection normalization
fields and non-none tone settings from a copy. Never overwrite accepted evidence.
The current exporter rejects legacy transformations before writing outputs.

See [historical normalization evidence](../acceptance/V2_NORMALIZATION.md) and
[the translucent-source test](../acceptance/V2_UNA_MATTINA.md), which motivated
retiring mandatory normalization.
