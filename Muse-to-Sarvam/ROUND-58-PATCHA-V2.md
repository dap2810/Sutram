# ROUND-58 — Patch A regenerated on current main (v2)

Base: origin/main `4bfb73d2` (one docs commit past the brief's base
`f9b281dc`; that commit adds only
`ChatGPT-to-Sarvam/ROUND-131-NIRMMITA-TRACE.md` and touches no
`examples/` file, so the drift below is unchanged from the brief).

Deliverable: `ROUND-58-patchA-v2.patch` (32,844 bytes, 36 files).
Claude's brief (`Sarvam-to-Claude/ROUND-58.md`) says Claude will wait
for this file, `git apply --check` it, and apply it. Patch A is still
NOT applied on main (verified: `sum` is still English in
`examples/11_forloop.sm`).

Note on spelling: Claude's brief misspells the rename as
`dvvitiya_pravan`. The tree says `dvitiya_pravan`, and v2 matches the
tree.

## WS1 — regeneration

Patch A v1 was re-downloaded from the outbox
(`Muse-to-Sarvam/ROUND-56-patchA.patch`) and blob-SHA verified:
`211c9e65563520e3cd86a67fbc261d5cb66abd64` (matches the R56
delivery), 32,896 bytes.

`git apply --check` of v1 on current main fails in exactly the two
brief-named files and nowhere else:

- `examples/126_numeric_pipeline.sm` — context line
  `likha(bindu(u, v))` is now `likha(bindu_gunan(u, v))`.
- `examples/208_kalana.sm` — context line
  `likha(pravan2(xs, ys, 5))` is now
  `likha(dvitiya_pravan(xs, ys, 5))`.

v2 was built by applying v1 unchanged to the other 34 files, then
applying v1's own variable renames code-only to the current 126/208:

- 126: `values` → `mulya`, `total` → `sarva_yog` (word-boundary,
  code only; neither identifier occurs in a string or comment in
  this file).
- 208: `xs` → `ank_suchi` only. `ys` is a Patch-B name and stays;
  `pravan` itself was not renamed.

## WS2 — whole-patch check

- `git apply --check` of v2 **passes** on a fresh current-main
  checkout.
- Applying v2 reproduces the regenerated tree byte-for-byte
  (diff of the applied tree against the regenerated tree: empty).
- Hunk-for-hunk against v1 (ignoring `index` lines): the same 36
  files, and **only the two hunks differ, only in those two context
  lines** (208's changed line carries the new function name,
  `dvitiya_pravan(ank_suchi, ys, 5)`, because that is what current
  main calls; the rename itself is unchanged).
- On the v2-applied tree: **proofs 226/226, suite PASS=225,
  NO-EXPECTATION=4, no golden changed.**
- Count: **2 hunks fixed, 34 files untouched, 0 further drift.**

## WS3 — which of the 12 Patch-A names appear in the first ten example files

The 12 Patch-A names (count ≥ 3, from v1): `st`, `xs`, `values`,
`sum`, `out`, `data`, `total`, `arr`, `buf`, `util_chinha`, `flag`,
`terms`.

Checked code-identifiers only (string literals and comments
stripped; field accesses excluded) in files 01–10
(`01_hello`, `02_arith`, `03_if_else`, `04_while`,
`05_func_params`, `06_rachana`, `07_module`, `08_demo`,
`09_comparisons`, `10_mathlib`):

**NONE of the 12 appears in code in the first ten files.** The
subset is empty, and that is the finding: Patch A's readability
value is in later files, not the beginner sequence. (For the record,
`08_demo.sm`'s `score` is a rachana field, not a variable, and is
not one of the 12 names — same as R56 WS3.)

The first Patch-A name a beginner meets is `sum` in the eleventh
file, `11_forloop.sm` (3 occurrences: declaration, accumulation,
print). Consistent with R56 WS3.

## NOT RUN

- Windows / WSL (no Windows environment here; nothing in this round
  touches Windows-specific code).
- The guard was not re-run: a variable rename cannot reach an
  executable, and Claude's side runs the guard on application per
  their brief.

## Files and verification

- v1 SHA verified before regeneration (above); v2 generated from
  the regenerated tree by git diff, so its hunks are exactly the
  tree difference.
- All verification above was run on fresh checkouts of current
  main, not on the working tree. The working tree is left clean
  (only the pre-existing untracked `build/` directory).
