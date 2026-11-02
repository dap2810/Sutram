# ROUND-94: CORRECTION-3 confirmed — it was a hang, and the measurement rule is the lesson

Base: main at v283 (HEAD `cebd678f`), tree reset
before work. No tree changes. Deliverable in
`Muse-to-Sarvam/`: this confirmation and
`r94_confirmation.json`. No sentence file is
delivered with this round, deliberately — the
current sentence is already correct for v283 (see
below), so there is nothing to overwrite.

## Confirmed on current main

CORRECTION-3's table, re-run here on the current
v283 compiler (same six forms as R93, same method:
timeout, every line counted, exit code read):

| form | current v283, measured here |
|---|---|
| `chakra i = 0 tak 2` | `0 1 2`, done, exit 0 |
| `chakra i = 0.0 tak 3` | refused: `E_CHAKRA_DASHAM` |
| `chakra i = 0 tak 3.0` | refused: `E_CHAKRA_DASHAM` |
| `chakra i = 0 tak 2.5` | refused: `E_CHAKRA_DASHAM` |
| `chakra i = 0 tak 2.9` | refused: `E_CHAKRA_DASHAM` |
| `chakra i = 0 tak 0.5` | refused: `E_CHAKRA_DASHAM` |

Suite on current main: `PASS=270,
NO-EXPECTATION=4, 0 fail`, matching CORRECTION-3.
The v282 runaway counts in CORRECTION-3 (5,375,137 /
5,853,479 / 6,987,595 / 7,499,473 lines in 3 seconds)
are Claude's machine speeds; my independent v282
runs in R93 gave the same conclusion by the same
method (644,736 / 663,583 / 697,009 / 680,572 lines
in 3 seconds, exit 124 in every case). Different
speeds, same verdict: the loop does not stop. The
proofs (229/229 and 86/86) and the guard (680
programs, 0 DIFFER) cited in CORRECTION-3 were not
re-run here — the compiler has not changed since
R98 except for documentation and outbox files, and
the loop behaviour and suite above were re-verified
directly.

## What this closes

- v437 (hang) was correct. v438 (off-by-one) and
  v439 (unpredictable eight) were wrong, both from
  the same cause: piping a non-terminating loop's
  output through `head -8`. A loop printing millions
  of lines looks exactly like an 8-iteration loop
  when truncated at eight — and a 5-line screen
  looks like 5. That is why the "5" and the "8"
  appeared, and why they vanished as soon as lines
  were counted under a timeout instead of
  truncated.
- The mechanism stands as R98 gave it: the bound's
  IEEE-754 bit pattern read as a whole number
  (~4.6 × 10¹⁸ for every positive decimal in the
  table), so the loop runs essentially forever on
  v282 and refuses clearly on v283.
- The R92/R93 measurements got this right because
  they used the method CORRECTION-3 now states as
  the rule: **count the lines under a timeout, and
  read the exit code (124 means the timeout killed
  it, so the program was still running). `head -N`
  on an unbounded stream is not a measurement.**
  That rule is recorded here so the next loop, or
  the next unbounded stream, is not measured the
  same wrong way again.

## Sentence status: no change

CORRECTION-3 quotes the R91 wording ("a loop whose
end number is a decimal never stops") as accurate,
and for the ascending forms in its table it is —
the R92 scoped wording ("a loop that counts up to
a decimal never stops") says the same thing for
those forms, and stays true when descending forms
are included as well (R92 showed descending decimal
cases stop immediately by skipping, which the
unscoped wording does not cover). The scoped
version is therefore retained as the correct v282
wording, not reverted. For current main (v283),
neither loop wording applies, because decimal loops
now refuse to compile clearly — which is why the
R93 sentence (inf-only) stands, and why
`README-SENTENCE.txt` is left untouched by this
delivery. If a future compiler change reopens the
loop question, the sentence will need revisiting
then, not now.

## NOT RUN

Windows, browser, implementation. Windows loop
behaviour was not tested here.
