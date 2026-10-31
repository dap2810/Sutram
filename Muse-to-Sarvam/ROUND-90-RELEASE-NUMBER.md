# ROUND-90: the number that decides the release note

Base: origin/main at v281 (compiler `Sutram 1.0 (v281)`),
tree reset to `7680d4ca` before work. No tree changes.
Deliverables in `Muse-to-Sarvam/`: this report and
`r90_probes.json` (the v281 probe outcomes). Method, as
in R88/R89: a script pass over the whole tree (267
examples, 24 modules, 306 functions), every candidate
read by hand, then the decisive cases run. The suite on
v281 is `PASS=263, NO-EXPECTATION=4, 0 fail` — which
matters for WS1, because it means the v281 conversion
fix broke nothing in the tree: every in-tree conversion
site was fixed to a whole value first.

## WS1 — wrong answers by arithmetic path, after v281

Three numbers, as asked — and all three wrong-answer
numbers are **zero**. That is not a shrug; each zero was
counted, and the reachability behind each zero is given
so the zero can be checked.

### 1. Overflow to non-finite: wrong answers 0; programs reaching non-finite 3, all deliberate

No program in the tree mistakes a non-finite value for a
finite answer. Three programs reach `inf`/`nan`, all
deliberately, as fixtures or demos:

- **289** (`289_r87_float_print.sm`): prints `inf` and
  `nan` (via the overflow loop, rewritten in v280),
  including the scientific line `1.234568e+22`. Matches
  its golden, exit 0.
- **291** (`291_r90_nan_compare.sm`): builds `inf` by
  overflow, `nan` by `inf - inf`, and prints the IEEE
  comparison table. Matches its golden, exit 0.
- **294** (`294_r160_nan_comparisons.sm`, new in v281):
  builds `inf` by squaring `1e20` four times
  (`1e20 → 1e40 → 1e80 → 1e160 → inf`), `nan` by
  `inf - inf`, and prints the six IEEE comparisons.
  Matches its golden, exit 0.

No other program reaches non-finite on its own inputs.
Checked as in R89: no literal in the tree has 30 or more
digits (so no literal is near the ~1.8e308 boundary);
the only `dasham` multiplications inside loops are the
three deliberate loops above, plus two library
accumulations that do not overflow on tree inputs
(`roop_sthir_mool`'s `p10f`, guarded — see below;
`vakyank.varna_tak_dashm`'s per-digit `* 10.0`, fed
only short inputs in the tree).

But the language path is still open, and it was run on
v281: the 10.0 loop prints `inf`, then `inf - inf`
prints `nan`, with no message and no refusal. A
400-digit literal prints `inf` and the program carries
on. So "overflow to non-finite" as a *behaviour* is
still silently available; as a *wrong answer in the
tree* it is 0, because the only three programs that use
it use it on purpose, correctly.

### 2. Conversion: wrong answers 0; silent truncation is closed

v281 refuses a non-whole `dasham` stored as a whole
number, in every checked place — not just `vitti`
assignment. Probed on v281, all with `E_DASHAM_VITTI`
(`dashama-phalam purnanka-seemayam na bhavati`), exit 1:

- `dasham d = 3.7; vitti i = d` → refused (the brief's
  case, confirmed; "reached" not printed).
- `vitti i = inf` (inf built by overflow) → refused
  (so a non-finite value cannot sneak into a `vitti`
  either).
- Passing `3.7` to an untyped function parameter used as
  an integer → refused (argument conversion is checked
  too, not just assignment).
- Storing `4.8` into an integer `kosh` element → refused
  (the 112 pattern; `kosh` stores are checked).

And whole values still convert, correctly:
`3.0 → vitti` gives 3, `7.5 / 2.0` stays `3.750000` as a
`dasham`, and the R88 census re-run on v281 finds five
`vitti` candidates — all now correct or refusing, none
truncating: `roop_sthir_mool`'s `rounded = scaled`
(`scaled` is now made whole first, by the same
`(s + 2^52) - 2^52` trick as Madhava, so it converts a
whole value); 93/94's `whole = blend(1.0, 3.0)` (= 2.0,
whole, converts); 295's `a = whole` (= 3.0, converts)
and `i = d` (= 3.7, refuses — the deliberate demo).
The two Madhava sites are gone entirely (`k` is now a
`dasham`, truncated explicitly in `dasham` arithmetic,
with the comment "same k, bit for bit, as the old
`vitti` k"). The suite passing 263/263 confirms no
in-tree program was left truncating by accident: every
site was fixed to a whole value in the v281 change
itself.

One mechanism sits *outside* the conversion check, and
it is reported here so it is not mistaken for a fourth
zero: storing a `dasham` into a `mala` element does not
convert and does not refuse — it stores the raw bits.
Probed on v281: `mala a[2]; a[0] = 3.7` (dasham var)
then `likha(a[0])` prints `4615514078110652826` (the
float64 bit pattern of 3.7, read back as an integer),
exit 0. No conversion is attempted, so this is not a
conversion wrong-answer in the sense of the other three
numbers — it is a raw qword store, like `nirmmita` cells
— but a student who stores a `dasham` in a `mala` and
reads it as an integer will get bits, silently. Tree
count for that trap: **0** (a scan of every
`name[i] = <dasham>` store in examples and library
found only `kosh dasham` stores, which are correct
float stores — including the three look-alikes
`ank_mala`, kalana `ok`, and samanvaya `out`, all of
which are `kosh dasham`, not `mala`).

### 3. Division by zero: wrong answers 0; refusals 2 patterns, both deliberate or guarded

Unchanged from v280, re-verified in the suite (293
passes): every `dasham` division by zero — literal,
computed, mixed, `0.0/0.0` — stops with
`E_SHUNYA_BHAJAN`, exit 1, and every integer division
by zero does the same (v276). The two `dasham`
zero-divisor patterns in the tree are 293 (computed
zero, deliberate demo, refuses) and 118's helper (empty
`kosh`, potential only — on its own inputs it prints
2.0, and on an empty `kosh` it now refuses, proved in
R89). So division produces no wrong answer and no
non-finite value on v281; it produces a named stop.

