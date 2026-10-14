# Sutram R59 — safe pre-emission no-op elimination (verified partial)

**Status:** Linux native built/tested and reviewable; no source merged. Baseline `e5dc8ac7571cfd4d2c10dfc51fce13f709e82443` (Sarvam accepted R58). Compiler still one pure NASM x86-64 source, preserves existing emitted native ELF/PE semantics, all frozen accepted goldens unmodified.

## What actually changed

At the start of `gen_stmt .gs_assign`, `r59_skip_existing_self_assign` identifies **existing named scalar assignments whose RHS is exactly the identical AST_VAR** (`x=x`), with no extra operation, call, indexing or implicit allocation. It checks equal identifiers with `strcmp` and an existing local declaration in `var_table` or an existing module global, **without calling `lookup_var`**, because that helper auto-allocates unknown locals. The optimization returns before any runtime bytes, branch displacements or relocation patch records are emitted. It eliminates the redundant original load *and* its store; float bit patterns and global memory are preserved because no evaluation is suppressed except a pure variable self-read.

It cannot remove other adjacent store-then-reload pairs yet. The compiler's existing `emit_reg_move_reg` already checks identical source and destination logical register IDs; R59 does not double-count that pre-existing same-register MOV prevention. **No general cancelling runtime push/pop pair has been added.** The compiler emits mixed instructions via `emit_byte` with branch offsets recorded in the stream, so an uninformed post-emission byte-stripper would corrupt code or embedded immediate data. This handoff intentionally reports R59 as a **verified partial**, not complete all-pattern peephole optimization. This leaves a follow-on safe emission-site design for independent Sarvam review.

## Native execution / genuine before-after disassembly

Same Linux Ubuntu-24.04 GitHub runner builds both old main compiler (pinned Git SHA) and R59 compiler. `tools/r59_native_acceptance.py` compiles and **executes** six fixtures under each; stdout and exits are compared with known literal expected outputs. A native NASM `ndisasm` decode from ELF executable entry offsets reports instruction-count changes (may include static bytes after code; used only for paired exact same-image comparisons). The purposefully added fixtures prove:

| fixture | old instruction count | R59 instruction count | reduction | runtime output |
|---|---:|---:|---:|---|
| `stack_self_10m.sm` | 76 | 74 | **-2** | `123\n` |
| `global_self_10m.sm` | 74 | 72 | **-2** | `213\n` |
| `self_assign_cases.sm` | 191 | 187 | **-4** | `9\n17\n33\n44\n` |

All three codepath controls `arithmetic_10m.sm`, `control_10m.sm` and `foldable_10m.sm` produced **byte-identical old/new binaries**. Therefore any timing differences for these are not a real R59 optimization.

### Timing variability (all best-of-3 and medians are actual measurements)

Green run https://github.com/dap2810/Sutram/actions/runs/38558185471:
- stack-self 10M: best 7.956179→6.894630 ms (**1.154×**); median 8.762870→7.946355 ms (**1.103×**).
- global-self 10M: best 6.897283→5.051117 ms (**1.365×**); median 7.185562→5.069644 ms (**1.417×**).
- arithmetic control median 5.738269→5.682916 ms; simple loop 4.108053→4.112139 ms.

Separate full-green run https://github.com/dap2810/Sutram/actions/runs/38558457846:
- stack-self: best 21.814991→22.510345 ms (**0.969×**, regressed), median 21.820918→23.116305 ms (**0.944×**, regressed).
- global-self: best 16.312173→6.835148 ms (**2.387×**), median 17.238770→7.805320 ms (**2.209×**).
- arithmetic control median ratio 0.999× and simple-loop ratio 0.998× (unchanged machine code).

**The stack case timing regressed in a different runner run despite removing instructions; do not hide or extrapolate guaranteed speedups.** The reliable result is the exact native stdout equivalence and instruction-count reduction. Timing is workload- and runner-sensitive.

## Regression and freezes

In repeated green Linux native workflows, pass **186 original expected tests + 3 additional examples**, **12 codegen**, **30 language packs**, **18 module-graph**, **161/161 library proofs**, **49/49 property proofs**, R57 stdout and R56 globals/R55 forwards, historic static/semantic tests. R57 original **6/6 frozen ELF hashes** and R58 original **8/8 frozen ELF hashes** remain intact. A new independent `tests/r59_check/CODEGEN-BASELINE.txt` records three observed ELF SHA-256 hashes and `tools/r59_codegen_baseline.py` regenerates/verifies **3/3**; no earlier manifest rewritten.

## Reproduce

```bash
git show e5dc8ac7571cfd4d2c10dfc51fce13f709e82443:src/sutram_compiler.asm >/tmp/r59-before.asm
nasm -f elf64 -I. /tmp/r59-before.asm -o /tmp/r59-before.o
ld -o r59_before /tmp/r59-before.o
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r59-new.o
ld -o r48_after /tmp/r59-new.o
python3 tools/r59_native_acceptance.py
python3 tools/r59_codegen_baseline.py
python3 tools/r58_codegen_baseline.py
# Complete pre-R57, R55/R56 and modern tests:
# .github/workflows/r59-native.yml
```

No Windows-native binary execution is claimed in R59; Windows runtime validation is tracked separately in Round 60. Do not merge source without Sarvam independent acceptance.
