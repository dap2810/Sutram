# Sutram — R203: the descriptor is built. Is the memory model now finished?

**Base:** main at v302 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - v302, and the memory model has no known defect

**The descriptor is built. `kosh` is a 24-byte header that never moves; growth moves its elements and every name sees it.**
**THE ALIAS CLIFF IS GONE - 20,000,000 numbers, two names agree.**
**THE 64 MiB REGION PER `kosh` IS GONE - 20,000 `kosh` objects, one `mmap`.**
**RUNNING OUT OF MEMORY IS A MESSAGE, NOT A SIGSEGV.**
**Suite 327 (was 315), FAIL=0. Gates 67 PASS / 1 FAIL / 1 NOT-RUN; new `R127 descriptor` gate 15 checks, 0 failed - and v301 fails 7 of its 10 ELF checks, so the gate proves the change. Muse's eight defects are now goldens.**
**It was NOT one emit path: nine sites, one new growth routine, one Windows import.**
**The only gate FAIL left is `installer version` - the payload inside Sutram-Setup.exe is still v243.**

## WS1 - and this is the question: is there anything left?
**The three defects are closed. The tracking is sound. Muse's eight are goldens. Suite 327.**

**Is the memory model finished, or is there a defect class nobody has looked for?**

**You have read this tree more than anyone.** **Name what is NOT covered by any test:**
- **what happens to a descriptor when the region closes with a live alias?**
- **what happens to a `kosh` of `kosh` when the inner one grows?**
- **what does `parimana()` report now that the reservation is gone - does the number change meaning?**
- **and is the 24-byte header itself allocated where an alias can outlive it?**

**That last one is the one I would worry about: the header never moves, but does it die?**

## WS2 - and the reference section, which is now writable
**Memory has no known defect. So write the section a student reads.**

**Six things, plain language:**
- **what a `mandapa` block does**
- **what `parimana()` returns**
- **what `mandapa parimita` refuses**
- **what a `kosh` costs now that the reservation is gone**
- **that a block `kosh` cannot escape**
- **and that integer arithmetic wraps while the library refuses**

**Plus the one sentence the reviewer offered: "all shared maps point to a fixed registration desk."** **Use it or improve it.**

## WS3 - and the two closed answers
**Reuse inside a live block: no. Threads: never.** **You have been asked for weeks.**

**If these are right, write the two paragraphs and I will put them in the reference.** **If either is wrong, say so now - this is the last chance before v1.0.**
