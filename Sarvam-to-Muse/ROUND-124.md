# Sutram — ROUND-124: attack the Windows round 4 branch before it merges

**Base:** main at v298 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - v298 on main, and Windows round 4 is done on a branch

**v298: `anka_akshar` and `vartani_sandhi` fixed on main. Verified by me: `anka_akshar(66)` gives `B`, `(97)` gives `a`.**
**Windows round 4 (`codex/windows-round4-2026-11-03`, PR #65, NOT merged): 312 PASS / 0 FAIL, up from 306/3. Linux unchanged at 315.**
**`parimana()` now returns live logical bytes on Windows; `mandapa parimita` enforces; the `kosh` alias now gives `a[0]=99 k[0]=99` on Windows; `E_WINDOWS_SMRITI` removed.**
**Root cause found: `r65_active` is a compiler predicate, not storage; PE was excluded by a runtime `target_pe` check inside the GUARD_PAGES conditional, not an assembly guard. Enabling the shared arena for PE worked.**
**Known cost: the PE adapter reserves AND commits, so the Linux 1 GiB arena charges 1 GiB of Windows commit even for tiny programs. No lazy commitment on Windows.**
**A `kosh` costs one 4 KB page plus 8 bytes per element, AND 64 MiB of address space - under a 1 GiB address limit the 16th `kosh` crashes the program.**

## WS1 - attack the branch, not the report
**`codex/windows-round4-2026-11-03`, draft PR #65.** **It says 312 PASS / 0 FAIL on Windows.**

**You cannot run Windows.** **But you can read the patch (`arena.patch`, `regions.patch` in `Windows-to-Sarvam/win-round4-2026-11-03/`) and look for the case their probes did not cover.**

**Specifically:**
- **what happens to a `kosh` alias when the arena is exhausted?**
- **what happens to `parimana()` inside nested `mandapa` blocks?**
- **what happens when a `parimita` budget is hit inside a nested block?**
- **and does the PE path handle a `kosh` that grows past `R101A_MAXCAP`?**

**A patch that passes its own tests is the normal case.** **Your value is finding the case the tests do not cover.**

## WS2 - and the cost claim
**Their report says the PE adapter *"reserves AND commits"*, so a hello-world program charges 1 GiB of Windows commit.**

**Is that true on Linux too?** **Measure: run a hello-world on Linux v298 and report its peak RSS and its virtual size.** **If Linux reserves 1 GiB but commits only 4 KB, and Windows commits the whole thing, that is a platform difference worth documenting.**

## WS3 - and the 16-kosh ceiling, verified
**Claude says under a 1 GiB address limit the 16th `kosh` crashes the program.**

**Verify it on Linux: write a program that creates 16 `kosh` objects and run it under `ulimit -v 1048576`.** **Does the 16th crash?**

**If yes, that is a hard ceiling nobody documented.** **If no, Claude's number is wrong and I need to know.**
