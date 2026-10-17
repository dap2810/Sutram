# R57 — Bounded register-tree expression evaluator

**Status: verified partial implementation; independent Sarvam review needed.** One production compiler remains hand-written NASM emitting standalone native machine code.

## Register discipline

- RAX: expression phal, temporary register slot 0.
- R10: scratch slot 1. R11: scratch slot 2. These are never allocated tak named locals.
- RBX/R12–R15: existing local scalar homes, read-only in this new expression path.
- Module globals: R56 RIP-relative reads directly into selected scratch slots.

A preflight walk checks the *entire* integer expression tree before emitting anything. For supported +, -, *, &, |, ^ operators with scalar integer register/global operands or literals, evaluate the left subtree into its slot, right subtree into the next slot, then combine directly using a GPR instruction. Source operand order is preserved. ADD/SUB small nonnegative immediates (0–127) and MUL by powers of two (2–64) can update a register directly without another temporary.

**Deterministic spill/fallback rule:** when a fourth live temporary would be necessary, or an expression involves stack locals, calls, arbitrary pointer dereferences, indexed values, floating point, division/modulo, comparison, short-circuit logic or unsupported shapes, reject the optimization for the whole subtree and use the proven legacy stack evaluator. No partially emitted tree, side-effect reordering, new runtime or ABI change. This is not a complete general-purpose allocator; arbitrary-depth spilling and effectful expressions remain future work.

## Measured evidence

- Benchmark fixture `tests/r57_check/arithmetic_10m.sm`: 10 million iterations of `s = s + i*2`.
- Control `tests/r57_check/control_10m.sm`: 10 million iterations of `s = s + i`.
- Baseline compiler: main commit `3631070a47bacabe25e9e78359daceb178301510`. Both compilers build on the same Linux runner; executable timings are collected on one CPU, one warmup and best-of-three, with stdout verified.
- In successful run https://github.com/dap2810/Sutram/actions/runs/38433918127: arithmetic 5.734884 → 3.509541 ms (1.6341×); control 3.518624 → 3.528028 ms (0.9973×). Runtime varies between runs. Sarvam's earlier 35.27 ms versus 6.58 ms NASM proxy is a separate environment, not directly comparable.
- Native tests include nested arithmetic, large 64-bit literals, precedence, global reads with RIP displacement, recursion and fallback for effectful function calls.
- R46 native reference stdout is compared exactly; **binary byte identity is expected tak change** in the expression-heavy programs. R48's old byte-equality gate is therefore deliberately excluded while other correctness diagnostics run.
- Complete workflow also runs R55/R56 acceptance, 186 original expected plus three Muse examples, 12 codegen gates, 30 packs, 18 graph tests, `proof_lib`, `proof_props`, and unchanged GUI/goldens.

## New proposed frozen codegen baseline

The six independent standalone program hashes in `tests/r57_check/CODEGEN-BASELINE.txt` come from actual successful R57 generated binaries. `tools/r57_codegen_baseline.py` recompiles them and enforces exact SHA-256 equality. The frozen corpus covers arithmetic, unaffected simple loop, nested trees, legacy call fallback, wide numeric literals and global variables. R46 imported-library reference SHA hashes are recorded as snapshots rather than frozen, because evolving `lib/` files legitimately change their emitted code.

## Limits

No Windows native execution test; PE globals remain structurally tested. Unsafe pointer bounds remain caller-managed. LICM, constant folding and peephole optimization were not added. Further generalization tak floating-point and more live registers requires separate correctness and performance evidence.
