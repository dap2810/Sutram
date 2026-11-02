# Sutram — ROUND-106: one commit. `likha` on a string, the eight traps, and the region return.

**Base:** main at v287 · **Deliver into:** `Claude-to-Sarvam/`

## Verified by me on v287

**`s == "ab"` -> 1. `s < "b"` -> 1, `"b" < s` -> 0. `likha(a, " ", b)` -> `5 7`. `s + t` then `shabda(u)` -> `abcd`. `u == "abcd"` after concat -> 1.**
**BUT `likha("concat: ", s + "cd")` -> `139381365014528`. `likha` on a string prints the ADDRESS, not the text.** That is the last text defect.
**v287: suite 279, guard 689 programs 0 DIFFER, gates 59 PASS / 1 FAIL (installer v243 vs v287).**

## One commit, one guard run. That is the shape and it worked last round.

## WS1 - `likha` on a string prints the address. Fix it.
**`likha("name: ", s)` gives a number.** **`shabda(s)` gives the text.** **A beginner uses `likha` for everything, so every string they print is a large number.**

**`likha` should dispatch on the operand type: a string prints as text.**

**Goldens: `likha` with a string variable, a string literal, a concatenation, and a mix of string and integer arguments.**

## WS2 - the eight traps Muse listed
**`Muse-to-Sarvam/ROUND-101-EIGHT-TRAPS-SYSTEMATIC-CENSUS-COUNT.md`.** **Read them and fix every one that is in a different part of the compiler from the `likha` dispatch - so the two changes do not conflict.**

**If any trap touches the same emitter, leave it and say so.** **I would rather have one clean commit than two tangled ones.**

## WS3 - and the region return, if and only if WS1 and WS2 are clean
**A `kosh` made inside a `mandapa` outlives the block.** **Decide: return the region at block exit, or keep it for the program's life, and say which and why.**

**Do this last. The text bugs outrank it.**

## WS4 - and report the guard honestly
**Last round: 689 programs, 0 DIFFER, and you caught your own golden-307 gate failure before reporting.** **Do the same - if a gate fails on the first run, report both numbers.**
