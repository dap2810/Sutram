# Sutram — ROUND-71: the loop bug was a parser bug, and the census is now the useful thing

**Base:** main at v265 · **Deliver into:** `Muse-to-Sarvam/`

## What the bug actually was

**Not the allocator.** **An indented body was parsed as ONE statement, so in my reproduction `i = i + 1` was outside the loop.** **Present since long before the memory work — it hangs on v261 too.** **Fixed at v265.**

## WS1 — the census, which now answers a different question

**I asked you to count `nirmmita` calls in loops.** **That count is still useful, but the question has changed:**

**1. How many programs in the tree write a MULTI-STATEMENT indented body — no braces — under `yavat`, `chakra`, `yadi` or `anya`?** **Name them.** **If the answer is zero, that is why 225 tests never caught it.**
**2. How many use braces?** **Those were never affected.**
**3. And of the ones with indented bodies, how many have more than one statement?** **That is the exact set that was silently doing less than written.**

**This is the number that tells us how much code was quietly wrong.**

## WS2 — and the count of what the bug cost
**A program that dropped statements still compiled and ran.** **So: are there examples whose OUTPUT was recorded from a program that was silently dropping statements?** **If a golden was recorded from buggy behaviour, it is a golden that locks the bug in.**

**Check the goldens that involve indented multi-statement bodies against what the source actually says.** **That is the check nobody has run.**
