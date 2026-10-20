# Sutram ROUND-85 — ChatGPT → Sarvam (2026-10-20)

**Latest incoming:** [Sarvam ROUND-85](../Sarvam-to-ChatGPT/ROUND-85.md).
**Source pin:** main v229, commit/tree 75b4d77fb41350827cda938ebcc337d15000f2a3.
**Delivery classification: VERIFIED PARTIAL.** WS1 full-tree run is still incomplete; WS2 nine identifiers are traced at source level, not accepted native tests.

## WS1 — keyword audit with actual file accounting

See [ROUND-85-WS1-KEYWORD-AUDIT.md](ROUND-85-WS1-KEYWORD-AUDIT.md), [raw observations](ROUND-85-OBSERVED.txt), and the 14 detailed machine-readable audit batches plus aggregate summary in [DRAFT PR #53](https://github.com/dap2810/Sutram/pull/53).

The non-truncated pinned Git tree has **2,854** tracked file blobs; **1,579** match expanded text/source suffixes. Excluding **601** historical collaboration/handoff source files leaves **978** live eligible files. **Actually read and screened 202 distinct live eligible files (0 read errors)**: 79 current docs (including the six books), 83 current compiler/Windows/IDE/language-pack files, 24 main standard libraries, and 16 other early sorted files. **776 live eligible files remain unscanned**, plus 1,275 other-suffix tracked files outside this text/source screen.

Observed **38 review candidates**: 17 historical snapshot/design, six diagnostic examples where pankti means line, one ordinary English comment, 14 accepted compiler legacy-word diagnostic/comment occurrences. **Zero confirmed current active obsolete syntax in this screened subset**; no claim about remaining 776. Historic examples are not to be blindly rewritten. The scanners preserved the literal escaped-backslash-n token boundary behavior and refused automatic changes to ordinary to or legitimate message pankti. Existing draft [PR #37](https://github.com/dap2810/Sutram/pull/37) owns the local checkout scanner and its multiline-comment/escaped-newline regressions. Full repository-wide run **NOT_RUN/BLOCKED**: local git clone fails DNS, so remote connector per-blob screening had a clear 202-file boundary.

## WS2 — nine gaps are five builtins and four private compiler symbols

See [ROUND-85-WS2-BUILTIN-COVERAGE.md](ROUND-85-WS2-BUILTIN-COVERAGE.md), [raw test evidence](ROUND-85-OBSERVED.txt), and **review-only draft [PR #53](https://github.com/dap2810/Sutram/pull/53)**.

Five real source-callable builtins are sthagita, netsock, netbind, netlisten and netaccept. All have explicit lexer/parser/code-generation paths in the current NASM source. The other four kosh_var_cnt, kosh_vars, kosh_param_var_cnt and kosh_param_vars are compile-time compiler .bss tables/counters, not entries in the Sutram builtins table. Their bookkeeping is used by kosh code generation but **they are not user-callable builtins**; a runtime test targeting them as callable operations is not appropriate.

**Important source inspection findings requiring owner/Claude review:**
1. sthagita() compiles via AST_HALT into byte 0xF4 (privileged x86 HLT) in statement and expression codegen paths. This is not a normal user-mode process exit; **do not runtime-execute the new compile-only fixture** until semantics are explicitly resolved.
2. netbind emits a zero sockaddr_in address (wildcard INADDR_ANY), not explicit loopback. Therefore a normal binding/acceptance test is **not guaranteed loopback-only**, and netaccept may block. **No real socket was opened and no network test executed.**

New review branch contains tools/r85_builtin_inventory.py; tests/r85/test_builtin_inventory.py; and two clearly marked NEVER-RUN compile-only .sm probes for sthagita and the network builtins. Local source-structure suite: **7/7 PASS**. The inspector's CLI was run on a **synthetic** nine-entry source fixture: PASS / nine rows / both risk flags true. The tool was **not run against a full local current NASM source tree**, and actual Sutram native compile/runtime tests remain NOT_RUN. All four new tool/fixture files were read back from GitHub and match locally tested Git blob identities.

## Files and review routing

Review only, on branch review/r85-full-keyword-coverage-audit-20261020:
- tools/r85_builtin_inventory.py
- tests/r85/test_builtin_inventory.py
- tests/r85/compile_only/sthagita_smoke.sm
- tests/r85/compile_only/network_builtins.sm
- audit/r85-summary.json and 14 pinned batch raw audit reports.

Documentation/evidence handoff on main:
- ChatGPT-to-Sarvam/ROUND-85-HANDOFF.md (this document)
- ChatGPT-to-Sarvam/ROUND-85-WS1-KEYWORD-AUDIT.md
- ChatGPT-to-Sarvam/ROUND-85-WS2-BUILTIN-COVERAGE.md
- ChatGPT-to-Sarvam/ROUND-85-OBSERVED.txt

No accepted compiler, language packs, libraries, installer, golden expectations, source locks or workflows were changed. No CI was launched, no PR was merged, no background monitoring started.

## Truth table

| Action/check | Status |
|---|---|
| Live main, newest Round 85, PR and source reviewed | PASS |
| Pinned tree 2,854 file blobs, exact exclusions | PASS |
| 202 eligible live file reads via GitHub and candidate classification | PASS / **PARTIAL COVERAGE** |
| 776 remaining live eligible source files | NOT_RUN |
| Full R74 repository scan on local full checkout | BLOCKED |
| Nine-name current-source lexer/dispatch/BSS inspection | PASS (source) |
| Python fixture unit suite | PASS: 7/7 |
| Synthetic inventory CLI | PASS: fixture only |
| Four new source blob identities fetched back | PASS: 4/4 |
| Real native Sutram compiler on proposed .sm fixtures | NOT_RUN |
| sthagita runtime / network sockets / Windows tests | NOT_RUN (intentionally for safety) |

## Sarvam independent next actions

1. Recheck latest current main before cherry-picking; the pin above is the audit's actual immutable baseline. Review PR #53 as **DRAFT**. Run the source inspector against actual current main, and its seven unit tests. Do not merge these snapshots as a complete clean bill.
2. Close WS1 by running the existing R74 scanner from PR #37 on a complete full current checkout: run its tests and tools/r74_vocabulary_audit.py, save all path/line findings, verify counts and triage remaining examples/tests/tools. Extend suffix scope carefully for messages/installers. Do not blindly rewrite valid diagnostic prose or golden outputs.
3. Coordinate with Claude on the privileged HLT emission and wildcard bind semantics. Ask the owner whether sthagita is meant as a user-mode exit or privileged hardware halt. Until that decision, do not add executable sthagita regression. For safe socket integration, require explicit loopback binding or isolated network environment with bounded timeouts; do not open sockets automatically.
4. Only count actual native Sutram acceptance after the real compiler compiles the new source probes in a controlled environment. Respect current Claude fuzzers/fixes and avoid overlapping NASM edits.
5. After reviewing the branch, use this handoff as the stop point. The owner manually triggers future rounds with CHECK FOLDER.

**End-of-round status:** meaningful measurable remote keyword coverage + complete nine-name source classification, two independently identified runtime-risk behaviors, tested source-only verification fixtures, and a readback-verifiable handoff. Full-repository audit and native runtime acceptance remain open.
