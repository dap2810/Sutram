# R116-00 — Fifteen of ChatGPT's sixteen library contracts are built, in one commit (v296). Row 11 (`patra_asti`) is STOPPED: it needs an operating-system query the compiler does not have. And a compiler defect the messages ran into is fixed: a string literal of 127 bytes or more crashed the program.

- **Commit on `main`:** `73253b3` (on top of `65de4b9`, v295).
- **Compiler: `Sutram 1.0 (v296) - sampurna sutra`** (was v295). Linux x86-64 cloud, 2 cores.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `suite: NO-EXPECTATION=4  PASS=312  (316 run)`**, FAIL=0. That is 297 plus the 15 new goldens 330-344; golden 207 is rewritten as a refusal.
- **The new `R116 contracts` gate: `r116 contracts: 132 checks, 0 failed`** (`evidence-r116/contracts.txt`).
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux):** **61 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, payload v243 inside Sutram-Setup.exe, as before; NOT-RUN: Windows execution). Run with v296 after R117's golden 345, so the suite inside is PASS=313 (`evidence-r116/gates.txt`).
- **The guard, origin/main (v295) → v296, 722 programs** (`evidence-r116/guard.txt`):
  - **ELF and PE: 397 byte-identical, 143 refused identically, 167 DIFFER, 15 new** (examples 330-344).
  - **Wine:** Wine (the Windows compiler under Wine): 397 byte-identical, 143 refused identically, 167 DIFFER, 15 new; its 1128 outputs are byte-identical to the Linux compiler's PE outputs.
  - **The brief's "0 DIFFER except where a refusal is emitted" is not what happened, and it could not be.** A library function is compiled into every program that imports it. So all 167 programs that import a changed module (directly or through another module) have different bytes. I checked this: every one of the 167 imports a changed module, and no byte-identical program does.
  - I ran each of the 167, old and new: **164 print the same output with the same exit code.** The other 3 changed on purpose:
    - example 207 now refuses, with the length mismatch;
    - `tests/stdlib/numeric29.sm` and `r76_known_values.sm` pinned the old wrapped values, and I rewrote them deliberately (below).

## WS1 - the sixteen rows

| # | function | v296 | how it fails | evidence (v295 → v296) |
|---:|---|---|---|---|
| 1 | `ganit.dvigun` | built | stops, `E_ATIPRAVAH` | `dvigun(2^62)`: −9223372036854775808 → refused |
| 2 | `ganit.trigun` | built | stops, `E_ATIPRAVAH` | `trigun(3074457345618258603)`: wrapped → refused |
| 3 | `ganit.vardh` | built | stops, `E_ATIPRAVAH` | `vardh(MAX)`: MIN → refused |
| 4 | `ganit.nirapeksh_mulya` | built | stops, `E_PHALA_SEEMA` | `(MIN)`: MIN → refused; `(MIN+1)` = MAX |
| 5 | `ganit.mahattam_samapavartak` | built | stops, `E_PHALA_SEEMA` | `(MIN, 0)`: MIN → refused; `(MIN, 2)` = 2, `(MIN, −1)` = 1 |
| 6 | `ank.viparyay_ank` | built | stops, `E_PHALA_SEEMA` | `1999999999999999999`: −8446744073709551625 → refused; `MIN` → −8085774586302733229 |
| 7 | `ganita.ganita_nirapeksh` | built | stops, `E_PHALA_SEEMA` | as row 4 |
| 8 | `ganita.brahmagupta_kshetr` | built (rewrite) | stops: bad sides `E_MULYA_AYOGYA`, area > MAX `E_ATIPRAVAH` | `(1,1,2,3)`: **0 → 2**; `(2,3,4,0)`: **0 → 2**; four MAX sides: 1 → refused |
| 9 | `aadhar.brihat_ank_se` | built | status 0, destination cleared, nothing printed | `[1,0,0]` into 2 digits: **1 → 0**, digits 0 0 |
| 10 | `brihat.brihat_ank_tak_laghu` | built | stops: bad digit / n<0 `E_MULYA_AYOGYA`, value > MAX `E_PHALA_SEEMA` | digits of 2^63: MIN → refused |
| **11** | **`patra.patra_asti`** | **STOPPED - not built** | — | see below |
| 12 | `sadhan.yog_seema` | built (rewrite) | never refuses; only the final sum saturates | `(2^62, 2^62)`: **MAX → 2^62** |
| 13 | `samanvaya.adish_gunan` | built | stops, `E_AKARA_ASAMYA` | 3 against 2 numbers: 14 (the shorter) → refused |
| 14 | `sankhyiki.bindu_gunan` | built | stops, `E_AKARA_ASAMYA` | the same; example 207's third line |
| 15 | `suchi.suchi_shreni` | built | status 0, list unchanged, nothing printed | a scratch the sort cannot have: **1 → 0** |
| 16 | `vakyank.varna_tak_dashm` | built | status: 0.0 and `ok[0] = 0`, nothing printed | `00000000000000000001`: **0.0 → 1.0**, ok 1 |

