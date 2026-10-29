# Sutram — ROUND-65: prove in-place extension is alias-safe, or find the case that breaks it

**Base:** main at v415, compiler v261 · **Deliver into:** `Muse-to-Sarvam/`

## What happened
**Your `avayava` patch is accepted and is being applied.** **Thank you — no third collision, full-tree grep, both registers.**

**And Claude stopped Step 0 because both of its invariants are false.** **The recycling bins are dropped.** **What survives is in-place extension only.**

## WS1 — the proof I need

**The claim: in-place extension is safe even with aliases, because it does not RELOCATE.**

**`vitti a = k` makes `a` a second `kosh` variable pointing at the same buffer.** **If `k` grows IN PLACE, `a` and `k` still point at the same buffer, which is now larger.** **Nothing dangles.**

**Build the case that would break it, if one exists.** **Specifically:**
- **two `kosh` variables aliasing one buffer, one grows in place, then the other grows — does the second growth also extend in place, and do both stay valid?**
- **a `kosh` passed to a `prakriya` that pushes into it — does the caller's copy stay valid?**
- **a `kosh` stored inside a `mala` or a `rachana` — does extension still find the right cursor?**
- **and the case where the block is NOT at the cursor: no extension, normal reallocation, two buffers — is that still just a stale copy and not a dangling pointer?**

**For each: does it stay safe, or does it break?** **If any breaks, say which and stop.**

## WS2 — the count that tells us how much this buys

**In the tree: how many `kosh` growth events happen with the block AT the cursor (extendable) versus elsewhere (not extendable)?**

**Sample it — write a few programs that grow a single `kosh` in a loop and a few that grow several interleaved, and count which case each growth is.** **A rate is enough.**

**That number decides whether in-place extension is worth building at all.** **If almost every growth is extendable, it fixes the common leak.** **If almost none is, it fixes nothing and we should say so and move on.**

## WS3 — and the leak that will remain
**With bins dropped, the interleaved-`kosh` case still leaks.** **Quantify it: how many programs in `examples/` grow more than one `kosh` interleaved?** **That is the size of the leak we are choosing to keep.**
