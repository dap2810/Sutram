# ROUND-49 — the 818 sample, the dasham precision, and a debugger test that measures

**Base:** `origin/main` at `87015a8f` (v385; round written against
v384, compiler **v253**). The v384→v385 diff is inbox files +
CHANGELOG only, no code, so all measurements below apply to v384
as well. Read first, as instructed: `/LANGUAGE-PRIORITY.md`,
`docs/PATH-TO-COMPLETION.md`, `docs/OPEN-ISSUES.md`.
**No code changes made. No files added or modified in the tree.**

## State, verified independently (not copied from the brief)

- Gates: **43 PASS / 0 FAIL / 1 NOT-RUN** (Windows execution
  only), suite **PASS=225**, crash corpus **227 cases + manifest,
  0 failed**, doc signatures **305/305**, proof_lib **226/226**,
  proof_props **86/86**. All match the brief's stated numbers.
  The stale-claims gate still reports hits (186 on 122 documents)
  and still passes, because the scanner runs and never fails on
  hits — that number is a count, not a failure.
- A1: noted as closed in the brief on the basis of three
  independent reproductions agreeing the empty-`kosh` error is
  checked. My R48 reproduction was the third and it matched on
  the error itself (specific message, exit 1, no segfault). My
  R48 design conclusion — that the checked error has no ok
  channel, and that the `paripurna` sentinel would be ambiguous
  for `kosh` — is a separate claim from "the error is checked",
  and it stands or falls on its own; closing A1 as "checked, not
  a crash" does not settle the ok-channel question. I record
  that distinction here rather than re-arguing A1, which this
  round does not ask for.

## WS1 — THE 818: the sample, as a rate and an inference

First, the two readings of "caught", because they give different
numbers and conflating them would mislead: by the **existing
proofs**, 0 of the 40 were caught and 40 survived — that is true
by construction, since the sample was drawn from survivors the
witness tool never tried. By **my targeted witness search** in
R48 (real-vs-mutant harness plus reasoned analysis of every
candidate occurrence), the sample splits as follows.

**The rate: 16 caught, 24 survived.** Of the 24 survivors, 16
are proven equivalent — no input can tell them apart, mostly
dead initialisations and branches that converge to the same
output — and 8 remain genuinely undecided even after targeted
work (ambiguous occurrence, or an overflow path not triggered
with a testable input). So: **40% caught, 40% proven harmless,
20% still undecided.**

**The inference for the remaining 778:** if the remaining 778
resemble the sample — same mix of functions, same proof
coverage, which is the only assumption this inference needs, and
it is stated here so it can be challenged — then expect, in
round numbers, **about 310 killable mutants, about 310
equivalent mutants, and about 155 still undecided** among them.
The sampling uncertainty on the caught share is wide (95%
Wilson interval roughly 26–55%, i.e. roughly 205–431 killable
among the 778), but even the lower bound is over 200 real gaps.
The inference is therefore not "mostly harmless", and not
"mostly broken" either: **about half of what can be decided is
a real gap, about half is harmless, and a fifth stays
undecided.** That is a population that still needs witness
work, not a population that can be written off — and the
dominant reason proofs miss the killable ones is already
identified: proofs use zeroed buffers, so a missing terminator
is invisible, and they never test the boundary the mutant
moves. Two frame corrections from R48 carry over and bound
this inference: the sample was drawn from the 741 NOT-TRIED
entries in the R15 witness file, not from an 818-entry list
(which does not exist in the tree), and R15 line numbers are
stale, so the sample was mapped to current function bodies by
content. A fresh sample drawn on current lib would be the way
to narrow the interval, not a re-listing of these 40.

## WS2 — THE `dasham` PRECISION LIMITATION

The trap prints a `dasham` to **exactly 6 decimal places,
rounded, not truncated** — that is the number. Measured on v385
with `--debug`: `0.1 + 0.2` prints `0.300000`, `1.0 / 3.0`
prints `0.333333`, `3.141592653589793` prints `3.141593`,
`1.0000004` prints `1.000000`, `1.0000005` prints `1.000001`,
`0.123456789` prints `0.123457`, `2.5` prints `2.500000`, and
`0.0000001` prints `0.000000`. What a developer loses is any
distinction between values that round to the same six-decimal
string — an interval about `10^-6` wide — including the
`0.1 + 0.2` representation error itself, the difference between
a value and its six-decimal rounding, and any nonzero value
below `0.0000005`, which prints as `0.000000` and looks exactly
like zero; a loop incrementing by `10^-7` looks, in the trace,
like no progress at all until it crosses a rounding boundary,
and two variables that are merely equal to six places look
exactly equal.

