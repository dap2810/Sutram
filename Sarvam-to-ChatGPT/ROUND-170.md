# Sutram — R170: THE MEMORY DESIGN ROUND. Fix every gap, and use Sanskrit to name it.

**Base:** main at v283 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour - run by me on v283, counting lines not truncating

**1M allocations, no block: 164 ms, exit 0, correct.** **1M allocations, in a block: 40 ms, exit 0, correct.** So a block is 4x faster at a million allocations, and neither crashes.
**I could NOT measure peak RSS.** `/proc` polling returns zero (the process finishes in under 200 ms); `ulimit -v` fails both versions so it does not discriminate. **The claim "a block bounds memory" has NO measurement behind it - only speed evidence.**
**`chakra i = 0 tak 3.0` -> REFUSED, `E_CHAKRA_DASHAM`.**
**`dasham avg = 15 / 4` -> `3.000000`** - integer division before the store, same as C.

## This is the most important round of the project. Take the space you need.

**The memory model is the one thing that could make this language genuinely better than C, Rust or Go for teaching.** **Right now it is good and incomplete. I want the design that finishes it.**

## WS1 - the four gaps, and a design that closes all four
1. **No reuse.** A block gives memory back only at exit. A program allocating in a loop grows without bound. **Untested, and the biggest unknown.**
2. **`kosh` growth abandons the old buffer.** A real leak, measured, unfixed.
3. **Aliasing.** `vitti a = k` then relocating growth leaves `a` on the old buffer. **This is why the recycling bins were dropped - so reuse is impossible until it is fixed.**
4. **The escape check is lexical, lifetime is dynamic.** A `kosh` of scratch pointers is invisible.

**Design ONE model that closes all four without a garbage collector and without a runtime.**

**And state what it costs: instructions per read, per write, per allocation, and bytes per live object.** **Measured or estimated - but labelled which.**

## WS2 - and the Sanskrit naming, which is the part I most want from you
**The existing vocabulary is `kshetra` (field), `mandapa` (pavilion), `kosh` (sheath), `nirmmita` (created), `nivartanam` (return).** **Those are good words because they describe what the thing IS, not what it does in C.**

**Propose Sanskrit names for the new concepts, and justify each from the language rather than from a translation:**
- **a generation or epoch that invalidates stale handles** - consider `kalpa`, `samskara`, `yuga`
- **reuse or return of a freed region** - consider `punaravritti`, `visarjana`, `mukti`
- **a bounded or finite region** - consider `parimita`, `maryada`, `seema`
- **an unbounded or infinite one** - `ananta`
- **a handle that knows its generation** - this is the hard one; what does Sanskrit call a thing that carries its own history?

**For each: the word, its literal meaning, why it fits, and one line of `.sm` code using it.**

**Reject any word that is a fragment rather than a complete word.** **That rule has held all project and it holds here.**

## WS3 - and the honest comparison
**After the design: is it better than C, Rust, Go and Zig on memory - and on WHICH axis?**

**Do not claim overall superiority.** **Name the axis where it wins, the axis where it loses, and the axis where it is equal.** **A design document that claims to win everywhere is not a design document.**

## WS4 - and the thing that decides whether we build it
**What is the smallest version of this design that fixes gap 1 alone - bounded memory without reuse?**

**If a program that allocates a million times in a loop can be made to run in bounded memory with a change of under 200 lines, that is worth doing. If it needs 2,000, say so.**
