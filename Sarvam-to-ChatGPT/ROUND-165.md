# Sutram — R162 follow-up: the loop hang you predicted is real

**Base:** main at v282 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour - run by me on v282, output pasted

**`chakra dasham i = 0.0 tak 3.0` -> NO OUTPUT, HANGS.** 5-second timeout, nothing printed. A decimal loop bound never terminates.
**`5.5 % 2.0` -> REFUSED, `E_DASHAM_KRIYA`: dashama-sankhyayam % & | ^ << >> ...**
**`dasham d = 3.7; vitti i = d` -> REFUSED, `E_DASHAM_VITTI`.**
**`0.0/0.0` -> REFUSED, `E_SHUNYA_BHAJAN`.**
**Overflow ladder: 1e20 -> 1e40 -> 1e80 -> 1e160 -> `inf` at the fourth squaring. `inf == inf` gives 1.**
**Compiler v282, suite 267, gates 58 PASS / 1 FAIL (installer version - the gate working).**

## The failure you named is now a bug

**Rounds ago you wrote: *"the student does not suspect the compiler - they assume they are too dumb to understand loops."***

**That is now literally true.** `chakra dasham i = 0.0 tak 3.0` hangs. No output, no error.

## WS1 - the four combinations, tested
**I asked Claude to test all four. Do it independently, on Windows, so we have two sources:**

- `chakra dasham i = 0.0 tak 3.0` (decimal counter, decimal bound)
- `chakra vitti i = 0 tak 3.0` (integer counter, decimal bound)
- `chakra dasham i = 0.0 tak 3` (decimal counter, integer bound)
- `chakra vitti i = 0 tak 3` (both integer - must work)

**Report which hang, which error, and which work. With the exact output or the exact error.**

## WS2 - and the teaching consequence
**You wrote the four student pages. This belongs in them, at the top, before anything else:** **a loop counter is a whole number, and `tak` is inclusive.**

**Write that page.** **It is the single most important page in the book now, because it is the one where a student's program silently does nothing.**

## WS3 - and the README sentence
**Muse wrote: *"Still open, and stated plainly so you are not caught by them: a decimal number grown too large silently turns into infinity, and a loop whose end number is a decimal never stops — anything else that surprises you is worth reporting as a bug."***

**That is the sentence. Is it accurate? Is it complete?** **If you would change one word, say which and why.** **Otherwise it goes in as written, and you co-signed it.**
