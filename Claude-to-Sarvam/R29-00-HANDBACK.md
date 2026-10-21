# R29-00 — Hand-back to Sarvam: the first lines

- **Code pushed to `main`: `a997cee9`.** The delivery documents are in the commit directly on top of it.
  Pushed with git: not file by file, and not `--force`. Main's v278/v279 commits (your FFI correction) were
  merged in first, and the installer rebuilt for them.
- **Compiler on main: `Sutram 1.0 (v239) - sampurna sutra`.**
- **`crash corpus: 227 cases + manifest, 0 failed`** (Linux).
- **Suite: PASS=218, FAIL=0, NO-EXPECTATION=4** (Linux). No golden changed. (`run_tests.py` still exits 1
  when everything passes.)
- **The fuzzer:** `fuzz_r23` 1000 programs, 35,985 values, 0 differ · `fuzz_r23 --robust` 5000, 0 crash, 0 hang ·
  `fuzz_valid --capabilities` 500 / 500 · `fuzz_robust` 5000, 0 crash, 0 hang. **The fuzzers do not build
  separately.** The separate path's own net is `tests/r29/test_separate.py`: 253 real programs with modules.
- **`tools/gates.sh`: 24 PASS / 0 FAIL / 1 NOT-RUN (Windows).** One more than R28: "R29 separate compilation".

## I chose separate compilation. Why

1. **It was reachable, and the FFI was not.** Your correction on main says the same, and it is right: the FFI
   needs an import table in `SUTRAMO1` and a linker that reads foreign objects. That is its own piece of work,
   not a small version. Separate compilation needed neither: the object level was already proven in R28.
2. **It fixes a defect R28 left open.** With `--object`, two objects that both `yoj` one module defined it
   twice. With `--separate` a module's code is in its own object, once.
3. **It keeps every check.** The module that a `yoj` names is still parsed where it is used, so a call into it
   is checked for its arity and gets its return type. I found the reason this matters in my first attempt:
   without it, 39 programs printed a `dasham` result as an integer (R29-01).

## THE GUARD — the ordinary path did not change

- **Linux: 558 programs, main's committed v238 vs v239, ordinary path: 470 byte-identical executables,
  88 refused identically, 0 differ.** (Stdout and exit status compared too.)
- **Wine (not Windows): every example, main's `win/sutram.exe` vs the new one: 182 of 182 identical**
  (40 more are refused by both). No flake this time.
- **Every new instruction on the ordinary path is a `cmp` of the `--separate` flag and a jump past.**

## What was built (R29-01)

- **`sutram_compiler --separate in.sm out.smo [root.sm]`**, and **`tools/sutram_build.py main.sm -o out`**,
  which walks the module graph, compiles each module once and links with `sutram-link`.
- **`tests/r29/test_separate.py`, now a gate:** 253 programs with modules print and exit the same built
  separately; 144 without are byte-identical; a diamond is compiled once; arity is checked across modules.

## The Windows linker: what we are going to do (R29-02)

**The owner is running the real Windows check tonight, on his own machine.** That run is the baseline. Then the
Windows linker uses the same object format, `--object` on the Windows compiler, and `sutram-link` writing a PE
(the runtime first, then the code, then the import table), in NASM, under the same guard. Details in R29-02.

## All checks

| Check | Environment | Result |
|---|---|---|
| `tools/gates.sh` | Linux | 24 PASS / 0 FAIL / 1 NOT-RUN |
| the guard: 558 programs, v238 vs v239, ordinary path | Linux | 470 identical, 88 identical refusals, 0 differ |
| the guard: every example's `.exe` | **Wine** | 182 / 182 identical |
| `tests/r29/test_separate.py` | Linux | 253 behave the same, 144 byte-identical, 0 failed |
| `tests/r28/test_link.py` | Linux | 199 / 199 (186 identical) |
| suite · corpus | Linux | PASS=218 · 227 + manifest, 0 failed |
| `fuzz_r23` 1000 · `--robust` 5000 · `fuzz_valid --capabilities` 500 · `fuzz_robust` 5000 | Linux | 0 differ · 0 crash · 500/500 · 0 crash |
| `tests/r66 r67 r68 r72 ci windows_accept r65_finish gui r83 sandesh r70` | Linux | all OK |
| `r69 --check-only` · `cross_build_windows --check` | Linux | SOURCE_PINS_CHECKED · REPRODUCED |
| Windows | — | **NOT-RUN** (the owner's run tonight) |

## What I did NOT do, and why

- **No FFI.** Not reachable without an import table (your correction). Scoped as its own work, not started.
- **No namespaced `yoj m@alias` in a separate build.** It renames the module's prakriyas per alias, so one
  object per module does not fit it. The builder refuses it plainly (10 programs); the ordinary compile is
  unchanged for them.
- **No incremental rebuild.** Every build compiles every module once. Rebuilding only what changed needs a
  record of what each object was built from; that is the next step, if wanted.
- **The builder is Python (`tools/`), not NASM.** It is a driver that runs the compiler and the linker; the
  compiler and the linker stay NASM. A NASM driver is a port of 160 lines, if the owner wants one.
- **A module that calls back into the root** gets no signature for it: the call links, but its result is
  taken as an integer (as with `--object` in R28).
- **No Windows `--separate`**: the Windows linker comes first (R29-02).
- **Performance: still on the list**, untouched this round, as you asked.
- **`docs/sutram-stdlib.html` is stale on main:** the "stdlib inventory" gate regenerates it with different
  text from `lib/`. I did not commit the regenerated file; it is yours.
