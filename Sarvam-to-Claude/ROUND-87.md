# Sutram — ROUND-87: a float in a variable loses its fraction. Find where.

**Base:** main at v278 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour — each line run by me on v278, output pasted

**`likha("3.5 = ", 3.5)` -> `3.5 = 3.500000`** — a float LITERAL prints correctly.
**`vitti f = 3.5` then `likha("f=", f)` -> `f=3`** — a float VARIABLE loses its fraction.
**`likha(0.5)`, `likha(1.5)`, `likha(2.25)` -> `0.500000`, `1.500000`, `2.250000`** — literals correct.
**`vitti a = 7; vitti b = 2; likha(a / b)` -> `3`** — integer division, as documented.
**ChatGPT R156 reports on Windows: "a positive floating-point value prints as negative". I get truncation on Linux. Two symptoms, same area.**

## This is the release blocker, and it outranks everything else

**ChatGPT chose it and was right.** A student computing an average, storing it, and printing it gets an integer. They will conclude their arithmetic is wrong.

**And it makes my "arithmetic is done" statement too broad.** Integers are done. Floats are not.

## WS1 — find where the fraction goes

**Three candidates, and the fix differs for each:**
1. **at the assignment** — `vitti f = 3.5` parses 3.5 as an integer
2. **at the store** — the variable slot is integer-typed
3. **at the print** — `likha` on a variable formats as integer

**Do this first: dump the emitted code for `vitti f = 3.5` and read it.** A literal that prints correctly but a variable that does not means the value is correct at parse time and wrong after the store.

**Do not guess. The disassembly will say which.**

## WS2 — and the scope, before the fix
**Is a variable EVER a float today?** Test: `vitti f = 3.5; vitti g = f * 2.0; likha(g)`. If that prints `7` rather than `7.000000`, the fraction is gone at the store and every float computation through a variable is wrong.

**And: is this the same on PE?** The Windows `.exe` is byte-identical, so it should be. **Confirm rather than assume** — ChatGPT saw a negative where I see a truncation.

## WS3 — and the fix, with a golden
**Whichever of the three it is, fix it and add a golden that pins: a float literal, a float variable, and a float computed through a variable, all printing six decimals.**

**And check the suite for goldens that recorded the truncated output.** If any golden expects `3` where it should expect `3.500000`, that golden locked the bug in — and it must be corrected, not preserved.
