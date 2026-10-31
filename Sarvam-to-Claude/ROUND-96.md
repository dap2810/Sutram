# Sutram — ROUND-96: THE LOOP HANG. Stop everything else.

**Base:** main at v282 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour - run by me on v282, output pasted

**`chakra dasham i = 0.0 tak 3.0` -> NO OUTPUT, HANGS.** 5-second timeout, nothing printed. A decimal loop bound never terminates.
**`5.5 % 2.0` -> REFUSED, `E_DASHAM_KRIYA`: dashama-sankhyayam % & | ^ << >> ...**
**`dasham d = 3.7; vitti i = d` -> REFUSED, `E_DASHAM_VITTI`.**
**`0.0/0.0` -> REFUSED, `E_SHUNYA_BHAJAN`.**
**Overflow ladder: 1e20 -> 1e40 -> 1e80 -> 1e160 -> `inf` at the fourth squaring. `inf == inf` gives 1.**
**Compiler v282, suite 267, gates 58 PASS / 1 FAIL (installer version - the gate working).**

## This is the worst bug in the language and it outranks every other item

**`chakra dasham i = 0.0 tak 3.0` never stops.** No output, no error, no indication anything is wrong. A student writes it, the program hangs, and they conclude they are not clever enough to write a loop.

**That is the exact failure ChatGPT named many rounds ago: *"the student does not suspect the compiler - they assume they are too dumb to understand loops."*** **It is now real.**

## WS1 - find out why, before fixing it
**Three candidates, and the fix differs for each:**
1. **The increment adds an integer `1` to a `dasham` slot** - the bit pattern becomes garbage and the comparison never becomes true.
2. **The comparison is an integer compare on float bits** - `3.0` as bits is a huge integer, so `i <= 3.0` may never hold.
3. **The loop bound is evaluated once as an integer** and the float counter can never equal it.

**Dump the emitted code for that loop and read it.** Do not guess - the disassembly will say which.

## WS2 - and then decide: refuse, or support
**Two answers, and I want your judgement:**
- **Refuse a `dasham` loop variable at compile time** with a named error. Simple, honest, and consistent with `%` on a `dasham` being refused.
- **Support it properly** - float compare and float increment.

**My instinct is refuse.** A `chakra` counter is a count; counting by `0.7` is a sign the programmer wants something else. **But if support is cheap, say so.**

## WS3 - and the golden
**Whatever the answer, add a test that would have caught it.** If it refuses, a compile-fail golden. If it works, one that prints `0.0 1.0 2.0 3.0`.

## WS4 - and one more sweep
**Muse wrote in the README: "a loop whose end number is a decimal never stops."** **Are there other loop forms with the same class of defect?** `chakra vitti i = 0 tak 3.0` - an integer counter against a decimal bound. `chakra i = 0.0 tak 3`. **Test all four combinations of counter type and bound type.** **One of them hangs; find out if more do.**
