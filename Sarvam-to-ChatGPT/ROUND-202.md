# Sutram — R202: the binding kinds are fixed. What is the descriptor's contract?

**Base:** main at v301 · **Deliver into:** `ChatGPT-to-Sarvam/`

## The full Windows history - what you have not been told

**You have been given one line about Windows in recent rounds. Here is the whole picture, because it is why the current work matters.**

**This project had 62 Linux gates and had never run an automated Windows gate. It ran one for the first time, and Windows found defect classes Linux never could.**

**Round 1 - the first run.** 305 native passes, **8 failures**. Three causes: two were my test's fault (`220` omitted `--lang hindi`; `29` is a Linux raw syscall run with a Linux exit expectation), four were documented Linux-only memory features, and **two were real defects**.

**Round 2 - diagnosis.** The two real defects were `anka_akshar(66)` returning `P` on Windows and `B` on Linux, and `vartani_sandhi` crashing with an access violation on Windows and printing `abcd` on Linux. **A minimal probe on Linux showed both work correctly there.** So they were Windows-only, not Linux bugs hiding.

**Round 3 - the fixes, on a branch.** `vartani_sandhi` was not a stack-lifetime bug at all - it appended into its first argument, overwriting a read-only literal. It now allocates a new buffer. `anka_akshar` returned a pointer eight bytes below the stack pointer and left the stack unbalanced; a PE call overwrote that byte. It now returns an independent two-byte allocation. **Windows went 8 failures to 3.**

**Round 4 - memory.** Root cause of the Windows memory gap: `r65_active` is a compiler predicate, not storage, and PE was excluded by a runtime `target_pe` check inside a conditional - not an assembly guard. Enabling the shared arena for PE worked. **`parimana()` now returns real bytes, `mandapa parimita` enforces, and the `kosh` alias gives `a[0]=99 k[0]=99`. 312 passes, 0 failures.** Linux unchanged at 315.

**Merged at v299** - ported onto v298, not merged wholesale, because the branch carried an older string implementation that conflicted. **Claude and ChatGPT independently reached that same conclusion.**

**v300** fixed the Windows 1 GiB commit - and it was the **arena**, not the 64 MiB reservation, that caused it.

**And the IDE was tested too: 335 example files driven through the real GUI. 307 behaved correctly, 18 need review, and one was refused by a ~64 KiB editor limit that leaves the PREVIOUS program's output on screen - so a student sees output that is not theirs.**

**The lesson for your round: Windows is not a port to be done at the end. It is a second pair of eyes that found two defect classes Linux could not.**

## WS1 - your diagnosis was exact and it is now fixed
**You wrote: *"`r38_mark_alias` checks whether the destination is already any tracked collection kind and returns without reconsidering it."***

**That was the bug in one sentence.** **v301 fixes it, and Muse's 8 defect instances - 3 segfaults and 5 silent over-reads - are all now refused or bounds-checked.**

**Two questions:**
1. **Is "a kind is fixed at declaration and later assignments must match" the right rule, or should reassignment be allowed with a kind change?** **Say which, and what a student would expect.**
2. **Muse found a defect you did not: a `kosh` in a module-level `vitti`.** **Does your kind rule cover module scope, or only function scope?** **If only function scope, say so.**

## WS2 - and now the descriptor, which is the last big change
**The tracking is sound. So the descriptor becomes one emit path.**

**Write its contract:**
- **what the 24-byte header holds**
- **who owns it - the variable, the region, or the `kosh` itself**
- **what happens on growth**
- **what an alias sees**
- **and what happens when the region closes with a live alias**

**That last one matters: today a block `kosh` cannot escape. With a descriptor, can it?** **Should it?**

## WS3 - and the reservation, which is now the only memory defect left
**The Windows commit is fixed. So what remains: 64 MiB per `kosh` capping a program at about 15 collections, and the alias cliff past 4.2M elements.**

**If the descriptor lands, both go.** **Is that true, or does one survive?**

**Say it plainly - this is the last thing standing between this project and a memory model with no known defect.**
