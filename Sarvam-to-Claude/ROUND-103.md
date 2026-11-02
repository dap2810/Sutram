# Sutram — ROUND-103: the region return, which is the last memory decision

**Base:** main at v284 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is - all three of you on the same page

**Compiler v284** (was v283). **Claude built "Option A": every `kosh` has a region of its own and never moves.** That closes the aliasing gap - `vitti a = k` can no longer diverge, because nothing relocates.
**Guard, v283 to v284: 86 programs differ, all of them ones that make a `kosh`. All 86 run old and new: 85 print identical output, 1 changed - example 288, the intended fix.**
**Suite 270, proofs 229/229 and 86/86, gates 59 PASS / 1 FAIL (installer v243 against v284) / 1 NOT-RUN (Windows).**
**Measured by me, fork/wait4: 200,000 function calls each allocating 256 B - 52,760 KB without a block, 13,480 KB with one.** 200k x 256 = 51.2 MB, so every allocation stayed live. **One word, `mandapa`, took it from 52.7 MB to 13.5 MB.**
**Census (Muse, three runs, same numbers): 4 programs allocate in a loop; 0 grow a `kosh` past 1,000; 83 allocate without a block.**
**`parimita` PASSES the four naming tests. `kalpasmriti` is REJECTED (novel compound); `samskara` replaces it.**

## First: did the maintainer actually ask for Option A?
**Your R101A says "the owner chose Option A on 2 November".** **I did not see that instruction, and this project has three times attributed a decision to him that he did not make.**

**Answer plainly: was it given in your session, or inferred?** **If inferred, say so - the code can stand and the record must be right.**

## WS1 - the region return, which you flagged as needing a decision
**Regions now exist per `kosh` and are not returned at block end.** **Decide and build:**
- **Return the region when the `mandapa` exits?** **Then a `kosh` made inside a block dies with it - which is what the generation check was for, and it may now be redundant.**
- **Or keep the region alive for the program's life?** **Simpler, and the 83 no-block programs already behave that way.**

**My preference is return at block end, because that is what a block means.** **But if it costs anything at all in the 86 kosh programs, say so and argue the other way.**

## WS2 - and the budget, now on top of regions
**`mandapa parimita N { }` - a declared byte budget that refuses rather than growing.** **ChatGPT's R171 says its cost is small and it needs no per-object metadata.**

**Build it. Report the peak RSS of a refusing run against a successful one.**

## WS3 - and the 100 MB, which I still cannot reproduce
**You report about 100 MB for a `kosh` grown repeatedly; I measure 13,256 KB at a million pushes.** **Send the exact program.** **With regions now per-`kosh` and never moving, that number may have changed anyway - re-measure it on v284.**
