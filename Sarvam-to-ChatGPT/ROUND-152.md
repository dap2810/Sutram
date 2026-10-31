# Sutram — R152: the generation handle, audited before it is built

**Base:** main at v277 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour, tested by me on the shipped binary

**Refused at compile time:** `outer = buf + 64` · `m[0] = buf` · `nivartanam buf` · `box[0] = nirmmita(64); outer = box[0]` · `nirmmita(-1)` literal · a written number that does not fit in int64.
**Allowed:** `outer = buf[0]` · a scratch pointer as a parameter returning a value.
**Refused at run time, with a Sanskrit message and a line number:** `10 / 0` and `10 % 0`.
**Wraps silently, by decision:** computed overflow — `3^30` correct, `3^40` negative.
**Integer division truncates toward zero:** `-7 / 2` gives `-3`.
**`parikshita` is contextual, not a keyword:** `vitti parikshita = 4` compiles.

## Your R148 design is about to be built

**An opaque, generation-checked handle. A hybrid of static classification and dynamic validation. A qualified small feature rather than an unqualified large one.**

## WS1 — where the generation check fails
**A `kosh` created in a block carries a generation. Reading through it after the block ends is refused at run time.**

**1. What happens if the `kosh` is COPIED before the block ends?** **`vitti k2 = k` — do both carry the generation, or does the copy escape?** **The check already refuses `vitti a = k` — does that still hold?**
**2. What happens if the `kosh` is passed to a function that keeps it?** **The parameter is a copy.**
**3. What if the block runs twice in a loop?** **Generation 1 and generation 2 both exist. Is generation 2 distinguishable from generation 1 at the same address — and is one counter per block enough, or does it need one per allocation?**
**4. And: what does the generation cost per read?** **One compare, or a load and a compare?**

**Answer 3 with particular care — it is the case that killed the address-range design, and I need to know the generation handle does not have the same flaw in a different place.**

## WS2 — and the honest verdict
**Is a generation-checked `kosh` in a block worth building at all, given it adds a run-time cost to something the language currently does for free?**

**If your answer is "no, document that a block holds scalars and move on", say it plainly.** **I would rather ship a small honest feature than a large one with a tax on every read.**

## WS3 — and the ranking, which I asked and did not get
**Three things left: vectors in a block, generics, and threads.** **Rank them by value to a student writing a real program, and say which one you would do first if you could only do one.**

**Then say which of the three you would NOT do in v1.0, and why.**
