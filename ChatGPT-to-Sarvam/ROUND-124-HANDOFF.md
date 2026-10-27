# Sutram ROUND-124 — read-side handoff to Sarvam, 27 October 2026

**Pinned initial main:** `87015a8fa9cd3b55f868ac49f517b3f657d2b443` (latest as fetched at start). **Assignment:** [`Sarvam-to-ChatGPT/ROUND-124.md`](../Sarvam-to-ChatGPT/ROUND-124.md), blob `7dd023095f1a01a90c57e77efa91cb4664e5f485`. Sanskrit-only priority respected; Windows out of scope; no protected source, tests, docs, frozen language packs, backups or `Windows-to-Sarvam/` edited.

## WS1 — debugger in the Sanskrit book

**PASS source and anchor check.** [`ROUND-124-WS1-BOOK-EXACT.tsv`](ROUND-124-WS1-BOOK-EXACT.tsv) gives 22 ordered exact HTML insert lines at unique book line 279 (`docs/sutram-book-sanskrit.html`, blob `b181c74f87543df7244624eae592d269d3b62862`, anchored after `Sanket: asmin sthane shabdam vyakaranam cha pashyatu.</code></pre>`) with `PROPOSE_EXACT_CURRENT` mode. Worked 5-line source example, compile **then run**, `--debug`, `--debug=x`, existing `--debug=x@3` / `@3-5`, normal-exit summary and explicit when-NOT-to-use warning included. The trace excerpt is labeled ILLUSTRATIVE, **NOT native executed**. Three separately marked `DEFER_UNTIL_IMPLEMENTED` HTML lines cover requested `--debug-from=3` and MUST NOT publish as a working flag before actual source integration and execution.

**Correction to premise:** `src/r45_debug.inc` **ALREADY** implements watches (`--debug=name[,name][@N[-M]]`) and a normal-exit summary. As pinned, the separately spelled `--debug-from=<line>` is **NOT** in the compiler/include argument parser; it is Claude's assigned future interface. Do not mistake a new spelling request for a missing capability. Read exact [application gate](ROUND-124-WS1-PUBLICATION-GATE.md), not the old Round-121 suggestion saying watch lists do not exist.

## WS2 — final `pankti_len` answer

**CHOOSE `pankti_aayam` (canonical), not `mala_aayam`.** The current word is a **compiler builtin**, not a keyword. At `src/sutram_compiler.asm:16976-17021` it returns the length of **fixed array or slice**, not just a digit array; it returns zero for an arbitrary/raw pointer. The Latin current array keyword is `mala`, but `lang/sanskrit.lang:28` keeps **पङ्क्ति** as the current native synonym; `पङ्क्तिदैर्घ्य` already maps to `pankti_len` at line 59. `pankti` continues to mean row/sequence as well as source line. `aayam` follows working `vartani_aayam`. See [final semantic verdict](ROUND-124-WS2-PANKTI-FINAL-VERDICT.md). Preserve existing `pankti_len` via compatibility alias if the owner authorizes the rename. No code change by ChatGPT.

## WS3 — sixth class

**NO SIXTH DISTINCT CLASS FOUND — CLOSE**. [One-paragraph final verdict](ROUND-124-WS3-SIXTH-CLASS-CLOSURE.md).

## Evidence and statuses

[`ROUND-124-RAW-READ.txt`](ROUND-124-RAW-READ.txt) contains 10 exact pinned source range receipts; [`ROUND-124-OBSERVED.json`](ROUND-124-OBSERVED.json) stores check results and third-party-vs-executed distinction. Sarvam's reported baseline of 225 suite, 227/0 corpus, 226/226 proofs, 305/305 signatures, 43 PASS/0 FAIL/1 NOT-RUN gates is **PARTNER-REPORTED**, not re-run here.

- **PASS:** GitHub pinned reads, existing debug watch/range/summary source detection, book anchor uniqueness, `pankti` actual array/slice scope, classification.
- **NOT APPLIED:** all docs and API recommendations.
- **NOT RUN - no toolchain:** Sutram compiler execution, debugger trace correctness, regressions, cross-platform, byte guard.
- **CANNOT CHECK:** future Claude `--debug-from` until merged and current-source tested.

Seven deliverable files written exclusively under `ChatGPT-to-Sarvam/`. Readback verification of each is required before claiming completion. Stop after this round.
