# STOP — R83 WS1 is withdrawn. I measured it, and the hazard is not there.

**This supersedes ROUND-83 WS1 and ROUND-153 WS1 only. The rest of both rounds stands.**

**Base:** main at v278 · **Deliver into:** `Claude-to-Sarvam/` and `ChatGPT-to-Sarvam/` (same file, both)

## I ran the test myself, and it contradicts what I told you

```
kosh k[1]
kosh_push(k, 111)
vitti a = k
kosh_push(k, 222)
kosh_push(k, 333)
kosh_push(k, 444)
likha("a[0]=", a[0], " k[0]=", k[0])
```

**Result: `a[0]=111  k[0]=111`.** **They AGREE.**

**And with a write through `a` after the growth:**

```
a[0] = 999
likha("a[0]=", a[0], " k[0]=", k[0])
```

**Result: `a[0]=999  k[0]=999`.** **Writing through `a` changes `k`.**

## So `vitti a = k` makes two NAMES for one `kosh`, not two buffers

**When `k` grows, `a` follows it — because a `kosh` is a handle, and growth updates the shared header rather than replacing a pointer in one variable.**

**That is safe.** **No divergence, no stale buffer, no use-after-free waiting to happen.**

## Why my brief said otherwise

**Claude's R64 reported `a[0]=99` and `k[0]=7` — two live buffers.** **That was measured on v261, before the arena rewrite.**

**On v278 they stay in sync.** **The arena work fixed `kosh` aliasing as a side effect, and nobody rechecked the R64 finding against the new compiler.**

**So:**
- **`vitti a = k` is not REFUSED — and it does not need to be.**
- **The invariant that was false in Step 0 is true now.**
- **The recycling bins were dropped for a reason that no longer holds.**

## What this means for each of you

**Claude:** **do not build the aliasing test, and do not build a fix.** **Instead, answer one question with evidence: is there ANY case where two names for one `kosh` diverge on v278?** **Try: growth inside a `mandapa` block; a `kosh` passed as a parameter then grown by the callee; a `kosh` stored in a `rachana` then grown. If all three stay in sync, the aliasing model is sound and should be documented as a feature, not a hazard.**

**ChatGPT:** **do not design the aliasing fix.** **Instead, answer this: now that Step 0's premise is false, should the recycling bins be reconsidered?** **They were dropped because the old buffer was not dead. If the old buffer IS dead on v278, the bins may be safe again — and they would fix the interleaved-`kosh` leak that in-place extension cannot. Say whether that is worth reopening, and what would have to be true.**

## And the rest of your rounds stands

**Claude: R83 WS2 and WS3 stand.** **ChatGPT: R153 WS2 (generics) and WS3 (the audit of my record) stand — and WS3 is now more useful than it was, because this is the fifth false claim I have made in a brief.**

## The process change, applied

**Every line of `## Verified behaviour` is now run in the turn it is written, with the output pasted. This file is the first one produced that way.**
