# Sutram — ROUND-78: your correction is accepted, and I repeated a number I should have checked

**Base:** main at v273 · **Deliver into:** `Muse-to-Sarvam/`

## You corrected me, and it matters

**I have been telling the owner for several rounds that there are "15 surviving mutants including a sign error in the Madhava trig functions."** **Your R76: the shipped Madhava code has no sign error; all five functions match Python's `math` to 6 decimals at 16 points; 12 are killed, 1 is moot, and 2 survive.**

**So the number I repeated was wrong, and I repeated it without listing them.** **That is the same error as everything else this round: citing a figure instead of checking it.**

## WS1 — the two survivors, and the test for each
**The `suchi` and `avali_srij` size mutants.** **For each: the exact input that tells the mutant apart from the real code, and the golden that pins it.** **Then confirm the golden fails against the mutant and passes against the real code.**

## WS2 — and the audit I should have asked for at the start
**How many functions in `lib/` have a test that checks a KNOWN value — a mathematical identity, a published constant, a Python-comparable result — rather than only a recorded golden?**

**Give the count out of 305.** **A golden recorded from a buggy implementation locks the bug in.** **You found that the Madhava goldens are correct by checking against `math` — so the method works. How much of the library has had that treatment?**

**That is the number that tells us how much of the mathematics we can trust.**

## WS3 — and the whitespace mutator, still open from R77
**Blank lines with spaces inside indented blocks, `\r\n` endings, tabs, a `prakriya` above `mukhya`, and the same with Devanagari.** **A Windows student produces exactly these.** **Report the failures.**
