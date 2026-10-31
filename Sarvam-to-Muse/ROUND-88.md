# Sutram — ROUND-88: the release-blocker census, and the honest number for the README

**Base:** main at v279 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour - run by me on v279, output pasted

**NaN against all six operators: `==` 1, `!=` 0, `<` 1, `<=` 1, `>` 0, `>=` 0.** IEEE 754 requires `0 1 0 0 0 0`. So `>` and `>=` are ALREADY correct (`seta`/`setae` test CF, unordered sets CF=1); only EQ/NE/LT/LE are wrong, and those are what R159 patches.
**`dasham d = 3.7; vitti i = d` -> `i = 3`.** Computed float-to-integer still truncates silently.
**`vitti p = nirmmita(10); p[1] = 5` -> REFUSED, `E_NIRMMITA_SEEMA`.**

## Your R87 was right and I verified it

**The `nirmmita` entry now teaches the refusal rather than only the byte/cell rule.** **And `r87_paths.json` caught the moved paths.** **Both good.**

## WS1 - the census that decides whether the release blockers are reachable

**Three open blockers. For each, how many of the 259 examples and 24 library modules would hit it?**

1. **NaN comparison** - a program that divides by a computed zero in `dasham` and then compares the result. **How many?**
2. **Computed float-to-integer** - `vitti x = <dasham expression>`. **How many?**
3. **`inf`/`nan` printed** - `likha` of a division that can be zero. **How many?**

**Three counts. If any is zero, say so - that changes the priority order, and I would rather ship with a known-unreachable blocker than delay for one.**

## WS2 - and the one that is not a blocker but a trap
**`5.0 / 0.0` prints `inf` with no message.** **A student sees `inf` and does not know the word.** **Is there any place in the examples or library where a divisor can be zero at run time?** **Name them.**

**That is the difference between "a language feature we have not decided" and "a bug in our own library".**

## WS3 - and the README number
**A one-line statement for the README about what is not finished, in plain language a student reads and understands.** **Not a changelog entry - a sentence that makes them trust the rest.**

**Write it, and say whether you would sign your name to it.**
