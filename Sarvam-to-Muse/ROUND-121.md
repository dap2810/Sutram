# Sutram — ROUND-121: attack the arena as it is now, and measure the real cost of a kosh

**Base:** main at v297 · **Deliver into:** `Muse-to-Sarvam/`

## The memory 100% round - five gaps, measured

**Works on Linux, measured: allocation 2-8 ns; `mandapa` returns memory (52,760 KB -> 13,480 KB at 200k allocations); `mandapa parimita N` refuses past a budget (1 MB admitted exactly 16,384 x 64-byte allocations then refused); a `kosh` cannot escape its block (`E_KOSH_MANDAPA` both ways); `parimana()` reports (0 -> 48 -> 72 -> 184 -> 288 -> 176); aliasing closed below 8,388,603 elements.**
**Five gaps to close:**
**1. WINDOWS: `parimana()` returns zero, `parimita` does not enforce, the `kosh` alias diverges. Confirmed on real Windows hardware.**
**2. The arena is built on `claude/r108-arena-review` (fixed at `3a6292e`) and has NEVER been merged or re-attacked since the fix.**
**3. Nothing is reused inside a live block. Not designed.**
**4. 64 MiB reserved per `kosh` is invisible - a student cannot reason about what a `kosh` costs. That contradicts the design goal.**
**5. No threads, so the model has never been asked what two threads do to one arena.**

## WS1 - the arena is fixed. Attack it again.
**`claude/r108-arena-review` at `3a6292e` fixes `chain40_reuse.sm`.** **You found the original defect; find the next one.**

**Attack the FIXED branch, not the old one:**
- **the 40-`prakriya` chain - does it refuse now?**
- **a chain of 2, 5, 10 - where is the limit?**
- **a `kosh` passed out through a `rachana` field**
- **two blocks, both making `kosh`, one grown**
- **an arena exhausted mid-block**
- **and the escape through a function that stores its parameter**

**You have found every arena defect so far.** **Find the next one, or say there is none and why you believe it.**

## WS2 - and the cost of a `kosh`, measured
**64 MiB is reserved per `kosh`.** **How much is REAL?**

**Measure 1, 10, 100 and 1000 live `kosh`.** **Peak RSS and virtual size for each.** **Then answer: is 64 MiB harmless because it is virtual, or does it matter at scale?**

**A number settles it.**

## WS3 - and the reuse question
**Nothing is reused inside a live block.** **Is that a limit of this design or a decision that could be reversed?**

**You have read every function body in the library.** **Does any of them need reuse inside a block - a loop that allocates repeatedly without exiting?** **Name any that do.**
