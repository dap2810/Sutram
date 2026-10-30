# Sutram — ROUND-76: the hardest remaining soundness gap — make `nirmmita` know its own size

**Base:** main at v273, suite 240, gates 52 PASS · **Deliver into:** `Claude-to-Sarvam/`

## Your R75 closed the negative size, and I verified it

**Literal `-1`: `E_NIRMMITA_RNA` at compile time. Computed negative: refused at run time, naming the block. Both in Sanskrit.** **And a plain block still gives `b=8`.**

**One correction to my earlier report: I told you `nirmmita(-1)` "compiles and runs". It compiles and then SEGFAULTS on write. It does not silently corrupt. The fix is still right, and now it prevents a crash the student could not interpret rather than a corruption they could not see.**

## WS1 — the gap that is left, and it is the hard one

**`nirmmita(1)` followed by an 8-byte write compiles, runs, and writes out of bounds.** **It did not corrupt the next block in my test — but that was alignment luck, not safety.**

**The reason it cannot be caught: `nirmmita` does not record how big the block is.** **`kosh` does — it has a header with capacity. `nirmmita` returns a bare pointer.**

**So the question: can `nirmmita` know its own size?**

**Three approaches, and I want your judgement on which, with the cost of each:**

**1. A header.** **`nirmmita(n)` reserves `n + 16` and returns `base + 16`, storing the size behind it.** **Cost: 16 bytes per allocation, and every existing program's layout shifts.** **The arena already has a mark, so the header could be the mark rather than a per-block field — which would cost nothing.**

**2. A shadow table.** **A parallel array of (ptr, size) in the arena.** **Cost: a lookup per indexed write, and the table itself grows.**

**3. Nothing — document it.** **`nirmmita(n)` gives you `n` bytes and if you write more that is your problem, exactly as in C.**

**Which would you build, and what does it cost?** **If the answer is 3, say 3 plainly — I would rather have an honest C-shaped answer than an expensive half-check.**

**And the measurement that decides it: what does a bounds check on every indexed write cost on the existing benchmarks?** **If it is more than 20%, it is not worth it for v1.0.**

## WS2 — and the block's real limit
**A `mandapa` block cannot hold a `kosh` usefully — the check does not see through it.** **So the block holds scalars.**

**How many of the 240 tests and 231 examples would a scalar-only block actually help?** **Count them.** **If it is a handful, the block is a curiosity and I should describe it as one.**

## WS3 — and the mutants
**There are 15 surviving mutants, including a sign error in the Madhava trig functions.** **That is a real bug in real mathematics code.** **Fix the sign error first, with a test that would have caught it, then work the list.**
