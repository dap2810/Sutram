# ROUND-37 — whole suite, guard, description sample

**Base:** `origin/main` at `1ccec720` (v341; round written against v338). Compiler v246.
**Environment for every check below:** Linux x86-64 (this VM), nasm 2.16.03 from
`~/workspace/build-tools/nasm-inst/bin` (not on PATH by default — the first
gates run failed with "nasm: not found" for that reason alone, and passed once
PATH was set), Python 3.12. No X11 display, no Windows, no Wine.
PASS / FAIL / NOT-RUN are reported separately throughout.

## WS1 — whole suite and the three new checks

| Check | Environment | Result |
|---|---|---|
| `sh tools/gates.sh` | Linux, nasm on PATH | **34 PASS, 0 FAIL, 1 NOT-RUN** (NOT-RUN = Windows execution) |
| `python3 tests/run_tests.py` | Linux | **NO-EXPECTATION=4, PASS=218** (as expected) |
| `python3 tools/crash_corpus.py --compiler ./sutram_compiler` | Linux | **227 cases + manifest, 0 failed** |
| `python3 tools/proof_lib.py --compiler ./sutram_compiler` | Linux | **224/224 PASS** |
| `python3 tools/proof_props.py --compiler ./sutram_compiler` | Linux | **86/86 PASS** |
| `python3 tools/check_layers.py` | Linux | **14 core, 9 alloc, 1 std — OK** |
| `python3 tools/check_alloc_bounds.py` | Linux | **26 allocations: 13 bounded, 13 exempt, 0 failed** |
| `python3 tools/doc_counts_gate.py --gates /tmp/gates37.txt` | Linux | **Every document agrees** (gates 34, suite 218) |
| `python3 tools/doc_stale_claims.py` | Linux | **116 documents, 160 hits** (was 115/160 on v334; +1 document, same hit count). Known FALSE: 1 unique claim (`docs/sutram-design-parameters.html:365`, "there is no FFI", 2 hits); the rest are TRUE limits, policies, design proposals, or HISTORICAL entries. Full re-triage was not repeated this round. |
| `python3 tools/check_doc_signatures.py` (NEW) | Linux, static only | **24 modules, 305 declarations, 305 signatures, 0 mismatches — PASS** |

No FAIL anywhere. The one NOT-RUN is Windows execution, as in every prior round.

## WS2 — the guard

**This round's number, Linux, on v341: 551 programs, 470 byte-identical
executables, 81 refused identically, 0 DIFFER.** (The round's "476" is the
Windows session's count; Linux holds at 470, as in R32–R36. Fresh build from
`src/r68_compiler_entry.asm` is byte-identical to the committed binary.)

## WS3 — are the documented descriptions accurate?

**Sampled: 31 functions** — every 10th of the 305, stratified across all 24
modules (method: lib comment, which is what the HTML regenerates from, checked
against the function body and, where present, its golden test).
**Wrong: 0. Missing (no description): 9** — asti_sampurna, dviguna, laghu2,
vardh, roop_asht, util_chinha, anwesh_sarak, asti_ank_akshar, avanat_sanket.
The other 22 descriptions match their code, including edge cases (empty
needle, negative prefix length, saturating overflow, one-sided ends).

**Worst one:** `brihat_ank_tak` — the main description is correct (render,
digit count, caller allocates ≥4n, base out of range → 0, −1 on alloc failure),
but its historical asides are stale: "n ≥ 22 overflowed the internal buffer"
predates the R39 wrap guard, and "(base 0 trapped with SIGFPE)" describes old
behaviour, not the current return-0. Not counted as wrong (the operative
claims are true), but it is the stalest prose in the sample.

## Delivery

- This report: `Muse-to-Sarvam/2026-10-26-round37-suite-guard-descriptions.md`
- No code or doc files changed (audit round).
- `git push` has no credentials here; delivery via the GitHub API as usual.
