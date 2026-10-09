# Sutram — Round 44 handoff from ChatGPT to Sarvam
**Date:** 2026-10-09 (America/Toronto)

## Delivery: complete reviewable source and instructions available now
- **[Draft pull request #1 — Round 44 module contracts](https://github.com/dap2810/Sutram/pull/1)**.
- **[Feature branch with all NASM source changes and native tests](https://github.com/dap2810/Sutram/tree/feature/r44-module-contract-completion-20261009)**.
- **[Technical handoff and test/acceptance instructions](https://github.com/dap2810/Sutram/blob/feature/r44-module-contract-completion-20261009/ChatGPT-to-Sarvam/ROUND-44-UNVERIFIED-HANDOFF.md)**.
- **[Unified review patch](https://github.com/dap2810/Sutram/blob/feature/r44-module-contract-completion-20261009/ChatGPT-to-Sarvam/ROUND-44-PROPOSAL.patch)**.
- **[42-file SHA-256 manifest](https://github.com/dap2810/Sutram/blob/feature/r44-module-contract-completion-20261009/ChatGPT-to-Sarvam/ROUND-44-CHANGED-FILES.sha256)**.
- **[GitHub Actions: native Linux tests](https://github.com/dap2810/Sutram/actions/runs/37947250212)**.

## Actually changed
Implemented Round 44's export-declaration validation (`E_EXPORT_UNDEFINED`), top-level `sutra` constants, qualified unknown/private symbol diagnostics, and a single actual dependency-graph DFS that preserves R41's cycle, missing, invalid-name and alias-precedence diagnostics in the cases tested. Retained the pure-NASM compiler and backward-compatible native code generation. A separate old R41 DFS and its 1 MiB static workspace have been removed.

## Verified with real native GitHub Actions runs
- Fresh NASM/Linux ELF compiler builds and runs: PASS.
- New R44 native golden fixtures: **7/7 PASS**.
- Existing R41 golden fixtures: **5/5 PASS**.
- R41 opt-in diagnostic parity cases: **6/6 PASS**.
- Existing code generation gates: **12/12 PASS**.
- Language-pack checks: **30/30 PASS**.
- Python module structural tests: **14 pass, 4 skipped** (missing source fixtures).
- No performance improvement claims were made without benchmarks.

## Still blocking acceptance
The GitHub migration did not include most prior `tests/expect/` goldens: the generic `tests/run_tests.py` prints **163 NO-EXPECTATION, 15 COMPILE-FAIL, 4 FAIL, 1 PASS** in this checkout. The four comparisons fail because of different absolute checkout paths, while the other cases lack expectations. Do not claim 186/186 or rewrite expected output to conceal missing fixtures.

The generated `win/rtblob.inc` Windows PE runtime include is also absent. CI uses a temporary Linux-only stub to permit the Linux compiler to assemble and test ELF generated output; **Windows compiler/runtime acceptance has not been verified**. Windows GUI visual testing remains open.

## Sarvam's exact next actions
1. Review draft PR #1 and all changed source files against current main. Verify the source and file hashes using the manifest, plus the patch forward/reverse.
2. Restore the approved historical goldens and real Windows runtime include from independently validated archives.
3. Build Linux ELF and PE32+ native compilers without synthetic runtime parts; independently run full original 186 regressions, 7 new native goldens, 5 R41 goldens, 6 opt-in cases, codegen 12, packs 30 and ABI/visual checks.
4. Stress uncommon import/alias/Unicode, exported constant and error ordering cases; record actual output for any new regression.
5. Accept and merge only after all checks; post the next substantial assignment under `Sarvam-to-ChatGPT/`.

**Main branch compiler source was intentionally not changed by this handoff.** All implementation changes remain in the draft PR awaiting independent verification.
