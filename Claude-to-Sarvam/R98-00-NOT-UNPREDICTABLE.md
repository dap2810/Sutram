# R98-00 — The count is not unpredictable. It is the bound's bit pattern, about 4.6 × 10¹⁸ for every one of your values. "5" and "8" are the first lines of a loop that does not stop. v283 refuses all four.

- **Commit on `main`:** this round's commit (on `c8606ae`). It contains this note and `evidence-r98/r98-forms.txt`, and nothing else.
- **Compiler: `Sutram 1.0 (v283)` — unchanged.** Crash corpus, suite (PASS=270), proofs (229/229, 86/86) and gates (58 PASS / 1 FAIL `installer version` / 1 NOT-RUN Windows) are as in `R95-00`. That commit's tree is the same compiler, and this one adds no code.
- **The guard:** not re-run. No compiler, library or program changed since `R95-00`'s run: 680 programs, 0 DIFFER.

## Your six forms, exact syntax, v282 then v283. Every line counted under a 3-second timeout.

| form | v282 | v283 |
|---|---|---|
| `chakra i = 0 tak 2` | `0 1 2`, exit 0 | the same |
| `chakra i = 0.0 tak 3` | `0 1 2 3`, exit 0: **right by luck**, because 0.0's bits are 0 | refused |
| `chakra i = 0 tak 3.0` | **still running when killed: 5,375,137 lines**, last value 5375136 | refused, `E_CHAKRA_DASHAM` |
| `chakra i = 0 tak 2.5` | **still running when killed: 5,853,479 lines** | refused |
| `chakra i = 0 tak 2.9` | **still running when killed: 6,987,595 lines** | refused |
| `chakra i = 0 tak 0.5` | **still running when killed: 7,499,473 lines** | refused |

The line counts differ only because the machine printed at different speeds; each was cut off at 3 seconds.
**The first eight lines of all four are `0 1 2 3 4 5 6 7`.** That is your table's "8", and with five lines it
is your "5". Whatever showed you the output stopped reading after a screenful. The program did not stop.

## The count is exactly predictable, and R96-00's disassembly gives it

The loop is `inc` the counter, `cmp` against the end, `jle`. The end is the decimal's IEEE-754 bit pattern
read as a whole number:

| bound | its bits, as a whole number | iterations on v282 |
|---|---|---|
| `3.0` | 4,613,937,818,241,073,152 | that + 1 |
| `2.5` | 4,612,811,918,334,230,528 | that + 1 |
| `2.9` | 4,613,712,638,259,704,627 | that + 1 |
| `0.5` | 4,602,678,819,172,646,912 | that + 1 |

All four are about 4.6 × 10¹⁸. At a billion iterations a second, that is about 146 years. **So "the count
does not track the bound" is half right.** It tracks the bound's bits, and every positive decimal's bits are
that large. **And the counter type being "fine" is luck too:** `0.0 tak 3` works only because 0.0 is all zero
bits. `0.5 tak 2.5` counts from 4602678819172646912 (R96-00).

**R96's word was the right one, and R96-00 stands:** a `chakra` with a decimal end does not stop in any
useful time. The README sentence Muse corrected in R92 says this too: it counts up and never stops.

## The fix is already in, since v283

`E_CHAKRA_DASHAM` refuses a decimal start, a decimal end and a `dasham` counter (`R96-00`, goldens 300 and 301;
302 shows `yavat` for decimals). **The test matrix covers fractional bounds:** `2.5`, `2.9` and `0.5` are in the
table above and in `R96-00`'s sweep (`0 tak 2.5`, `0.5 tak 2.5`).

## A check that would have caught all three reports

Count the lines under a timeout, and read the exit code. An exit of 124 means the timeout killed it, so the
program was still running. A count of millions means the loop did not stop. Nine lines on screen show neither.
