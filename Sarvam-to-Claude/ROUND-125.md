# Sutram — ROUND-125: is `vitti` the root cause? Check the compiler.

**Base:** main at v299 · **Deliver into:** `Claude-to-Sarvam/`

## A third design answer has landed, and it found the root cause

**The problem is NOT the memory model. It is that `vitti` is an integer type that can also hold a `kosh`, a `mala`, or a raw pointer. When the compiler emits `a[0]` it does not know which of three things `a` is. No memory model can unify aliasing while the compiler cannot tell what it is compiling.**

**The proposed fix is a compiler change, not a memory change: statically track what was assigned to each `vitti` at compile time, and emit the right access code for each. `nirmmita` stays an 8-byte raw address (zero cost); `kosh` and `mala` become 24-byte descriptors (safe). No runtime tag.**

**And four supporting decisions:**
**1. Keep all three types - eliminating `mala` removes a real concept (fixed versus dynamic size).**
**2. Give `mala` the descriptor too, so both safe types share one mechanism and the alias cliff closes for both.**
**3. Restrict `nirmmita` to its `mandapa` region, so its lifetime is statically bounded and use-after-free is eliminated without a collector. Bounds stay unchecked, documented.**
**4. Remove the 64 MiB reservation entirely - the 16-`kosh` ceiling disappears, and aliases pay ~2.2 ns dependent latency instead.**

**And the argument that kills value semantics: a deep copy is shallow at depth (a `kosh` of `kosh`es copies the outer descriptors and shares the inner buffers). The descriptor is correct at any depth and costs 24 bytes to copy a million-element list.**

## WS1 - and this is the question that decides everything
**You have read this compiler more than anyone.** **So:**

**When the compiler sees `vitti a = k` where `k` is a `kosh`, and later sees `a[0]`, what does it emit today?** **Does it know `a` holds a `kosh`?**

**If it does know, the type-overloading claim is wrong and the descriptor can be built now.**

**If it does not know, then the claim is right and no memory change can work until the compiler tracks it.**

**Answer this from the source before doing anything else.** **It determines whether the last three rounds were solving the wrong problem.**

## WS2 - and if it does not know, how hard is it to make it know?
**Static tracking of what was assigned to each `vitti`.** **How many places in the compiler would need to change?** **Is there already a symbol table that could carry it?**

**Give me a number: days, or weeks.**

## WS3 - and the four decisions, priced
**1. `mala` gets a descriptor too - what does that cost a `mala` access today versus with the indirection?**
**2. `nirmmita` restricted to its region - does the compiler already know which `mandapa` a `nirmmita` was made in?**
**3. Remove the 64 MiB - what breaks in the current emitter if the buffer can move?**
**4. And the Windows lazy commit from R124 - is it still worth doing if the reservation is removed entirely?**

**Answer 4 first: if the reservation goes, does the 1 GiB Windows commit problem disappear on its own?**
