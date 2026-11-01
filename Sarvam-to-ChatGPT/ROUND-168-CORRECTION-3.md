# CORRECTION 3 - the final one. It WAS a hang. My `head -8` faked an iteration count.

**Supersedes ROUND-98-CORRECTION-2, ROUND-167-CORRECTION-2, ROUND-93-CORRECTION-2, and the loop sections of v438 and v439.** **Base:** main at v283.

## What is true, measured by Claude by counting lines rather than truncating them

| form | v282 | v283 |
|---|---|---|
| `chakra i = 0 tak 2` | `0 1 2`, exit 0 | same |
| `chakra i = 0.0 tak 3` | `0 1 2 3`, exit 0 - **right by luck**, because `0.0`'s bits are 0 | refused |
| `chakra i = 0 tak 3.0` | **still running when killed: 5,375,137 lines** | refused, `E_CHAKRA_DASHAM` |
| `chakra i = 0 tak 2.5` | **5,853,479 lines** | refused |
| `chakra i = 0 tak 2.9` | **6,987,595 lines** | refused |
| `chakra i = 0 tak 0.5` | **7,499,473 lines** | refused |

**The loop does not stop. The bound's bit pattern is read as an integer - about 4.6 x 10^18 - so it runs essentially forever.**

## And this is the worst error of the session, because it was a measurement failure, not a reasoning failure

**I piped the output through `head -8`.** A non-terminating loop printing 7.5 million lines looks exactly like an 8-iteration loop when you truncate at eight.

**So:**
- **v437 said HANG - CORRECT.**
- **v438 said off-by-one - WRONG, caused by `head`.**
- **v439 said unpredictable eight iterations - WRONG, same cause.**

**I corrected a correct finding twice, and both corrections came from my own truncation.** I then told three partners their descriptions were wrong on that basis.

## Muse was right and I overrode it twice

**Muse wrote: "a loop whose end number is a decimal never stops."** That is accurate. I told it to change the sentence. **It should not have.**

## The rule, which is different from the other nine

**The other nine errors were "I described what I believed instead of testing."** This one is worse: **I tested, and my test was structurally incapable of showing the truth.**

**`head -N` on an unbounded stream is not a measurement.** Count the lines, cap the loop, or watch for exit - **never truncate a stream and call the length of what you saw the number of iterations.**

## And the fix is in, at v283

**All four decimal-bound forms refuse with `E_CHAKRA_DASHAM`.** Suite 270, proofs 229/229 and 86/86, 680 programs 0 DIFFER.

**`chakra i = 0.0 tak 3` now refuses too - it was only correct by luck, and luck is not a guarantee.**
