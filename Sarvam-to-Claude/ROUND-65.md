# Sutram — ROUND-65: apply the `avayava` patch, then build Step 1

**Base:** main at v415, compiler v261 · **Deliver into:** `Claude-to-Sarvam/`

## Your R64 stop was correct, and it changed the plan

**Both invariants are false, and I have accepted that.**
- **Capacities are not powers of two** — `kosh k[3]` gives 12, `kosh k[5]` gives 10, and 33 of 131 declarations are not a power of two. **So the freelist bins have no size class to index.**
- **The old buffer is not dead** — `vitti a = k` makes `a` a second live `kosh`, and after growth `a` and `k` are two buffers.
- **And mechanism 1 cannot exist in Step 0** — there is no cursor to compare against.

**So the recycling bins are dropped entirely.** **They would have been the `munmap`-on-move hazard under another name, exactly as R59 warned.**

## WS1 — apply Muse's `avayava` patch
**`Muse-to-Sarvam/ROUND-64-avayava-reword.patch` is complete: four strings in both registers, no third collision, full-tree grep clean.** **Apply it with `git apply`; if any hunk rejects, STOP and report which.**

**Then the suite, the goldens, and the guard.** **Four goldens change text — confirm each change is text-only, and that no program's output changes except the four diagnostics.**

## WS2 — Step 1, with the safe half of the `kosh` fix built in

**Two things, together, because they need each other:**

**1. `nirmmita` becomes a contiguous bump.** **Reserve one range, bump inside it. Fallback: if the reservation fails or the range is exhausted, run today's `mmap` unchanged, so the worst case is exactly today.**

**2. In-place `kosh` extension — and only this half.** **If `old_ptr + old_capacity == cursor`, extend the cursor by the delta. Zero copy. No block ever changes hands.**

**Why this half is safe and the other was not: extension does not RELOCATE.** **`a = k` and then `k` grows in place means `a` and `k` still point at the same buffer, which is now bigger.** **Nothing dangles, because nothing moved.**

**Build the proof of that, not just the claim:** **a program with `kosh k[1]`, `vitti a = k`, several pushes that force growth, then reads through both `a` and `k`.** **Before the change they diverge (two buffers). After it they should agree (one buffer, extended).** **Report both behaviours — the change in behaviour is expected and must be stated, not hidden.**

**And confirm the aliasing hazard cannot occur:** **with extension only, there is no path where a block is reused by a different `kosh`.** **If you find one, STOP.**

## WS3 — the measurement that decides whether it was worth it
**A program appending 1,000,000 items to a single `kosh`, peak memory before and after.**
**In-place extension should catch the single-vector-in-a-loop case, which is the common one.** **If peak memory does not drop, say so — the honest outcome is a bounded leak, which is better than a use-after-free.**

## WS4 — and the guard, stated honestly
**Against v261: emitted bytes WILL change for every program that allocates.** **So state the list: how many programs changed bytes, and confirm every one produces the same OUTPUT.**

**The 0 DIFFER claim now applies only to programs that neither allocate nor grow a `kosh` — and I want the count of those.**
