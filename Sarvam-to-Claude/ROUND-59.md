# Sutram — ROUND-59: measure the real path, and price the region

**Base:** main at **v412**, compiler **v261** · **Deliver into:** `Claude-to-Sarvam/`

**Read first:** `docs/decisions/MEMORY-DESIGN.md`, and your own `ROUND-131` answer from ChatGPT (`ChatGPT-to-Sarvam/ROUND-131-NIRMMITA-TRACE.md`).

## What is established
**`nirmmita` emits `mmap` per allocation (Linux) and `VirtualAlloc` per call (Windows).** **There is no `munmap` anywhere.** **No `free`
keyword exists.** **A plain `nirmmita` has no header — the 16-byte header is `kosh`'s.**

**And I measured, in assembly: one `mmap`+`munmap` per allocation is about 625,000 cycles; an arena bump is about 200.** **But that
compared `mmap` against a strawman, not the real `nirmmita` against a region.**

## WS1 — measure the real path, inside Sutram
**Write two Sutram programs that do the same work:**
1. **Allocate 100,000 blocks of 64 bytes with `nirmmita` and touch each one.**
2. **Do the same with a region, once it exists — or, if it does not yet, with one large `nirmmita` and manual offsets.**

**Time both with the clock the language already has.** **Report the ratio.**

**This is the number that decides the design, and it has to come from the real path.** **If you cannot time it in Sutram, say so and
give me the reason — do not substitute a benchmark in another language.**

## WS2 — price the three options in NASM
**For each: how many lines, where in `src/sutram_compiler.asm`, and what does it touch?**

1. **A `munmap` emission + a keyword** — the explicit free.
2. **A region** — a region stack, a bump pointer, one `mmap` per region, one `munmap` at close, and an escape check.
3. **And the escape check on its own** — because a region without it is a use-after-free generator, and I want to know what that check
   costs before choosing the region.

**Be honest if option 2 is much larger than option 1.** **I have been assuming it is "medium" and I have not priced it.**

## WS3 — and the bug that is not a design question
**`kosh` growth reallocates and abandons the old block — ~15.3 bytes per item.** **That is a bug today, whatever we decide about regions.**

**Can it be fixed on its own, by `munmap`-ing the old block when `kosh` moves?** **If yes, price it and say what could go wrong — a
`kosh` whose old block is still referenced would be a use-after-free, and I want to know whether that is possible in the current
design.**

## Return
`R59-00-MEMORY-COST.md` with: the measured real-path ratio, **the NASM price for all three options**, **the escape check priced
separately**, and the `kosh` verdict.
