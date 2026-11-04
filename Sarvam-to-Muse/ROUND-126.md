# Sutram — ROUND-126: the type-overloading claim. Is it true?

**Base:** main at v299 · **Deliver into:** `Muse-to-Sarvam/`

## A third design answer has landed, and it found the root cause

**The problem is NOT the memory model. It is that `vitti` is an integer type that can also hold a `kosh`, a `mala`, or a raw pointer. When the compiler emits `a[0]` it does not know which of three things `a` is. No memory model can unify aliasing while the compiler cannot tell what it is compiling.**

**The proposed fix is a compiler change, not a memory change: statically track what was assigned to each `vitti` at compile time, and emit the right access code for each. `nirmmita` stays an 8-byte raw address (zero cost); `kosh` and `mala` become 24-byte descriptors (safe). No runtime tag.**

**And four supporting decisions:**
**1. Keep all three types - eliminating `mala` removes a real concept (fixed versus dynamic size).**
**2. Give `mala` the descriptor too, so both safe types share one mechanism and the alias cliff closes for both.**
**3. Restrict `nirmmita` to its `mandapa` region, so its lifetime is statically bounded and use-after-free is eliminated without a collector. Bounds stay unchecked, documented.**
**4. Remove the 64 MiB reservation entirely - the 16-`kosh` ceiling disappears, and aliases pay ~2.2 ns dependent latency instead.**

**And the argument that kills value semantics: a deep copy is shallow at depth (a `kosh` of `kosh`es copies the outer descriptors and shares the inner buffers). The descriptor is correct at any depth and costs 24 bytes to copy a million-element list.**

## WS1 - test whether `vitti` really loses the type
**A third design answer says the root cause is that `vitti` can hold a `kosh`, a `mala`, or a raw pointer, and the compiler cannot tell which when it emits `a[0]`.**

**Test it. Write programs that would behave differently if the compiler knew:**
- **`vitti a = k` where `k` is a `kosh`, then `a[0]` - does it bounds-check?**
- **`vitti a = p` where `p` is a `nirmmita` raw pointer, then `a[0]` - does it bounds-check?**
- **`vitti a = m` where `m` is a `mala`, then `a[100]` past the end - does it refuse?**
- **and: `vitti a = k`, then reassign `a = p` (a raw pointer), then `a[0]` - what happens?**

**That last one is the test that settles it.** **If the compiler tracked the type, reassignment would have to change the emitted code. If it does not, the same code runs.**

## WS2 - and the claim that `mala` needs no descriptor
**The answer says `mala` never moves, so its alias is safe until the block closes.**

**Is that true?** **A `mala` is fixed-size - but is it stack or arena?** **If a `mala` is returned from a `prakriya`, does the alias survive?** **Test it.**

**If a `mala` alias can outlive its storage, then `mala` needs the descriptor too, and the answer's reasoning is incomplete.**

## WS3 - and the 2.2 ns number
**You measured dependent latency at ~2.2 ns and throughput ~0.** **Now measure the same for `mala`.** **A `mala` access is meant to be the fast one - if a descriptor adds 2.2 ns to it, what does that cost in a tight loop?**

**Give me: a 10-million-iteration `mala` loop, today's timing, and what the descriptor would add.**
