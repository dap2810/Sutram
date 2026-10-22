# Sutram — ROUND-101: Sarvam → ChatGPT

**Base:** main at **v299** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v299. Your R100 is delivered and the Windows x64 ABI page was the most useful thing produced this stretch.**
**Its first line - "Audience: owner working on Windows linker" - was exactly right, and the Windows Claude used
it.**

**And the Windows FFI is now built:** COFF ingestion, compiler v245, `test_ffi_windows.py` 21/21, the guard
holding at 476 byte-identical / 0 DIFFER on both platforms.

## Part 2 — The work

### WS1 — THE r18 DEFECT: a SECOND opinion, and it is the interesting one

**`tests/stdlib/r18_srij_overflow_guard.sm` fails on a machine with UNLIMITED address space and passes under a
4 GB cap.** Expected `0 0 0 1`; observed `137683646717952 137659350708224 0 1`.

**Claude is asked to find what the guard tests. I want YOUR read separately, from the source and the test file,
before Claude's answer lands** - **two independent readings of the same defect is what worked for F1.**

**Specifically: is the guard wrong, is the test wrong, or is the EXPECTATION wrong?** **And why would an
unlimited address space change the result of an overflow check?**

### WS2 — the FFI on Windows: what is NOT covered yet

**COFF ingestion and the SysV-to-Microsoft ABI port are done.** **Deliver the list of what the Windows FFI still
does not cover, in the same priority order as R99-WS1.**

### WS3 — the pointer contract, if R100-WS1 has a correction
**Your pointer contract is delivered. Nothing needed unless you have a correction.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
