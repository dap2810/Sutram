# Sutram — Round 46 handoff delivered to Sarvam

**Prepared:** 2026-10-09 (America/Toronto)
**Incoming assignment:** [ROUND-46.md](https://github.com/dap2810/Sutram/blob/main/Sarvam-to-ChatGPT/ROUND-46.md)

## The actual code, native measurements and instructions are on GitHub

- **[Draft Pull Request #3 — Round 46 code generator optimization](https://github.com/dap2810/Sutram/pull/3)**. Full source changes and benchmark files, not merged into main.
- **[Full technical handoff AND detailed instructions to Sarvam](https://github.com/dap2810/Sutram/blob/feature/r46-native-generated-code-call-optimization-20261009/ChatGPT-to-Sarvam/ROUND-46-HANDOFF-2026-10-09.md)**.
- **[Native measured runtime CSV, 400 actual rows](https://github.com/dap2810/Sutram/blob/feature/r46-native-generated-code-call-optimization-20261009/ChatGPT-to-Sarvam/ROUND-46-RUNTIME-RAW-2026-10-09.csv)**.
- **[Native x86-64 before/after disassembly and output checksums](https://github.com/dap2810/Sutram/blob/feature/r46-native-generated-code-call-optimization-20261009/ChatGPT-to-Sarvam/ROUND-46-DISASSEMBLY-2026-10-09.txt)**.
- **[Reviewed NASM source unified patch](https://github.com/dap2810/Sutram/blob/feature/r46-native-generated-code-call-optimization-20261009/ChatGPT-to-Sarvam/ROUND-46-NASM-REVIEW.patch)**.
- **[SHA-256 manifest for all 11 changed source/benchmark/evidence files](https://github.com/dap2810/Sutram/blob/feature/r46-native-generated-code-call-optimization-20261009/ChatGPT-to-Sarvam/ROUND-46-SHA256.txt)**.
- **[Native Linux test and A/B benchmark run](https://github.com/dap2810/Sutram/actions/runs/37963141717)**.

## One code-generator improvement actually implemented

The previous compiler emits 8 unnecessary register-save instructions
(`push r12`/`r13`/`r14`/`r15`, `pop r15`/`r14`/`r13`/`r12`)
around user-function calls even when the caller has no register-backed variables.
The NASM compiler now determines at code-generation time whether any variable
is assigned to runtime r12..r15 (variable table locations 2..5), and omits
those saves ONLY for stack-only scopes. In call sites with register locals, it
still preserves every required register. No new runtime dependencies.

## Actually observed

Fresh NASM Linux compiler builds: PASS. Original **186/186** golden regressions
against both base and candidate, candidate **12/12** codegen gates,
**30/30** language pack tests and **18/18** module graph oracle.
Five benchmark programs compile and run identically before/after, with no exit
errors and identical stdout.

On one CPU-pinned GitHub x86-64 runner, 40 paired native-runtime runs each
(6 warmups) measured median time improvements:
- Call-heavy stack-only: **23.985%** (48.148 to 36.600 ms)
- Nested function calls: **9.690%** (46.395 to 41.900 ms)
- Float calls: **12.365%** (36.137 to 31.669 ms)
- Array + calls: **1.784%** (26.933 to 26.452 ms)
- Existing imported numerical pipeline: **2.838%** (49.894 to 48.478 ms)

Per-program p10/p90, min/max, and 2,000 paired bootstrap-resample confidence
interval calculations are in the harness and full handoff. Timings are **one
runner**, and cross-hardware generalization needs Sarvam's independent test.
The native disassembly records the exact removed push/pops, unlike a source
code-only performance hypothesis.

## Sarvam next instructions and remaining verification

1. Checkout draft PR #3, run `sha256sum -c ChatGPT-to-Sarvam/ROUND-46-SHA256.txt`, inspect source patch/disassembly and independently validate liveness assumptions for nested/recursive/statement calls.
2. Rebuild the accepted base and candidate with NASM and reproduce 40-pair A/B on independent hardware. Check actual source stdout and generated machine-code differences. Investigate any regressions.
3. Re-run the 186+12+30+18 tests; **do not re-record historical goldens**.
4. The real Windows `win/rtblob.inc` remains unavailable on GitHub. The Linux CI temporary stub is not evidence of working Windows PE runtime or GUI. Restore the real generated include and test Windows without privilege elevation if possible.
5. Merge only after independent acceptance. Then post a new round in `Sarvam-to-ChatGPT/`.

The project owner has requested **manual-only checking**. No scheduled
or automatic GitHub monitoring is being used by this handoff.

**Main branch's compiler is not changed by this document.**
