# Sutram — ROUND-123: merge PR #65. One commit, one guard.

**Base:** main at v298 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is - v298 on main, and Windows round 4 is done on a branch

**v298: `anka_akshar` and `vartani_sandhi` fixed on main. Verified by me: `anka_akshar(66)` gives `B`, `(97)` gives `a`.**
**Windows round 4 (`codex/windows-round4-2026-11-03`, PR #65, NOT merged): 312 PASS / 0 FAIL, up from 306/3. Linux unchanged at 315.**
**`parimana()` now returns live logical bytes on Windows; `mandapa parimita` enforces; the `kosh` alias now gives `a[0]=99 k[0]=99` on Windows; `E_WINDOWS_SMRITI` removed.**
**Root cause found: `r65_active` is a compiler predicate, not storage; PE was excluded by a runtime `target_pe` check inside the GUARD_PAGES conditional, not an assembly guard. Enabling the shared arena for PE worked.**
**Known cost: the PE adapter reserves AND commits, so the Linux 1 GiB arena charges 1 GiB of Windows commit even for tiny programs. No lazy commitment on Windows.**
**A `kosh` costs one 4 KB page plus 8 bytes per element, AND 64 MiB of address space - under a 1 GiB address limit the 16th `kosh` crashes the program.**

## WS1 - merge the Windows round 4 branch
**`codex/windows-round4-2026-11-03`, draft PR #65.** **It reports 312 PASS / 0 FAIL on Windows and Linux unchanged at 315.**

**Verify it yourself before merging:**
- **does `parimana()` return real bytes on Windows in their probes?**
- **does `mandapa parimita` enforce?**
- **does the `kosh` alias give `a[0]=99 k[0]=99` on Windows?**
- **and on Linux, is the suite still 315 and the guard 0 DIFFER?**

**Then merge, one commit, one guard run.**

**If anything in it is wrong, do not merge - say what and why.** **You have stopped three rounds on a real blocker and each time you were right.**

## WS2 - and the 1 GiB commit cost
**The branch's own report says: *"enabling the Linux 1 GiB arena unchanged charges 1 GiB of Windows commit, even for tiny programs."***

**That is a real limitation, not a correctness bug.** **Two questions:**
- **Is 1 GiB of commit acceptable for a teaching language?** **On a 4 GB machine, a hello-world program taking 1 GiB of commit is not.**
- **What would a smaller arena cost?** **If `R101A_REGION` were 64 MiB instead of 1 GiB, how many `kosh` could a program have before the 8,388,603-element cap binds?**

**Give me the trade in numbers.** **Do not change it this round - just price it.**

## WS3 - and the 16-`kosh` ceiling
**Measured: 64 MiB of address space per `kosh`, so under a 1 GiB address limit the 16th `kosh` crashes.**

**That is a hard ceiling a student could hit.** **Is it acceptable, or does `R101A_REGION` need to be smaller?**

**Same question as WS2, from the other direction: the reservation is what makes aliases safe, and it is also what caps the collection count.** **Say what the right number is and why.**
