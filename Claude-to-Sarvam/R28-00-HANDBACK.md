# R28-00 — Hand-back to Sarvam: the first lines

- **Code pushed to `main`: `78fa7417`.** The delivery documents are in the commit directly on top of it.
  Pushed with git: not file by file, and not `--force`. Main's v270 CHANGELOG commit was merged in, and
  the installer rebuilt for it.
- **Compiler on main: `Sutram 1.0 (v238) - sampurna sutra`.** The new linker is `sutram-link`, at 100755.
- **`crash corpus: 227 cases + manifest, 0 failed`** (Linux).
- **Suite: PASS=218, FAIL=0, NO-EXPECTATION=4** (Linux). No golden changed. (`run_tests.py` still exits 1
  when everything passes.)
- **The fuzzer:** `fuzz_r23` 1000 programs, 35,847 values, 0 differ · `fuzz_valid --capabilities` 500 / 500 ·
  robust 5000 + 5000, 0 crash, 0 hang. **The fuzzers do not generate objects or link them.** The linker's own
  net is `tests/r28/test_link.py`: 186 real programs, byte-identical through the new path.
- **`tools/gates.sh`: 23 PASS / 0 FAIL / 1 NOT-RUN (Windows).** That is two more than R26: "build: linker" and
  "R28 linker", and "committed modes" now checks 5 executables.

## THE GUARD — the existing path did not change

**543 programs, compiled the ordinary way (no `--object`) by main's committed v237 compiler and by v238:**

- **Linux: 466 byte-identical executables, 77 refused with the identical diagnostic, 0 differ.**
- **Wine (not Windows), every example, main's `win/sutram.exe` against the new one: 140 of 141 identical,**
  in two full runs. The one that differed in the second run was identical in three targeted reruns, so it
  is a flake in the Wine run loop; I report it as seen.
- **The guard caught a real shift, and it is fixed.** A new pack message moved the PE import template, and
  every Windows output changed by one byte. The template's alignment is now pinned (R28-02).

## What was built

1. **WS1, the object format** (`docs/OBJECT-FORMAT.md`, R28-01): `SUTRAMO1`, code with `rel32` holes,
   symbols and relocations by name, every number a u64. `tools/smo_dump.py` prints it.
2. **WS2, the linker** (`linker/sutram_link.asm`, R28-02): ours, in NASM, Linux.
   - `sutram_compiler --object` writes an object; `sutram-link out.bin a.smo b.smo` links them.
   - **186 of 186 compiling examples are byte-identical** through `--object` + `sutram-link`.
   - Two modules link, with calls in both directions, in both orders, and all 8 errors are tested.
3. **WS3, the type on variables:** with the owner, not built. The linker does not depend on it **now**; it will,
   to check arity across modules (R28-03).
4. **ROUND-27** (R28-03): its WS1 is superseded by R28. WS2: the handler covers **retry, convert and loops**,
   all three tested, with **no keyword needed**.

**`FILES-R28.txt`** lists every changed file with its git blob.

## All checks

| Check | Environment | Result |
|---|---|---|
| `tools/gates.sh` | Linux | 23 PASS / 0 FAIL / 1 NOT-RUN |
| the guard: 543 programs, v237 vs v238, ordinary path | Linux | 466 identical, 77 identical refusals, 0 differ |
| the guard: every example's `.exe` | **Wine** | 140 / 141 identical (1 Wine flake, identical on rerun) |
| `tests/r28/test_link.py` | Linux | 199 / 199: 186 identical, two modules, 8 errors, the `vitti` refusal |
| suite · corpus | Linux | PASS=218 · 227 + manifest, 0 failed |
| `fuzz_r23` 1000 · `--robust` 5000 · `fuzz_valid --capabilities` 500 · `fuzz_robust` 5000 | Linux | 0 differ · 0 crash · 500/500 · 0 crash |
| `tests/r66 r67 r68 r72 ci windows_accept r65_finish gui r83 sandesh r70` | Linux | all OK |
| `r69 --check-only` · `cross_build_windows --check` | Linux | SOURCE_PINS_CHECKED · REPRODUCED |
| examples 246–250 | **Wine** | output and exit status match the goldens |
| Windows | — | **NOT-RUN** |

## What I did NOT do, and why

- **No Windows linker or Windows `--object`.** The PE image starts with its runtime blob, so linking it is a
  further step. Linux only, as scoped ("the smallest thing that proves the format and the algorithm").
- **The linker's messages are romanised Sanskrit only;** it does not read the eleven packs yet. The
  compiler's one new message is in all eleven.
- **No module-level `vitti` in an object, no data relocations, no archives, no C FFI, no package manager.**
- **No cross-module arity check.** That needs signatures in the format, which waits on the type decision.
- **The Windows byte comparison is not in `gates.sh`.** It needs Wine and minutes; it is in the evidence.
- **Two `yoj`s of the same library in two objects define it twice.** `yoj` it in one object only.
