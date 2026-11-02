# Sutram — R175: reference types across the whole language. The class, not the cases.

**Base:** main at v287 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified by me on v287

**`s == "ab"` -> 1. `s < "b"` -> 1, `"b" < s` -> 0. `likha(a, " ", b)` -> `5 7`. `s + t` then `shabda(u)` -> `abcd`. `u == "abcd"` after concat -> 1.**
**BUT `likha("concat: ", s + "cd")` -> `139381365014528`. `likha` on a string prints the ADDRESS, not the text.** That is the last text defect.
**v287: suite 279, guard 689 programs 0 DIFFER, gates 59 PASS / 1 FAIL (installer v243 vs v287).**

## Your R174 specification worked. Claude implemented it in one commit.
**"Text equality compares bytes without coercion; text addition produces a fresh immutable value; NUL termination is sufficient."** **Six operators and `+` landed, guard 0 DIFFER.** **That is what a usable specification buys.**

## WS1 - and the class is wider than text
**I tested v286 and found: `kosh == kosh` -> 1, `mala == mala` -> 1. Both compare addresses.**
**So the defect was never "strings". It is every REFERENCE TYPE compared with any operator.**

**On v287, are `kosh == kosh` and `mala == mala` still address comparisons?** **And `kosh < kosh`?**

**Specify the rule for all four reference types - `string`, `kosh`, `mala`, `rachana` - across all seven operators - `==`, `!=`, `<`, `<=`, `>`, `>=`, `+`.**

**A table: type by operator, and what each must do.** **Refuse, compare contents, or something else. With the reason.**

## WS2 - and `likha` on a string prints the address
**`likha` should print text for a string and a number for an integer.** **Specify the dispatch rule for every type `likha` can receive.**

**And: should `shabda` remain a separate function once `likha` dispatches?** **If `likha` handles strings, `shabda` may be redundant - or it may be the explicit form. Say which and why.**

## WS3 - and the traps nobody has classified
**Muse found eight more after five.** **Is there a systematic generator that would find this class, or does each need someone to happen to try it?** **If Muse has one, audit it. If not, specify one.**
