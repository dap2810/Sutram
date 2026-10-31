# R17-01 — WS1: D1, D2, D3 and D4 are fixed

**Branch `claude/round-17`, draft PR #54.** Base: main `75b4d77f` (v229). Every file was read from that
commit before it was changed. Environment for every check: **Linux**, unless a line says Wine or Windows.

## The result in one paragraph

**All four are fixed in `src/sutram_compiler.asm`, each with a file that fails on v226's compiler and passes
now** (examples 238–241, with goldens). **Then seed 15's 20,000 programs were re-run with every workaround
removed from the generator: 20,000 of 20,000 agree** (388,616 lines compared). Against v226's compiler the
same generator fails **178 of 300** (seed 2), because it now writes `!`, the two `anya` shapes and the
documented precedence freely.

## Each fix

| | What was wrong | The fix | The file (fails on v226, passes now) |
|---|---|---|---|
| **D1** | The lexer skipped a `!` that was not followed by `=`, so `!x` meant `x`. | The lexer emits `!` as an operator. `parse_primary` builds `!e` as `(e == 0)`, the same node a comparison uses, so it prints 0 or 1; a literal is folded. | `examples/238_r17_d1_unary_not.sm`: `1 1 0 1 111` |
| **D2, D3** | After the `anya` body was generated, the jump over it was patched through `rcx`, which `gen_block` had changed. | One line: reload `rcx` before the patch, as the no-`anya` path already did. | `239_r17_d2_anya_loop_krama.sm`: `0 10`; `240_r17_d3_anya_self_assign.sm`: `0` |
| **D4** | `& ^ \|` bound tighter than every comparison, and all six comparisons shared a level. | The parser chain is now the documented one: `\|\|` → `&&` → `\|` → `^` → `&` → `== !=` → `< > <= >=` → `<< >>` → `+ -` → `* / %` → unary. `parse_cmp` became `parse_eq` and `parse_rel`. | `241_r17_d4_precedence.sm`: `1 0 1 0` |

**Also found and fixed on the way (by the robustness fuzzer, seed 16):** an empty `guna (x) { }` compiled to
a null statement and crashed the compiler in code generation. It is now an empty block
(`242_r17_empty_guna.sm`: `7`).

## D4: the decision I took, and why

**The compiler now follows the documentation, not the other way round.** The reasons:

1. **The table in `LANGUAGE-REFERENCE.md` §3 is the contract,** and the books teach it. v32's CHANGELOG entry
   says it placed the bitwise operators "between comparisons and shifts" as "C ordering"; it is not C's,
   and the table says C's.
2. **No program in the tree depended on the old order.** I scanned every `.sm`, `.smlib`, book and document
   for an expression that mixes a comparison with `& ^ |` at one parenthesis level: **none**. So no
   golden, proof or example moved.
3. **Every reader of a C-family language expects this order.**

**The cost, which the owner should know:** `x & 1 == 0` now means `x & (1 == 0)`, as in C, not `(x & 1) == 0`.
A user program written against the old behaviour without parentheses changes meaning. **There is no such
program in the tree.**

**It cannot drift again:** `tools/check_precedence.py` writes, for every ordered pair of the 18 binary
operators, one expression whose value differs between the two parses, and checks the compiler against the
table. **314 pairs, 0 disagree.** It is a gate now ("operator precedence"). On v226's compiler it reports
44 disagreements.

## The fuzzer without its workarounds

**Removed from `tools/fuzz_valid.py`:** `--fuzz-not`, `--include-known`, `--precedence`, and the generator
logic behind them (it no longer avoids `!`, nor `krama`/`agrim`/`x = x` directly in an `anya` block, and it
prints with the documented precedence). `fuzz_reduce.py` and `fuzz_robust.py` follow.

| Run | Compiler | Result |
|---|---|---|
| seed 15, 20,000 programs | this branch, before the version-string change | **20,000 agree, 0 fail;** 388,616 lines |
| seed 15, 20,000 programs | this branch, the committed compiler (`4d628b90…`) | **20,000 agree, 0 fail** (`evidence-r17/fuzz-valid-seed15-20000-final.txt`) |
| seed 2, 300 programs | this branch | 300 agree |
| seed 2, 300 programs | v226 (main) | **178 fail** |

The distribution of variables in called functions is in the log, as before (51,000 of 55,000 functions have
20 or more).

## Checks

| Check | Environment | Result |
|---|---|---|
| suite · library proofs · property proofs · packs · pack messages | Linux | **PASS=210** NO-EXPECTATION=4 · 217/217 · 86/86 · 33/33 · OK |
| `check_precedence.py` | Linux | 314 pairs, 0 disagree |
| `r69_build.py --check-only` · `r70_negative_corpus.py` · `tests/r70` | Linux | SOURCE_PINS_CHECKED · PASS · OK |
| `tests/r66 r67 r68 r72 ci windows_accept r65_finish gui r83 sandesh` · translit · `r64_source_gate` | Linux | all OK · 24,761/0 · PASS |
| `tests/r69` (2), `tests/r71` (1) | Linux | FAIL, **the same on main** (open since R12) |
| `gates.sh` | Linux | 14 PASS / 1 FAIL (`test_x11_edscroll`, as on main since before R13) / 1 NOT-RUN |
| `win/sutram.exe`: `--version`, examples 238, 239, 241, 242, and R1 | Wine 9.0 | v229 · the goldens · the diagnostic |
| `cross_build_windows.py --check` · `Sutram-Setup.exe --self-test` | Linux · Wine 9.0 | REPRODUCED · exit 0 |
| Windows | — | **NOT-RUN** |

## What moved with the compiler

- **`--version` is v229** (the CHANGELOG's head; your gate allows a lag, not a lead).
- **Pins:** `tools/r69_build.py`, its lock, the R70 manifest, `docs/BUILDING.md`, `docs/reports/NEGATIVE-CORPUS.md`
  (compiler blob `d96aa571` → `5b144a70`; `src/r11_sandesh.inc` regenerated for the version).
- **Binaries:** `sutram_compiler`, `win/sutram.exe`, `sutram.exe`, `Sutram-Setup.exe` and its hash file.
  `sutram-ide-gui.exe` is byte-identical (the IDE's messages do not carry the version).
- **The three Linux binaries are 100755 again.** The R15 merge uploaded them one by one and lost it, as every
  merge before. **Please merge this branch with `git merge` or a cherry-pick.**
