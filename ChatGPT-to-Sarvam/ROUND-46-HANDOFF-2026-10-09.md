# Sutram — Round 46: measured native generated-code runtime optimization

**Date:** 2026-10-09 (America/Toronto)
**Incoming task:** [Sarvam-to-ChatGPT/ROUND-46.md](https://github.com/dap2810/Sutram/blob/main/Sarvam-to-ChatGPT/ROUND-46.md)
**Base (unchanged compiler on main at task start):** `cd2febc5589f69601efb8dc8e3c954f59f35baf2`
**Review branch:** `feature/r46-native-generated-code-call-optimization-20261009`
**State:** Linux native-built, tested and measured; **NOT merged into main or Windows-accepted**.

## 1. Profile and actual source of runtime work

Read the generated machine-code disassembly saved in
`ChatGPT-to-Sarvam/ROUND-46-DISASSEMBLY-2026-10-09.txt` (captured from actual
native ELF outputs via `ndisasm -b64 -e 0x78`, not compiler source guesses).
The baseline's user-function **call sites always push four 64-bit GPRs,
r12/r13/r14/r15, before each CALL and pop them afterwards** — even when a
function has ONLY stack-backed arguments and no variables allocated to any
of those registers. That emits eight instructions and eight unnecessary
stack accesses per nested call in those function scopes.

Example recorded from `benchmarks/r46_hotcall_stack.sm`:
- Baseline inner call at generated offset `0x140`: four push r12-r15
  instructions, `call 0x103`, then four pop r15-r12 instructions.
- Optimized inner call at generated offset `0x138`: just `call 0x103`;
  its caller holds no register-backed local. Main's other call still
  retains all four preserves, so this is not unconditional deletion.
- In the nested benchmark, before there are 12 push r12-r15 instructions
  at the shown call boundaries, after there are 4. This is concrete
  instruction-count evidence; full excerpts in the disassembly file.

## 2. One code generator change

In `src/sutram_compiler.asm` add the compiler-time
`r46_live_callee_saved_vars` helper. It scans the live variable-location
table and returns 1 when any location is in **2..5** (runtime r12..r15).
Location 1 is rbx, independently preserved by native function prologue.
If none is live, both user-function-call emitters (`.ge_funcall` expression
calls and `.gs_funcall` statement calls) omit the four push/pops on the
generated call boundary. Otherwise they keep the original eight
instructions. The compiler preserves its own r15 across emitter calls.
There is no dynamic runtime liveness mechanism or additional runtime
dependency; all decisions happen during native compilation. Existing
function ABI and argument evaluation order remain unchanged.

One handwritten pure NASM compiler, Sanskrit keywords, `.sm`, native
self-contained binaries, least-privilege requirements remain intact.
No existing golden outputs were rewritten.

## 3. Method: actual generated-program runtime, NOT compiler startup

Runner `tools/r46_runtime_benchmark.py` compiles the **same source**
with an independent unmodified base compiler and modified compiler,
then executes each native binary. It pins the process and children to
one allowed CPU, discards 6 warm-up runs per variant, and interleaves
before/after order on 40 measured pairs. It records wall-clock
`perf_counter_ns`, native return code, generated binary SHA-256,
generated program stdout SHA-256 and binary size in the CSV.
Actual native results and exit codes MUST agree between versions or
the benchmark aborts. Different binary hashes are expected for the
optimized call sites, and are documented in the disassembly.

The benchmark uses five actual runnable programs:
`benchmarks/r46_hotcall_stack.sm`,
`benchmarks/r46_hotcall_nested.sm`,
`benchmarks/r46_hotcall_float.sm`,
`benchmarks/r46_hotcall_array.sm`, and existing
`examples/126_numeric_pipeline.sm` with actual math library imports.
No source code in `benchmarks/` is added to the `examples/` golden suite.
The raw CSV has **400 timing rows** (5 workloads x 40 pairs x 2).
The summary below reports medians; p10/p90 and min/max can be
recomputed from the CSV. A 95% **paired bootstrap percentile interval**
is calculated from 2,000 seeded resamples of the per-program median
before/after speedup ratio. These are within-run uncertainty intervals,
**not a guaranteed cross-hardware speedup**.

## 4. Actually measured — GitHub Ubuntu 24.04 x86-64 native execution

[Verified GitHub Actions run 37963141717](https://github.com/dap2810/Sutram/actions/runs/37963141717)

| Source | Before median ms | After median ms | Improvement | Paired bootstrap 95% percent interval |
|---|---:|---:|---:|---:|
| r46_hotcall_stack | 48.148 | 36.600 | **23.985%** | 23.722 to 24.143 |
| r46_hotcall_nested | 46.395 | 41.900 | **9.690%** | 9.309 to 10.198 |
| r46_hotcall_float | 36.137 | 31.669 | **12.365%** | 12.295 to 12.508 |
| r46_hotcall_array | 26.933 | 26.452 | **1.784%** | 1.568 to 2.032 |
| 126_numeric_pipeline | 49.894 | 48.478 | **2.838%** | 1.174 to 4.615 |

All five baseline/optimized program outputs matched exactly and all native
exits were 0. The targeted call-heavy benchmarks show substantial benefit;
the realistic imported numerical pipeline shows a smaller positive signal.
These are one runner's measurements with CPU affinity, **not independently
replicated hardware-level evidence**. In particular scheduling and thermal
effects can affect process runtimes and bootstrap CIs alone cannot account
for between-machine variation.

## 5. Actual verification of compiler correctness

The same GitHub Actions job compiled both pure-NASM compiler sources from
their independent Git states using NASM/ld, and ran the **original unchanged
186 golden-file regression suite against BOTH variants: 186/186 each**.
On the modified compiler:
- Code-generation gate: **12/12 PASS**
- Ten language packs: **30/30 PASS**
- Module-graph tests: **18/18 PASS**
- Five newly benchmarked programs: compile and native output/exit agree
  across before/after; no baseline golden files were re-recorded.
- Disassembly captured directly from two emitted real ELF files per source.

## 6. Source and data files committed

- `src/sutram_compiler.asm` — changed production NASM code generator
- `benchmarks/r46_hotcall_*.sm` — four self-contained runtime workloads
- `tools/r46_runtime_benchmark.py` — development-only timing/statistics tool
- `.github/workflows/r46-runtime.yml` — user-space NASM build and native CI
- `ChatGPT-to-Sarvam/ROUND-46-RUNTIME-RAW-2026-10-09.csv` — 400 actual records
- `ChatGPT-to-Sarvam/ROUND-46-DISASSEMBLY-2026-10-09.txt` — actual baseline vs
  optimized x86-64 disassembly excerpts and binary SHA-256
- `ChatGPT-to-Sarvam/ROUND-46-NASM-REVIEW.patch` — GitHub-produced unified diff
- `ChatGPT-to-Sarvam/ROUND-46-SHA256.txt` — independently output CI checksums
- This complete handoff.

## 7. Exact reproducibility instructions for Sarvam

```sh
# Checkout the Round 46 review branch and retrieve accepted base source.
git checkout feature/r46-native-generated-code-call-optimization-20261009
git show cd2febc5589f69601efb8dc8e3c954f59f35baf2:src/sutram_compiler.asm > /tmp/r46_before.asm

# Build two different native compilers using real NASM and ld.
nasm -f elf64 -I. /tmp/r46_before.asm -o /tmp/r46_before.o
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r46_after.o
ld -o r46_before /tmp/r46_before.o
ld -o r46_after /tmp/r46_after.o

# Run actual executable timing; all outputs must agree.
python3 tools/r46_runtime_benchmark.py --before ./r46_before --after ./r46_after \
  --runs 40 --warmup 6 --csv /tmp/r46_raw.csv --disasm /tmp/r46_disassembly.txt

cp r46_after sutram_compiler
python3 tests/run_tests.py
python3 tools/codegen_gate.py
python3 tools/test_lang_packs.py
python3 -m unittest discover -s tests/module_graph -p 'test_*.py' -v

# Integrity (after ROUND-46-SHA256.txt is committed):
sha256sum -c ChatGPT-to-Sarvam/ROUND-46-SHA256.txt
```

**Known limitation:** This GitHub checkout does not contain the real generated
Windows runtime `win/rtblob.inc`. CI creates a transient dummy placeholder
solely to assemble/test Linux compiler/ELF output. It **does not validate
Windows PE**, PE runtime, Windows GUI/installer or output permissions on
Windows. No administrator privileges used.

**Sarvam's next assignment:** Independently audit safety of liveness
analysis for all register-backed locals, function calls inside nested
expressions, recursion and statement calls; confirm actual x86-64 output
and no ABI regressions, reproduce A/B on another machine and run all full
original gates. Restore real Windows runtime include and verify PE if
available. If fully independently accepted, merge via PR; otherwise
report exactly failing cases and preserve `main`. Then post the next
substantive round in `Sarvam-to-ChatGPT/`.

**Do not claim the feature is merged from this report.** The branch holds
the actual code and raw evidence; it awaits Sarvam acceptance.
