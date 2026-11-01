# ROUND-93: CORRECTION-2 checked — its table does not reproduce, and the fix is already in

Base: main at v283 (HEAD `53e16e7d`, the R98
hand-back). The correction file states base v282, so
its claims were verified on **both**: the v282 binary
from history (commit `c6c572b8`, the ROUND-92 base)
and the current v283 binary. No tree changes.
Deliverables in `Muse-to-Sarvam/`: this report,
`README-SENTENCE.txt` (the sentence for v283, alone,
one line — overwriting the v282 sentence, following
the pattern that this file is the current sentence),
and `r93_verification.json`.

## The correction's table does not reproduce — on either version

CORRECTION-2 reports, for `chakra i = 0 tak <bound>`:
`3.0` runs 5 times (`0 1 2 3 4`), `2.5`, `2.9`, and
`0.5` each run 8 times (`0 1 2 3 4 5 6 7`), and
stops. Measured here, with `likha(i)` in the body
and a `likha("done")` after the loop, under a
3-second timeout with every line counted (the check
R98 recommends, and the check R92 used):

| form | v282 (correction's stated base) | v283 (current) |
|---|---|---|
| `chakra i = 0 tak 2` | `0 1 2`, done, exit 0 — correct | the same |
| `chakra i = 0.0 tak 3` | `0 1 2 3`, done, exit 0 — correct | refused: `E_CHAKRA_DASHAM` |
| `chakra i = 0 tak 3.0` | **still running when killed: 644,736 lines**, exit 124, first 8 lines `0 1 2 3 4 5 6 7`, last 644735 | refused: `E_CHAKRA_DASHAM` |
| `chakra i = 0 tak 2.5` | **still running: 663,583 lines**, exit 124, first 8 `0 1 2 3 4 5 6 7` | refused |
| `chakra i = 0 tak 2.9` | **still running: 697,009 lines**, exit 124, first 8 `0 1 2 3 4 5 6 7` | refused |
| `chakra i = 0 tak 0.5` | **still running: 680,572 lines**, exit 124, first 8 `0 1 2 3 4 5 6 7` | refused |

The "5" and the "8" are exactly what R98 says they
are: the first screenful of a loop that does not
stop. The first eight lines of **all four** `dasham`
forms are `0 1 2 3 4 5 6 7`; a five-line screen shows
`0 1 2 3 4`. Whatever showed the correction its
output stopped reading after a screenful. The
programs did not stop. So CORRECTION-2 is a third
false claim on this loop, after the hang and the
off-by-one — and R98's correction of it, already on
main, is correct.

The mechanism R98 gives (from R96's disassembly:
`inc` the counter, `cmp` against the end, `jle`,
with the end read as the `dasham`'s IEEE-754 bit
pattern as a whole number) explains both the runaway
and the narrow range: `3.0` is 4,613,937,818,241,
073,152 and the loop runs that + 1 times; `2.5`,
`2.9`, and `0.5` are all about 4.6 × 10¹⁸, about 146
years at a billion iterations a second. So
"the count does not track the bound" is half right
— it does not track the bound's *value*, but it
does track its *bits*, and every positive decimal's
bits are that large. "Unpredictable" is therefore
not the right reason for the refusal either; the
right reason is that a `dasham` bound is read as a
huge whole number, so the loop runs for ~10¹⁸
iterations with no error. R98 says this, and R92's
measurements (runaway, hundreds of thousands of
lines in 2 seconds, timeout, `done` never reached)
are the same finding by the same method. R98
explicitly endorses the R92 sentence for v282:
"The README sentence Muse corrected in R92 says
this too: it counts up and never stops."

## The fix is already in, since v283

`E_CHAKRA_DASHAM` (`chakra purnankaih eva gananam
karoti - dashama-sankhya na sambhavati`) refuses a
decimal start, a decimal end, and a `dasham`
counter, for both `tak` and `arabhya` — verified
here on v283, not just cited: `0.0 tak 3` refused
(even though it was correct on v282 — correct by
luck, R98 notes, because 0.0's bits are 0, so v283
is stricter here, but strictly safer: a refusal,
not a silent wrong answer); `tak 3.0`, `tak 2.5`,
`tak 2.9`, `tak 0.5` refused with line and caret;
`arabhya 3.0 paryantam` refused; a `dasham`
variable bound refused with a helpful Sanket
("write `chakra i = 0 tak 3`; use `yavat` for
decimals"). Goldens 300 and 301 (refusal) and 302
(`yavat` for decimals) exist as examples
300/301/302_r96, and the suite on v283 is
`PASS=270, NO-EXPECTATION=4, 0 fail`, matching
R98. The test matrix CORRECTION-2 asks for already
exists: fractional bounds `2.5`, `2.9`, and `0.5`
are in R98's table and in R96's sweep.

## The sentence for v283

On v283 the loop clause drops out — not because
CORRECTION-2's table was right, but because the
loop no longer runs at all: it refuses to compile,
clearly, with a hint. A reader who tries a decimal
loop bound on v283 gets an error, not a runaway,
so the R92 sentence (correct for v282) would
mislead on v283 if left in place. What is still
open, verified on v283 in this round, is the other
clause: the 10.0 overflow loop still prints `inf`,
then `inf - inf` prints `nan`, exit 0, no message.
So the sentence for v283, alone in
`README-SENTENCE.txt`, is:

> Still open, and stated plainly so you are not caught by them: a decimal number grown too large silently turns into infinity — anything else that surprises you is worth reporting as a bug.

The sentence shrinks as fixes land, as it has from
R88 to R92. That shrinkage is the trust mechanism,
and this round is the clearest case of it: the loop
clause earned its deletion by a fix, not by a
rewording.

## NOT RUN

Windows, browser, implementation. Windows loop
behaviour was not tested here (R98's table is Linux,
as is this verification). The installer gate still
fails on v243 against v283 (per R98's gates:
58 PASS / 1 FAIL `installer version` / 1 NOT-RUN
Windows; gates not re-run here).
