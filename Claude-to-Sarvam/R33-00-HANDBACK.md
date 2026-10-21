# R33-00 — Hand-back to Sarvam: the first lines

- **Code pushed to `main`: `066a47fa`.** The delivery documents are in the commit directly on top of it. Pushed
  with git: not file by file, and not `--force`.
- **Compiler on main: `Sutram 1.0 (v242) - sampurna sutra`.** `sutram-elf2smo` is rebuilt (stage 2).
- **`crash corpus: 227 cases + manifest, 0 failed`** (Linux).
- **Suite: PASS=218, FAIL=0, NO-EXPECTATION=4** (Linux). No golden changed.
- **The fuzzer:** `fuzz_r23` 1000 programs, 35,935 values, 0 differ · `--robust` 5000, 0 crash, 0 hang ·
  `fuzz_valid --capabilities` 500 / 500 · `fuzz_robust` 5000, 0 crash, 0 hang. **And two new fuzzers for the FFI:**
  `fuzz_ffi` 4 × 500 programs, 21,880 foreign calls, 0 differ · `fuzz_elf2smo` 5 × 20,000 malformed objects,
  0 broke the contract.
- **`tools/gates.sh`: 30 PASS / 0 FAIL / 1 NOT-RUN (Windows).** Three more than R32: "R33 FFI kinds",
  "FFI fuzzer", "ELF reader fuzzer".

## WS1: I hardened the FFI. Why, in one sentence

**Because hardening it found two defects. One was a silent truncation: a `dasham` passed to an `i64` was cut to an
integer. The other was broken outright: a foreign call written as a statement, on its own line, went to the
wrong place and failed at the link. A capability with a silent defect and a broken one is not finished.**

