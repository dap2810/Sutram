# ROUND-88: the release-blocker census, and the honest number for the README

Base: origin/main at v279 (compiler `Sutram 1.0 (v279)`), tree
reset to `c807c6d9` before work. No tree changes. Deliverables in
`Muse-to-Sarvam/`: this report and `r88_census.json` (the division
and float-site data behind the counts). Method: static analysis
of all 24 library modules and all 262 example files (the brief
says 259 — the tree has 262 `examples/*.sm` now; the brief's
number is R84's, and the three new files are 288, 289, 290),
with every candidate then read by hand for guards and
never-zero divisors. A script count alone would have been wrong:
the first pass reported 28 dasham divisions with computed
divisors, and 23 of them are guarded or never zero.

## WS1 — the three counts

### 1. NaN comparison: ZERO — 0 examples, 0 modules

By the brief's definition (a program that divides by a computed
zero in `dasham` and then compares the result) and by the strict
definition (a program that can actually produce a NaN and
compare it with a wrong operator: `==`, `!=`, `<`, `<=`), the
count is **zero both ways**.

Why: only two `dasham` divisions in the whole tree can be zero
at runtime (see WS2: 118 and 289), and neither compares its
result. 118's `madhya` returns its quotient and the example
prints it; 289 prints its `inf` and its (mislabeled) "nan".
The two comparisons the strict scan flagged are on finite
values, not on division-by-zero results: `madhava_vargmool`'s
`<` compares the Newton iterate `g`, which is clamped to
`g >= 1.0` (and `v <= 0` returns early), so it can never be
`inf` or NaN; 133's `>` compares `s`, whose divisor
`ardh(x)` is `x / 2.0` with `x = 2.0`, so it is 1.0, never
zero. The one strict `inf - inf` pattern in the tree,
`dvitiya_pravan`'s `(dr - dl) / hm`, is guarded on all three
sides (`hl == 0`, `hr == 0`, `hm == 0` all return 0.0 before
their divisions), so `dr` and `dl` are finite and their
difference is finite, not NaN. And 289's `z / z` — which the
example labels "nan" — is `0.0 / 0.0`, which in Sutram is 0,
not NaN (verified in R84 and again here: the example prints
`0.000000` under the "nan" label, a mislabel, not a NaN).

So the NaN comparison bug is real (the brief's operator table
is confirmed: `==` 1, `!=` 0, `<` 1, `<=` 1 against IEEE's
`0 1 0 0`, with `>` and `>=` already correct) but currently
**unreachable** in the tree: no example and no library function
produces a NaN and compares it. That changes the priority
order, as the brief anticipated: this is a known-unreachable
blocker, not a live trap. Ship with it documented; do not
delay for it. (The R159 patch still matters for user programs
that do compute `inf - inf` and compare it — the tree just
does not contain one.)

### 2. Computed float-to-integer: FIVE — 2 examples, 3 library functions

`vitti x = <dasham expression>` (computed, not a bare written
fraction — written fractions are refused on v279 and are not
counted): **5 sites**.

- Library (3, all deliberate): `madhava_sin` (`k = x / pi2`,
  the period count for range reduction), `madhava_cos` (same),
  `roop_sthir_mool` (`rounded = scaled`, the half-away rounding
  step). In all three the truncation is the mechanism, not a
  mistake (R85).
- Examples (2, both the same pattern): 93 and 94
  (`vitti whole = blend(1.0, 4.0)` → prints 2, where a newcomer
  who does not yet know `vitti` truncates predicts 2.5). The
  name `whole` hints at the integer part and the golden pins
  2, so a careful reader is warned — but the pattern is the
  trap for a newcomer, and it survives v279 (computed
  truncation is still silent).

Priority input, not just a count: if the fix refuses computed
truncation the way v279 refuses written fractions, all five
sites break and need rewriting — including two core library
functions (`madhava_sin`, `madhava_cos`) whose range reduction
depends on it. The fix needs an explicit conversion (or an
explicit "truncate" form) first, or it is a breaking change to
the library's own core.

### 3. `inf`/`nan` printed: TWO examples, ZERO modules — and no real NaN printed anywhere

`likha` of a division that can be zero: **2 example files,
0 library modules** (no library function prints a division
result at all — the library returns values; only examples
print).

- **289** (`289_r87_float_print.sm`): prints `inf`
  deliberately — `dasham z = 0.0; dasham inf = 1.0 / z;
  likha("inf ", inf, ...)`. This is the printer demo from
  R87, and it is the only program in the tree that prints
  `inf` on its own inputs. It also prints `z / z` under the
  label "nan" — but that value is 0, not NaN (see above).
- **118** (`118_t18_kosh_param.sm`): prints
  `likha(madhya(mulya))`, where its local `madhya` divides by
  `kosh_len(a)` with no empty check. On the example's own
  inputs `mulya` has 3 elements, so it prints 2.0, not `inf` —
  but any caller passing an empty `kosh` would get `inf`
  printed. It is the one unguarded `dasham` divisor in the
  tree that is not a deliberate demo.

