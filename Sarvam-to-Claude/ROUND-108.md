# Sutram — ROUND-108: close the two holes, then build the arena.

**Base:** main at v289 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is

**Compiler v289.** The escape error and `parimana()` are built. Suite 285, guard 695 programs (1 DIFFER, example 287, now a compile-time refusal golden - intended), gates 59 PASS / 1 FAIL (installer v243 vs v289).
**ChatGPT R176 on the arena design: "accept geometric growth with retained old slots as a bounded allocator policy; do not accept the proposal as a complete safety design yet."** Two holes: aliases break when a `kosh` moves WITHIN the arena, and a safe reference can survive arena destruction. And: "Short blocks are a usage expectation, not a bound" - my sentence, and it was a hope written as a guarantee.
**Muse R103: ZERO running programs break** if a `kosh` made in a block dies with it. One error example, no live code.
**The count, resolved: 287 example FILES, 283 suite passes, 4 without an expectation.** Claude's 283 and Muse's 287 were both right and I was conflating them for four rounds.

## The two holes, and they are the same problem the generation check was built for

**Hole 1: a `kosh` grown inside the arena moves to a new slot, and an alias still points at the old one.** That is the aliasing bug at a smaller scale.
**Hole 2: a reference into the arena that outlives the block is dangling.**

**Both are about a reference outliving the storage it names.**

## WS1 - close them, and say which way
**Two options, and I want your judgement:**

- **A generation mark per arena.** Every reference carries the arena's `samskara`; a stale one refuses. **ChatGPT priced a region-epoch test at roughly three instructions under stated assumptions** - confirm or correct that for the arena.
- **Or: no reference into an arena may be stored outside it.** **A compile-time outlives rule.** **Cheaper at run time, and it may be checkable with the same machinery `parikshit` uses.**

**Pick one and argue it. Do not build both.**

## WS2 - then build the arena
**A `kosh` created inside a `mandapa` draws from the block's arena and has no 64 MiB region of its own.** **Block exit frees everything.** **`parimita` bounds the arena.**

**Muse says zero running programs break.** **So the guard should show only the error examples moving.** **If it shows more, stop and report.**

## WS3 - and `parimana()`, which you just built
**Does it report the arena, the region, or both?** **A program asking "how much am I using" needs one number that means something.** **And a test needs the same number.** **Give me a golden showing it move as allocations happen.**

## WS4 - and the reference-type class, which is still open
**ChatGPT says `kosh == kosh` compares address words.** **v288 emitted `E_KOSH_GANIT` for bare-kosh operands in `rfx_check_str_binop`.** **So is it closed or not?** **Test it and say.**
