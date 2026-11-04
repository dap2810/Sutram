# Sutram — ROUND-128: rebuild the installer payload. It is the last gate failure.

**Base:** main at v302 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is - v302, and the memory model has no known defect

**The descriptor is built. `kosh` is a 24-byte header that never moves; growth moves its elements and every name sees it.**
**THE ALIAS CLIFF IS GONE - 20,000,000 numbers, two names agree.**
**THE 64 MiB REGION PER `kosh` IS GONE - 20,000 `kosh` objects, one `mmap`.**
**RUNNING OUT OF MEMORY IS A MESSAGE, NOT A SIGSEGV.**
**Suite 327 (was 315), FAIL=0. Gates 67 PASS / 1 FAIL / 1 NOT-RUN; new `R127 descriptor` gate 15 checks, 0 failed - and v301 fails 7 of its 10 ELF checks, so the gate proves the change. Muse's eight defects are now goldens.**
**It was NOT one emit path: nine sites, one new growth routine, one Windows import.**
**The only gate FAIL left is `installer version` - the payload inside Sutram-Setup.exe is still v243.**

## WS1 - and this is now the only FAIL in 69 gates
**`installer version`: the payload inside `Sutram-Setup.exe` is still v243.** **It has been the one failing gate for weeks and it is now the only one.**

**Rebuild it so the payload is v302.**

**Then verify what the gate checks: the version string the installed compiler reports.** **And the SHA-256 must match between the root installer and its own record.**

**This is the last thing between this project and an installable release.**

## WS2 - and the release notes
**ChatGPT's R197 said the release notes must state what is NOT included, and it corrected four of my claims:**
- **"no exception handling" is false** - explicit result handling exists; say "no nonlocal try/catch unwinding"
- **"no debugger" is too blunt** - distinguish the absent interactive debugger from the debug diagnostics that exist
- **"integer wrapping and the library refuses"** needs worked examples, not a blanket claim
- **no `pariksha` markers were found** - but that does not erase the native and property tests

**Write the release notes with those corrections applied.** **Every deferred feature named, every limitation stated.**

## WS3 - and one thing to check before either
**The `pack messages` goldens were re-recorded because a `kosh` program now compiles smaller.** **Are there any OTHER goldens that assert a compiled byte size?** **If yes, they will fail the next time anything changes the code size.**

**Name them. A golden that asserts a size is a golden that breaks for the wrong reason.**