**No program prints a real NaN.** The only NaN-producing
arithmetic in the language (`inf - inf`, `inf / inf`) appears
nowhere in examples or library, and `0.0 / 0.0` is 0. So the
`nan` half of this blocker is, like the NaN comparison,
currently unreachable; the `inf` half is one deliberate demo
plus one unguarded helper.

## WS2 — every place a divisor can be zero at runtime

**`dasham` divisors (the silent-`inf` ones): exactly two.**

1. `examples/118_t18_kosh_param.sm`, local `madhya`:
   `sarva_yog / kosh_len(a)` — `a` is a caller-supplied
   `kosh`, and an empty `kosh` makes the divisor 0. Unguarded
   (contrast the library's `sankhyiki.madhya`, which returns
   0.0 for an empty `kosh`). Does not trigger as written
   (`mulya` has 3 elements).
2. `examples/289_r87_float_print.sm`:
   `1.0 / z` with `z = 0.0` (deliberate — the printer demo)
   and `z / z` (which is 0, not NaN, and is printed under a
   "nan" label that is wrong).

That is the complete list. Every other `dasham` division with
a computed divisor in the tree is either guarded or never
zero, and the guards are explicit in the code (this is the
hand-checked part of the census, and it is why the script's
28 candidates collapse to 2):

- Guarded (zero check returns 0.0 before dividing):
  `kalana.pravan` (`dx == 0.0`), `kalana.dvitiya_pravan`
  (`hl`, `hr`, `hm` all checked), `sankhyiki.madhya` and
  `prasaran` (`n == 0`), `kalana.simpson` (`n < 3` returns
  early to `trapiz`, so `n - 1 >= 2` on the division path).
- Never zero (named constants, constant-derived values,
  branch conditions, or index formulas `>= 1`):
  `madhava_sin`/`cos` (`pi2` = 6.283...),
  `madhava_atan` (`ax` only when `ax > 1.0`; `2.0 * k + 1.0`
  with `k >= 0`), `madhava_vargmool` and
  `sankhyiki_vargmool` (`v <= 0` returns early, so `g > 0`
  on the division path), `madhava_pi` and the series examples
  (`root12` = sqrt(12), `denom = 2 * k + 1`), and the
  performance examples' divisors (`b`, `e`, `q`, `a`, `c`,
  `weight`, `gun_maap`, `ardh(x)`, `dasham_nirm(0.5)`) — all
  set to nonzero constants or computed-nonzero values on
  every path, read one by one.

**Integer divisors (a different, handled case): 53** with
computed divisors across library and examples (most:
`lib/ganita.smlib` 14, `lib/chandas.smlib` 5,
`lib/ganit.smlib` 5). These stop with `E_SHUNYA_BHAJAN` and
the line if zero — they are not silent, so they are not the
`inf` case, but they are places where a divisor can be zero
and the program stops by design (v276+).

**Literal-zero divisors: 0.** No program in examples or
library divides by a literal `0` or `0.0`. The brief's
`5.0 / 0.0` is a probe, not a tree program.

**So the brief's distinction resolves in favour of the
language, not against the library: there is no bug in our own
library here.** The library has zero `dasham` divisors that
can be zero (every one is guarded or never zero); the two
`dasham` cases are one deliberate demo and one unguarded
example helper that does not trigger as written. What remains
is a language semantic that has not been decided — `dasham`
division by zero silently yields `inf` (and, via `inf - inf`,
a NaN that then compares wrongly) — with no library code
tripping over it.

## WS3 — the README sentence

> Still open, and stated plainly so you are not caught by
> them: comparing a not-a-number value gives the wrong answer,
> a computed decimal stored into an integer silently loses its
> fraction, and dividing by zero in decimals prints 'inf'
> without explaining it — anything else that surprises you is
> worth reporting as a bug.

**I would sign my name to it.** Each clause is verified on
v279: the NaN operator table (the brief's, confirmed in R85:
`nan == 5` true, `nan != 5` false), the computed truncation
(the brief's `dasham d = 3.7; vitti i = d` → `i = 3`, and the
five sites above), and the silent `inf` (`5.0 / 0.0` prints
`inf` with no message). The sentence does not claim the
library is affected — and the census shows it is not, for
NaN and for `inf` (the library's `dasham` divisors are all
guarded or never zero) — so it warns about behaviours, not
about live traps in the book's own code. The closing clause
is deliberate: it does not claim everything else is perfect
(the float `tak` bound from R86, the aliasing divergence,
and the Tier-2 wraps are all still open and documented
elsewhere); it invites a report instead, which is what makes
the rest trustworthy.

## NOT RUN

Windows, browser, implementation. The census is static
analysis plus hand-reading of every candidate (guards and
divisor assignments read in the source, not inferred from
the script's output); no tree program was run for new
behaviour except the brief's own verified cases, which were
taken as stated. The NaN-unreachable verdict is a statement
about the current tree (262 examples, 24 modules) — a user
program that computes `inf - inf` and compares it will still
hit the bug, which is why the R159 patch matters even though
the count is zero.
