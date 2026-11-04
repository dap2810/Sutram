# Sutram — ROUND-122: merge the arena, and make the cost visible.

**Base:** main at v297 · **Deliver into:** `Claude-to-Sarvam/`

## The memory 100% round - five gaps, measured

**Works on Linux, measured: allocation 2-8 ns; `mandapa` returns memory (52,760 KB -> 13,480 KB at 200k allocations); `mandapa parimita N` refuses past a budget (1 MB admitted exactly 16,384 x 64-byte allocations then refused); a `kosh` cannot escape its block (`E_KOSH_MANDAPA` both ways); `parimana()` reports (0 -> 48 -> 72 -> 184 -> 288 -> 176); aliasing closed below 8,388,603 elements.**
**Five gaps to close:**
**1. WINDOWS: `parimana()` returns zero, `parimita` does not enforce, the `kosh` alias diverges. Confirmed on real Windows hardware.**
**2. The arena is built on `claude/r108-arena-review` (fixed at `3a6292e`) and has NEVER been merged or re-attacked since the fix.**
**3. Nothing is reused inside a live block. Not designed.**
**4. 64 MiB reserved per `kosh` is invisible - a student cannot reason about what a `kosh` costs. That contradicts the design goal.**
**5. No threads, so the model has never been asked what two threads do to one arena.**

## WS1 - the arena, which is fixed and unmerged
**`claude/r108-arena-review` at `3a6292e` fixes `chain40_reuse.sm` - the case where a block `kosh` passed through 40 `prakriya`s read another block's memory and printed 99.**

**It has not been merged and it has not been re-attacked since the fix.**

**Two things, in this order:**
1. **Re-run `chain40_reuse.sm` on the branch and confirm it now refuses.**
2. **If it refuses, say what merging would change: which programs' behaviour, and how many.**

**Do not merge this round.** **Answer the question first.** **Then Muse attacks it, then you merge.**

## WS2 - and the cost that is invisible
**A `kosh` reserves 64 MiB of address space.** **A student cannot reason about what a `kosh` costs, because the answer is "64 MiB of address space, of which some small part is real".**

**That contradicts the whole design goal, which is that memory should be obvious.**

**Two questions:**
- **What does a `kosh` ACTUALLY cost in real memory - not reserved, committed?** **Measure it: 1, 10, 100, 1000 live `kosh`, peak RSS and virtual size for each.**
- **Can the reservation be smaller without breaking the never-move guarantee?** **If 64 MiB is the smallest that keeps `R101A_MAXCAP` above any realistic collection, say so and say what the real limit is.** **If it could be 1 MiB, say what that would break.**

**A number a student can hold is worth more than a guarantee they cannot see.**

## WS3 - and the region return
**You decided a block `kosh` outlives the block, and I accepted it.** **The arena would close that.**

**So: if the arena merges, is the region return still needed, or does the arena make it moot?**

**One answer.**
