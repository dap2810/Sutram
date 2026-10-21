# R31-00 — Hand-back to Sarvam: the first lines

- **Code pushed to `main`: `20bbdcfa`.** The delivery documents are in the commit directly on top of it. Pushed
  with git: not file by file, and not `--force`.
- **Compiler on main: `Sutram 1.0 (v240) - sampurna sutra`, unchanged this round.** The work is in the builder.
- **`crash corpus: 227 cases + manifest, 0 failed`** (Linux).
- **Suite: PASS=218, FAIL=0, NO-EXPECTATION=4** (Linux). No golden changed.
- **The fuzzer:** `fuzz_r23` 1000 programs, 35,953 values, 0 differ · `--robust` 5000, 0 crash, 0 hang ·
  `fuzz_valid --capabilities` 500 / 500 · `fuzz_robust` 5000, 0 crash, 0 hang. **The fuzzers do not use the
  cache;** its net is `tests/r31/test_incremental.py`.
- **`tools/gates.sh`: 26 PASS / 0 FAIL / 1 NOT-RUN (Windows).** One more than R30: "R31 incremental".

## WS1: my call, in one sentence, and the FFI question

**I built incremental rebuilds, because a separate compilation that recompiles every module on every build
delivers only half of what it exists for, and it needed no decision from the owner.**

**You asked whether the FFI fits the model or is restructuring. It fits; it is not restructuring.**

- **The compiler side** is two existing mechanisms with one new table: the R7 arity check looks a name up in a
  foreign-declaration table after its own, and the call becomes an R28 relocation carrying the external name.
- **The linker side** is one new input reader, which turns a foreign object's code, symbols and relocations into
  the same lists `sutram-link` already builds from `SUTRAMO1`.
- **Neither touches `SUTRAMO1` or the ordinary path.**

**Why I have not started it:** ChatGPT's own spec says *"THIS IS NOT ACCEPTED SYNTAX OR AN IMPLEMENTED FLAG"*.
The sidecar is the declaration route, and it is a language decision. **When the owner accepts it (or another
route), I can build it as its own piece of work.** The type on variables is in the same place: it is with the
owner.

## What was built: `--cache` (R31-01)

```
python3 tools/sutram_build.py --cache .sutram-cache main.sm -o prog
sutram-build: 4 modules: 2 compiled, 2 reused from the cache, linked to prog
```

- **A module's object is stored under a SHA-256 key of everything it depends on:** the compiler's bytes,
  `SUTRAM_LANG`, the module's path and bytes, and the path and bytes of every module it reaches through `yoj`.
- **`tests/r31/test_incremental.py`, now a gate:** 254 programs are **byte-identical** clean, with a cold cache
  and with a warm one; the warm builds compile nothing. Edit one module and **only it and what reaches it** are
  recompiled.

## WS2: what the module `vitti` costs the ordinary path — nothing that reaches a program

- **The guard: R29's compiler (v239) vs R30's (v240), ordinary path: 559 programs, 471 byte-identical,
  88 refused identically, 0 differ.** That is your 470, plus my one new test program from R30.
  23 of the 559 declare a module-level `vitti` themselves.
- **What R30 put on the ordinary path:** three compare-and-branch pairs in the compiler. Two run once per
  top-level `vitti`; one runs once per compile that has a `vitti`. **None of them emits anything into the program.**
- **The compiler binary** grew 1,160 bytes (405,824 → 406,984). **Compile time:** within the noise (about
  1.2 ms per program for both; three alternating runs over all 559).
- **Wine:** the R30 guard stands (182 / 182). The Windows compiler is unchanged this round.

Details: `evidence-r31/ws2-ordinary-path-cost.txt`.

## WS3: what is left from R30

**One item is still open:** the `yoj` scanner fix on branch `claude/round-30-yoj-scan` (R30-02) waits for the
owner's word. I am not re-sending it.

## All checks

| Check | Environment | Result |
|---|---|---|
| `tools/gates.sh` | Linux | 26 PASS / 0 FAIL / 1 NOT-RUN |
| WS2 guard: 559 programs, v239 vs v240 | Linux | 471 identical, 88 identical refusals, 0 differ |
| `tests/r31/test_incremental.py` | Linux | 254 identical clean / cold / warm; only what changed; the key |
| `tests/r28` · `r29` · `r30` (in the gates) | Linux | all PASS |
| suite · corpus | Linux | PASS=218 · 227 + manifest, 0 failed |
| fuzzers (4) | Linux | 0 differ · 0 crash · 500/500 · 0 crash |
| `cross_build_windows --check` | Linux | REPRODUCED (installer rebuilt: `docs/` changed) |
| Wine | — | **NOT-RUN this round**: the compiler and `win/sutram.exe` did not change; R30's 182 / 182 stands |
| Windows | — | **NOT-RUN** (the owner's run is still to come) |

## What I did NOT do, and why

- **No FFI, no type on variables:** both wait on a language decision by the owner (above).
- **The cache is not cleaned:** old objects stay in the directory until someone deletes it. It is opt-in
  (`--cache DIR`), so nothing is written anywhere unless asked.
- **The cache trusts its own files:** an object someone edits by hand inside the cache directory is not
  detected. The linker still checks the format of every object it reads.
- **Still not done from R29:** namespaced `yoj m@alias` in a separate build, and a NASM driver.
