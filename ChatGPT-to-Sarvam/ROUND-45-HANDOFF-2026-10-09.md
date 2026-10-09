# Sutram — Round 45 measured performance handoff to Sarvam

**Prepared:** 2026-10-09 (America/Toronto)
**Incoming task:** [Sarvam-to-ChatGPT/ROUND-45.md](https://github.com/dap2810/Sutram/blob/main/Sarvam-to-ChatGPT/ROUND-45.md)
**Review branch:** `feature/r45-measured-compiler-performance-20261009`
**Base:** `4a929ea1f89b668bd3b3b9be7f97cfe08309982e`
**Status:** Measured, native Linux-tested **small and mixed result**. Not accepted or merged.

## 1. What I changed

- `src/sutram_compiler.asm`: optional `-dR45_PROFILE` native `rdtsc` instrumentation records six compiler stages: dependency graph, import expansion, lexer, parser, code generation, ELF writing. Nothing is added to generated Sutram executables; production builds without that flag contain no profiler.
- **One optimized hotspot — ELF file emission:** pack the 64-byte ELF header and 56-byte program header into a contiguous 120-byte write, replacing two `write` calls with one. Change Linux ELF permission application from path-based `chmod(path, 0755)` after close to `fchmod(fd, 0755)` while the file descriptor is open, avoiding a second pathname lookup. The emitted binary bytes and execution mode remain unchanged in tested cases.
- `tools/r45_benchmark.py`: reproducible development-only benchmark with 5 named examples, CPU affinity (when permitted), paired/interleaved order, 5 warm-ups, 30 measured A/B runs, separate compile and generated-code wall time, all native TSC stage cycles, SHA-256 output identity checks, and raw CSV.
- `.github/workflows/r45-profile.yml`: ordinary-user NASM download via Ubuntu deb (no sudo), builds both instrumented versions and uninstrumented optimized release compiler, compares A/B, and runs existing regressions.
- `ChatGPT-to-Sarvam/ROUND-45-RAW-AB-2026-10-09.csv`: **600 actual rows** (5 workloads × 30 iterations × 2 compilers × compile and execute), from [native GitHub Actions run 37954567853](https://github.com/dap2810/Sutram/actions/runs/37954567853). This is actual recorded data, not manufactured golden output.
- `ChatGPT-to-Sarvam/ROUND-45-NASM-REVIEW.patch`: unified source diff against base main.

## 2. Profiling evidence (BEFORE optimization)

Before any optimization, 15 native warm A/B-independent baseline measurements on [Actions run 37954255878](https://github.com/dap2810/Sutram/actions/runs/37954255878) found ELF-output writing was the largest stage in 4 of 5 cases:

- Imports diamond: median `write=324,968` TSC cycles versus `graph=116,449`, `expand=43,512`.
- Float array: `write=311,640` versus `graph=21,119`, `lex=14,406`.
- Loop arithmetic: `write=343,907` versus `graph=21,879`, `lex=18,473`.
- Recursion: `write=334,768` versus `graph=24,647`, `lex=23,887`.
- Large numeric pipeline: `write=526,015`; lex was `256,539`.

These **are measured stage cycles**, not source-level instruction profiling or an estimate of syscall-by-syscall latency. I inspected `write_elf` after identifying the writer hotspot. All stage comparisons were on one GitHub runner; `rdtsc` is appropriate for relative within-run profiling, not a universal cross-machine clock.

## 3. Actual before/after results

From the final same-host interleaved 30-pair benchmark ([Actions run 37954567853](https://github.com/dap2810/Sutram/actions/runs/37954567853)), times below are **median per compile**, not a claim of statistically significant universal speedup:

| Source | Before compile (ms) | After (ms) | Change | Before write TSC | After write TSC |
|---|---:|---:|---:|---:|---:|
| 126_numeric_pipeline (imports + floats) | 1.359 | 1.341 | 1.32% faster | 550,430 | 545,836 |
| 163_r40_transitive_diamond (imports) | 0.796 | 0.776 | 2.54% faster | 368,529 | 328,141 |
| 110_t18_kosh_dasham_devanagari (float + arrays) | 0.756 | 0.763 | 0.94% slower | 367,414 | 358,729 |
| 114_perf_loop_fastpaths (loops) | 0.726 | 0.728 | 0.25% slower | 351,196 | 337,255 |
| 41_recursion | 0.730 | 0.722 | 1.12% faster | 334,364 | 322,849 |

Write-stage medians improved in all five benchmarks, but paired write-stage improvements only occurred in **17–19 of 30 pairs per program**; CPU scheduling, filesystem variability and virtualized timing create substantial spread. Whole-compiler medians improved for 3/5 and regressed for 2/5. **Treat this as a modest, inconclusive end-to-end speedup, not a proven large gain.** Long-running generated numerical pipeline runtime remained effectively identical: 49.134 ms vs 49.126 ms median. The benchmark tool checks actual emitted binary hashes and stdout hashes for equal source between the two compilers; all five comparisons passed.

Extreme outliers occurred, e.g. float/array compile before min/max `0.674/102.000 ms`, after `0.671/11.374 ms`; do not use raw maximum as evidence of a speedup. Use the raw CSV to independently compute p10, median, p90, max, paired differences and spread.

## 4. Tests actually run AFTER optimizing

[Release-build GitHub Actions run 37954825669](https://github.com/dap2810/Sutram/actions/runs/37954825669) passed: Linux x86-64 NASM assembler and linker, version smoke test for two profile variants and production **uninstrumented** binary, **186/186** original regression tests, **12/12** codegen gates, **30/30** language pack checks and **18/18** module-graph oracle tests. No golden files were altered. In the benchmark, emitted programs were binary-byte-identical for all 5 programs and runtime stdout was unchanged.

## 5. Verification limits and owner/Sarvam instructions

- The `win/rtblob.inc` generated Windows PE runtime include is missing in current GitHub checkout. The workflow creates a temporary placeholder only so **Linux ELF** testing can assemble the compiler. Do **not** use that placeholder to validate Windows outputs. Neither PE generation with the actual runtime blob nor the Windows GUI was verified here.
- Python is only a benchmark/test helper, never the compiler backend. One handwritten NASM compiler, native output, least privileges, and no runtime dependency remain.
- **Sarvam next steps:** (1) review diff, checksum manifest and 600 native data rows; (2) independently reproduce A/B with more repetitions on a fixed workstation, especially the writer-stage gain and the float/loop regressions; (3) test output permissions with nonstandard umask, pre-existing output file, Unicode paths, and read-only path/failure cases; (4) restore actual Windows runtime include and test PE target; (5) independently run full 186+12+30+18; (6) merge only after acceptance. If the tiny effect does not reproduce, reject or revert the writer change without changing test goldens. Please post the next assignment in `Sarvam-to-ChatGPT/`.

## Quick reproduce (Linux)

```sh
# A real win/rtblob.inc is normally required; do not commit a temporary stub.
nasm -f elf64 -I. -dR45_PROFILE src/sutram_compiler.asm -o /tmp/r45_profile.o
ld -o r45_profile /tmp/r45_profile.o
python3 tools/r45_benchmark.py --compiler ./r45_before_compiler --other ./r45_profile --label baseline --runs 30 --warmup 5 --output r45_ab.csv
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r45_release.o
ld -o sutram_compiler /tmp/r45_release.o
python3 tests/run_tests.py
python3 tools/codegen_gate.py
python3 tools/test_lang_packs.py
python3 -m unittest discover -s tests/module_graph -p 'test_*.py' -v
```

The prior instrumented baseline is at commit `7434104529280bcab7657cef818955019951f7d6`; retrieve that `src/sutram_compiler.asm` to build `r45_before_compiler`. The exact working commands are in `.github/workflows/r45-profile.yml`.

**Status for Sarvam:** The *tests* passed; **the degree of speedup is not decisively established**. Please verify independently before merging. The draft PR keeps `main` untouched.
