# Sutram — ROUND-59: the memory change surface — every site, counted

**Base:** main at **v412**, compiler **v261** · **Deliver into:** `Muse-to-Sarvam/`

**Read first:** `docs/decisions/MEMORY-DESIGN.md`.

## Why you
**Before anything is designed, I need to know how big the change is.** **That is counting, and counting is what you do better than anyone
here — your variable count and your two-patch split both changed decisions this session.**

## WS1 — every `nirmmita` site
**Count every `nirmmita` call in the tree:** `lib/`, `examples/`, `tests/`, `docs/`. **By directory, with the distinct call shapes.**
**A call that allocates a fixed size and a call that allocates a computed size are different problems — separate them.**

## WS2 — every `kosh` growth point
**`kosh` grows when it exceeds capacity.** **Find where that happens — the compiler emitter or the library — and say whether the old
block is abandoned.**
**If it is in the emitter, it is one place and the fix is small.** **If it is in the library, it may be many.** **Which is it?**

## WS3 — and the question that decides whether a region is usable
**How many `nirmmita` results ESCAPE the function that allocated them?** **A region cannot hold an object that outlives it.**

**So: sample the call sites and classify them:**
- **(a) allocated and released inside one function** — a region handles it perfectly.
- **(b) allocated and RETURNED** — a region cannot, unless the region outlives the function.
- **(c) allocated and stored somewhere that outlives the scope** — the hardest case.

**Give me the counts.** **If most are (a), a region is a clean win.** **If many are (b) or (c), a region is a trap and option A is the
honest answer.**

**That single classification decides the design, and nobody has measured it.**

## Return
`ROUND-59-MEMORY-SURFACE.md` with: the `nirmmita` counts by directory and shape · the `kosh` growth location · **the (a)/(b)/(c)
escape classification with counts** · and your own recommendation, in one paragraph, on whether a region is usable here.
