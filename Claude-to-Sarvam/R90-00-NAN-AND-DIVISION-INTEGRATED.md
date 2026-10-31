# R90-00 — Two of ChatGPT's patches are in, as written; the narrowing prototype is not; the change found one library routine relying on the old NaN bug, and one defect of mine

- **Commit on `main`:** this round's commit (parent `f118344`). It contains compiler v280, two of ChatGPT's patches applied unchanged, one fix of mine, one library fix, three goldens, docs and evidence.
- **Compiler: `Sutram 1.0 (v280) - sampurna sutra`** (was v279). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=261`, FAIL=0** (three new goldens: 291, 292, 293). Library proofs **229/229**. Property proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 57 PASS / 0 FAIL / 1 NOT-RUN (Windows execution).** See "One intermittent gate" below.
- **The guard, origin/main (v279) → v280: 671 programs, 447 byte-identical, 128 refused identically, 93 DIFFER, 3 new (291–293)** — Linux ELF and Linux PE.
  - **I ran all 93 DIFFER programs, old binary and new: all 93 print the same bytes with the same exit code, on ELF and on PE.**
  - **The Windows compiler under Wine** was run before the library fix. It produced the same counts, and its 1080 outputs were byte-identical to the Linux compiler's PE outputs.

## WS2 first, since you named it the risk: did any program change its answer?

**No program in the tree changed its output.** The bytes changed in 93 programs because they compare floats or
divide them, but none of them compares a NaN, divides a `dasham` by zero, or hits the `likha` defect below. So
there was no case where I had to judge whether the old or the new answer was right.

**The guard did not catch the one place that relied on the old bug. A proof did.**

- `roop_sthir`, the library's fixed-decimal formatter, detected NaN with `v == 0.0 and v < 0.0`. Its own
  comment explained why: "NaN == NaN is true and NaN != NaN is false — v != v does NOT detect NaN here".
- That test was true only because comparisons were wrong. On v280 it is false for NaN, so `roop_sthir(nan, 2, buf)`
  would have printed garbage.
- Property `edge30 float` failed and showed it. No tree program passes NaN to `roop_sthir`, so the guard
  could not see it.
- **I fixed the library guard to `v != v`**, which is now the correct test. That is the only workaround of the
  kind in `lib/`; I checked every NaN mention.
- **The lesson for the next semantic change:** the guard proves the tree's own programs; the proofs probe edge
  inputs the tree never uses. Both are needed.

## ChatGPT's patches — reviewed, applied, tested

| patch | SHA-256 (I computed it) | verdict |
|---|---|---|
| `ROUND-159-NAN-COMPARE.patch` | `f41af541…855eaaaf3f6a4e5` | **applied unchanged** |
| `ROUND-159-FLOAT-DIVISION.patch` | `8572f4d9…0d8a5c38c6d` | **applied unchanged** |
| `ROUND-159-FLOAT-NARROW-PROTOTYPE.patch` | `009b0880…5dd7` | **not applied** — below |

The handoff's SHA for the NaN patch is 63 hex digits long: one `a` is missing in `…855eaa_f3…`. The patch
itself is intact.

**The NaN patch is correct.**

- I checked what it relies on. `dl` is runtime scratch at both sites. The general path already pops the left
  operand into `rdx`, so nothing can rely on `rdx` surviving a float comparison.
- `seta`/`setae` need no parity test, because unordered sets CF.
- **Its oracle: v279 5/10, v280 10/10**, on ELF and PE, and also in the peephole build, the XMM-cache build and
  the build with both.
- I added my own test, every comparison in a different context (`evidence-r90/nan-in-context.txt`), against
  IEEE. Contexts: variables, expressions, `x op x`, `yadi`, `yavat`, call arguments, a `dasham` parameter,
  `kosh dasham` elements, and inside integer arithmetic.
  - **v279 got 9 of 10 lines wrong. v280 matches IEEE on all 10.**

**The division patch is correct.**

- A `dasham` divided by `+0.0` or `-0.0`, written or computed, now stops with `E_SHUNYA_BHAJAN` at the right line.
- A NaN divisor is not mistaken for zero.
- The three division fast paths fall back to the checked general path.
- XMM cache: the check uses `xmm2`, which the cache can hold. The cached-assignment path now declines
  division and the statement takes a cache barrier first, so this is safe as ChatGPT built it. The default
  build has no cache.
- **Its oracle: v279 1/8, v280 8/8.**
- **Cost:** `c = a / b` with register floats went from 4 instructions to the general path, about 100 bytes,
  most of it the inline error message, which only runs on a zero divisor. The codegen gate pinned 16
  instructions for that shape. I took the division out of `float_reg_destination` (now 3 operations, 12
  instructions) and raised `float_reg_compare` from 36 to 44: two instructions for each of `==`, `!=`, `<`, `<=`.
  The gate now checks the parity instructions by name.

**What ChatGPT warned about, and I handled:** its NaN oracle made NaN with `0.0 / 0.0`, which the division
patch makes an error. Both its oracle and my golden 289 now make infinity by overflow (×10 in a loop) and NaN
as `inf - inf`. Both of ChatGPT's tests now also run on Linux; on Windows they write `.exe` as before.

**The narrowing prototype is not integrated, and should not be in this form** (`evidence-r90/narrowing-prototype-measured.txt`):

- **It refuses 25 programs in the tree** that compile and run correctly on v280: every program that imports
  `madhava` or `roop`, the `fmt_*` and `madhava_*` library tests, examples 93, 94, 99, 102, 126 and 201, and
  `r79_real`.
- The refusal is inside the library (`madhava.smlib:53`, `vitti k = x / pi2`), but **it reports the user's own
  file with no line**: `201_madhava_library.sm: Sutram Error [E_DASHAM_VITTI]: …`. A student calling
  `madhava_sin` would be told their file is wrong.
- ChatGPT said all this itself; the numbers confirm it.

## WS1 — the computed conversion `dasham d = 3.7; vitti i = d`: still silent, and why I didn't refuse it

Refusing it means the library must convert explicitly, and **the explicit conversion needs a name.** Under
`docs/vocabulary/VOCABULARY-RULE.md` (owner-agreed), every new builtin name is yours to approve. This is the
smallest complete version, ready to build once you name it:

1. A builtin, say `X(d)`: truncate toward zero, and stop with a message if `d` is NaN, infinite or out of range.
   It would be the only sanctioned float-to-integer path.
2. Rewrite the library sites to use it: `madhava` (2 sites) and `roop`. Those are the only two modules that trip
   it.
3. Then refuse the implicit form with a real line and column. A computed expression has no position stored
   today; the literal check uses the literal's.

**Name it and I'll build it next round**, with the guard over all 25 programs.

## A defect of mine, found while testing — fixed

**`likha("y ", a / b, a % b, b * a)` printed `y 3`, `1`, `14` on three lines** (v276–v279).

- The division-by-zero check (R80) writes its message with ordinary `likha` calls at compile time. Those consumed
  the "no newline" flag that a multi-value `likha` sets for each value.
- `r80_emit_div_fatal` now saves and restores the flag. The output is `y 3114`.
- Golden **292** pins it (`evidence-r90/likha-after-division.txt`).
- The float-division patch calls the same routine, so without this fix it would have spread to `dasham` division.

## Goldens

- **291 `r90_nan_compare`**: all six operators against NaN, on either side and against itself; `yadi (n == n)`;
  infinity.
- **292 `r90_likha_after_division`**: values after a division stay on one line.
- **293 `r90_float_divide_by_zero`**: `5.0 / 2.0` prints `2.500000`, then dividing by a computed zero stops, exit 1.
- All three, and 289, are identical on PE.

**289 no longer divides by zero**: its `inf`/`nan` lines come from overflow and `inf - inf`, with the same output.

## Docs

- **Reference §15:** NaN comparisons follow IEEE, and `n != n` tests for NaN. A `dasham` divided by zero stops,
  and inf still comes from overflow. The old "comparisons with NaN are wrong" warning is gone.
- **§3a's division row** mentions `dasham`.
- **CHANGELOG:** a v280 entry. It is kept at 20 entries; v424 moved to the archive.

## One intermittent gate

`guard pages` reported `suite FAIL=1` in one full gate run this round, and in one in R87. It did not reproduce in
`tools/guard_page.py` run alone (twice), or in a second full run that kept every gate's output. That run was
57/0/1. **I can't name the test**, and I am not calling it a pass. Next time it fails I'll have the output; the
gate script with kept output is in my scratch notes.

## Not done

- **The computed float-to-`vitti` refusal:** it waits for the name above.
- **Integer `kosh` stores of a fraction** (`kosh_push(a, 2.9)`) are still silent.
- **Message placement:** `likha("a / b = ", a / b)` with a zero divisor prints `a / b = Sutram Error …` on one
  line. The text is printed before the value is computed; the same happens for `vitti`.
- **The installer:** ChatGPT's WS4 needs a Windows build host, and the integrity manifest needs your review
  first.
- **Not run:** real Windows; the Wine-compiler guard after the `roop.smlib` fix (the binary is the same as the
  run above).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.
- R88 and R89 were already done in `cd7a1b5`.
