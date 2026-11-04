# Sutram — ROUND-125: test the reviewer's claims. Do not trust them.

**Base:** main at v299 · **Deliver into:** `Muse-to-Sarvam/`

## An independent review has landed, and it proposes a different design

**A reviewer with no prior knowledge of the project read the memory model and answered. Its verdict: *"region-based allocation paired with strict compile-time escape prevention is conceptually sound... However, the current collection design fundamentally contradicts this soundness by attempting to graft infinite growth semantics into a finite bump-allocator."***

**Four proposals, in order of impact:**

**1. STABLE DESCRIPTORS. A `kosh` variable points at a 24-byte descriptor (buffer pointer, length, capacity). Aliases point at the descriptor, so growth updates the pointer inside it and every alias sees the new buffer. Cost: one extra indirection, 1-3 cycles per access, 24 bytes per object.**
**2. AND THE CONSEQUENCE NOBODY HERE SAW: if aliases follow the descriptor, the buffer can move freely - so the 64 MiB reservation is no longer needed at all. Two of the three defects, one change.**
**3. VALUE SEMANTICS as an alternative to the whole problem: make `vitti a = k` a DEEP COPY. *"Aliasing simply does not exist. There is no alias cliff. Escape analysis becomes trivial."* Justified by the project's own goal: mental model simplicity, not speed.**
**4. Windows lazy commit, concretely: `MEM_RESERVE` at startup (free), a `committed_cursor`, and commit in 1 MiB chunks on demand. *"Roughly 4-5 assembly instructions... Hello World drops from 1 GB to a few kilobytes."***

**And two closed answers: reuse inside a live block is NO (a bump allocator cannot know an object is dead, and naive reuse would corrupt aliases); threads are NEVER (the arena cursor races and would return the same address to two threads).**

## WS1 - test the four claims, the way you test everything
**A reviewer with no stake in this design made four proposals.** **Your job is to find where they are wrong.**

**1. The descriptor eliminates the 64 MiB reservation.** **Is that true?** **If the buffer moves freely, what happens to a raw `nirmmita` pointer that points into it?** **And to `p[i]` on a `mala`?**
**2. The descriptor costs 1-3 cycles per access.** **Is that a guess or a measurement?** **It says "roughly". Test whether a dependent load on modern hardware costs 1-3 cycles or 4-5 when it misses L1.**
**3. Value semantics eliminates the alias cliff.** **Does it?** **What does `vitti a = k` cost when `k` holds a million elements?** **Is that acceptable?**
**4. The Windows lazy commit is 4-5 instructions.** **Is the commit check on the hot path or only on allocation?**

**Report which claims survive and which do not.** **A reviewer with no stake is still a reviewer who can be wrong.**

## WS2 - and the one claim I most doubt
**"Aliasing simply does not exist" under value semantics.** **But the language still has `nirmmita` raw pointers and `mala` arrays.** **Do those alias?**

**If they do, value semantics for `kosh` closes one door and leaves two open.** **Say whether that is true.**

## WS3 - and measure what the reviewer says to measure
**It said: *"Allocate 1,000 collections containing one element each. The current design would crash under a 1 GiB limit; the new design will consume a few kilobytes."***

**Test the first half on v299.** **Write a program with 16 `kosh` and run it under `ulimit -v 1048576`.** **Does it crash?** **And with 15?**

**That number has been quoted twice now and verified zero times.**
