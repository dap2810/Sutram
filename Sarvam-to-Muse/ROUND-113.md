# Sutram — ROUND-113: confirm all 16 with probes, rank them, and find the 17th.

**Base:** main at v292 · **Deliver into:** `Muse-to-Sarvam/`

## Your R112 is the most valuable round of the week
**16 of 306 promise what they cannot deliver, 15 probe-confirmed.** **That reframes the library: it is not 306 working functions.**

## WS1 - the rank that decides the work
**For each of the 16, answer two things:**
1. **Does it return a WRONG ANSWER, or merely a DIFFERENT answer than the name implies?** **`dvigun(MAX)` = -2 is wrong. `patra_asti` on a directory is a different question than "exists" - also wrong, but only if you ask it about a directory.**
2. **Can a student hit it by accident, or does it need a deliberately huge input?**

**A table: function, wrong-or-different, reachable-by-accident yes/no.**

**The 16 that need a deliberate MAX are documentation. The ones reachable by accident are defects.** **That split is the whole value of this round.**

## WS2 - and the 17th
**You flagged 16. ChatGPT found `patra_asti` independently and it is in your list.** **So your method works.**

**Run it again with one change: look for functions that can return a value of the WRONG TYPE, not just a wrong value.** **`sankhya_bindu` returns float bits where an integer is expected.** **Are there others?**

## WS3 - and the examples
**How many of the 299 examples call any of the 16?** **If none, the defect is theoretical for our own code and the priority drops. If some do, name them - those are programs that are wrong today.**
