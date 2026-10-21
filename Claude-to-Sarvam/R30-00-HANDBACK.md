# R30-00 — Hand-back to Sarvam: the first lines

- **Code pushed to `main`: `d0527487`.** On top of it: main's v283 merged in, the installer rebuilt for it
  (`b774d2bb`), and the delivery documents. Pushed with git: not file by file, and not `--force`.
- **Compiler on main: `Sutram 1.0 (v240) - sampurna sutra`.**
- **`crash corpus: 227 cases + manifest, 0 failed`** (Linux).
- **Suite: PASS=218, FAIL=0, NO-EXPECTATION=4** (Linux). No golden changed.
- **The fuzzer:** `fuzz_r23` 1000 programs, 35,818 values, 0 differ · `--robust` 5000, 0 crash, 0 hang ·
  `fuzz_valid --capabilities` 500 / 500 · `fuzz_robust` 5000, 0 crash, 0 hang. **The fuzzers do not generate
  module-level `vitti` across modules;** that net is `tests/r30/test_vitti.py`.
- **`tools/gates.sh`: 25 PASS / 0 FAIL / 1 NOT-RUN (Windows).** One more than R29: "R30 module vitti".

## WS1 or WS2: my call, in one sentence

**I continued capabilities (WS2), because the FFI is its own piece of work — an ELF reader in `sutram-link`
plus a declaration route the owner has not chosen — while module state was the last thing stopping a real
module from being compiled separately.** ChatGPT's R96/R97 design work is the right start for the FFI when it
is taken; I have not built any of it.

## What was built: a module-level `vitti`, in an object, shared across modules (R30-01)

- **R28 and R29 refused a module-level `vitti` in an object.** Now each object holds its own `vitti`, after its
  code, and exports it as `vitti:<name>`. In `--separate`, an imported `vitti` is a relocation, so **the program
  has one copy**, in its own module's object. The root initializes every `vitti` at the start of `mukhya`, as
  the one-pass compile does.
- **No format change and no linker change.** R28 said this would need a second kind of relocation. **I was wrong:**
  the access's displacement is the instruction's last four bytes, the same arithmetic as a call.
- **One refusal remains, narrower:** a library object under plain `--object` refuses a `vitti` with an
  initializer, because no `mukhya` would run it.

## WS3: what was left from R29 — ChatGPT's scanner finding (R30-02)

**ChatGPT is right, and it is worse than it reported: the bug is in the compiler, not only the builder.** The
builder copied the compiler's rule exactly. **On main today, the ordinary compile:**

| Program | What happens |
|---|---|
| `likha("yoj bogus")` | **fails**, `E_MODULE_MISSING` |
| `likha("yoj ganit ")` | **compiles ganit's source into the string**, silently |
| `vitti sanyoj = 4` | **fails**, `E_MODULE_MISSING` |

**The fix is ready on a branch, `claude/round-30-yoj-scan`, and NOT on main,** because it changes the ordinary
path (only for programs like these, which fail or miscompile today). **On that branch: 559 programs, 0 differ
from v240; Wine 182 / 182 identical; gates 26 / 0 / 1.** **Merging it is the owner's decision** (R30-02).

## Your v283 hand test

**I ran the same shape by hand, from the program's own directory, and it works:**

```
lib/util.smlib          prakriya dvi(x) { prati x * 2 }
main.sm                 yoj util ... likha(dvi(21))

sutram_compiler --separate main.sm main.smo            -> Siddh: 187 baait sankalit
sutram_compiler --separate lib/util.smlib util.smo main.sm   -> Siddh: 84 baait sankalit
sutram-link prog main.smo util.smo && ./prog           -> 42
```

**The one thing that is easy to miss:** a module compiled by itself needs the root as its fourth argument
(`main.sm` above), or its own `yoj` is looked up next to the module. **`tools/sutram_build.py main.sm -o prog`
does all of it.** If your second attempt still made no `.smo`, send me the exact commands and I will find out why.

## THE GUARD — the ordinary path did not change

- **Linux: 559 programs, main's v239 vs v240: 471 byte-identical executables, 88 refused identically, 0 differ.**
- **Wine (not Windows): two full runs of every example.** Run 2: **182 of 182 identical.** Run 1: 181, and
  `43_nested_likha.sm` differed; it was identical in three targeted reruns (old vs new, and old vs old). A flake
  in the Wine loop, as in R28; reported as seen.

## All checks

| Check | Environment | Result |
|---|---|---|
| `tools/gates.sh` | Linux | 25 PASS / 0 FAIL / 1 NOT-RUN |
| the guard: 559 programs, v239 vs v240 | Linux | 471 identical, 88 identical refusals, 0 differ |
| the guard: every example's `.exe` | **Wine** | 182 / 182 (run 2); 181 + 1 flake (run 1) |
| `tests/r30/test_vitti.py` | Linux | 8 / 8 |
| `tests/r28/test_link.py` | Linux | 201 / 201; identity now **187** (the `vitti` example is compared, not refused) |
| `tests/r29/test_separate.py` | Linux | 254 behave the same, 145 byte-identical, 0 failed |
| suite · corpus | Linux | PASS=218 · 227 + manifest, 0 failed |
| fuzzers (4) | Linux | 0 differ · 0 crash · 500/500 · 0 crash |
| `tests/r66 r67 r68 r72 ci windows_accept r65_finish gui r83 sandesh r70` | Linux | all OK |
| `r69 --check-only` · `cross_build_windows --check` | Linux | SOURCE_PINS_CHECKED · REPRODUCED |
| branch `claude/round-30-yoj-scan`: guard · Wine · gates · its test | Linux / **Wine** | 0 differ · 182/182 · 26/0/1 · 5/5 (4 of 5 fail on main) |
| Windows | — | **NOT-RUN** (the owner's run is still to come) |

## What I did NOT do, and why

- **No FFI.** See the one sentence above.
- **The `yoj` scanner fix is not on main.** It changes the ordinary path; it waits for the owner (R30-02).
- **One test expectation changed, on purpose:** `tests/r28/test_link.py` expected `--object` to refuse
  `vitti G = 5` in a program with `mukhya`. That refusal is the R28 limit this round removes, so the check now
  expects the direct compile's bytes, and a new check keeps the remaining refusal. No golden changed.
- **The refusal message is reused:** `vastu-patre ghatak-star vitti asamarthita` now means "an initialized
  `vitti` in a library object". No new message, so the eleven packs are unchanged.
- **Still not done from R29:** namespaced `yoj m@alias` in a separate build, incremental rebuilds, a NASM driver.
- **Windows:** no Windows `--object` yet; the plan in R29-02 stands, after the owner's real Windows run.
- **`docs/sutram-stdlib.html` is still stale on main** (the gate regenerates it; I did not commit it).
