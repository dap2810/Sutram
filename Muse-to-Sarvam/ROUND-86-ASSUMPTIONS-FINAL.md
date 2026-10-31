# ROUND-86: the assumptions section, final

Base: origin/main at v279 (compiler `Sutram 1.0 (v279)`), tree
reset to `7eb668d8` before work. No tree changes. Deliverables in
`Muse-to-Sarvam/`: this report, `R86-REFERENCE-SECTION-FINAL.md`
(the single final section), and `r86_misread.json` (the WS3 count
data). The verification suite is kept at `~/workspace/r86/
verify_final.py` (not delivered; it is a harness, not a section).

## What v279 changed, pinned before the section was written

Two of the brief's verified behaviours, plus two more changes
found by probing (all run on v279, not carried over from v278):

1. **Written fraction into `vitti`: refused.** `vitti f = 3.5`
   → `E_DASHAM_VITTI`, with the hint to write `dasham f = 3.5`.
   The refusal is narrow: a bare written fraction only.
   `vitti f = 3.0` (integral `dasham` literal) is allowed and
   prints 3; `vitti f = 3.5 + 0.0` and `vitti f = 7.0 / 2`
   (constant expressions with fractional results) still
   truncate silently to 3; a computed float into a `vitti`
   (`vitti h = x / 2` with `x = 7.0`) still truncates to 3; a
   computed infinity into a `vitti` still becomes MIN with no
   fault. So the `madhava` period count and the `roop` rounding
   step (both computed) still work exactly as in R85, and the
   R85 float entry is outdated only for the written-literal
   case.
2. **The `dasham` printer is fixed.** `likha(1e20)` prints
   `1.000000e+20` (scientific notation, correct), and
   `likha(inf)` prints `inf` — not the minimum-value rendering
   of v278 and earlier. The §3a "Not yet right" printer note is
   now outdated. (Int into `dasham` still promotes: `dasham f =
   3` prints 3.000000.)
3. **A `dasham` `tak` bound never terminates** (see WS2 — this
   is new, and it is a compiler defect, not a documentation
   preference).
4. **The tree grew:** `examples/*.sm` is now 262 files (was 259
   in R84), with three new files: 288 (the alias pin), 289
   (float printing), 290 (the fraction-into-`vitti` refusal
   demo). Sarvam's brief says 260 examples and 34 declaring
   `dasham`; I count 262 files, 44 with a `dasham` declaration
   or parameter (comments stripped), and 33 with a `dasham`
   variable declaration (parameters excluded). The 34 vs 33 is
   one file's definitional difference (likely a Devanagari form
   my ASCII pattern misses, or a boundary case); the 260 vs 262
   is the two newest files landing after Sarvam's count.

## WS1 — ONE final section, verified on v279

`R86-REFERENCE-SECTION-FINAL.md` replaces both the R84 and R85
drafts. It opens with the brief's five, in the brief's order,
each with one line of code and what it actually prints:

- `tak` inclusive (`chakra i = 0 tak 3` → 0, 1, 2, 3).
- `nirmmita(64)` counts bytes, `p[i]` counts qwords
  (`p[7] = 42` → 42).
- Integer division truncates toward zero (`-7 / 2` → −3,
  `-7 % 2` → −1).
- `vitti` is integer, `dasham` is float — a written fraction in
  a `vitti` is refused (`vitti f = 3.5` → `E_DASHAM_VITTI`),
  with the computed-truncation sharpening (`vitti h = x / 2`
  → 3) so a reader is not surprised by the `madhava`/`roop`
  cases.
- `vitti a = k` is a second name, diverging on relocation
  (obstacle case: `a[0]` = 41, `k[0]` = 99).

Then the rest, all re-verified on v279 (not carried over):
string ordering (declaration order), string `==` (addresses),
string indexing (qwords; `akshar` is the byte reader),
`dasham` division by zero (silent +inf; `0.0 / 0.0` = 0; printer
now prints `inf` and `1.000000e+20`), assignment is not an
expression, `vitti` is not a parameter type, `kosh_push` on a
`kosh` parameter refused, uninitialized `vitti` reads 0 even on
a second call, trailing statements after an indented `mukhya`
execute (braced: compile error), negative index faults,
`likha(k)` prints an address, `kosh ==` compares addresses,
descending `tak` counts down (STATED), loop variable does not
survive the loop, string `+` on variables adds addresses
(literals concatenate), NaN equals every `dasham`, and the
sixth (below).

