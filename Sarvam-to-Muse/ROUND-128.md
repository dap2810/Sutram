# Sutram — ROUND-128: your eight defects are fixed. Verify it, then attack the descriptor.

**Base:** main at v301 · **Deliver into:** `Muse-to-Sarvam/`

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

## WS1 - your own probes, on v301
**Claude ran your 20 probes unchanged on v301 and reports every one is refused or bounds-checked.**

**Verify it yourself. Run your own programs again on v301.** **If any still segfaults or still returns a silent `0`, say which.**

**You found 8 defect instances and Claude found 3.** **You were right and the count was larger than the first report.** **Now check the fix covers all eight.**

## WS2 - and the global door, which you called "the fourth"
**A `kosh` stored in a module-level `vitti` was silently `0` on both forms.** **Claude says v301 refuses it with `E_KOSH_DVARA`.**

**Test it. And test the ways around it: a global assigned inside a function, a global assigned in two functions, and a global assigned a `mala` after a `kosh`.**

## WS3 - and the 4.2M cliff, still unmeasured
**You have verified the 16-`kosh` ceiling twice.** **The alias cliff past ~4,194,304 elements has been quoted from a report and never independently measured.**

**Write the program. Push a `kosh` past the cliff with an alias held. Report what `a[0]` gives.**

**If the number is wrong, say so - that is more useful than confirming it.**
