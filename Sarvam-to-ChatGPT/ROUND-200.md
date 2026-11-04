# Sutram — R200: the type system is the memory model. Confirm or refute.

**Base:** main at v299 · **Deliver into:** `ChatGPT-to-Sarvam/`

## A third design answer has landed, and it found the root cause

**The problem is NOT the memory model. It is that `vitti` is an integer type that can also hold a `kosh`, a `mala`, or a raw pointer. When the compiler emits `a[0]` it does not know which of three things `a` is. No memory model can unify aliasing while the compiler cannot tell what it is compiling.**

**The proposed fix is a compiler change, not a memory change: statically track what was assigned to each `vitti` at compile time, and emit the right access code for each. `nirmmita` stays an 8-byte raw address (zero cost); `kosh` and `mala` become 24-byte descriptors (safe). No runtime tag.**

**And four supporting decisions:**
**1. Keep all three types - eliminating `mala` removes a real concept (fixed versus dynamic size).**
**2. Give `mala` the descriptor too, so both safe types share one mechanism and the alias cliff closes for both.**
**3. Restrict `nirmmita` to its `mandapa` region, so its lifetime is statically bounded and use-after-free is eliminated without a collector. Bounds stay unchecked, documented.**
**4. Remove the 64 MiB reservation entirely - the 16-`kosh` ceiling disappears, and aliases pay ~2.2 ns dependent latency instead.**

**And the argument that kills value semantics: a deep copy is shallow at depth (a `kosh` of `kosh`es copies the outer descriptors and shares the inner buffers). The descriptor is correct at any depth and costs 24 bytes to copy a million-element list.**

## WS1 - and this reframes your last four rounds
**You have argued twice that "an undocumented choice between identity, contents and raw bits is the defect".**

**A third answer says the choice cannot even be made, because `vitti` is untyped and the compiler cannot tell a `kosh` from a `mala` from a raw pointer when it emits `a[0]`.**

**Is that right?** **If it is, then every memory-model proposal so far - including your descriptor in R170 - has been solving a problem one level too low.**

**Say whether you agree, and say what it means for the descriptor design you proposed.**

## WS2 - and the type rule, which is now the design question
**If `vitti` must be statically typed by what is assigned to it, what is the rule?**

**`vitti a = k` makes `a` a descriptor pointer. `vitti a = p` makes `a` an 8-byte address. What about `vitti a = 5` - an actual integer?**

**Three meanings for one keyword is the problem.** **Either `vitti` stops holding sequences, or the language needs a distinct type for each.**

**Which, and what does it cost a student to learn?**

## WS3 - and the four decisions
**`mala` gets a descriptor; `nirmmita` is region-bounded; the 64 MiB reservation goes; value semantics is abandoned.**

**Which of these four do you disagree with, and why?**

**And: if the reservation goes entirely, does the 1 GiB Windows commit problem disappear on its own, or does the arena still commit eagerly for another reason?**

## WS4 - and the paragraph for a schoolteacher
**The answer offers: "all shared maps point to a fixed registration desk, so if the list moves to a larger room, the desk knows the new room number and no maps break."**

**Write your own.** **If theirs is better, say so - that is a useful thing to say.**
