# Sutram — ROUND-129: attack v302's descriptor. Find the tenth defect.

**Base:** main at v302 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - v302, and the memory model has no known defect

**The descriptor is built. `kosh` is a 24-byte header that never moves; growth moves its elements and every name sees it.**
**THE ALIAS CLIFF IS GONE - 20,000,000 numbers, two names agree.**
**THE 64 MiB REGION PER `kosh` IS GONE - 20,000 `kosh` objects, one `mmap`.**
**RUNNING OUT OF MEMORY IS A MESSAGE, NOT A SIGSEGV.**
**Suite 327 (was 315), FAIL=0. Gates 67 PASS / 1 FAIL / 1 NOT-RUN; new `R127 descriptor` gate 15 checks, 0 failed - and v301 fails 7 of its 10 ELF checks, so the gate proves the change. Muse's eight defects are now goldens.**
**It was NOT one emit path: nine sites, one new growth routine, one Windows import.**
**The only gate FAIL left is `installer version` - the payload inside Sutram-Setup.exe is still v243.**

## WS1 - you found eight. Find the ninth.
**Claude built the descriptor and your eight are now goldens.** **So the tracking is closed.**

**But the descriptor is new code, and new code has new defects.** **Attack it:**

- **a `kosh` grown to exactly the capacity boundary - one element either side**
- **two aliases, one grown, the other read - do both see the new buffer?**
- **a `kosh` inside a `kosh`, grown at the inner level - does the outer see it?**
- **a `kosh` passed to a `prakriya` that grows it - does the caller see the growth?**
- **a `kosh` grown inside a `mandapa` block, read after the block closes**
- **20,000 `kosh` objects, then grow one - does it still work?**
- **and the out-of-memory path: exhaust the arena and confirm it is a message, not a crash**

**You have found every defect in this area so far.** **Find the next one, or say there is none and why you believe it.**

## WS2 - and verify the two headline numbers yourself
**"20,000,000 numbers, two names agree" and "20,000 `kosh`, one `mmap`."**

**Both are Claude's measurements.** **Reproduce both.** **If either is wrong, that matters more than if both are right.**

## WS3 - and the cliff number I have asked for twice
**The alias cliff was at ~4,194,304 elements.** **It is now claimed gone at 20,000,000.**

**Push past 4,194,304 with an alias held, and past 20,000,000.** **Report what `a[0]` gives at each.**

**This is the third time I have asked.** **If it is verified, it closes.**
