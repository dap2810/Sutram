# R26-00 — Hand-back to Sarvam: the first lines

- **Commit pushed to `main`: `597a6bb8`** (the code). The delivery documents are in the commit directly on
  top of it. Pushed with git, not file by file and not `--force`.
- **Compiler on main: `Sutram 1.0 (v237) - sampurna sutra`**
- **`crash corpus: 227 cases + manifest, 0 failed`** (Linux)
- **Suite: PASS=218, FAIL=0, NO-EXPECTATION=4** (Linux). That is 217 + `250_r26_dosh_handler`; no
  existing golden changed. (`run_tests.py` still exits 1 when everything passes.)
- **The fuzzer covers the handler: yes.** `fuzz_r23.py --seed 26 --count 1000`: **1000 programs, 36,112
  values, 0 differ.** Robust mode: 5000 mutations, **0 crash / 0 hang**.
- **`tools/gates.sh`: 22 PASS / 0 FAIL / 1 NOT-RUN (Windows).**

## The three decisions

1. **WS1, the handler: decided and built** (R26-01). The form is `yadi dosh (q = f(...)) { failure: q is
   the code } anya { success: q is the value }`. There is **no new keyword**; it reads as "if failure", and
   a failure can now be recovered from anywhere.
2. **WS2, the linker: not started. It is restructuring by the standing rule** (R26-02). It changes the one
   step every program goes through. **The alternative:** keep the source-level `yoj` for modules, and for
   the FFI an **opt-in object-file output linked by the system's linker,** never a linker of our own. That
   is the owner's yes or no.
3. **WS3, the type on variables:** with the owner, **not built** (R26-03).

## All checks

| Check | Environment | Result |
|---|---|---|
| `tools/gates.sh` | Linux | 22 PASS / 0 FAIL / 1 NOT-RUN |
| suite | Linux | PASS=218 |
| crash corpus | Linux | 227 + manifest, 0 failed |
| `tests/r25/test_phal.py` (error type + handler) | Linux | 21 / 21 |
| `fuzz_r23` 1000 · `--robust` 5000 | Linux | 0 differ · 0 crash, 0 hang |
| `fuzz_valid --capabilities` 500 | Linux | 500 / 500 |
| `fuzz_robust` 5000 mutations | Linux | 0 crash, 0 hang |
| `tests/r66 r67 r68 r72 ci windows_accept r65_finish gui r83 sandesh r70` | Linux | all OK |
| `r69 --check-only` · `cross_build_windows --check` | Linux | SOURCE_PINS_CHECKED · REPRODUCED |
| examples 246–250 | **Wine** (not Windows) | output and exit status match the goldens |
| Windows | — | **NOT-RUN** |

**`FILES-R26.txt`** lists every changed file with its git blob.

## What I did NOT do, and why

- **The linker:** restructuring, so I stopped, as the rule says (R26-02).
- **A type on variables:** it waits for the owner.
- **Keeping a result in a variable, `phal<T>`, and matching on codes:** not needed for the handler, and
  the last two wait on the type decision.
- **`fuzz_valid` does not generate the error type or the handler;** `fuzz_r23` does, and it is a gate.
- **Windows not run.** Wine is not Windows.
