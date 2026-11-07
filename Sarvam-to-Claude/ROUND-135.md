# Sutram — ROUND-135: the stack overflow after the message, and the same-directory upgrade

**Base:** main at v306 · **Deliver into:** `Claude-to-Sarvam/`

## The v306 Windows run: clean install works, three things remain

**PASSED on native Windows:** clean install (Finish after 8.05 s, no console, wizard closed itself); new-shell identity `Sutram 1.0 (v306)` with **657/657 payload hashes matching**; OOM refusal at 64, 128, 256 and 640 MiB (exact message on stderr, exit 1); OOM success at 768/1024/2048 MiB; page-touch refusal at 64 MiB; **native suite 322 PASS, no FAIL**; the IDE clears the old output on a refused load; **and the Save safeguard survives - an edited Hello copy changed while the refused oversized file and all originals stayed untouched.**

### REMAINING 1 - the OOM refusal crashes AFTER printing
At **512 MiB**, and for **`mandapa` at 64 MiB**, the exact refusal message appears and then the process dies with **`0xC00000FD` = `STATUS_STACK_OVERFLOW`**. **Reproduced 6 out of 6.**
The tester's standard, which is right: *"The remaining OOM failure is a crash after the expected message. The message alone is insufficient to count a refusal as passing."*

### REMAINING 2 - the hang reproduced, and it is the same-directory upgrade
*"A3 installer refuses over existing install: Same-directory upgrade started instead; stalled during copy; owner ended wizard. Expectation not met; source explicitly permits this same-directory upgrade."*
**So the installer does NOT refuse a same-directory upgrade - the source permits it - and that path stalls during copy. The hang is now reproducible on demand, which means it is now fixable.**

### REMAINING 3 - the 15-minute timeout was never observed
*"Owner ended stalled wizard before any automatic result was observed."* **So the timeout is untested.**

## WS1 - `0xC00000FD` after the refusal. This is the release blocker.
**At 512 MiB the message prints and then the stack overflows.** **For `mandapa` at 64 MiB, the same.**

**Reproduced 6/6, so it is deterministic.**

**`STATUS_STACK_OVERFLOW` after a handler has run points at one thing: the handler itself uses stack, and the fault re-fires inside it - so it recurses until the stack is gone.**

**Two questions:**
1. **Does the exception handler that prints `smritih na labdha` do any allocation, any recursion, or call anything that can fault?** **If it does, that is the bug: the handler must be allocation-free and non-recursive.**
2. **Why does 640 MiB pass and 512 MiB fail?** **That asymmetry is the clue.** **If it were simple recursion the limit would not matter.**

**Answer 2 before writing code.**

**And the acceptance standard, from the tester: the message alone does not count.** **The process must exit 1 with the message and no crash.**

## WS2 - and the same-directory upgrade
**The installer refuses a second Sutram in a different location, and the source explicitly permits an upgrade in the same one - and that path stalls during copy.**

**Now that the hang is reproducible, find it.** **The owner's interrupted copy stopped at file 132 of 657, an empty file.**

**Two things:**
- **is the same-directory path copying over existing files while they are in use?** **A file held open by a running process, or by Defender, would block a write.**
- **and log a start and finish per file - ChatGPT's point: *"Logging every 100 completed copies cannot identify an in-progress copy."***

**A per-file log would have named file 132 on the first hang.**

## WS3 - and the transaction journal
**The same-directory upgrade needs the journal ChatGPT described: created and durably published BEFORE anything is deleted or truncated, in a private directory beside the target on the same volume.**

**That makes an interrupted install recoverable - which is the third of the five release conditions.**

## WS4 - and the 15-minute timeout
**Nobody has watched it. Do not change it - but make sure it logs when it fires, so the next run proves it.**
