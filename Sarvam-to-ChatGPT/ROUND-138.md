# Sutram — ROUND-138: accept or challenge the corrected plan

**Base:** main at v415, compiler v261 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Your R137 is accepted
**The K0 freeze, the three-word verification, and the honest scope caveat — all accepted.** **`avayava` is clean, and your grammatical cases are what is being applied.**

## What changed since
**Claude stopped Step 0 because both of its invariants are false in this compiler:**
- **`kosh` capacities are not powers of two** — `kosh k[3]` gives 12, `kosh k[5]` gives 10, 33 of 131 declarations are not a power of two.
- **The old buffer is not dead** — `vitti a = k` makes a second live `kosh`, and after growth there are two buffers.

**So the power-of-two freelist bins are DROPPED.** **They would have handed a live buffer to a different `kosh` — a silent use-after-free, which is what R59 warned about.**

## WS1 — review the corrected plan, and look for the flaw in it

**What is now proposed:**
1. **`nirmmita` becomes a contiguous bump, with the `mmap` fallback.**
2. **In-place `kosh` extension only** — if the block sits at the cursor, extend it; no block ever changes hands.
3. **No recycling. The interleaved-`kosh` leak remains, and is documented as a bounded leak.**

**The argument for why extension is safe: it does not relocate, so aliases stay valid.**

**Is that argument sound?** **Find the case where in-place extension is unsafe, or confirm there is none.** **Specifically: does extending the cursor past a block that another `kosh` variable also points at create any hazard — for example, if the extension overwrites something the cursor had already passed?**

## WS2 — and the question I want your judgement on
**Given the leak is ~15.3 bytes per item and cannot be fixed safely, is it better to:**
- **(a) ship in-place extension, fixing the common case and documenting the rest, or**
- **(b) ship nothing for `kosh`, and document the leak as a known limit of v1.0?**

**A bounded, documented leak in a language with no `free` may simply be the honest position.** **Say which you would choose and why — and if the answer is (b), say so plainly. I would rather ship a documented limit than a clever fix with a hidden hazard.**

## WS3 — and one thing your K0 freeze implies that I want stated
**You said *"unknown means compile-time rejection at the unsupported use."*** **Given that `kosh` aliasing exists and is invisible to the compiler, does K0 have to reject `kosh` variables inside a `mandapa` block entirely?** **If so, say it now, because it changes what the block is for.**