**Full before/after for every example: `evidence-r116/before-after.txt`.**

Every message is the exact string in `ROUND-189-IMPLEMENTATION-MATRIX.json`. The gate compares stderr byte for byte: the message, then a newline, then nothing else. The suite now checks it too (next section).

### How a library function stops

R189 says to build the shared failure path first and not to add an OS call to a core module. **`abhava(cond)`, the existing assertion, now takes an optional message:**

- `abhava(cond, "text")` writes the text to stderr (fd 2) and exits 1 when `cond` is 0.
- The compiler emits the write and the exit itself, so `ganit` and `ganita` stay core modules (`layer check`: 14 core, 9 alloc, 1 std).
- An `abhava` without a message compiles to the same bytes as before.
- `yadi dosh` cannot catch it, as R189 requires.
- Tested on ELF, and on PE under Wine (`dvigun(MAX)` prints the message and exits 1).

### The rewrites, checked against an independent oracle

- **Row 8, `brahmagupta_kshetr`.**
  - **Method:** P = (T−2a)(T−2b)(T−2c)(T−2d) = 16·area² is formed exactly in base-2^30 limbs. The area > MAX check is P ≥ 2^130, done before the square root. The result is isqrt(P)/4, computed one bit at a time from bit 64. There is no float and no wrapped intermediate.
  - **Checked:** against Python's `math.isqrt` on 221 valid side sets (random sides from 2^3 to 2^63, plus boundaries), with 0 wrong (`evidence-r116/oracles.txt`). The largest square that fits, 3037000499⁴ → 9223372030926249001, is exact, and 3037000500⁴ is refused.
  - **New public helpers:** four, `bk_khand`, `bk_kaarak`, `bk_gunan`, `bk_na_adhik`. `doc signatures` requires every `prakriya` to be documented, so they are; the library now has 310 functions.
- **Row 12, `yog_seema`.**
  - **Method:** sum = s·n/2, halving whichever factor is even. When s or n does not fit, it is never formed; its size alone decides the saturation.
  - **Checked:** against Python's exact sum, clamped, on **720 pairs** (all 20×20 boundary pairs, MIN … MAX, plus 300 random): 0 wrong.
- **Row 5 (gcd)** follows R189's method: Euclid on non-positive operands, with −1 as a special case. **Row 6 (reverse)** builds the number in a non-positive accumulator with R189's limit test.
- **Row 16, `varna_tak_dashm`.**
  - **Leading zeros:** they no longer spend the 18-digit budget, and a leading zero after the point only moves the exponent.
  - **Range test:** it now uses the number's magnitude, not the exponent alone. v295 read `12345e-310` (1.2×10⁻³⁰⁶) as 0; v296 gives 1.2345×10⁻³⁰⁶, and `3e-324` gives the smallest subnormal, as Python does.
  - **Exponent text:** it saturates near 10⁹ and cannot wrap.
  - **Not done:** correct rounding. R189 keeps the documented 18-digit truncation.
- **Row 15, `suchi_shreni`.** `mil_shreni` now returns its 0 explicitly; before, success was whatever value the last call left behind.
  - **Gap:** an allocation failure cannot be injected through `nirmmita` in this setup.
  - **What I tested instead:** the other refusal that happens before mutation. A list whose length is 2^60 cells has its scratch refused, and the gate shows 0 with the cells unchanged.

### Row 11, `patra_asti` - STOPPED, as the brief says

**It cannot be built as written.** R189 requires followed-target existence from an **OS metadata query**:

