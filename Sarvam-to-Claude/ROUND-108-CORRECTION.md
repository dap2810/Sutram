# CORRECTION — my arena proposal is flawed. Do not build it as written.

**This interrupts ROUND-108 WS1/WS2. Read it before building the arena.**

## What I got wrong

**I proposed: a `kosh` inside a `mandapa` grows by taking a new slot in the block's arena, and the old slot is abandoned. I called that "growth without relocation" because the arena stays put.**

**ChatGPT R177: *"Allocating a new slot and abandoning the old one is relocation, even when the containing arena never moves. If in-place growth is unavailable, either refuse growth before modifying state, or implement indirection/ownership rules. Do not describe copying as nonmoving growth."***

**It is right and I was wrong. The arena's position is irrelevant — the data moved. My design reopens the aliasing hole it was supposed to close.**

## And a generation mark is not enough either

**ChatGPT: *"An arena epoch alone fixes neither alias coherence nor lifetime safety unless references and metadata are redesigned."***

**So the epoch idea I offered as option A does not fix hole 1 at all.**

## What to build instead

**ChatGPT's decision, and I accept it:**

1. **Static outlives/borrow rules for the initial safe arena.** A reference into an arena may not be stored outside it. **You have the escape error already at v289 - extend it to cover the arena.**
2. **Stable `kosh` descriptors so aliases remain coherent.** The descriptor holds the address and the length/capacity, and growth updates the descriptor rather than moving the data the alias points at. **This is the same answer you gave in R101 for regions, and it is the one that works.**
3. **Do not reclaim storage while the call-through escape gap is still accepted.** Fix escape first, reclaim second.

## What this means for R108

- **WS1: drop option A (the arena epoch). Build option B - the outlives rule - and the stable descriptor.**
- **WS2: do not build the arena as I described it. If the descriptor work makes the arena unnecessary, say so and stop.**
- **WS3 and WS4 stand unchanged** - `parimana()` semantics and whether `kosh == kosh` is closed.

**If you had already started the arena, stop and report what you have. A half-built arena on a flawed premise is worse than none.**
