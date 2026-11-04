# Sutram — R199: the descriptor, the deep copy, and the two closed answers

**Base:** main at v299 · **Deliver into:** `ChatGPT-to-Sarvam/`

## An independent review has landed, and it proposes a different design

**A reviewer with no prior knowledge of the project read the memory model and answered. Its verdict: *"region-based allocation paired with strict compile-time escape prevention is conceptually sound... However, the current collection design fundamentally contradicts this soundness by attempting to graft infinite growth semantics into a finite bump-allocator."***

**Four proposals, in order of impact:**

**1. STABLE DESCRIPTORS. A `kosh` variable points at a 24-byte descriptor (buffer pointer, length, capacity). Aliases point at the descriptor, so growth updates the pointer inside it and every alias sees the new buffer. Cost: one extra indirection, 1-3 cycles per access, 24 bytes per object.**
**2. AND THE CONSEQUENCE NOBODY HERE SAW: if aliases follow the descriptor, the buffer can move freely - so the 64 MiB reservation is no longer needed at all. Two of the three defects, one change.**
**3. VALUE SEMANTICS as an alternative to the whole problem: make `vitti a = k` a DEEP COPY. *"Aliasing simply does not exist. There is no alias cliff. Escape analysis becomes trivial."* Justified by the project's own goal: mental model simplicity, not speed.**
**4. Windows lazy commit, concretely: `MEM_RESERVE` at startup (free), a `committed_cursor`, and commit in 1 MiB chunks on demand. *"Roughly 4-5 assembly instructions... Hello World drops from 1 GB to a few kilobytes."***

**And two closed answers: reuse inside a live block is NO (a bump allocator cannot know an object is dead, and naive reuse would corrupt aliases); threads are NEVER (the arena cursor races and would return the same address to two threads).**

## WS1 - you proposed the descriptor in R170 and R187. This reviewer agrees with you.
**Its proposal: a 24-byte descriptor holding buffer pointer, length and capacity; aliases follow the descriptor; growth updates the pointer.**

**And it adds the consequence: with the descriptor, the 64 MiB reservation is unnecessary.**

**Was that in your R170 design, and did you see the reservation could go to zero?** **If you did, say so - and if you did not, say what made you keep the reservation.**

**And price the whole thing: what does the descriptor design cost in total, now that it replaces the reservation rather than adding to it?**

## WS2 - and value semantics, which nobody here proposed
**Make `vitti a = k` a deep copy. No aliasing.**

**You have argued twice that "an undocumented choice between identity, contents and raw bits is the defect".** **This reviewer's answer is: choose contents, and make the choice by copying.**

**Is that right for this language?** **What does it cost on a large collection?** **And does it close the class you have been describing, or move it?**

## WS3 - and the two closed answers, which I want on the record
**Reuse inside a live block: no, because a bump allocator cannot know an object is dead and naive reuse corrupts aliases.**
**Threads: never, because the arena cursor races and would return the same address to two threads.**

**You have been asked about both for weeks.** **If these are the right answers, say so and write the two paragraphs for the reference.** **A closed question with a reason is worth more than an open one.**

## WS4 - and the paragraph for a schoolteacher
**The reviewer wrote one: a notebook you open at a `mandapa`, write on the next blank line, never erase, and throw the whole notebook away at the end.**

**Write your own version.** **If yours is better, say why.** **If theirs is better, say that too.**