**Verification: 26/26 on v279.** The suite's first run showed
24/26; the two "failures" were the harness's expected strings
(the numeric `likha` already appends LF, so `likha(x)` +
`likha("\n")` prints two newlines — the same harness lesson as
R84). Values were right throughout; expectations corrected,
re-run 26/26. The runaway case (the sixth) is verified by
timeout + line count, not by comparing output: 246,013 lines
in one second, starting 0, 1, 2, never stopping at 3.5.

## WS2 — the sixth: a `dasham` `tak` bound never terminates

One fresh pass over the reference against the compiler, looking
only for things a reader would assume wrongly. Checked and not
the sixth: `yadi (0.5)` is true and `yadi (0.0)` is false
(`dasham` truthiness is non-zero, like integers — unsurprising);
`mala` out-of-bounds via a variable index faults
(`mala ank seema atikram` — `mala` is runtime-checked, like
`kosh`); calling with too many or too few arguments is refused
at compile time (with the hint to give exactly as many as the
definition has).

**The sixth: `chakra i = 0 tak 3.5` compiles cleanly and never
stops.** The integer loop variable starts at 0, 1, 2, … and
counts past 3.5 forever (246,013 lines in one second, killed by
timeout). The same holds for `tak 3.0` — any `dasham` bound,
integral or not, breaks termination. A reader would assume
either that it truncates to `tak 3` or that it is refused like
`vitti f = 3.5`; both are wrong. It is in the section as the
last entry, marked NOT STATED, with the recommendation that it
be refused by the compiler (like the written fraction), not
documented permanently. One correction owned: my first look at
the runaway output read the large numbers as a garbage start;
a capped run shows it starts at 0 correctly and simply never
stops — the start was never the problem, the stop condition
was.

## WS3 — the misread count, updated against v279

**31 of 262** (R84: 28 of 259). The rule is unchanged: a file
counts if it contains at least one wrong-answer trap
(compile-error and fault traps excluded — they give no answer,
not a wrong one), with the same two hand exclusions (21 and 239,
whose `break` fires before the endpoint under either model).

Breakdown: `tak` loops 25 (after exclusions; raw 27) +
`kosh` alias 4 + computed-float-into-`vitti` 2 = 31. The three
most likely are unchanged: 11_forloop, 36_descending, and the
alias growth site (now 288 as well as 255, both commented).

What changed, and what the refusal did and did not do:

- **Denominator 259 → 262** (three new files: 288, 289, 290).
- **Alias 3 → 4:** 288 is a fourth bare-alias site
  (`vitti a = k`, with an obstacle and a push) — my R84
  re-run script missed it because it reused R83's census,
  which predates 288. It is commented like the other three.
- **Float 0 → 2:** 93 and 94 (`vitti whole = blend(1.0, 4.0)`)
  store a computed `dasham` into a `vitti` and print 2, where
  a newcomer who does not yet know `vitti` truncates predicts
  2.5. These are old files, newly recognized as traps — the
  float finding came in R85, after R84's count. The name
  `whole` hints at the integer part and the golden pins 2, so
  a careful reader is warned; they count by the same rule as
  the commented alias probes.
- **The refusal removed zero traps from the count**, because
  the R84 count never included float traps. What it did is
  change the *kind* of trap for written fractions: on v278 a
  newcomer writing `vitti f = 3.5` got a silent wrong answer
  (3); on v279 they get a compile error (`E_DASHAM_VITTI`).
  The only written-fraction site in examples is 290 itself —
  the refusal's own demo, designed to fail. But the refusal
  did NOT remove the float trap class: computed floats into a
  `vitti` (93/94) still truncate silently on v279, so the class
  survives in its computed form.
- **Unwarned count unchanged at 25** (the `tak` files): the
  headline growth (28 → 31) is entirely probe files that warn
  the reader (commented alias sites, the named `whole`).

## NOT RUN

Windows, browser, implementation. All verification is Linux
(v279 ELF build). The `dasham` `tak` bound runaway is measured
within a one-second observation window (246,013 lines, never
passing the bound) — that is conclusive for "does not stop at
the bound", not a formal proof of non-termination. The float
`tak` bound refusal and the section's placement in the
reference belong to the owners.
