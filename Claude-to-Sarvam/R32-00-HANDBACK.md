# R32-00 — Hand-back to Sarvam: the first lines

- **Code pushed to `main`: `69634d7a`.** The delivery documents are in the commit directly on top of it. Pushed
  with git: not file by file, and not `--force`.
- **Compiler on main: `Sutram 1.0 (v241) - sampurna sutra`.** New: **`sutram-elf2smo`**, at 100755.
- **`crash corpus: 227 cases + manifest, 0 failed`** (Linux).
- **Suite: PASS=218, FAIL=0, NO-EXPECTATION=4** (Linux). No golden changed.
- **The fuzzer:** `fuzz_r23` 1000 programs, 35,980 values, 0 differ · `--robust` 5000, 0 crash, 0 hang ·
  `fuzz_valid --capabilities` 500 / 500 · `fuzz_robust` 5000, 0 crash, 0 hang. **The fuzzers do not generate
  FFI calls;** the FFI's net is `tests/r32/test_ffi.py`.
- **`tools/gates.sh`: 27 PASS / 0 FAIL / 1 NOT-RUN (Windows).** One more than R31: "R32 FFI". "committed modes"
  now checks 6 executables, and "build: ELF reader (R32)" builds the new one.

## WS1: THE FFI — built, the smallest version that works

```
$ cat ffi.sffi
sutram-ffi-v1|linux-x86_64-sysv
s_add|2|i64,i64|i64|sutram_ffi_add
$ sutram_compiler --ffi ffi.sffi --object prog.sm prog.smo      # likha(s_add(17, 25))
$ sutram-elf2smo  add.o add.smo                                  # gcc -c -ffreestanding ...
$ sutram-link     prog prog.smo add.smo && ./prog
42
```

**The two rules that make it a checked declaration, both tested:**

1. **`s_add(17)` and `s_add(17, 25, 1)` are `E_ARITY`** at `2:11`, the call's own location, exit 1, and **no
   `.smo` exists afterwards**. This holds with `--object` and with `--separate`.
2. **No stub, no `FUNCDEF`:** the declaration exports nothing. The call is a relocation named
   **`sutram_ffi_add`** (the foreign name), never `s_add`. A prakriya, builtin or keyword with either name is an
   error.

**And it is opt-in:** `--ffi` is accepted only before `--object` or `--separate`. **The ordinary compile never
reads a sidecar.** Details in R32-01.

## WS2: THE GUARD — the ordinary path did not change

- **Linux: 560 programs, main's committed v240 vs v241, ordinary path: 471 byte-identical, 89 refused
  identically, 0 differ.** Your 470 has held for four rounds. The new program is `tests/r32/main.sm`, which the
  ordinary compile refuses on both, because it does not know `s_add`.
- **Wine (not Windows): every example, main's `win/sutram.exe` vs the new one: 182 of 182 identical.**
- **What R32 put on the ordinary path:** checks of "was a sidecar given", and nothing else. Once per compile,
  one `strcmp` against `--ffi` and one compare-and-branch. Once per direct call site, one compare-and-branch.
  Once per call to a name with no definition, one compare-and-branch. **They emit nothing into the program.**

## WS3: what is left

**Still open, and not re-sent:** the `yoj` scanner fix on branch `claude/round-30-yoj-scan` waits for the owner.

## All checks

| Check | Environment | Result |
|---|---|---|
| `tools/gates.sh` | Linux | 27 PASS / 0 FAIL / 1 NOT-RUN |
| the guard: 560 programs, v240 vs v241 | Linux | 471 identical, 89 identical refusals, 0 differ |
| the guard: every example's `.exe` | **Wine** | 182 / 182 identical |
| `tests/r32/test_ffi.py` | Linux | 44 / 44 |
| `tests/r28` · `r29` · `r30` · `r31` | Linux | 201/201 · 254 + 145 · 8/8 · 254 |
| suite · corpus | Linux | PASS=218 · 227 + manifest, 0 failed |
| fuzzers (4) | Linux | 0 differ · 0 crash · 500/500 · 0 crash |
| `tests/r66 r67 r68 r72 ci windows_accept r65_finish gui r83 sandesh r70` | Linux | all OK (r83's message counts moved 137 → 139 for the two new messages) |
| packs: `sandesh.py --check` · my structure check | Linux | 116 + 23 messages x 11 packs OK · 0 hard |
| `r69 --check-only` · `cross_build_windows --check` | Linux | SOURCE_PINS_CHECKED (`src/r32_ffi.inc` pinned) · REPRODUCED |
| Windows | — | **NOT-RUN** (the owner's run is still to come) |

## What I did NOT do, and why

- **Stage 1 only, as ChatGPT scoped it:** `i64` arguments and an `i64` result; **foreign code with no
  relocations** (a C function that calls another function, or uses data or read-only data, is refused). A
  `ptr`, `f64` or `void` kind is refused like any malformed line, with its line number, not with a separate code.
- **The sidecar is read after parsing, not before:** that way its diagnostics are in the `SUTRAM_LANG` pack's
  language. It is still read before the arity check and before any code, so a bad sidecar writes nothing. A
  program with a syntax error reports that first.
- **An undeclared call is not made foreign; the link refuses it** (`agyat prakriya: t_x`, no executable). The
  compile cannot refuse it in object mode, because an undefined name there may be another Sutram module's
  prakriya (R28). That is the R28 rule, unchanged.
- **No function value of a foreign function:** `f = s_add` is an unknown name, as before. A call through a
  variable needs a typed signature.
- **Linux only.** No Windows FFI, no libc, no dynamic loading, no archives.
- **The C compiler is not part of Sutram:** `tests/r32/foreign.o` is committed with its source and the exact
  `gcc` command, so the test needs no C compiler.
- **The installer:** rebuilt, because `docs/` changed.
