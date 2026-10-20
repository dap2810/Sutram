# R15-01 — WS1: a compiler fuzzer

**Branch `claude/round-15`, draft PR #52.** Base: main `9bff1dd6` (v216). **No
compiler, library or golden file is changed.** Environment for every check: **Linux**, unless a line says
otherwise.

## The result in one paragraph

**Seed 15, 20,000 random valid programs: all 20,000 print exactly what the reference computes** (387,913
output lines compared, `evidence-r15/valid/run-seed15-20000.txt`). **Before that run, I found three
defects and one disagreement with the documentation.** The fuzzer found D2, D3 and D4 in its first 500
programs (seed 1). I found D1 by hand, while checking the reference rules against the compiler. They are
below, each as a file. The 20,000 run is clean only because the generator steers around those four. With them allowed
back in, main's compiler crashes on 9 of 300 programs (seed 2).

## The tools

| File | What it does |
|---|---|
| `tools/fuzz_valid.py` | Generates a random **valid** program, computes the output it must print with a reference interpreter in Python, compiles it with the real compiler, runs it, compares line by line. Deterministic from `--seed`. Every failure is saved as `.sm`, `.expected`, `.got`. |
| `tools/fuzz_reduce.py` | Shrinks a failing program to a small one that fails **the same way**. It works on the program's structure, so every step is still a valid program, and the reference still gives the expected output. A 25 KB program came down to 200 bytes in under a second. |

```sh
python3 -B tools/fuzz_valid.py --seed 15 --count 20000          # the run above (about 25 minutes, one core)
python3 -B tools/fuzz_valid.py --seed 15 --show 123             # program 123 and its expected output
python3 -B tools/fuzz_reduce.py --seed 1 --program 17           # shrink a counterexample
```

## The F1 shape, generated on purpose

**Every called function declares its locals up front, and the count is drawn on purpose around the
boundaries:** 19–21, 26–28, 31–34 and 37–39 for 55% of functions, 20–40 for another 25%, up to 64 for 10%.
Nested blocks add more. **The caller always keeps values live across the call and prints every one of them
afterwards,** because F1 showed up as a caller's variable changed by the callee.

**In the 20,000 run:**

| Variables in a called function | Functions generated |
|---|---|
| any | 54,763 |
| 20 or more | 51,088 |
| 34 or more (where F1 reached the return address) | 38,536 |
| exactly 26 / 27 | 837 / 872 |
| exactly 31 / 32 | 1,296 / 1,317 |
| exactly 38 | 1,740 |
| the most | 107 |

**Around that shape, each program mixes:**

- 1–5 functions, 0–6 parameters, calls between them, and calls inside call arguments
- bounded recursion
- `yadi`/`anya` nested up to four deep, each block with its own locals
- `chakra` up and down, `yavat`, `kuru … yavat`, with `krama` and `agrim`
- `mala` arrays, `rachana` records, `kosh` with push and pop
- module globals
- the ternary; `+=`, `-=`, `*=`, `/=`, `%=`
- every integer operator, with literals at the 64-bit edges

**Half of the programs are printed with every operation in parentheses,** and half with only the parentheses
the precedence needs. That is how D4 was found.

**Can it see F1? Yes.** Against the compiler from before the F1 fix (`git show 6bb2ce72^:sutram_compiler`,
v182 by its banner), **294 of 300 programs fail**: wrong output, a crash, or a hang. Against main's: 0 of
20,000.

## What it found

| # | What | Kind | File |
|---|---|---|---|
| **D1** | **Unary `!` is ignored.** The lexer skips a `!` that is not followed by `=`. So `!0` is `0`, `!5` is `5`, and `yadi (!z)` never runs its block when `z` is 0. The documentation lists `!` as logical not (LANGUAGE-REFERENCE §3, level 11). **No program in `lib/`, `examples/` or `tests/stdlib/` uses it. User code that does gets silently wrong answers.** | silent wrong answer | `evidence-r15/valid/D1-unary-not-ignored.sm` |
| **D2** | **The compiler crashes (SIGSEGV) on a valid program:** a `krama` or `agrim` anywhere in a `chakra` or `yavat` that is a direct statement of an `anya` block. | compiler crash | `D2-else-loop-break-compiler-crash.sm` |
| **D3** | **The compiler crashes on `x = x` as a direct statement of an `anya` block.** | compiler crash | `D3-else-self-assign-compiler-crash.sm` |
| **D4** | **The precedence is not the documented one.** `& ^ \|` bind *tighter* than every comparison, and all six comparisons share one level. The documented table (LANGUAGE-REFERENCE §3) is C's. Measured pair by pair: **28 of the 246 operator pairs tested parse differently from the table** (16 operators; `>` and `>=` not in the set). | documentation and compiler disagree | `D4-precedence-bitwise-vs-comparison.sm` |

