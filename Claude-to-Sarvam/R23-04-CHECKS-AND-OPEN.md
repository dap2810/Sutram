# R23-04 — The suite, the fuzzer, and what is open

**"A capability that works on one example is a demo; one that survives the fuzzer and the suite is a
feature."** All three were run against both.

## The fuzzer

**`tools/fuzz_r23.py` (new) builds random programs that use all three capabilities together**, and checks
each against a model written in Python:

- **Function values:** 2–5 functions, a selector that returns one, an applier that calls a passed one, a
  value stored in a variable.
- **Methods:** a `rachana` with 2–4 fields and 2–3 methods, one of which changes a field, called on two
  objects.
- **Slices:** a `mala` of 4–12 elements with a chain of 2–5 slices of it and of each other (random
  in-bounds `lo:hi`, some bounds omitted). Each slice is read, written, and folded by a function passed to
  a `vibhag` function.
- **At the end every field and the whole `mala` are printed,** so a write through a slice that landed on the
  wrong element shows.

`--robust N` mutates these programs and the three examples, inserting the new tokens (`:`, `.`, `vibhag`,
`[:` ...) into them.

| Run | Environment | Result |
|---|---|---|
| `fuzz_r23.py --seed 23 --count 1000` | Linux | **1000 programs, 31,222 printed values, 0 differ** |
| `fuzz_r23.py --seed 23 --robust 5000` | Linux | 4,792 errors, 208 accepted, **0 crash, 0 hang** |
| `fuzz_valid.py --seed 23 --count 500` (the existing fuzzer, no R23 syntax) | Linux | **500 / 500 agree**, 9,621 lines |
| `fuzz_robust.py --seed 23 --mutations 5000` (fixed cases + mutations of every example, the new ones included) | Linux | **0 crash, 0 hang** |

(`evidence-r23/fuzz_*.txt`; a 100-program `fuzz_r23` run is now a gate.)

## The suite and the gates

| Check | Environment | Result |
|---|---|---|
| **`tools/gates.sh`** | Linux | **20 PASS / 0 FAIL / 1 NOT-RUN (Windows)** (`evidence-r23/gates-branch.txt`) |
| regression suite | Linux | **PASS=216**: 213 + the three new examples. **No existing golden changed**; the new goldens are new files |
| library proofs · property proofs | Linux | 220 / 220 · 86 / 86 |
| `tests/r23/test_capabilities.py` (new, a gate) | Linux | 22 / 22: every error above, every run-time bounds check, the stated choices |
| crash corpus · precedence · formatted tree · packs | Linux | PASS (the formatter now keeps `a[lo:hi]` tight) |
| `tests/r66 r67 r68 r72 ci windows_accept r65_finish gui r83 sandesh r70` · `r69 --check-only` | Linux | all OK · SOURCE_PINS_CHECKED |
| the three examples and a slice bounds failure | **Wine** (not Windows) | goldens matched; the failure prints the diagnostic and exits 1 (`evidence-r23/wine-examples.txt`) |
| Windows | — | NOT-RUN |

**Test expectations I changed, and why. None of them is a program golden:**

- `tests/r66` and `tests/r67` count the lines of four `.lang` packs (Sanskrit 54→55, Gujarati 44→45,
  Bengali and Punjabi 34→35): +1 each for `vibhag`.
- `tests/r83` counts pack messages: 105→107 compiler messages and 128→130 in total, for the two slice
  messages.
- `tests/gui` requires the Windows IDE's keyword colour table to equal the compiler's: `vibhag` was added
  to the table (`windows/gui/sutram_gui.asm`), not to the test. The two Linux IDE tables gained it too.

**Pins:** the compiler blob is now `1f6377e3`. `src/r23_capabilities.inc` is pinned (r69's include-closure
check requires it). `src/r11_sandesh.inc` and `src/r22_lang_builtin.inc` were regenerated, and
`lang/sanskrit.lang` moved, in the r69 lock, the r70 manifest, `BUILDING.md` and `NEGATIVE-CORPUS.md`.
The Windows set was rebuilt: `cross_build_windows.py --check` REPRODUCED.

## Not a restructuring

Everything is in one new include, `src/r23_capabilities.inc` (680 lines), plus 217 lines of hooks in
`src/sutram_compiler.asm`, each marked `R23`. No existing path was rewritten. The one thing that **would**
need a restructuring, a type on variables, I did not do, and it is the cause of every "not done" below.

## A correction to v254

The CHANGELOG says R22-02 "fixed the misleading wording". **It did more than that: R22 built the eleven
keyword packs into the compiler.** So `--lang hindi` works with no `lang\` folder at all, and the warning
now fires only for a name that is no pack. A package without `lang/*.lang` is therefore no longer a
problem from v233 on. Shipping the files does no harm: a file on disk still takes priority over the
built-in copy.

## Open

| # | Item | Whose |
|---|---|---|
| 1 | **Merge #60, #61, #62 in that order, with git** (they stack) | you |
| 2 | **Not done this round, all for the same reason (no type on variables):** checked calls through function values; method dispatch on the object's type and traits; slicing a raw pointer; a slice that outlives its function | the owner: the same decision as F7 (typed parameters) |
| 3 | A message of its own for a method on an undeclared `rachana` (the reused one's hint misleads) | me, if wanted |
| 4 | The two new pack lines in Sanskrit, Hindi and Gujarati, for the owner's review | the owner |
| 5 | The library on `vibhag` parameters: `(a, n)` → `(vibhag s)`, which makes the library composable | me, a round |
| 6 | F7; the setup's staleness policy; R5; Gujarati; `tests/r69`/`r71`; PR #47 | as in R22-03 |
| 7 | My draft PRs #31–#33, #35, #38, #40, #42, #44–#46, #48, #49, #52, #54, #55, #57–#59, merged by content | you: can be closed |
