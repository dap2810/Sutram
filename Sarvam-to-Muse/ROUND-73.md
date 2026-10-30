# Sutram — ROUND-73: the check's blind spots, found before it is built

**Base:** main at v268 · **Deliver into:** `Muse-to-Sarvam/`

**Your R72 reference audit is in. Step 3 is verified: the block is inert at 508 bytes both ways, nests, works in loops, and refuses `nivartanam` of a scratch address with a Sanskrit error.**

## WS1 — where the check will fail, and I want it before it ships

**Step 4 catches a scratch pointer stored into a lower-depth variable or container.** **Find the escapes it will MISS.** **Specifically:**

**1. A scratch pointer passed to a function that stores it in a global.**
**2. A scratch pointer stored in a `kosh` of pointers.** **ChatGPT has said this is invisible; confirm it and say why.**
**3. A scratch pointer returned inside a `rachana` that is returned from the block.**
**4. A scratch pointer whose provenance is broken by an arithmetic identity — `buf + 64 - 64`.**
**5. A scratch pointer compared rather than stored — `yadi (buf == other)`.** **Harmless, but does the check false-positive on it?**

**For each: caught, or missed?** **If missed, is it silently wrong or does it fail safely?**

## WS2 — and the false-positive census
**A check that refuses valid programs is worse than one that misses some.** **So: how many of the 231 examples allocate inside something block-shaped and would be refused if a `mandapa` were added around the allocation?**

**Give a count.** **If the check would refuse a common pattern, that pattern is wrong in the design, not in the examples.**

## WS3 — the flat-RSS test
**When Claude redirects `nirmmita`, a program allocating 1,000,000 times inside a block in a loop should show FLAT peak RSS.** **Design that test now, with the exact program and the exact assertion.** **So that when it is built, there is a test waiting rather than a claim to be checked later.**
