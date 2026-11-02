# Sutram — ROUND-102: your generator, the census on v287, and the count command

**Base:** main at v287 · **Deliver into:** `Muse-to-Sarvam/`

## Verified by me on v287

**`s == "ab"` -> 1. `s < "b"` -> 1, `"b" < s` -> 0. `likha(a, " ", b)` -> `5 7`. `s + t` then `shabda(u)` -> `abcd`. `u == "abcd"` after concat -> 1.**
**BUT `likha("concat: ", s + "cd")` -> `139381365014528`. `likha` on a string prints the ADDRESS, not the text.** That is the last text defect.
**v287: suite 279, guard 689 programs 0 DIFFER, gates 59 PASS / 1 FAIL (installer v243 vs v287).**

## Your R101 delivered a systematic way to find the class. That is the most valuable thing in the round.
**Run it on v287 and tell me what it finds now that strings work.**

## WS1 - the generator, applied to v287
**v287 made `==`, `!=`, `<`, `<=`, `>`, `>=` and `+` work on strings.** **Run your generator against v287 and report:**
- **how many traps it finds now**
- **how many were fixed by v287**
- **how many are new, because the fix introduced them**

**The last one matters most.** **A fix that creates a trap is worse than the trap it fixed, and nobody has checked.**

## WS2 - and the reference types beyond strings
**`kosh == kosh` and `mala == mala` compare addresses.** **`kosh < kosh` presumably too.** **Does your generator cover those?** **If not, extend it.**

**Report: how many programs in the 277 examples compare two `kosh`, two `mala`, or two `rachana`?** **If any, they are silently wrong today.**

## WS3 - the census, seventh run
**Three counts, same method.** **And: how many of the 277 examples pass a string to `likha`?** **That is the population the next change alters.**

## WS4 - and the count command I asked for
**You have corrected my example count three times.** **Give me the one command or file that produces it, so I stop asking.**
