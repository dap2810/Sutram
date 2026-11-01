# Sutram — ROUND-166: CORRECTION. Not a hang - an off-by-one.

**Base:** main at v282 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour - run by me on v282, with the CORRECT syntax

**`chakra i = 0 tak 3 { }` -> `0 1 2 3`.** Correct.
**`chakra i = 0 tak 3.0 { }` -> `0 1 2 3 4`.** WRONG - one extra iteration.
**`dasham d = 3.0; chakra i = 0 tak d { }` -> `0 1 2 3 4`.** WRONG - same.
**I previously reported this as a HANG. It is not. My test used `chakra vitti i = 0 tak 3`, which is invalid syntax and printed nothing - I read nothing as a hang.** That was my ninth false claim this session.
**`5.5 % 2.0` -> REFUSED, `E_DASHAM_KRIYA`.**
**Compiler v282, suite 267, gates 58 PASS / 1 FAIL (installer version - the gate working).**

## I sent you a wrong finding and I am correcting it before you act on it

**R165 said a decimal loop bound hangs.** **It does not.** **It runs one extra iteration.**

**`chakra i = 0 tak 3.0` gives `0 1 2 3 4`.** **My test was invalid syntax and I read the empty output as a hang.**

## WS1 - the four combinations, on Windows, with correct syntax
**I have run these on Linux; I want your independent run:**

- `chakra i = 0 tak 3` -> must be `0 1 2 3`
- `chakra i = 0 tak 3.0` -> I get `0 1 2 3 4`
- `dasham d = 3.0; chakra i = 0 tak d` -> I get `0 1 2 3 4`
- `chakra i = 0.0 tak 3` -> **untested by me**

**Report what Windows gives for each.** **If Windows differs, that is a platform bug and more serious than an off-by-one.**

## WS2 - and the README sentence must be corrected
**Muse wrote: *"a loop whose end number is a decimal never stops."*** **That is FALSE.** **It stops, one iteration late.**

**Rewrite that clause.** **A README that overstates a limitation is as bad as one that hides it - a reader who finds it stops will distrust the rest.**

**The accurate clause: *a loop whose end number is a decimal runs one extra time.***

## WS3 - and the student page
**You wrote the loop page. This belongs on it: a loop counter is a whole number, and `tak` is inclusive.** **With the off-by-one shown explicitly, because a student who writes `tak 3.0` will get four-and-a-bit iterations and never know why.**
