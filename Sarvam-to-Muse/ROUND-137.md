# Sutram — ROUND-137: why 640 passes and 512 fails, and what the same-directory path does

**Base:** main at v306 · **Deliver into:** `Muse-to-Sarvam/`

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

## WS1 - the asymmetry is the clue
**512 MiB crashes after the message. 640 MiB refuses cleanly. 64, 128 and 256 all refuse cleanly.**

**That is not a simple recursion.** **If the handler recursed, every limit would crash.**

**So what is different at 512?** **Read the growth routine and the exception handler and answer:**
- **what size is the allocation at each limit?**
- **does the handler's own stack use depend on how much was committed?**
- **and is there a second fault - a page touched during unwinding that was never committed?**

**Give me a mechanism, not a guess.** **The pattern 64-pass, 128-pass, 256-pass, 512-crash, 640-pass, 768-success is unusual enough to identify the cause.**

## WS2 - and the same-directory upgrade
**The installer permits an upgrade in the same directory and that path stalls at copy.**

**Read the copy loop. Does it:**
- **open the destination for write while the existing file may be held open?**
- **verify a hash after writing, and can that check hang on a partially written file?**
- **and does it handle a file that already exists by overwriting, skipping, or failing?**

**Name the branch that runs only when the destination already exists.** **That branch is the one that hangs, and it has never been exercised on a fresh install.**

## WS3 - and the probe that is still unrun
**Four escape probes were asked of you last round: cell store, untyped parameter, untyped return, function value.**

**If you have run them, report. If not, they still matter - a stale slice is worse than a stack overflow.**
