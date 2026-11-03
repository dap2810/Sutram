# Sutram — ROUND-115: the arena's silent wrong answer. Find it, name it, fix it.

**Base:** main at v292 · **Deliver into:** `Claude-to-Sarvam/`

**Do this AFTER ROUND-114, not instead of it.**

## Where the project is - v292

**22 builtins renamed as aliases, `asti`/`nasti` are `==`/`!=`. Suite 295, gates 60 PASS, guard 705 programs 0 DIFFER.**
**Memory: blocks return memory (measured 52,760 KB -> 13,480 KB at 200k allocations); `mandapa parimita N` refuses past a budget; the outlives rule refuses storing or returning a block `kosh`; `parimana()` reports (0 -> 48 -> 72 -> 184 -> 288 -> 176).**
**The block-arena is BUILT on `claude/r108-arena-review` (0e71e54), UNMERGED, and Claude R109 reports a SILENT WRONG ANSWER on it that nobody has diagnosed.**
**`dasham` into a `mala` element stores the raw IEEE bits: `3.0` becomes `4613937818241073152`. Found by Muse, confirmed by me, never assigned.**
**55 distinct error codes, no exception handling - a program cannot raise or recover from an error.**

## WS1 - the defect you reported
**Your R109 says there is a silent wrong answer on `claude/r108-arena-review`.** **I do not know what it is.**

**Name it in the first line of your reply: the program, the expected output, the actual output.**

**Then diagnose it.** **The likely candidates are the ones ChatGPT named: an alias taken before growth seeing stale data, or a reference surviving arena destruction.** **But do not assume - run it.**

## WS2 - and then decide
**Three outcomes, and all three are acceptable:**

1. **Fix it and merge.** **Say what the fix costs.**
2. **It cannot be fixed cheaply - leave the branch unmerged and say why.** **An unmerged branch is a better outcome than a wrong one on main.**
3. **The defect is inherent to the arena design - say so and close the branch.**

**What is not acceptable is leaving it undiagnosed.** **A known defect in built code with no diagnosis is the worst state this project can be in.**

## WS3 - and the region return, which depends on this
**A `kosh` made in a `mandapa` outlives the block.** **The arena would close that gap - but only if the arena is sound.**

**So: do not build the region return this round.** **Answer this first: if the arena were sound, would returning regions at block exit be a small change or a large one?**

## WS4 - and one thing I want tested on main, not the branch
**`dasham d = 3.0; mala m[4]; m[0] = d` stores the raw bits.** **I measured `4613937818241073152` on v286 and nobody has touched it since.**

**Test it on v292 and report what it does now.** **Do not fix it this round - just tell me whether it still stores bits, converts, or refuses.**
