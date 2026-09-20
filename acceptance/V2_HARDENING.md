# V2 final hardening — PASS

V1 COMPLETE · V2 CORE COMPLETE · V3 ACTIVE. Cleanup only; no V3 implementation.

- Removed test-song metadata and the machine-specific Arial path from the V2 exporter.
- Optional plan metadata: title, artist. Unknown values are omitted. Optional font
  path is relative to the plan; otherwise Pillow's portable bundled font is used.
  Non-default scripts may require an explicitly supplied font with suitable glyphs.
- Normal output has supplied metadata and page numbers. show_header=false suppresses
  it; debug=true opts into engineering labels. No proprietary fonts committed.
- Used the accepted plan and extracted frames only; no raw-video reconstruction.
- SHA-256 comparison: 57 measure PNGs, measures.json, full_score.png and all 15 row
  images are unchanged. Three page bodies below the header are pixel-identical.
- The 3-page PDF opens, has A4 dimensions, and embeds exactly the page PNG pixels.
  All three actual Poppler-rendered pages were visually inspected and are readable.
- Five automated tests pass. Export presentation cases cover missing metadata,
  supplied title/artist, explicit font, no header and debug mode with unchanged
  primary outputs. Helper code has no song/artist constants or Windows font path.
- The previous PDF could not be overwritten, so the accepted output was preserved
  and the new export placed in runs/v2-yukinohana-hardening/result/.

Local-video V2: validated. URL acquisition: supported in workflow, not validated.
Second video style: not validated. These gaps do not block V3. No additional
raster-score beautification unless V3 fails and visual scores become primary.

Private evidence: runs/v2-yukinohana-hardening/working/before_hashes.json and
result/inspection/hardening_verification.json. Source plan metadata belongs in
the run, never in reusable helper code. The stable measures/ and measures.json
contract remains the direct V3 input.
