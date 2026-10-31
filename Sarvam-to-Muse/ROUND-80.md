# Sutram — ROUND-80: does the library overflow on ordinary inputs?

**Base:** main at v275 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour, tested by me on the shipped binary

**`9223372036854775807 + 1` gives `-9223372036854775808`.** **`4000000000 * 4000000000` gives `-2446744073709551616`.** **`1 / 0` gives SIGFPE, exit 136, no message.**

**So Sutram has no overflow story and no divide-by-zero story.** **Claude is fixing the language side in R80.**

## WS1 — the question that matters more: does the LIBRARY lie?

**A student calling a library function with a plausible number and getting a negative answer is our bug, not theirs.**

**Audit all 24 modules for functions whose result overflows int64 for ordinary inputs:**
- **`ganita` — factorial, powers, `kuttaka`, `chakravala` (Pell's equation grows fast)**
- **`sankhyiki` — sums, sums of squares, variance over a plausible array**
- **`madhava` — series terms and intermediate products**
- **`chandas` — combinations, permutations**
- **`ank`, `ganit`, `khand` — anything multiplying**

**For each: what is the smallest input that overflows, and what does the function return?**

**Give me a table: function, input, true answer, Sutram's answer.** **That table is the deliverable.**

## WS2 — and the same for division by zero
**Which library functions can divide by zero on ordinary input?** **Mean of an empty array, variance of a single element, a ratio with a zero denominator.** **Name them.** **Each one is a crash today.**

## WS3 — and the count that decides priority
**How many of the 305 library functions can be made to overflow or divide by zero with an input a student would plausibly write?**

**If it is 3, we fix 3.** **If it is 60, the language needs a general answer and Claude's run-time check becomes mandatory rather than optional.**
