# Sutram — ROUND-127: the tracking is fixed at v301. Now the descriptor.

**Base:** main at v301 · **Deliver into:** `Claude-to-Sarvam/`

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

## WS1 - v301 catches all eight of Muse's defects
**Muse attacked v300's tracking without reading your R125 and found 8 defect instances: 3 segfaults and 5 silent over-reads.** **You ran its own programs on v301 and every one is now refused or bounds-checked.**

**That is the right result and it is worth saying plainly: your fix covered defects you had not found yourself.**

**Two things:**
1. **Are all eight now goldens, so they cannot regress?** **If any is not, add it.**
2. **Muse found the *global* door - a `kosh` stored in a module-level `vitti` was silently `0` on both forms.** **Is that closed by design, or by a check that could be bypassed?**

## WS2 - and now the descriptor, which is one emit path
**Your R125 said: once the tracking is sound, `vitti a = k` knows enough to emit a descriptor access.** **The tracking is now sound.**

**So: build the descriptor. A 24-byte header holding buffer pointer, length and capacity; aliases follow the header; growth updates the pointer inside it.**

**If that is right, it closes the alias cliff past 4.2M elements AND lets the 64 MiB reservation go - which closes the 15-`kosh` ceiling.**

**If it is not that simple, say what blocks it before writing code.**

## WS3 - and the order
**ChatGPT R201 says: fix binding kinds first, then change collection representation.** **You have done the first.**

**So give me the order for the second, with a number for each step.**
