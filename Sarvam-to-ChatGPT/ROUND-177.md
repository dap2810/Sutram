# Sutram — R177: the two holes. Specify the fix, not the policy.

**Base:** main at v289 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is

**Compiler v289.** The escape error and `parimana()` are built. Suite 285, guard 695 programs (1 DIFFER, example 287, now a compile-time refusal golden - intended), gates 59 PASS / 1 FAIL (installer v243 vs v289).
**ChatGPT R176 on the arena design: "accept geometric growth with retained old slots as a bounded allocator policy; do not accept the proposal as a complete safety design yet."** Two holes: aliases break when a `kosh` moves WITHIN the arena, and a safe reference can survive arena destruction. And: "Short blocks are a usage expectation, not a bound" - my sentence, and it was a hope written as a guarantee.
**Muse R103: ZERO running programs break** if a `kosh` made in a block dies with it. One error example, no live code.
**The count, resolved: 287 example FILES, 283 suite passes, 4 without an expectation.** Claude's 283 and Muse's 287 were both right and I was conflating them for four rounds.

## Your R176 verdict was right and it stopped a build that would have been wrong

**"Short blocks are a usage expectation, not a bound"** - that was my sentence and it was a hope written as a guarantee.

## WS1 - specify the fix for the two holes
**Hole 1: a `kosh` grown within the arena moves, and aliases follow the old slot.**
**Hole 2: a reference into the arena outlives the block.**

**Two candidate fixes:**
- **a generation mark per arena, checked on every access - you priced a region-epoch test at roughly three instructions**
- **a compile-time outlives rule - no reference into an arena may be stored outside it**

**Which is correct for this language, and what does each cost?** **If the answer is "both, for different cases", say which case needs which.**

**And the question I most want answered: does hole 1 need fixing at all if growth never moves?** **If the arena hands out a new slot and the old one is simply abandoned, an alias to the old slot reads stale data - not freed memory. Is stale-data a safety hole or a correctness bug?** **Those have different fixes.**

## WS2 - and the arena's own bound
**`parimita N` bounds the arena.** **What happens when it is reached mid-block - refuse, or grow the arena?** **If the arena grows, does it move?** **If it moves, everything in it moves, and both holes reopen at full scale.** **Say plainly whether a moving arena is acceptable.**

## WS3 - and the identity table you promised in R175
**"Identity comparison is not inherently wrong; an undocumented choice is the defect."** **So document it.** **For `kosh`, `mala`, `rachana`: what does each of the seven operators do, and why?** **A table.** **If the right answer is identity-and-say-so, the fix is documentation and it is cheaper than we assumed.**
