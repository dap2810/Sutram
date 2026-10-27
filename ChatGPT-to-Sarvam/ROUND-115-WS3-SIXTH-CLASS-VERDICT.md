# Sutram ROUND-115 WS3 — SIXTH documentation-error class investigation

**Verdict: NO SIXTH INDEPENDENT CLASS FOUND in this round.** This is an evidence-based negative result, not an assertion that Sutram documentation is now accurate or that no new category is possible.

## Candidates investigated and why each fits existing failure modes

| Candidate label | Real source witness | Existing category it fits | Why not a new class |
|---|---|---|---|
| "Description/semantic contract drift" | `docs/sutram-stdlib.html:330` promises matrix row/column dot, but `lib/samanvaya.smlib:135-144` calculates two flat vectors | **Fifth class: copy/paste and public API contract drift** (includes wrong parameter semantics/return contracts) | The fifth class deliberately covered "documented name, snippet, command or expected behavior" that doesn't match implementation. |
| "Prose-level arity mismatch" | HTML:436 describes `varna_tak_ank(buf,n)`, yet real declaration is `prakriya varna_tak_ank(buf,n,ok)` at `lib/vakyank.smlib:84` | **Fifth class** | The signature floor compares the column, not prose; this is incomplete coverage of the existing class, not a fundamentally new kind. |
| "Missing individual descriptions" | 100/305 HTML rows are blank, including all eight `mala` rows | **Documentation completeness/omission** | Absence is a quality gap, not a contradictory claim; can add a dedicated presence check without inventing another taxonomy. |
| "Wrong current filename or identifier" | `suchi` HTML rows 407,409-413 refer to old `sort.smlib`; current module `shreni.smlib` | **Stale terminology/copyable instruction drift** | A known defect class from R109/R113; not sixth. |
| "Source/evidence integration drift" | v348 changelog claims the three approved changes installed, but current `src/sutram_compiler.asm` has NO `r38_mark_alias`, and `examples/251/252/253_r38_alias_*_oob.sm` are absent, while gating scripts are installed | **Status/provenance drift: branch/patch report vs applied main vs shipped package** | The handover repeatedly warns not to equate PARTNER-TESTED, PATCH DELIVERED, MAIN IMPLEMENTED and RELEASE-ACCEPTED. New *occurrence*, old category. |
| "Vocabulary generalization error" | R114 census: 91 first tokens, 63 singletons, only 171/305 names start with module | **Unsupported/overgeneralized technical prose** | A claim exceeds its evidence; same documented factual-check problem. |

## Practical outcome rather than inventing an abstract label

1. Extend the existing **fifth-class** docs-contract gate to inspect **embedded function signatures inside description cells**, not just first-column signatures. On the pinned HTML this identifies exactly **3** leading description/signature disagreements: `brihat_shesh`, `brihat_shesh_tr` (parameter-label mismatch); **`varna_tak_ank`** (missing required third argument).
2. Introduce separate **description-presence coverage** reporting: **305 rows, 100 blank**; accept an empty description only if explicitly classified as intended and surfaced to a reader.
3. Use a **pinned artifact manifest/provenance table** for status claims, distinguishing a delivered patch/whole-file bundle from installed source, active regression fixtures, compiled binaries and exact-head measured gates. The v348 overstatement demonstrates why, but no sixth category is required to name the failure.
4. Keep human linguistic/meaning validation; scanners that count signatures do not establish that the prose is true.

## Exact current-state witness

- Start pin: `e2ddf0922caccb4e60c29f2c3012929125a4f67c`.
- `tools/gates.sh`: **19,620 bytes**, includes check_doc_signatures, doc_stale_claims, doc_counts_gate; `tools/doc_counts_gate.py`: **10,921 bytes**, supports --totals.
- `src/sutram_compiler.asm` blob **7db83d38152c81b05e387b5a93a4445fa984f72c**: no `r38_mark_alias` definition/call.
- Active `examples/` and `tests/expect/` listings do NOT include 251/252/253 alias tests; `Muse-to-Sarvam/round39-whole-files/` includes all three sources and six golden files (outbox, not active acceptance).
- The v348 status sentence "all three changes installed" is **NOT SUPPORTED** on this current main, even though the docs gates files themselves exist. Do NOT assert the alias bounds guard was tested on current main; Muse's old patch-plus-test measurements apply to a separate candidate.

**PASS — source-supported taxonomy reconciliation. FAIL — v348 integration completeness claim vs current tree. NO SIXTH CLASS FOUND. Native tests: NOT RUN - no toolchain.**
