# Sutram — ROUND-124: the descriptor. Price it, then decide.

**Base:** main at v299 · **Deliver into:** `Claude-to-Sarvam/`

## An independent review has landed, and it proposes a different design

**A reviewer with no prior knowledge of the project read the memory model and answered. Its verdict: *"region-based allocation paired with strict compile-time escape prevention is conceptually sound... However, the current collection design fundamentally contradicts this soundness by attempting to graft infinite growth semantics into a finite bump-allocator."***

**Four proposals, in order of impact:**

**1. STABLE DESCRIPTORS. A `kosh` variable points at a 24-byte descriptor (buffer pointer, length, capacity). Aliases point at the descriptor, so growth updates the pointer inside it and every alias sees the new buffer. Cost: one extra indirection, 1-3 cycles per access, 24 bytes per object.**
**2. AND THE CONSEQUENCE NOBODY HERE SAW: if aliases follow the descriptor, the buffer can move freely - so the 64 MiB reservation is no longer needed at all. Two of the three defects, one change.**
**3. VALUE SEMANTICS as an alternative to the whole problem: make `vitti a = k` a DEEP COPY. *"Aliasing simply does not exist. There is no alias cliff. Escape analysis becomes trivial."* Justified by the project's own goal: mental model simplicity, not speed.**
**4. Windows lazy commit, concretely: `MEM_RESERVE` at startup (free), a `committed_cursor`, and commit in 1 MiB chunks on demand. *"Roughly 4-5 assembly instructions... Hello World drops from 1 GB to a few kilobytes."***

**And two closed answers: reuse inside a live block is NO (a bump allocator cannot know an object is dead, and naive reuse would corrupt aliases); threads are NEVER (the arena cursor races and would return the same address to two threads).**

## WS1 - price the stable descriptor honestly
**The proposal: a `kosh` variable points at a 24-byte descriptor in the mandapa, holding buffer pointer, length and capacity. The data buffer lives further up the arena. Growth relocates the buffer and updates the pointer inside the descriptor.**

**Answer four things with numbers:**
1. **What does one read cost now, and what would it cost with the indirection?** **Instructions, and whether it adds a cache miss.**
2. **What does one allocation cost now, and with 24 extra bytes?**
3. **What breaks?** **Every place the compiler currently emits a direct buffer address has to go through the descriptor.** **How many emit sites is that?**
4. **And the payoff: with descriptors, can `R101A_REGION` go to zero - no reservation at all?**

**If the answer to 4 is yes, this single change closes the alias cliff AND the 16-`kosh` ceiling AND the 64 MiB invisibility.** **That would be the largest improvement in this project's history.**

## WS2 - and the Windows lazy commit, which is cheap and separate
**`MEM_RESERVE` at startup, a `committed_cursor`, and `MEM_COMMIT` in 1 MiB chunks on demand. The reviewer estimates 4-5 instructions on the allocation path.**

**Build this one first.** **It is small, it is independent of the descriptor work, and it takes a Windows hello-world from 1 GB of commit to a few kilobytes.**

**Verify: hello-world on Windows must commit kilobytes, not 1 GiB. And Linux must be unchanged.**

## WS3 - and the value-semantics idea, which I want your judgement on
**Make `vitti a = k` a deep copy rather than an alias.** **No aliasing at all.**

**That would eliminate the cliff by removing the concept.**

**Is it viable in this compiler?** **What does `a = k` on a 1-million-element `kosh` cost?** **And would it break the 319 examples?**

**Do not build it.** **Answer whether it is worth considering.**

## WS4 - and the two closed answers
**Reuse inside a live block: the reviewer says no, because a bump allocator cannot know an object is dead and naive reuse corrupts aliases.** **Threads: never, because the arena cursor races.**

**Do you agree?** **If yes, say so and I will put both in the reference as closed questions.**
