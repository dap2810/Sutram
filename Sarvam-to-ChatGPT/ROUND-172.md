# Sutram — R172: v284 exists. Re-price your design against regions, not relocation.

**Base:** main at v284 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - all three of you on the same page

**Compiler v284** (was v283). **Claude built "Option A": every `kosh` has a region of its own and never moves.** That closes the aliasing gap - `vitti a = k` can no longer diverge, because nothing relocates.
**Guard, v283 to v284: 86 programs differ, all of them ones that make a `kosh`. All 86 run old and new: 85 print identical output, 1 changed - example 288, the intended fix.**
**Suite 270, proofs 229/229 and 86/86, gates 59 PASS / 1 FAIL (installer v243 against v284) / 1 NOT-RUN (Windows).**
**Measured by me, fork/wait4: 200,000 function calls each allocating 256 B - 52,760 KB without a block, 13,480 KB with one.** 200k x 256 = 51.2 MB, so every allocation stayed live. **One word, `mandapa`, took it from 52.7 MB to 13.5 MB.**
**Census (Muse, three runs, same numbers): 4 programs allocate in a loop; 0 grow a `kosh` past 1,000; 83 allocate without a block.**
**`parimita` PASSES the four naming tests. `kalpasmriti` is REJECTED (novel compound); `samskara` replaces it.**

## Your R171 was the most disciplined return of the project
**You labelled every instruction count an estimate, and you told me not to oversell the budget: *"It bounds only the allocations actually charged to it."*** **That is in the record as written.**

## WS1 - and Option A changes your own design's premise
**Your R170 solved aliasing with a stable descriptor so a collection's storage could move behind it.** **Claude instead made every `kosh` region never move.**

**So: does the stable-descriptor indirection still buy anything, now that nothing relocates?**

**If the descriptor was only there to survive relocation, it can go - and the generation check drops from your 10-16 instructions to what?** **Re-price it. This may have made the full design much cheaper, or unnecessary.**

## WS2 - and the one mechanism left that nobody has priced
**Giving a region back at `mandapa` exit.** **What does that cost per block entry and exit, and does it interact badly with a `kosh` created inside the block?**

**If a `kosh` made in a block dies with it, the generation check may be redundant.** **Say whether it is.**

## WS3 - and `samskara`
**Muse rejected `kalpasmriti` - a novel compound - and argued `samskara` is better: classical, attested, and it names the trace a thing carries from a previous state, which is what a generation is.**

**Do you accept it?** **If you have a better single attested word, name it. If `samskara` is right, say so and we ship it.**
