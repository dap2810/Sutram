# Sutram — ROUND-110: attack the REAL arena branch, and confirm the `mala` defect

**Base:** main at v292 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - v292

**22 builtins renamed as aliases, `asti`/`nasti` are `==`/`!=`. Suite 295, gates 60 PASS, guard 705 programs 0 DIFFER.**
**Memory: blocks return memory (measured 52,760 KB -> 13,480 KB at 200k allocations); `mandapa parimita N` refuses past a budget; the outlives rule refuses storing or returning a block `kosh`; `parimana()` reports (0 -> 48 -> 72 -> 184 -> 288 -> 176).**
**The block-arena is BUILT on `claude/r108-arena-review` (0e71e54), UNMERGED, and Claude R109 reports a SILENT WRONG ANSWER on it that nobody has diagnosed.**
**`dasham` into a `mala` element stores the raw IEEE bits: `3.0` becomes `4613937818241073152`. Found by Muse, confirmed by me, never assigned.**
**55 distinct error codes, no exception handling - a program cannot raise or recover from an error.**

## WS1 - your R105 attack hit the wrong branch
**ChatGPT R179 corrected me on this and it was right: your R105 WS2 says PENDING, because ChatGPT's R178 design had not landed. Your executed attack targeted Claude's older one-name branch.**

**So the arena has never been properly attacked.** **Attack `claude/r108-arena-review` at `0e71e54` now.**

**Specifically:**
- **an alias taken before growth inside the arena - does it see the new data?**
- **a `kosh` that outlives its block - is it refused, and at which point?**
- **an arena exhausted mid-block - what happens?**
- **two `kosh` in one arena, one grown - does the other survive?**
- **and `parimana()` while the arena is in use - does it report something meaningful?**

**Report the program, the output, and whether the output is wrong or merely unexpected.** **Claude says there is a silent wrong answer on this branch and has not named it - find it independently so we have two sources.**

## WS2 - and the `mala` defect, confirmed by running
**`dasham d = 3.0; mala m[4]; m[0] = d`** **- I measured the raw IEEE bits on v286.** **Run it on v292 and report exactly what happens: bits, converted value, or refusal.**

**Then: what SHOULD it do?** **Convert to an integer, refuse, or store the bits deliberately with the reference saying so?** **Give one recommendation.**

## WS3 - and the census, twelfth run
**Three counts, same method.** **And: how many of the 291 examples store a `dasham` into a `mala`?** **That is the population the fix would affect.**
