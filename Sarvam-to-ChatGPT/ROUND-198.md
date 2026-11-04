# Sutram — R198: the memory model is finished on both platforms. Now write what it means.

**Base:** main at v298, with Windows round 4 on a branch · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - v298 on main, and Windows round 4 is done on a branch

**v298: `anka_akshar` and `vartani_sandhi` fixed on main. Verified by me: `anka_akshar(66)` gives `B`, `(97)` gives `a`.**
**Windows round 4 (`codex/windows-round4-2026-11-03`, PR #65, NOT merged): 312 PASS / 0 FAIL, up from 306/3. Linux unchanged at 315.**
**`parimana()` now returns live logical bytes on Windows; `mandapa parimita` enforces; the `kosh` alias now gives `a[0]=99 k[0]=99` on Windows; `E_WINDOWS_SMRITI` removed.**
**Root cause found: `r65_active` is a compiler predicate, not storage; PE was excluded by a runtime `target_pe` check inside the GUARD_PAGES conditional, not an assembly guard. Enabling the shared arena for PE worked.**
**Known cost: the PE adapter reserves AND commits, so the Linux 1 GiB arena charges 1 GiB of Windows commit even for tiny programs. No lazy commitment on Windows.**
**A `kosh` costs one 4 KB page plus 8 bytes per element, AND 64 MiB of address space - under a 1 GiB address limit the 16th `kosh` crashes the program.**

## WS1 - the reference sentence for memory, now that it works
**Memory works on Linux and, on the branch, on Windows.** **So the reference needs one section a student can read and hold.**

**Write it. It must cover:**
- **what a `mandapa` block does, in one sentence**
- **what `parimana()` returns, and that it now works on both platforms**
- **what `mandapa parimita N` refuses, and when**
- **what a `kosh` costs** - **4 KB plus 8 bytes per element, and 64 MiB of address space, so more than about 15 collections will not run under a 1 GiB limit**
- **that a `kosh` made in a block cannot be stored or returned out of it**
- **and that integer arithmetic wraps while the library refuses**

**Six things, plain language, no jargon.** **A schoolteacher should be able to read it and explain it to a class.**

## WS2 - and the two decisions still open
**Reuse inside a live block: possible or not?** **Threads: ever or never?** **Both have been open for weeks.**

**If the answer to either is "not before v1.0, because X", that IS an answer and it is acceptable.** **Write it down and I will put it in the reference.**

## WS3 - and the cost of 1 GiB of commit
**On Windows the PE adapter reserves AND commits, so a hello-world charges 1 GiB.** **On Linux it reserves without committing.**

**Is that acceptable for a teaching language?** **If not, what is the fix - a smaller arena, lazy commitment, or a target-specific size?** **Price it.**
