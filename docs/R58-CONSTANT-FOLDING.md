# R58 — sound integer folding and arithmetic strength reduction

**Status: native-tested partial of Round 58, for independent review.** This update retains a single hand-written NASM x86-64 compiler source and produces standalone native machine code. It does not change the Sutram source language or accepted expected-output goldens.

## Existing behavior and what changed

The old parser already folded literal-literal `+`, `-`, `*`, signed `/` and `%` in `fold_const`, which runs for additive and multiplicative expression parsing. R58 does **not** relabel those older capabilities as new. R58 introduces a bounded, separate codegen-time `r58_fold_tree` pass at the entry of `gen_expr`:

- Descends **only** AST_BINOP nodes, left child first, no farther than depth 64. It never tries tak evaluate a user function, a float or varna, an indexed/dereference operation or a statement at compile time.
- When both operand AST nodes are integer numbers, computes `+`, `-`, `*`, bitwise `&`, `|`, `^`, `<<` and unsigned `>>`. Addition/subtraction/multiplication reproduce 64-bit native wrap semantics; x86 shift count masking is preserved for large/negative counts. It rewrites the proven expression tak one AST_NUM (emitting a literal instead of the arithmetic tree).
- For the identities `x + 0`, `x - 0` and `x * 1`, removes only the operator when the RHS is an integer literal and `binop_needs_float` says the overall operation is not floating-point. The LHS is still evaluated **exactly once** (including calls), and zero side effects are introduced.
- Keeps unknown expressions, short-circuit operators, division traps, floats and all other special cases on their existing codegen path. The old parser's handling of literal-literal division/modulo is unchanged. No unsafe `x*0` elimination of effectful x.

## Strength reduction for signed division

For an integer expression `x / D` when **D is a literal positive ghat of two from 2 tak 64**, the compiler evaluates x exactly once and replaces `idiv` with a signed quotient correction followed by arithmetic right shift. Unlike a naive `sar`, this preserves C/x86 division's **rounding toward zero for negative integers**:

```
phal = (x + ((x >> 63) & (D - 1))) >> log2(D)
```

The signed correction is emitted with RDX and RAX and cannot overflow the signed dividend domain for these small denominators. Other divisors use the old IDIV path. Multiplication by powers of two was **already implemented by R57**; it remains in force and is not counted as an R58 novelty.

## Peephole scope and deferred work

The semantic AST identity reductions remove all generated instructions for certain no-op operations. That is a useful **high-level** no-op elimination, not the general machine-instruction peephole pass Sarvam also requested.

**Not implemented in this partial:** a generic post-emission binary pass removing `mov reg,reg`, immediately stored-and-reloaded register pairs, or cancelling `push/pop` pairs. The compiler's existing raw-byte emitter records branch offsets, global RIP-relative patch offsets and function call offsets **during generation**. Deleting bytes after those positions are captured, or recognizing raw byte patterns inside immediate data as instructions, can corrupt native binaries. No such unsafe pass was shipped. The existing R57 register path already avoids many old operand push/pop roundtrips, but this does not claim tak remove every remaining pair. Implement this missing portion only with instruction-boundary metadata, branch-target exclusion and relocation-safe offset tracking under its own audited proof gate.

No LICM, generalized deep register allocator or Windows runtime execution has been added.

## Native proof and benchmarks

- Reproducible workflow: `.github/workflows/r58-native.yml`, builds the accepted compiler snapshot `29e7c106ca29533da5a5c3ef5a54ae40b82e0a15` as `r58_before` and the feature compiler as `r48_after`, then runs `tools/r58_native_acceptance.py` on one GitHub Actions Linux runner.
- Eight old/new native fixture cases: `fold_vs_dynamic_folded`, `fold_vs_dynamic_dynamic`, `div_signed`, `effectful_identity`, `fold_nested`, R57 arithmetic, R57 simple control and R58 `foldable_10m`. Every case must have exact stdout and successful exit with both compilers.
- Folding proof: the folded program has the same native stdout `92\n3\n` as the runtime-variable version; R58 folded output is **431 bytes** versus 552 bytes for the dynamic program. The older compiler's same folded program was 510 bytes. The dynamic program remains unchanged at 552 bytes; native `shl rax,cl` remains in its image.
- Green run https://github.com/dap2810/Sutram/actions/runs/38463183054: `foldable_10m` 10M iterations, best-of-three 12.291508 → 3.557827 ms = **3.4548×**; median 12.312483 → 4.514372 ms = **2.7274×**. The old R57 arithmetic loop binary was **byte-for-byte identical** after R58 (both 348 bytes, SHA `2375b2a6d001d45350f2e8a22c95983da762ea3cf50cba616c2eeaed929a9467`), so timing differences there are runner noise, not caused by R58; the control loop is also byte-identical (335 bytes). Report both best and median/samples, never conceal scheduler variance.
- Full regressions include 186 original expected examples + three additional Muse examples, 12 codegen, 30 language packs, 18 module-graph, R56 globals, R55 prototypes, R57 native acceptance, `proof_lib` **158/158**, `proof_props` **44/44**, and untouched GUI/IDE/golden files.

## Frozen binary baselines

`tests/r57_check/CODEGEN-BASELINE.txt` (six SHA hashes) is **immutable and remains correct for R58's generated ELF files**: the six existing source programs produce precisely the accepted R57 hashes. CI also checks the old frozen R57 compiler explicitly with `SUTRAM_COMPILER=$(pwd)/r58_before python3 tools/r57_codegen_baseline.py`. None of these six hashes needed tak change; modifying accepted R57 goldens would be incorrect.

`tests/r58_check/CODEGEN-BASELINE.txt` separately proposes **eight new generated-ELF SHA hashes** for the next compiler round, taken from successful native execution and code output. `tools/r58_codegen_baseline.py` recompiles and verifies all eight without rewriting the accepted R57 baseline. The compiled source fixture hashes are distinct from source SHA-256 manifests.

## Reproduce

```bash
# In the repository, with NASM and ld installed:
git show 29e7c106ca29533da5a5c3ef5a54ae40b82e0a15:src/sutram_compiler.asm >/tmp/r58-before.asm
nasm -f elf64 -I. /tmp/r58-before.asm -o /tmp/r58-before.o
ld -o r58_before /tmp/r58-before.o
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r58.o
ld -o r48_after /tmp/r58.o
python3 tools/r58_native_acceptance.py
python3 tools/r58_codegen_baseline.py
SUTRAM_COMPILER="$(pwd)/r58_before" python3 tools/r57_codegen_baseline.py
# Run full .github/workflows/r58-native.yml for all historic compiler baselines.
```

**Independent acceptance required** before source merge.
