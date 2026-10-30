# Sutram — R145: Step 4 is starting, and your K0 limit is now the design

**Base:** main at v268 · **Deliver into:** `ChatGPT-to-Sarvam/`

**Step 3 is done and verified by me: the `mandapa` block compiles, is byte-identical to no block (508 bytes both ways), nests, works inside loops, and refuses `nivartanam` of a scratch address with `E_SCRATCH_ESCAPE` in Sanskrit.**

## WS1 — the check's blind spots, priced
**Step 4 catches a scratch pointer stored into a lower-depth variable or container.** **You have said repeatedly that a `kosh` of pointers is invisible.**

**So: give me the complete list of escapes the check will miss, and for each say whether it is SILENTLY WRONG or FAILS SAFELY.**

**That distinction is the whole value of the check.** **A missed escape that crashes is a bug. A missed escape that silently reads another allocation is the use-after-free we have spent this session avoiding.**

## WS2 — and the question the whole design rests on
**If the check cannot see a scratch pointer inside a `kosh`, then a `mandapa` block containing a `kosh` of scratch pointers is unsafe.** **You have said K0 forbids `kosh` in a checked function for this reason.**

**But: does K0 forbid it, or does it only refuse to CHECK it?** **Those are different promises.** **"We do not check this" is honest. "We refuse this" is a restriction. Which is it in v1.0?**

**And if it is "we refuse", how does a programmer put a list of strings in a block — or is the answer that they cannot?**

## WS3 — the false-positive bar
**A check that refuses valid programs is worse than one that misses some.** **What is the acceptable false-positive rate, and what is the test that establishes it?** **Give me a number and a method, not a principle.**
