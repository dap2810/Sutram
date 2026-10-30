# Sutram — R148: the hard design question. Make the block usable with vectors, or say it cannot be.

**Base:** main at v273 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Your R146 and R147 changed this project's direction twice

**You said the README sentence was not true — it was not, and it now carries three claims instead of four.**
**You found the negative-size gap — it is closed at v273, with a Sanskrit error for both a literal and a computed negative.**
**You said K0 does not refuse `kosh`, only declines to check it — that is now the written answer.**

**So this round is the question that decides whether the block is a real feature.**

## WS1 — the hard one: a `mandapa` block that can hold a vector

**Today a block holds scalar scratch.** **A programmer cannot put a `kosh` in it and be protected, because a scratch pointer inside a `kosh` is invisible to the check.**

**So design a way for a block to hold a vector SAFELY.** **Not "check harder" — the check is lexical and the container is dynamic, which is why it fails.**

**Consider, and reject what deserves rejecting:**
- **a `kosh` created inside a block being implicitly scoped to it** — its lifetime is the block's, enforced by construction rather than by analysis
- **a distinct container type that carries its region** — `kosh` inside a block is a different type from `kosh` outside
- **making the block's scratch range addressable** — the check refuses any pointer whose address falls in the scratch range, regardless of how it got there. **A run-time range check rather than a compile-time taint.**
- **and anything you think of that I have not**

**For each: does it actually close the hole, what does it cost, and what does it break?**

**And the one I want your judgement on: the fourth option is a RUN-TIME check, which means it costs on every dereference.** **Is a run-time region check cheaper than a compile-time analysis that misses cases?** **Argue it both ways and pick.**

## WS2 — and the honest fallback
**If no design closes the hole at acceptable cost, say so.** **Then answer: should the block ship as scalar-only, or should it not ship at all in v1.0?**

**A feature that is safe but nearly useless is worse than no feature, because it takes space in the reference and gives a beginner a false sense of what it does.**

## WS3 — and one more hard question
**Given everything you now know about this compiler — four parser defects, two memory gaps, 15 surviving mutants — what is the single biggest risk to v1.0 that nobody has named?**

**Not a list. The one. And what would you do about it this week?**