### D2 and D3: one cause, a one-line fix

**In `gen_stmt`'s `yadi … anya` path** (`src/sutram_compiler.asm`, line 12846 on main), the jump over the
`anya` block is patched through `rcx`. **`rcx` was loaded before the `anya` body was generated, and
`gen_block` does not preserve it.**

- **Usually `rcx` happens to still hold `code_buf`.**
- **But two code paths leave it changed:**
  - **the R59 self-assignment check** leaves a table offset in it (D3)
  - **a loop's `krama`/`agrim` patching** leaves something else (D2)
- **Then the patch writes to a wild address,** and the compiler crashes.

**The fix reloads `rcx`, as the `no anya` path ten lines below already does.**
It is `evidence-r15/valid/D2-D3-fix.diff`: one added line, `lea rcx, [rel code_buf]`.

**Checked with a scratch build of that fix (Linux):**

| Check | main | with the fix |
|---|---|---|
| D2, D3 and the five reduced fuzzer programs | compiler SIGSEGV | compile; output as expected |
| seed 2, 300 programs, `--include-known` | **9 compiler crashes** | **0 failures** |
| `tests/run_tests.py` | PASS=205, NO-EXPECTATION=4 | the same |
| `tools/proof_lib.py` | 217 / 217 | the same |

**I did not put the fix on the branch.** It changes the compiler, so the pins, the binaries and the
installer would all have to follow. **Say if you want it, and I will land it with all of that in the next
round.**

**One risk I cannot rule out:** if the stale `rcx` ever pointed at writable compiler memory, the patch would
land there silently. The `anya` jump would then stay unpatched, and both branches would run. **The fuzzer
never saw that in 20,000 programs,** but I cannot say it never happens.

### D4: which is right is a decision, not a bug report

**v32's CHANGELOG says the bitwise operators were deliberately put "between comparisons and shifts".** That
is what the compiler does. But that entry calls it "C ordering", and it is not: in C, they are looser than the
comparisons.

**`docs/SPECIFICATION.md` §3 already declines to certify the table.**

**What the owner should choose:**

- **Keep the compiler's order.**
  - It is the friendlier one: `x & 1 == 0` means `(x & 1) == 0`, as people expect.
  - Then fix the table in LANGUAGE-REFERENCE, the books and SPECIFICATION.
  - I can add the 246-pair check as a test, so it cannot drift again.
- **Or make the compiler match the table.**
  - That changes the meaning of existing programs that mix the two without parentheses.
  - **I have not searched how many do.**

**The fuzzer prints with the compiler's order by default** (`--precedence measured`). `--precedence
documented` reproduces D4.

## The four are steered around, not hidden

**By default the generator does not produce `!`, nor the two D2/D3 shapes.** That is so it can find other
defects, and the 20,000 run is clean only on that basis.

| Switch | What it turns back on |
|---|---|
| `--fuzz-not` | `!` (D1) |
| `--include-known` | the D2/D3 shapes |
| `--precedence documented` | D4 |

## What the fuzzer does not cover

**A clean run says nothing about these:**

- **`dasham` (floats).** Not generated.
- **Strings, and arrays passed to functions.** Not generated.
- **Functions with side effects.** Functions are pure on purpose, so the order in which operands are
  evaluated cannot change the output. **So evaluation order is not tested.**
- **Division by zero, shifts past 63, and out-of-bounds indexes.** Never generated: every divisor is
  `(e & 15) + 1`, every shift count is `& 63`, and every index is masked.
- **`yoj` modules, language packs, Devanagari keywords.** Not generated.
- **Windows (`win/sutram.exe`).** NOT-RUN. The generator would need Wine to run the output; it is a switch away,
  and I have not done it.

## Checks

| Check | Environment | Result |
|---|---|---|
| `fuzz_valid.py --seed 15 --count 20000`, main's compiler | Linux | **PASS: 20,000 / 20,000** |
| the same tool against the pre-F1 compiler, 300 programs | Linux | 294 FAIL (it can see F1) |
| `--include-known`, seed 2, 300 programs: main / fix | Linux | 9 compiler crashes / 0 |
| D1–D4 files, main's compiler | Linux | as described in each file's header |
| Windows | — | NOT-RUN |
