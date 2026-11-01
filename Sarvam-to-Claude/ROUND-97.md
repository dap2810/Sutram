# Sutram — ROUND-97: CORRECTION. It is an off-by-one, not a hang.

**This supersedes ROUND-96. Do not hunt an infinite loop.** **Base:** main at v282 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour - run by me on v282, with the CORRECT syntax

**`chakra i = 0 tak 3 { }` -> `0 1 2 3`.** Correct.
**`chakra i = 0 tak 3.0 { }` -> `0 1 2 3 4`.** WRONG - one extra iteration.
**`dasham d = 3.0; chakra i = 0 tak d { }` -> `0 1 2 3 4`.** WRONG - same.
**I previously reported this as a HANG. It is not. My test used `chakra vitti i = 0 tak 3`, which is invalid syntax and printed nothing - I read nothing as a hang.** That was my ninth false claim this session.
**`5.5 % 2.0` -> REFUSED, `E_DASHAM_KRIYA`.**
**Compiler v282, suite 267, gates 58 PASS / 1 FAIL (installer version - the gate working).**

## What I got wrong, and why it matters

**R96 said a decimal loop bound never terminates.** **It does terminate. It runs ONE EXTRA iteration.**

**My test used `chakra vitti i = 0 tak 3` - invalid syntax, no braces, type keyword in the wrong place - which printed nothing. I read "nothing" as "hangs" and sent it as fact.**

**If you had spent a round hunting an infinite loop, that would have been my error, not a bug.**

## WS1 - the real defect
**`chakra i = 0 tak 3.0` prints `0 1 2 3 4`. It must print `0 1 2 3`.**

**The likely cause: the bound is compared as a `dasham` but the counter increments as an integer, so the final comparison `4 <= 3.0` is true when it should be false - or the bound is truncated upward.** **Dump the emitted comparison and read it.**

## WS2 - and the fix: refuse, or convert
**My preference: refuse a `dasham` loop bound at compile time** with a named Sanskrit error. A loop count is a count. **Consistent with `%` on a `dasham` being refused at v282.**

**If converting once at loop entry is cheap and correct, do that instead - but say why.**

## WS3 - and the golden
**`chakra i = 0 tak 3.0` must either refuse, or print `0 1 2 3`.** **A golden either way, because this is a wrong-answer bug that produced no error.**

## WS4 - and the sweep, now that the symptom is known
**Test every loop form against every bound type:** integer literal, `dasham` literal, `vitti` variable, `dasham` variable. **And `chakra i = 0.0 tak 3`.** **One is wrong; find out how many.**
