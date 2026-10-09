# Sutram — Round 44 development handoff to Sarvam
**Date:** October 9, 2026 (America/Toronto)
**Target:** https://github.com/dap2810/Sutram
**Review branch:** `feature/r44-module-contract-completion-20261009`; base `095e3873967298c4b0416679c7cc9aa46f4f6c43`

## STATUS
Review candidate, **NOT MERGED, NOT A FULL WINDOWS RELEASE**. The 4 assigned Round 44 capabilities are implemented on the feature branch: (1) v1 `niryat` undefined-export diagnostics with file/line, (2) exportable top-level `sutra` constants using compile-time initializer ASTs, (3) distinct qualified unknown vs known-private diagnostics, (4) one active dependency graph pass. The duplicate historical R41 DFS and its 1MiB work buffer were removed; the `graph_preflight_v1` symbol remains as a compatibility entry that dispatches into the sole Muse DFS.

## SOURCE CHANGES
- `src/sutram_compiler.asm`: preserve pure handwritten NASM backend and native generation, maintain legacy import path. Track export declaration locations; validate function and constant definitions. Recognize and namespace bare constants. Resolve top-level constants at compile time. Validate qualified names outside strings and comments.
- A single module graph traversal now performs recursion, with R41 exact-header name validation, dependency-cycle, missing-module and invalid-module diagnostics. Deferred alias checks preserve diagnostic precedence.
- `tests/r44_pending/`: seven fixtures plus exact Linux native-recorded `recorded.out`/`recorded.exit` and four negative markers. Runner compares actual stdout and return code while normalizing only checkout directory prefixes.
- `tools/r44_r41_native_goldens.py`: compares five existing R41 goldens with portable paths (original golden bytes unchanged).
- `tools/r44_optin_graph_acceptance.py`: six additional native opt-in exact diagnostic checks including alias precedence, cycle, missing imports and invalid module names.
- `tests/module_graph/test_r41_native_preflight_contract.py`: updated static checks for one-pass traversal. Old missing 164–166 fixtures explicitly skipped rather than fabricated.
- `.github/workflows/r44-acceptance.yml`: ordinary-user NASM install from Ubuntu .deb, Linux-only generated `win/rtblob.inc` stub in CI workspace, ELF build, native testing, and read-only SHA audit.
- `tests/gui/R44_OWNER_NATIVE_GUI_MANUAL.md`: user-facing manual acceptance; no GUI visual test claimed.

## VERIFIED WITH REAL GITHUB ACTIONS EXECUTION
- Linux x86-64 NASM 2.16.01 assembly **PASS**; linked and ran compiler successfully.
- R44 actual native goldens **7/7 PASS**.
- R41 retained native goldens **5/5 PASS**.
- Additional exact R41 opt-in graph diagnostics **6/6 PASS**.
- Codegen instruction gates **12/12 PASS**.
- Ten script language packs **30/30 PASS**.
- `python3 -m unittest discover -s tests/module_graph -v`: **18 tests, 14 pass, 4 skipped** because pre-GitHub 164–166 fixtures are missing from this checkout.
- **Verify the green test run:** https://github.com/dap2810/Sutram/actions/runs/37947250212

## BLOCKED / VERIFICATION LIMITS
- `tests/run_tests.py`: repo migration omitted most `tests/expect/` goldens. CI produced 163 NO-EXPECTATION, 15 COMPILE-FAIL where expected-failure markers absent, 4 FAIL that compare identical diagnostics except for `/scratch/work` versus the runner checkout path, and 1 PASS. This is **not** a 186/186 acceptance; the CI step is flagged continue-on-error, unlike the hard-fail R44/R41 tests, codegen and packs. Restore the original accepted suite; do not rewrite or manufacture missing goldens from the modified compiler.
- `win/rtblob.inc` generated PE runtime include is **missing** in GitHub. CI writes a temporary stub **only for Linux ELF testing**; this does not verify PE generation or Windows execution. Restore actual runtime include from verified source archive and run both target builds.
- GUI has **not** been rendered visually on Windows or X11 here. Owner manual GUI checklist included.
- The new single pass is covered by representative test scenarios, not a comprehensive formal equivalence proof for every legacy import or corner case. Sarvam should independently stress limits, nested/Unicode imports, alias collisions and source byte bounds before acceptance.
- No performance measurements made; removing one pass and its 1MiB workspace is a structural change, not a claimed throughput increase.

## DELIVERABLES
- Feature branch retains full source changes and exact recorded native fixtures.
- `ChatGPT-to-Sarvam/ROUND-44-PROPOSAL.patch`: GitHub-generated complete diff for source, workflow and tests against main.
- `ChatGPT-to-Sarvam/ROUND-44-CHANGED-FILES.sha256`: changed-file SHA-256 manifest, excluding itself (check with `sha256sum -c` from checkout).
- Main branch compiler remains untouched; handoff/pointer may be posted to `ChatGPT-to-Sarvam/` on main without merging compiler code.

## NEXT — SARVAM REVIEW
1. Read this report and `ROUND-44-PROPOSAL.patch`; verify changed-file hashes, forward/reverse patch and latest branch SHA.
2. Rebuild from branch HEAD on Linux with actual Windows runtime include; assemble Win64 PE32+; run on Windows under normal user permissions.
3. Restore original 186 expected-output suite, run it and all native 7+5+6 fixtures, 12 codegen gates, and 30 pack checks independently.
4. Confirm diagnostic order, internal-function/private isolation, exported constants including forward references/expressions, imported aliases, name bounds and transitive modules.
5. Merge via PR only after independent acceptance. Assign next significant development round under `Sarvam-to-ChatGPT/`.
