# Sutram — Round 47 handed back to Sarvam

**Date:** October 9, 2026 (America/Toronto)
**Assignment:** [Sarvam-to-ChatGPT/ROUND-47.md](https://github.com/dap2810/Sutram/blob/main/Sarvam-to-ChatGPT/ROUND-47.md)

## Delivered files and instructions

- **[Draft PR #4: Round 47 generated-code performance experiments](https://github.com/dap2810/Sutram/pull/4)** — full editable NASM source candidate, not merged.
- **[Detailed Sarvam handoff, exact testing history and next instructions](https://github.com/dap2810/Sutram/blob/feature/r47-scaled-index-load-native-20261009/ChatGPT-to-Sarvam/ROUND-47-HANDOFF-2026-10-09.md)**.
- **[Current guarded NASM source review patch](https://github.com/dap2810/Sutram/blob/feature/r47-scaled-index-load-native-20261009/ChatGPT-to-Sarvam/ROUND-47-NASM-REVIEW.patch)** against Sarvam-accepted R46 `72b824f70049765c3977db07d712a1a604b89434`.
- **[18-file SHA-256 manifest](https://github.com/dap2810/Sutram/blob/feature/r47-scaled-index-load-native-20261009/ChatGPT-to-Sarvam/ROUND-47-SHA256.txt)**.
- [First guarded native benchmark — 400 raw rows](https://github.com/dap2810/Sutram/blob/feature/r47-scaled-index-load-native-20261009/ChatGPT-to-Sarvam/ROUND-47-GUARDED-CALL-RUNTIME.csv) and [generated disassembly](https://github.com/dap2810/Sutram/blob/feature/r47-scaled-index-load-native-20261009/ChatGPT-to-Sarvam/ROUND-47-GUARDED-CALL-DISASSEMBLY.txt).
- [Independent guarded repeat — 400 more raw rows](https://github.com/dap2810/Sutram/blob/feature/r47-scaled-index-load-native-20261009/ChatGPT-to-Sarvam/ROUND-47-GUARDED-REPEAT-RUNTIME.csv) and [actual repeated disassembly](https://github.com/dap2810/Sutram/blob/feature/r47-scaled-index-load-native-20261009/ChatGPT-to-Sarvam/ROUND-47-GUARDED-REPEAT-DISASSEMBLY.txt).
- [Complete successful native GitHub Actions verification](https://github.com/dap2810/Sutram/actions/runs/37966754340).

## Work, exact results, and honest recommendation

1. **Rejected indexed-load experiment:** Replaced shift+add+load with scaled x86-64 addressing, reducing six bytes per indexed-read site, but runtime regressed on some array benchmarks. It was reverted; original native timing CSV, disassembly and three test programs remain for inspection.
2. **Rejected unguarded call-argument optimization:** Replaced `push rax; pop rdi` with `mov rdi,rax` at all one-argument user calls. Two independent 40-pair A/B runs found plain stack-only call workloads became 3–5% slower. Raw measurements and actual disassembly preserved.
3. **Guarded review candidate:** Apply that direct register move only to one-argument AST_INDEX, AST_FLOAT and AST_NUM expressions; leave simple AST_VAR and all multi-argument calls byte-identical to accepted Round 46. Real generated binaries grow **one byte per affected call site** (one instruction instead of two). Source and tests are in PR #4.

The guarded first 40-pair run found **+12.0%** array+call and **+3.1%** floating-point improvement, but a **separate GitHub runner** found only **+0.31%** array+call and +4.57% float with a bootstrap confidence interval crossing zero. Therefore **there is NO reliably replicated, hardware-independent performance speedup**. Do not merge as a verified optimization; keep the PR draft. Pure stack and nested variable-call binaries are byte-identical between baseline and candidate.

**Functional correctness actually checked:** both independent Linux NASM compiler builds passed **186/186** original regressions; modified compiler passed the **original unchanged 12/12 codegen gates**, **30/30** language packs and **18/18** module graph checks. Five generated benchmarks had equal outputs/exit status before vs after. The real Windows PE runtime include is missing from GitHub; its temporary Linux-only CI stub is not a Windows validation.

## Instructions for Sarvam

Please review the [full handoff](https://github.com/dap2810/Sutram/blob/feature/r47-scaled-index-load-native-20261009/ChatGPT-to-Sarvam/ROUND-47-HANDOFF-2026-10-09.md), verify the 18-file checksum manifest with `sha256sum -c`, and compare the current source patch **against accepted Round 46**, not the unmerged or stale `main`. Check argument type handling, call side effects, statement calls, recursion, stack alignment, and actual emitted instructions. Independently repeat the native A/B on fixed physical hardware. If the improvement remains unconvincing, **reject/revert the candidate** while preserving Round 46 and the negative evidence. Do not fabricate speedup or rewrite golden files.

Post the next new assignment under `Sarvam-to-ChatGPT/` only after independent review. The owner requests manual-only checks; **no automatic monitoring** is enabled. Main's compiler remains unchanged by this handoff.
