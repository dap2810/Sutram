# Sutram — ROUND-99: v284 changes the tree. Re-run the census and settle `samskara`.

**Base:** main at v284 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - all three of you on the same page

**Compiler v284** (was v283). **Claude built "Option A": every `kosh` has a region of its own and never moves.** That closes the aliasing gap - `vitti a = k` can no longer diverge, because nothing relocates.
**Guard, v283 to v284: 86 programs differ, all of them ones that make a `kosh`. All 86 run old and new: 85 print identical output, 1 changed - example 288, the intended fix.**
**Suite 270, proofs 229/229 and 86/86, gates 59 PASS / 1 FAIL (installer v243 against v284) / 1 NOT-RUN (Windows).**
**Measured by me, fork/wait4: 200,000 function calls each allocating 256 B - 52,760 KB without a block, 13,480 KB with one.** 200k x 256 = 51.2 MB, so every allocation stayed live. **One word, `mandapa`, took it from 52.7 MB to 13.5 MB.**
**Census (Muse, three runs, same numbers): 4 programs allocate in a loop; 0 grow a `kosh` past 1,000; 83 allocate without a block.**
**`parimita` PASSES the four naming tests. `kalpasmriti` is REJECTED (novel compound); `samskara` replaces it.**

## You were right about `dasham -> mala` and I misread your data
**Your R90 said "it stores the raw bits". I read the "0" in your census - a count of examples - as a stored value, and told three partners you had said "stores zero".** **That was my error and it is in the record.**

## WS1 - the census on v284, fourth run
**Option A gave every `kosh` a region of its own and made it never move.** **That changes what allocation means.**

**Re-run the three counts on v284:**
1. **Programs allocating inside a loop**
2. **Programs growing a `kosh` past 1,000**
3. **Programs allocating without a `mandapa`**

**If any number moved, say which and why.** **If they are identical, say that - the third identical run is itself evidence.**

## WS2 - and `samskara`, which is your argument
**You rejected `kalpasmriti` as a novel compound and proposed `samskara`.** **ChatGPT is being asked whether it accepts.**

**Give me the final form: the word, its literal meaning, why it names a generation, and one line of `.sm` code using it.** **If the concept is no longer needed at v284 - because nothing relocates and a `kosh` made in a block dies with it - say that instead, and save us a keyword.**

## WS3 - and the misread audit
**How many of your reports have I misread?** **You have corrected me four times now.** **List the ones you know of, so the record is complete rather than only carrying my side.**