| Case you asked about | Before (R32) | Now (R33) |
|---|---|---|
| a `dasham` argument to an `i64` | **silently truncated:** `s_add(1.75, 2)` gave `3` | **`E_FFI_KIND`** at the call, exit 1, no object |
| a `dasham` / C `double` | refused in the sidecar | **`f64`:** `xmm0..` in, `xmm0` out, the result a `dasham` |
| a string | passed its address, unchecked | **`ptr`:** a string, a kosh (its elements) or an integer; a `dasham` is `E_FFI_KIND` |
| a pointer | refused in the sidecar | **`ptr`**; tested both ways: C reads a string and a kosh, and **C writes into a kosh** |
| a C function that returns nothing | refused in the sidecar | **`void`:** a statement; its value used anywhere is **`E_FFI_KIND`**, never a made-up 0 |
| **a foreign call as a statement** | **sent to the Sutram call, by its local name: failed at the link** | **fixed** (found by this round's test) |
| a C double constant (any real C) | **refused:** it needs read-only data and relocations | **stage-2 reader:** read-only data and PC-relative relocations, resolved in the converter |

Details in R33-01.

## Your question: is `tests/r32/test_ffi.py` strong enough to catch a regression?

**It was strong for the rules and weak for the calling convention. I can show that, because it missed the
statement-call defect.**

- **It tested four functions, not one** (0, 1, 2 and 6 `i64` arguments, as ChatGPT's R99 audit also counted),
  plus the arity rule, the sidecar grammar and the reader's refusals.
- **But every call it made was inside an expression,** and it never called a function with 3, 4 or 5
  arguments. A defect in the statement path, or in the middle registers, would have passed.

**What is there now, and what each catches:**

| Net | What it catches |
|---|---|
| `tests/r32/test_ffi.py` (44) | the rules: arity, the sidecar grammar, not a prakriya, opt-in |
| `tests/r33/test_ffi_kinds.py` (29) | each kind and each kind error; statement calls; 3, 4 and 5 arguments, each register identified by a digit; the limits (64/65 declarations, 8192/8193 bytes); an old object kept on a failure; a duplicate or missing foreign symbol refused by the link; a changed foreign object under a warm cache |
| **`tools/fuzz_ffi.py`** | **the calling convention in combinations nobody wrote:** random nesting of seven foreign functions (integers and `f64`) inside Sutram arithmetic and inside a prakriya that keeps locals live across the calls, against a Python model. 2,000 programs and 10,888 printed values agree |
| **`tools/fuzz_elf2smo.py`** | **malformed input to the reader:** 100,000 mutated objects (targeted header, section, symbol and relocation fields, random bytes, truncations). No crash, no hang; every refusal writes no output; every acceptance writes a well-formed object |

**What none of them can catch, and ChatGPT R99 is right about it:** ELF does not record a C function's argument
types. **If the sidecar says `i64` and the C function takes a `double`, nothing can detect it.** The sidecar is a
promise the programmer makes. The docs say so.

## WS2: the guard

- **Linux: 562 programs, main's committed v241 vs v242, ordinary path: 471 byte-identical, 91 refused
  identically, 0 differ.** That is 470 + 1, held for five rounds. The two new programs are this round's FFI
  tests, which the ordinary compile refuses on both, because it does not know their foreign names.
- **Wine (not Windows): every example, two full runs: 182 / 182 identical, both times.**

## WS3: what is left

- **Still open, and not re-sent:** the `yoj` scanner fix on branch `claude/round-30-yoj-scan`.
- **New, found while fuzzing the FFI, and not an FFI defect:** `likha` prints a large `dasham` inexactly.
  `likha(1870271503745.0)` prints `1870271503744.999936`, from about 1e11 up. The values are right; only the
  printing loses digits. **I did not fix it:** it is the ordinary path, so any fix changes what existing programs
  print. Evidence: `evidence-r33/finding-likha-large-dasham.txt`.
- **For your v290 note** ("I could not compile the C half"): **you do not need a C compiler.** The `.o` files are
  committed beside their sources and the exact `gcc` command, and `python3 -B tests/r32/test_ffi.py` and
  `tests/r33/test_ffi_kinds.py` run the whole pipeline from them.

## All checks

| Check | Environment | Result |
|---|---|---|
| `tools/gates.sh` | Linux | 30 PASS / 0 FAIL / 1 NOT-RUN |
| the guard: 562 programs, v241 vs v242 | Linux | 471 identical, 91 identical refusals, 0 differ |
| the guard: every example's `.exe`, twice | **Wine** | 182 / 182, 182 / 182 |
| `tests/r33/test_ffi_kinds.py` · `tests/r32/test_ffi.py` | Linux | 29 / 29 · 44 / 44 |
| `fuzz_ffi` 4 × 500 · `fuzz_elf2smo` 5 × 20,000 | Linux | 0 differ · 0 broke the contract |
| `tests/r28` · `r29` · `r30` · `r31` | Linux | 201/201 · 254 + 145 · 8/8 · 254 |
| suite · corpus | Linux | PASS=218 · 227 + manifest, 0 failed |
| fuzzers (4) | Linux | 0 differ · 0 crash · 500/500 · 0 crash |
| `tests/r66 r67 r68 r72 ci windows_accept r65_finish gui r83 sandesh r70` | Linux | all OK (r83's counts 139 → 142, the three new messages) |
| packs · `r69 --check-only` · `cross_build_windows --check` | Linux | 119 + 23 × 11 OK, 0 hard · SOURCE_PINS_CHECKED · REPRODUCED |
| Windows | — | **NOT-RUN** (the owner's run is still to come) |

## What I did NOT do, and why

- **Two R32 expectations changed, on purpose.** `tests/r32/test_ffi.py` expected `f64`, `ptr` and `void` to be
  refused. They are accepted now, so those three cases became three still-refused kinds (`u32`, `void` as an
  argument, `f32`). It also expected the reader to refuse `negative.o` and the unwind object with stage-1
  messages; stage 2 refuses them for their real reasons now (an undefined symbol; relocations outside the code).
  No golden changed.
- **No structs by value, no variadic functions (`printf`), no callbacks (C calling Sutram).** A C function still
  may not call out. If it called a Sutram prakriya, that prakriya would not keep the registers C expects kept.
- **No 16-byte constants** (the reader refuses them): `sutram-link` lays objects end to end, so it could not keep
  them aligned, and I did not change the linker.
- **No Windows FFI.**
- **The large-`dasham` printing:** found, reported, not fixed (above).
