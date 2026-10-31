# Sutram — ROUND-82: vectors in a block — the last memory gap

**Base:** main at v277, suite 253, gates 56 PASS · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour, tested by me on the shipped binary

**Refused at compile time:** `outer = buf + 64` · `m[0] = buf` · `nivartanam buf` · `box[0] = nirmmita(64); outer = box[0]` · `nirmmita(-1)` literal · a written number that does not fit in int64.
**Allowed:** `outer = buf[0]` · a scratch pointer as a parameter returning a value.
**Refused at run time, with a Sanskrit message and a line number:** `10 / 0` and `10 % 0`.
**Wraps silently, by decision:** computed overflow — `3^30` correct, `3^40` negative.
**Integer division truncates toward zero:** `-7 / 2` gives `-3`.
**`parikshita` is contextual, not a keyword:** `vitti parikshita = 4` compiles.

## Your R81 is the best-engineered round of this work

**`parikshita` built, transitive, refused at the first bad edge.** **0 DIFFER across 663 programs on three paths — unmarked code untouched in bytes, because the checker emits nothing on unmarked bodies.** **Contextual rather than a keyword, so no pack changed and the vocabulary budget is unspent.**

**And the honest number: 63 of 306 library functions can be marked as they are.**

**That is exactly the shape of a feature that ships: opt-in, provably inert, and honest about its reach.**

## WS1 — the last memory gap: a vector inside a block

**Today a `mandapa` block holds scalar scratch.** **A `kosh` created in a block is invisible to the check, because the pointer goes into a container rather than a named variable.**

**ChatGPT's R148 design: an opaque, generation-checked handle.** **Not an address range — both Gemini and ChatGPT rejected that independently, because after reuse an old pointer and a valid new pointer have the same address.**

**Build the smallest version that works:**
- **a `kosh` created inside a block carries a generation counter**
- **reading through it after the block ends is refused at run time, with a Sanskrit error naming the block**
- **and a `kosh` created OUTSIDE a block is unchanged — byte-identical, as `parikshita` was**

**The test that decides it: a block that creates a `kosh`, pushes, reads inside the block, and returns a computed VALUE — accepted and correct.** **Then the same `kosh` read after the block — refused with a message.**

**And the guard must show 0 DIFFER for every program that does not create a `kosh` in a block.**

## WS2 — and the cost
**A generation check on every `kosh` read costs something.** **Measure it on the existing benchmarks and report the percentage.** **If it is more than 15% for programs that never use a block, that is the wrong design — say so and stop.**

## WS3 — and the count I want at the end
**After this, how many of the 306 library functions could be marked `parikshita`?** **63 today.** **Does a block-safe `kosh` raise that number, and by how much?** **If it does not raise it, then vectors-in-a-block is a feature for user code only and I should say so.**
