# V2 source-faithful normalization — PASS

V1 COMPLETE · V2 CORE COMPLETE · V3 ACTIVE (status only; no V3 implementation).
This user-requested preparation stage follows the completed generic exporter
hardening and supersedes its restriction on further raster work for this scope.

## Accepted input and method

Reused the accepted local video's selected frames and plan in
`runs/v2-yukinohana-normalized/`; no new video reconstruction. Original acceptance
remains 209.95 seconds, 69 inspected frames, 57 complete logical measures with no
known omissions, duplicates or order errors. No new video frames were inspected.
The user-owned original and both previous output runs remain unchanged.

Representative source crops have dark notation on pale gray, with occasional
yellow edge highlighting and gray antialiasing. Compared original color,
white-point adjustment, continuous contrast adjustment and binary output on
eight representative measures. Selected a song-wide max-channel grayscale
conversion followed by explicit levels (black 40, white 235, gamma 1.4).
These parameters belong only to this run's plan. The binary candidate coarsened
edges; continuous gray preserves thin lines and curves while whitening the
background and strengthening black glyphs. No redrawing or musical inference.

## Result and review

- 57 untouched selected RGB crops in source_measures/, pixel-equal to selected
  frame regions including existing boundary context; 57 preferred measures/.
- All 57 source/output pairs visually compared across 15 readable contact sheets.
  Enlarged checks: 2, 6, 23, 30, 32, 43, 51, 56, 57 (multi-digit frets, dots,
  parentheses, thin stems, ties/slurs, technique text, rests, tuplets and curves).
- No known musical visual information lost or false notation introduced.
  Status counts: normalized 57, partial 0, source_preserved 0; high confidence,
  source_faithful true and uncertainty null after review.
- Identical identities, order, source timestamps/frames, crop/context coordinates,
  core geometry and layout compared with the accepted hardening plan/records.
  Preferred pixels intentionally change; source_output and normalization records
  are added to measures.json. The primary V3 contract remains measures/ plus JSON.
- full_score.png inspected in three contiguous readable sections covering all
  57 measures. All three page PNGs and three actual Poppler PDF renders inspected.
  The PDF opens, has A4 landscape dimensions and embeds exactly the page PNG pixels.
  Full-score pixels equal concatenated normalized cores. Reviewed PNG hashes
  remained unchanged when final review statuses were written and re-exported.
- White backgrounds and dark notation are consistent. Fine antialiasing remains
  gray intentionally; this is not a forced one-bit export. Existing context
  fringes and source raster limitations remain, without further layout polish.

## Mechanical regression and limits

Eleven automated tests pass, including five presentation variants. They cover
exact original fallback, explicit transformations, intermediate stroke values,
review guard, external-image geometry, per-measure override, raw context retention
and composition from preferred cores. Pixel fixtures test mechanisms, not musical
recognition or second-style robustness. Every-pair visual QA remains mandatory.

No song-specific metadata or Windows-only font path is present in reusable
export/normalization helpers. Optional metadata, portable/default or explicit
font, generic headers and opt-in debug labels remain intact.

Local-video V2: validated. URL acquisition: supported in workflow, not validated.
Second video style: not validated. Dark/translucent or moving-image backgrounds
have not passed real-video normalization acceptance. Future sources require
their own visual method selection and source fallback when unsafe.

Private evidence: `working/decisions.json`, `working/normalization_review.json`,
`working/reviewed_image_hashes.json`, and `result/inspection/` with comparison
sheets, closeups, full-score sections, actual PDF renders and
`normalization_verification.json`. Preferred delivery is the new result directory;
previous runs are preserved as historical evidence.