- 0 only for ENOENT/ENOTDIR;
- a fatal `E_PATRA_PARIKSHA` for permission, a symlink loop or an I/O error;
- no open, so a FIFO's contents are never touched;
- a Windows equivalent.

**Sutram has no such builtin.** I searched the compiler and found no `stat` or `GetFileAttributes`. R189 says itself: "dvaram alone cannot implement the distinction". Building it means a new builtin name, a Linux `newfstatat` backend, a Windows backend, and its error translation. That is a language addition, not a library row. **Not improvised.**

What `patra_asti` does today (`evidence-r116/patra_asti-today.txt`, v296, unchanged):

- file 1, directory 1, missing 0, dangling symlink 0, `file/x` 0: **correct under R189's contract**;
- a symlink loop gives **0** (R189: refuse);
- **a FIFO hangs**: the program blocks in `open` and was killed by `timeout` after 3 s;
- permission denial: NOT RUN, because the session runs as root.

**The FIFO hang is a defect in the current function, reported here.**

## The compiler defect the messages ran into - found, fixed

R189's messages are 88-151 bytes. **Up to v295, a string literal of 127 bytes or more was skipped with a one-byte `jmp` that wrapped backwards into the code** (`evidence-r116/long-literals.txt`, v295 against v296). Depending on the length:

- the program crashed (SIGSEGV or SIGILL);
- or it ran on and printed nothing;
- or it printed the wrong text.

`likha` and `likha_rup` of a literal also stored only the low byte of the length, so a 300-byte literal printed 44 bytes.

**I found no document reporting this.** v296 emits a 4-byte jump past 127 and the full length:

- every literal of 126 bytes or fewer compiles to **the same bytes as before**: no program outside the 167 that import a changed module differs;
- the gate prints 125-5000-byte literals three ways each;
- under Wine, a 300-byte literal prints all 300 bytes, three ways.

## WS2 - the goldens

- **Examples 330-344, one per built row.** Each shows success at the boundary and then the refusal: stdout so far, the exact stderr, exit 1. Rows 9, 15 and 16 show the status instead, and row 12 shows the exact sum.
- **The suite now records stderr.** `tests/run_tests.py` compares a `<name>.err` file when one exists; without one, nothing changes. The 12 refusal goldens have one.
- **Example 207** is R189's "explicit negative". Its comment says the mismatched case is refused, and its golden is 11, 5, then the `E_AKARA_ASAMYA` line and exit 1. v295 printed 7.
- **Tests that pinned the old wrapped values were changed deliberately, not re-recorded.** Each old pin is replaced by the exact boundary value, plus a separate one-call program that must stop with the right code:
  - in `tools/proof_props.py`: `numeric28` (abs of MIN), `numeric29` (`dvigun`/`trigun`/`vardh`(MAX), `viparyay_ank`, `brahmagupta` of four 2^62 sides) and `edge30 conversion` (`brihat_ank_tak_laghu` of 2^63's digits);
  - in `tests/stdlib/`: `numeric29.sm` and `r76_known_values.sm`. In the latter, `(16, 5, 4, 1000)` "→ 0" is now refused, and the line uses `(1,1,2,3)` = 2, which v295 got wrong as 0.
  - **Result:** property proofs 86/86, library proofs 229/229.

## WS3, WS4

- **`sankhya_bindu`** is not in R189's sixteen, and it stays withdrawn.
- **The reference.** `docs/LANGUAGE-REFERENCE.md` §3a now has:
  - R189's WS3 paragraph, verbatim;
  - a table of where each of the sixteen stands, with row 11 marked "not changed".
  - I removed "as in C or Java", as R189 asks. The keyword table no longer calls `abhava` "negation".
- **The arena is not merged.** `claude/r108-arena-review` is still at `3a6292e`.

## Not done, and why

- **Row 11:** stopped, as above. It needs a new OS builtin.
- **Injected allocation failure (row 15):** no injection point reaches `nirmmita` here. I tested the size refusal instead.
- **The optional reporting adapter** for the status rows' catalog strings: R189 says to build it only together with that facility, so it is not built.
- **`E_PHALA_SEEMA`, `E_MULYA_AYOGYA`, `E_AKARA_ASAMYA`:** new library diagnostics. Their Sanskrit needs native-speaker review (NOT RUN).
- **The trapping compiler build:** NOT RUN for these functions.
- **Windows native execution:** NOT RUN (Wine only).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, every pack file, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
