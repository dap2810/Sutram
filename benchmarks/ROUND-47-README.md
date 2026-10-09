# Sutram Round 47 — repeatable native generated-code performance

The handwritten NASM compiler has one final **guarded single-argument call**
optimization on the feature branch. Development-only benchmark harness
`tools/r47_runtime_benchmark.py` is a close adaptation of the already accepted
Round 46 native runtime harness (same CPU-pinned process execution, 40
interleaved pairs, 6 discarded warm-ups, seeded 2,000-resample bootstrap,
binary/output SHA-256 checks and actual ndisasm evidence).

## The experiments and why the final choice differs

**Experiment A (REJECTED):** `a[index]` was lowered from four native
instructions (shift index, pop base, add, load) to two (pop base, scaled
memory load). This saved 6 bytes per site and preserved all native
results, but measured runtime on five array workloads was mixed, with
a repeatable array+call regression. Retained evidence:
`ChatGPT-to-Sarvam/ROUND-47-RAW-NATIVE-RUNTIME.csv` and
`ROUND-47-DISASSEMBLY.txt`. **This experiment was reverted from the
production source**. Its three synthetic input programs remain under
`benchmarks/r47_pankti_reads.sm`, `r47_kosh_reads.sm`,
`r47_array_mix.sm` for future performance exploration.

**Experiment B (REJECTED UNGUARDED):** a user-function call with exactly
one argument emitted a `push rax; pop rdi` stack round-trip, even
when the typed argument was already computed in RAX. Replacing that
round-trip with `mov rdi,rax` improved array and float calls but made
pure stack-only calls 3–5% slower on two A/B runs. Evidence:
`ChatGPT-to-Sarvam/ROUND-47-CALL-RUNTIME-RAW.csv` and
`ROUND-47-CALL-DISASSEMBLY.txt`.

**Experiment C (CURRENT REVIEW CANDIDATE):** restrict the direct
`mov rdi,rax` call transfer to one-argument calls where the argument
AST is `AST_INDEX`, `AST_FLOAT` or `AST_NUM`. Plain `AST_VAR` and
all multi-argument calls retain the R46 stack transfer. This retains
the R46 binary unchanged for pure stack variable-call benchmarks and
improves some indexing/float cases. Evidence:
`ChatGPT-to-Sarvam/ROUND-47-GUARDED-CALL-RUNTIME.csv` and
`ROUND-47-GUARDED-CALL-DISASSEMBLY.txt`.

## Current five runtime inputs

The reused R47 runner tests:
- `benchmarks/r46_hotcall_stack.sm`
- `benchmarks/r46_hotcall_nested.sm`
- `benchmarks/r46_hotcall_float.sm`
- `benchmarks/r46_hotcall_array.sm`
- `examples/126_numeric_pipeline.sm`

These are real generated ELF executables, measured after compilation.
The before compiler is the accepted Round 46 SHA
`72b824f70049765c3977db07d712a1a604b89434`, not main's
older Round 44 compiler. Generated stdout and process return codes
must agree exactly for every iteration or the harness aborts.

## Reproduce

```sh
python3 tools/r47_runtime_benchmark.py --before ./r47_before \
  --after ./r47_after --runs 40 --warmup 6 \
  --csv r47_runtime_raw.csv --disasm r47_machine_disassembly.txt
```

Build commands, ELF-only missing Windows runtime limitation and
full acceptance checks are in `.github/workflows/r47-runtime.yml`.

**Unchanged original goldens:** The 186 regression suite and existing
12 codegen shape gates must pass without re-recording. A deliberately
failed earlier gate led to restoring the original gates after adding
a guard for the `AST_VAR` path; see the GitHub run history. Do not
claim uniform speedup or independent cross-hardware confirmation.
