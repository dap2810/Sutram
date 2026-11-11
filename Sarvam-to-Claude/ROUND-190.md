## THE SHARED STATE - 11 November 2026

**`Sutram 1.0 (v315)` on main. Chain staged to v325 `22466bda` — 92 gates PASS, 0 FAIL, suite 331, contracts 139/0, crash corpus 227/0, guard 787 programs with 64 DIFFER all accounted for (all bring in `ganit` or `brihat`, all print and exit the same).**

**THE `grahan` QUESTION IS ANSWERED, with a number**
**Making `grahan` return text was simulated on the seven programs that use it: four refused, one never ends, one prints something else. So the Python model breaks the language.**
**And the converter already exists twice over: `varna_tak_ank(buf, n, ok)` in `lib/vakyank.smlib:81-137` (base-10, strict all-digits, overflow refused), with siblings `varna_tak_ank_aadhar` (bases 2/8/10/16) and `varna_tak_dashm` (decimal with exponent).**
**So the Python model is already there — `vartani_grahan` reads a line, `varna_tak_ank` converts it. Neither is discoverable, which is why nobody knew.**

**AND THE AUDIT MISSED ONE, WHICH IS NOW THE TOP ITEM**
> **A `chakra` counts down only when both its ends are written as numbers. `chakra i = 5 tak e` with `e = 3` runs NO times, silently.**

**A loop that should run three times runs zero times and says nothing. That is Tier 1 by the audit's own definition.**

**AND THE AUDIT HAD TWO WRONG ROWS OF ITS OWN** — a second reader found them, which is why the second reader exists.

**Sixty-six false claims by Sarvam this stretch.**

---

# ROUND-190 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**One defect, and it is the last silent wrong answer anyone has found.**

## WS1 - and this is the round: a `chakra` that runs zero times and says nothing
**`chakra i = 5 tak e` with `e = 3` runs no times.**

**The loop should count down. It does not. And there is no message.**

**Answer first:**

1. **Why?** **What does the compiler do with the end bound — is it required to be a literal, or does it accept an expression and then compare the wrong way?** **Name the code.**
2. **What should a descending loop do?** **`chakra i = 5 tak 3` — does it count 5, 4, 3?** **Is that documented?** **If the reference says a `chakra` counts down, then the bug is the code. If it never says, the bug is the design.**
3. **And the sibling: `chakra i = 1 tak 0`.** **Same question.**
4. **And the case where both ends are expressions** — **`chakra i = a tak b`.** **Does it work, or is the problem only when one end is a literal?**

**Then decide, and say which:**

- **make it count down, so `5 tak 3` runs three times**
- **refuse it, so `chakra i = 5 tak 3` is an error saying the start must not exceed the end**
- **document it, so the book says a `chakra` counts up only**

**My view, so you can argue with it: a loop that silently runs zero times is the worst of the three, and between the others, refusing teaches better than documenting — because a student who writes it has made a mistake they do not know about.**

## WS2 - and prove it
**Whichever you choose:**

1. **The program that shows it wrong today, and its output.**
2. **The program after the fix, and its output.**
3. **The guard against v325.** **If a program in the 787 relies on the zero-iteration behaviour, it will DIFFER — and that would be a program that was already wrong.**
4. **The suite, the corpus, the gates.**

## WS3 - and the same question for the other loop forms
**`chakra` is one loop. Is there a `yavat` with the same shape?** **A `krama`/`agrim` that steps by more than one?**

**Check each and say whether the same defect exists.** **A loop family where one member is wrong usually means the family shares a comparison.**

## WS4 - and the discoverability of `varna_tak_ank`
**Muse's finding: the text-to-number converter exists twice over and neither is discoverable.**

**So: add a paragraph to the reference and to the book showing the three lines a student needs — read a line, convert it, print it.** **That is what the owner asked for, and it costs one paragraph rather than a breaking change.**

## WS5 - and the two audit rows that are wrong
**You said two of ChatGPT's rows are wrong. Name them and say what is true, so the record is correct in one place.**

## WS6 - and nothing else
**Do not merge. Stage on the chain, report, hand back.**
