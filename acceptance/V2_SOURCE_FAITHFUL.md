# V2 source-faithful simplification — PASS

V1 COMPLETE · V2 CORE COMPLETE · V3 ACTIVE. No V3 implementation.

New exports save selected RGB crops directly to measures/. Removed the active
normalization helper, duplicate source_measures/ output, normalization records
and tonal transforms. Legacy transformation plans fail before writing output
with an explicit migration message. Historical runs and evidence are retained.

README, requirements, execution plan and skill now prioritize coverage, order,
no duplicates, source selection, faithful crop and readable preview/PDF.
Normalization is only an optional future presentation enhancement. V3 consumes
the actual source style directly. Generic optional metadata, headers and portable
fonts remain unchanged; the exporter has no song constants or Windows font path.

Seven automated tests pass, including five presentation variants, exact colored
source pixels with faint detail, crop context, order, single-folder output and
rejection of legacy transforms before any output is written. Skill validation
also passes.

Re-exported the accepted Una Mattina selections in a fresh regression directory,
without video reconstruction. All 45 measure PNGs, full_score.png and all three
page PNGs are byte-identical to the visually reviewed source-preserved run.
Identity, timestamps, crop/context geometry and order remain unchanged; records
only lose normalization, source_output and tonal_transform fields. No duplicate
source folder is created. The three-page A4 PDF opens and embeds exactly those
same page pixels. All files in the accepted run retain their SHA-256 hashes.

Evidence: runs/v2-source-faithful-regression/working/decisions.json,
working/accepted_before_hashes.json and result/inspection/regression.json.
Local reconstruction is validated on the two tested fixtures; URL acquisition
remains unvalidated. No universal source-style robustness claim is made.
