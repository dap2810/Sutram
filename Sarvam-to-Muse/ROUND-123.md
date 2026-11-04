# Sutram — ROUND-123: do the docs describe v297, or a language that no longer exists?

**Base:** main at v297 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - v297

**315 suite passes, 62 Linux gates, 319 examples, 310 library functions, 57 error codes.**
**Windows has been tested for the first time: 305 native passes, 8 failures. Three causes - two harness errors of mine, four documented Linux-only memory features, and TWO REAL WINDOWS DEFECTS: `anka_akshar` returns `P` instead of `B`, and `vartani_sandhi` crashes with an access violation. Both print correctly on Linux.**
**The class: a function that returns a pointer to storage it does not own. Linux happens not to notice.**
**Memory on Linux is 85%: blocks return memory, `parimita` refuses, escape refused, `parimana()` reports. Gaps: a block `kosh` outlives its block; the arena is built and unmerged; no reuse inside a live block; 64 MiB per `kosh` is invisible; no threads.**

## WS1 - the documentation audit
**This project has changed enormously in two weeks.** **22 builtins renamed, `asti`/`nasti` added, `Sutram Error` became `Sutram truti`, `sankhya_bindu` withdrawn, 15 library contracts now refuse, `patra_asti` still broken.**

**Does the documentation describe that language, or an older one?**

**Check every file in `docs/` and the root:**
- **does it still say `Sutram Error` where the compiler now says `Sutram truti`?**
- **does it list `kosh_push` as the primary name rather than an alias?**
- **does it mention `asti`/`nasti` at all?**
- **does the memory section mention `parimita` and `parimana`, and does it say they are Linux-only?**
- **does it still describe `sankhya_bindu` as available?**
- **does the library reference list 306 functions when there are 310?**

**Name the file, the line, and what it should say.** **A stale doc is worse than a missing one, because a reader trusts it.**

## WS2 - and the Windows gap in the docs
**A student on Windows gets a `parimana()` that returns zero and a `parimita` that never refuses.** **Does any doc say so?**

**If not, that is the single most important missing paragraph in the project.**

## WS3 - and the memory reference section
**Memory on Linux is 85% done and the remaining 15% is five documented gaps.** **Does the reference state all five?**

**List them, and say which the reference omits:**
1. a block `kosh` outlives its block
2. the arena is built but unmerged
3. no reuse inside a live block
4. 64 MiB per `kosh` is invisible
5. no threads

**A gap that is documented is a limitation. A gap that is not is a surprise.**
