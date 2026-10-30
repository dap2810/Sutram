# Sutram — ROUND-76: the 15 mutants, and the sign error in the Madhava series

**Base:** main at v273 · **Deliver into:** `Muse-to-Sarvam/`

## The hard task: real bugs in real mathematics

**There are 15 surviving mutants.** **One is a sign error in the Madhava trig functions.** **That is not a hypothetical — it is a wrong answer from a 600-year-old series, in a language whose whole purpose is teaching Indian mathematics.**

## WS1 — the Madhava sign error
**1. Find it.** **Which function, which term, which sign.**
**2. Write the test that would have caught it.** **A known value — `sin(pi/2) = 1`, `cos(0) = 1` — to enough digits that a sign error is visible.**
**3. And check the rest of `lib/madhava.smlib` for the same class: does every alternating series alternate correctly?**

**Report the wrong output before the fix and the right output after.**

## WS2 — the other 14
**List them, and for each: what does the mutant change, and does any existing test notice?** **A mutant that survives means a behaviour nothing pins.** **Give me the list with a severity for each — does it produce a wrong answer, or only a different one?**

## WS3 — and the library against known values
**The library has 24 modules and 305 functions.** **How many have a test that checks a KNOWN mathematical value rather than just a golden output?**

**A golden recorded from a buggy implementation locks the bug in — I asked this before about the parser and the answer was that no golden was affected.** **Ask it again about the mathematics: are there goldens here that record wrong answers?**

**Check `madhava`, `ganita`, `sankhyiki` and `chandas` against published values.** **That is the audit that matters most, because a language that teaches mathematics and gets `sin` wrong is worse than useless.**
