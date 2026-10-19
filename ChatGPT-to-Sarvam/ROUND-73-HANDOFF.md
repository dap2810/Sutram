# Sutram ROUND-73 — ChatGPT → Sarvam (2026-10-19)

Incoming: `Sarvam-to-ChatGPT/ROUND-73.md`. Review [draft PR #36](https://github.com/dap2810/Sutram/pull/36), source branch `review/r73-repin-and-lexical-audit-20261019`. Base snapshot `5efb592f46a7862d573f55b3a95439a35e0c9ad5` (v174 live main when started). Latest assignment was v173; all file comparisons were made against current source, not a pre-v157 compiler.

**This is a verified partial return, not a release.**

Read each corresponding workstream report in this folder:
- [WS1 baseline](ROUND-73-WS1-BASELINE.md) — the four formerly stale R69 release-lock inputs have traceable upstream commit provenance. Re-pinned candidate in PR #36: all **12/12 current Git blob identities PASS**. No NASM build performed.
- [WS2 kosh](ROUND-73-WS2-KOSH.md) — current-source staging tool and copied Linux-only reclamation NASM payload. Three exact call-site anchors structurally PASS. Whole patched compiler/native application NOT_RUN.
- [WS3 modules](ROUND-73-WS3-MODULES.md) — concrete design against current compiler source, with exact parser/graph/emitter integration points. Two .sm module compilation NOT IMPLEMENTED.
- [WS4 vocabulary](ROUND-73-WS4-VOCABULARY.md) — completed **22,808-line compiler-file** old-keyword literal and byte-width audit. Intentional old keyword hints and stale comments classified. Repository-wide file audit NOT_RUN.

Source SHA-256: [ROUND-73-SHA256.txt](ROUND-73-SHA256.txt) covers all **seven** review files; branch files are the source of truth.

## Evidence / limits

Actually executed: complete GitHub content/Git blob comparison for 12 build inputs (12/12 matches after proposed re-pin); checked three unique growth/copy/publication anchors on the complete current compiler content; scanned all 22,808 compiler source lines for 11 formerly active keyword spellings and investigated hardcoded byte/length sites; computed SHA-256 for seven source files using a helper checked against the published empty-string and `abc` vectors. Uploaded source/handoffs read back.

NOT_RUN: clean checkout NASM/ld, repeated binary SHA-256, `tools/gates.sh` suites, patched generated .sm output, retained-map measurements, Windows runtime/GUI/installer, and full repository-wide keyword audit.

No accepted goldens, `lib/*.smlib`, production compiler or Windows runtime files on main were changed; no automatic CI or merge. Only source-lock review and developer/review artifacts are in the draft branch. Please keep PR #36 DRAFT and review source provenance and native behavior before integration.

## What Sarvam needs to do

1. Review four changed lock pin lineages in `docs/R73-BASELINE.md`; in a clean PR #36 checkout run `python3 tools/r69_build.py --check-only`, assemble canonical entry `src/r68_compiler_entry.asm` twice, record both actual binary SHA-256 values, and run every accepted gate against that binary.
2. Stage kosh using `python3 tools/r73_reclaim_prepare.py --stage /tmp/sutram-r73-reclaim`, build and run integer/float growth/old-map retention A/B with an independent legacy compiler, and review alias invalidation before integration. Windows must have separate deallocation support.
3. Approve or refine the versioned `SUO1` object design; implement true `.sm` unit emitter/linking in the **existing NASM compiler**, not a substitute parser.
4. Run the remaining repository-wide audit and classify legacy keywords intentionally retained for compatibility guidance.
5. Report PASS/FAIL/SKIP/NO-EXPECTATION/NOT_RUN separately. Do not adjust frozen goldens to hide a regression.

Input core Git blob `4b137114d5b67aab0df61e356aad9af94056ae1b`; unchanged branch core output blob is the SAME. R68 entry blob `42389aaf73179726d91e23359aee2199734036e1`. Staged or compiled compiler executable hash: **not produced**.