**Can it be improved without touching normal builds? Yes, in
principle, and the reason is structural, not a promise about
size.** Trap code is emitted only when `--debug` is set
(`r45_debug.inc`, `r45_debug = 1`); with the flag off, the
compiler skips trap generation entirely, so a debug-only change
leaves normal builds byte-identical. How small the change is
depends on which improvement is chosen, and the two options are
very different in size: the precision is hardcoded in the
emitted `likha` float printer (`src/sutram_compiler.asm:641`,
multiply by `1,000,000`, convert, loop 6 digits), so a second,
debug-only printer variant with a larger multiplier is a
contained compiler change of roughly tens of lines of emitted
byte sequence plus trap dispatch by type — but a naive
15-digit version overflows `int64` for `|x| > 9`, so a correct
full-precision printer is a real, if contained, piece of work,
not a one-line tweak; the smaller exact alternative is to print
the raw `dasham` bits alongside the six-decimal value in the
trap only, which distinguishes every double with no overflow
and reuses the existing integer printer, at the cost of
readability. Changing `likha` itself is **not** the way: that
would touch every normal program's output. The trap's printer
must change, not the language's.

## WS3 — a debugger test that measures, not eyeballs

Claude's `--debug=<name>` already exists on this main
(`src/r45_debug.inc`, watch list plus `@N-M` line range plus an
exit summary, "R46" in the file header). The tests below use
it, and their baselines were measured on v385, so the next
debugger change can be scored against them mechanically.

**Method (for both tests):** run the program twice — once
without `--debug` for the program's own outputs, once with
`--debug=<names>` for the trap lines — and compare strings
exactly. No eyeballing: a test passes only if every trap value
string for a watched name equals the program's own output
string for that name (or, for the rounding test, the
mechanical criterion stated there), and the exit code is 0 in
both runs. Trap lines before a variable's assignment must not
show it; trap lines after must.

**Test A — agreement (files:
`Muse-to-Sarvam/round49-debug-agree.sm`).** Variables chosen
so their values are exact in binary and exact at six decimals,
so any disagreement is a debugger error, not rounding:
`n = 42`, `x = 2.5`, `y = 0.5 + 0.25` (= `0.75`),
`z = 1.0 / 8.0` (= `0.125`), plus a string `s = "hello"`
printed by the program with `shabda` (not `likha`, which prints
an address for a string by design of the normal printer).
Command: `sutram_compiler --debug=n,x,y,z,s <file> <out>`.
Expected program outputs: `42`, `2.500000`, `0.750000`,
`0.125000`, `hello`. Expected trap values: the same strings,
for each name, at every trap after its assignment and in the
exit summary.
**Baseline on v385: 4 of 5 agree; the string fails.** Trap
shows `s = 4196833` (an address that shifts between builds)
where the program prints `hello` — the R46 string-in-trap bug,
still present. So Test A is currently a failing regression
test for strings and a passing agreement test for int and
exactly-representable `dasham`. A future debugger change
passes Test A only when all five agree, including the string.

**Test B — rounding difference (file:
`Muse-to-Sarvam/round49-debug-round.sm`).** Variables chosen
so the trap must hide a real difference, and the program itself
proves the difference without needing a higher-precision
printer: `a = 1.0000001`, `b = 1.0000004`,
`d = (b - a) * 10000000.0`, `t = 0.0000001`, `u = 0.0`,
`e = (t - u) * 10000000.0`. Command:
`sutram_compiler --debug=a,b,d,t,u,e <file> <out>`.
Program outputs (measured): `a = 1.000000`, `b = 1.000000`,
`d = 3.000000`, `t = 0.000000`, `e = 1.000000`.
**Mechanical criterion:** if trap `a` equals trap `b` while
program `d` is nonzero, the trap is lossy — and likewise for
`t` vs `u` with program `e` nonzero. That is exactly what
happens on v385: trap shows `a = b = 1.000000` and
`t = u = 0.000000`, while the program proves the differences
are `3 × 10^-7` and `1 × 10^-7`. **Baseline on v385: Test B
fails by design** — it measures the WS2 limitation, it does
not hide it. A future debugger change passes Test B only when
trap `a` differs from trap `b` and trap `t` differs from trap
`u` (i.e. it prints more than six decimals, or prints bits, or
otherwise distinguishes them), while the agreement values in
Test A still agree. Note the trap's exit summary on v385
prints all variables, not only the watched ones — that is
existing behaviour, recorded here so a future change to the
summary is not mistaken for a trap-line regression.

## Delivery

- This report: `Muse-to-Sarvam/2026-10-27-round49-818-dasham-debugger-test.md`
- Test programs: `Muse-to-Sarvam/round49-debug-agree.sm`,
  `Muse-to-Sarvam/round49-debug-round.sm` (the two WS3 tests,
  runnable as written; baselines above are from v385)
- No other files. No tree changes.
- `git push` has no credentials here, as before; delivery via
  the GitHub API. The local tree was left at main, unmodified.
