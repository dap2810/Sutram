# Sutram — ROUND-176: split the two changes. The hoist lands; the zeroing is a decision.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Your R175 built both and reported honestly that the guard cannot read 0.** **That honesty is why this round can be a decision rather than an argument.**

---

## 1. The two changes are not the same change

| Change | Guard | Cost | What it fixes |
|---|---|---|---|
| **Made once anywhere in a loop** | **0 DIFFER** | **none — strictly better** | **37,516 and 50,012 KB → 16-20 KB** |
| **Zero at block exit** | **38 DIFFER** | **13.2 ns against 5.6 — 2.4× slower for a small block in a loop** | **a real correctness bug** |

**The first is free.** **The second fixes something real and makes the common case slower than not using a block at all.**

---

## 2. WS1 - and this is the round: ship the hoist alone
**Stage the hoist without the zeroing, on top of v318, and report its guard.**

**It should read 0 DIFFER — step 1 already did.**

**And measure the speed:** the nested `yadi` and `mandapa` cases, before and after, at 800,000 passes.** **If the hoist alone costs anything, say so.**

**That branch is the one that can merge. The zeroing waits.**

## WS2 - and the zeroing, as a decision rather than a side effect
**Two facts, and they pull opposite ways.**

**Fact 1: it fixes a real bug.** **An ordinary `nirmmita` after a block can read the block's data. Deterministically. That is a correctness defect in shipped code.**

**Fact 2: it costs 2.4× on the exact pattern the book teaches.** **A student writing `chakra { mandapa { ... } }` gets 13.2 ns instead of 5.6 — slower than if they had written no block at all.**

**So the question is not "is the fix correct" — it is.** **It is "what does the student pay for it, and is there a version that costs less".**

### Answer these

1. **Is there a version that zeroes only what was written?** **A block that allocates 64 bytes and writes 8 would zero 8, not 64.** **Does the compiler know what was written, or would that need per-store tracking?**
2. **What is the 13.2 ns made of?** **`rep stosq` startup, the store bandwidth, or the extra instructions?** **A tiny block should be one or two stores — if it costs 7.6 ns more than 5.6, something larger is happening.**
3. **And the option that costs nothing: leave the memory dirty and make `nirmmita` refuse to hand out memory a block wrote.** **Is that possible — a one-bit-per-page dirty map, or a check against the block's own range?**
4. **And the blunt option: document it.** **A block's memory is not cleared; a `nirmmita` after a block may contain what the block wrote; initialise before you read.** **Reference §19 already documents three behaviours; a fourth sentence is cheap.** **Would that be honest, or is it a bug left in?**

**My view, so you can argue with it: the cost is real and the bug is real, and a student who never reads before writing never sees the bug.** **So a documented limitation may be worth more than a 2.4× slowdown on the pattern the book recommends.**

**Argue with that if you disagree.**

## WS3 - and the 38th program
**One of the 38 prints 99 where it printed 0 — a pinned known limit.**

**That program was reading uninitialised memory and getting 99.** **So it was relying on the bug.**

**Answer:** **is that program in the tree, and is it an example or a test?** **If it is an example a student reads, the book now teaches something that only worked because of a defect.** **Name it.**

## WS4 - and the scope
**Say in the report:**

- **the hoist is staged and gate-clean, ready to merge**
- **the zeroing is staged and NOT ready, pending the decision above**
- **the nested cases now reclaim: `yadi`, `mandapa` inside a loop, `yavat`**
- **and what still does not: a block never returns memory to the OS; a dead big `kosh` keeps its reservation**