**So the three numbers are 0, 0, 0** — for wrong
answers. The reachability behind them is: overflow 3
deliberate, conversion 2 refusal demos (295, 112) plus
whole-converting sites, division 2 refusing patterns.
One scope note, so the zeros are not over-read: these
three numbers do not include integer `int64` wraps
producing finite wrong answers (the R80/R81 Tier-2
wraps — `dvigun`, `trigun`, `vardh`, and friends — are
still open and documented elsewhere). Within the three
paths the brief named, there is no silent wrong answer
left in the tree.

## WS2 — scientific notation: 1 example, and it IS documented

**How many examples print a value in scientific
notation? One, on its own inputs: 289** (the line
`above 2^63 1.234568e+22`). Method: every golden in
`tests/expect/*.out` and `tests/stdlib/*.out` was
searched for the scientific pattern
(`digit.digits e±digits`) — one file matched, 289 —
and the four no-expectation examples (215, 216, 217,
219) were run and their outputs searched the same way —
none matched. (Since the suite passes 263/263, goldens
equal actual outputs for suite-covered examples, so the
golden search is an output search, not just a file
search.) Scope, stated plainly: with a large enough
input, *any* example that prints a `dasham` would print
scientifically — the count of 1 is for the examples'
own inputs, which is the count a student actually meets.

**Is the format documented? Yes — in §15, fully.** The
paragraph "How `likha` prints a `dasham` (v279)" states:
six decimal places, rounded, for every value below
2⁶³ (9.2×10¹⁸); from 2⁶³ up, `d.dddddde+N`
(`1.234568e+22`); infinities print `inf` and `-inf`;
NaN prints `nan`; and `examples/289` pins the printer.
§15 also states the complementary literal rule, which
matters for the brief's shorthand: there is *no*
scientific notation in literals (`1e5` is refused).
Probed on v281, the documentation matches exactly:
`9e18` prints fixed, `9.999e18` (above 2⁶³) prints
`1.000000e+19`, `1e20` squared twice prints
`1.000000e+80` (the brief's case, reproduced), negative
large values print `-1.000000e+20`, and small values
stay fixed at six decimals (`0.0000001` prints
`0.000000` — rounding, not scientific, for small values).
And the brief's `1e20` is shorthand, not syntax: on
v281 `dasham h = 1e20` is a compile error
(`E_UNDEFINED_NAME: agyat naam 'e20'`) — a student
must write the full decimal, as 294 does
(`100000000000000000000.0`).

So the premise of the WS2 question does not hold on
the current tree: the format is documented, the
threshold and the mantissa format are stated, and the
one example that prints it is the one the reference
points to. That is not a gap a student hits in week
one — it is a documented behaviour with one pinning
example. (If the question is really "is it documented
*prominently enough* for week one", §15 is where a
student reading about floats would find it, which is
the right place; no change is proposed here.)

## WS3 — the README sentence, for v281 (asked a third time)

This sentence has now been sent three times — R88,
R89-updated, and now v281 — not because it was missed
each time, but because each compiler version changed
what is true, and sending a stale sentence above the
fold would be worse than resending. v280 closed NaN
comparison and division-by-zero; v281 closed
conversion. The sentence shrinks as the work lands,
which is itself the trust mechanism. If the question
is wrong in any way, it is only in scope: this sentence
is for the README above the fold, i.e. for a student
meeting the language — so it covers student-facing
surprises, not the full open-issues list (parikshita
marking at 0/306, Tier-2 wraps, and the rest belong in
the release notes and the reference, not in one line).
Within that scope, here it is for v281:

> Still open, and stated plainly so you are not caught
> by them: a decimal that grows past the largest finite
> value silently becomes infinity, and a decimal loop
> bound never terminates — anything else that surprises
> you is worth reporting as a bug.

**I would sign my name to it.** Both clauses were
verified on v281 in this round: overflow (the 10.0 loop
prints `inf`, the 400-digit literal prints `inf`,
neither with a message), and the decimal loop bound
(`chakra i = 0 tak 3.5` printed 235,734 lines in one
second on v281 and never stopped — the R86 sixth,
still open). The closing clause is deliberate, as
before: it does not claim everything else is perfect,
it invites a report. And the sentence is now two
clauses instead of three because v281 earned the
deletion — a reader who watched the sentence shrink
from R88 to R90 has a reason to trust the next version
too.

## NOT RUN

Windows, browser, implementation. The string-parse
overflow and the `mala` raw-store mechanism were
probed (mala) or hand-read (string parse, as in R89);
everything else in WS1–WS3 was run on v281 (Linux ELF
build), including the full suite (263 pass, 4
no-expectation, 0 fail). Marking the 63, an overflow
refusal or message, a `tak`-bound refusal, and a
`mala`-store check belong to the owners.
