# R135-00 — v308. WS1: the handler does not recurse or allocate. The stack overflow comes after the message: the commit limit that refused the page also leaves the thread's stack no room to grow while the process exits. Whether that happens depends on how much commit the failed request left over, which is why 512 MiB fails and 640 passes. v308 keeps 64 KiB of commit from the start and gives it back before the message. WS2: in the reproduced stall, Windows reported every thread of the engine and the wizard's original threads suspended - something outside Sutram stopped them. WS3: the journal is built (R134-00). WS4: the 15-minute stop now writes to the log - and it cannot fire if the wizard thread that waits is itself suspended.

## Release line

Same candidate as R134-00:

```
gates: 73 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v308) - sampurna sutra
```

- **Commit:** the one carrying this file (SHA in my chat report).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **The guard (v307 → v308):**
  - ELF: 584 identical, 162 refused identically, 1 DIFFER (`safe1`, now refused, R134), 8 new;
  - PE: 585 DIFFER (the runtime);
  - **Run old and new under Wine: 584 the same output and exit, 0 changed; `safe1` is refused by v308 and has no new binary.**
  - The Windows compiler under Wine = the Linux PE output for all 755.
- **Installer** `e737086849052a7a42076734b28a183b0ba329f9727ab9a5a9da09e89a7b9686`.

**Not done:**
- **The stack-overflow fix is NOT verified natively.** Wine cannot impose a commit limit, so the two failing cases (B3 at 512 MiB, `mandapa` at 64 MiB) are the owner's test.
- **Under Wine I could check only** that the out-of-memory path, with its new release step, still prints the message and exits 1. A test runtime forces every lazy commit to fail.
- **Nothing ran on native Windows here.**

## WS1 - `0xC00000FD` after the message

**Your question 1 - does the handler allocate, recurse, or call something that can fault? No.**
- `.v_nomem` writes a static message with `GetStdHandle` and `WriteFile`, restores the code page with `SetConsoleOutputCP`, and calls `ExitProcess`.
- It does not allocate, does not call Sutram's runtime, and does not retry the fault.
- It does not handle `0xC00000FD` either: `rt_veh` acts only on `0xC0000005` on a reserved page, so a stack overflow goes straight to Windows.
- **The handler itself is not the bug.** And the message was written every time, so the failure comes after `WriteFile`.

**Your question 2 - why 640 passes and 512 fails. You were right that the asymmetry is the clue.**
- **A thread's stack is itself committed page by page as it grows.** Each new stack page is charged to the same commit limit.
- **The failing request is the handler's 64 KiB commit.** When it is refused, the job has 0 to 60 KiB of commit left. How much depends on exactly where the program's allocations put it against the limit: the regions double, then they are committed 64 KiB at a time as touched.
- **Then the exit runs on that stack, deeper than the program ever went.** The exception dispatch (the context record alone is about 1.2 KB), the handler, `WriteFile` into the console, and `ExitProcess`, which runs every DLL's detach routine.
- **If that needs a stack page that is not yet committed, and the job has less than a page left,** the guard page cannot move. Windows raises `STATUS_STACK_OVERFLOW`, nothing handles it, and the process ends with `0xC00000FD`.
- **The remainder is fixed for a given program and limit.** So 512 MiB fails 6 of 6, 640 MiB passes 6 of 6, and 64/128/256 MiB happened to leave enough.
- **`mandapa` at 64 MiB** is the same: a different allocation pattern, a different remainder.
- **If it were recursion, every limit would fail. It is not recursion; it is the stack's own commit.**

**This is the explanation that fits all six measurements. It is not observed directly:** no native debugger trace was taken. It predicts that the fix below turns both failing rows into exit 1.

**The fix (`win/winrt_blob.asm`, `win/pe_layout.inc`).**
- `rt_init`, after the handler is registered, commits 64 KiB (`VirtualAlloc(MEM_COMMIT | MEM_RESERVE)`) and keeps its address in a new runtime slot, `RT_OOM_RESERVE` (byte 496 of the runtime data).
- The import block ends at 495, and `pe_imports.inc` now refuses to assemble if it grows into the slot.
- **`.v_nomem` first releases that block** (`VirtualFree(MEM_RELEASE)`), so 64 KiB of commit is back in the job before the message and exit need the stack.
- **The handler still allocates nothing on that path; it only gives memory back.**
- If the reserve could not be had at start, the slot is 0 and the exit goes on as before.
- **The cost is 64 KiB of commit per program.** The lazy-commit gate measures against a base program, so it does not move.

**Why not the other remedies:**
- **Pre-touching the stack at start** covers only the depth touched. A program deep in recursion would fault below it.
- **`TerminateProcess` instead of `ExitProcess`** needs new imports, and still needs stack for `WriteFile`.
- **The reserve works at any depth.**

**Tested here, under Wine.** Gate `R133 handler registration` now has a fourth case: a test runtime built with `-DR135_FAIL_COMMIT`, where every lazy commit fails. It must print nothing to stdout, `Sutram truti: smritih na labdha` to stderr, and exit 1. **It passes.** That proves the release step does not break the path. **It does not prove the stack fix:** Wine never runs out of commit.

**Your acceptance standard holds:** the message alone does not count. The owner's test is B3 at 512 MiB and `mandapa` at 64 MiB, each 6 times. Each run must exit 1 with the message, never `0xC00000FD`. The 64/128/256/640 MiB rows and the 768+ MiB successes must stay as they are.

## WS2 - the same-folder upgrade stall, reproduced on v306

**What the native run shows** (`Windows-to-Sarvam/win-v306-2026-11-06/`, ChatGPT's observer):
- the engine deleted the previous payload's files (21:32:41-45: 4 s);
- it began copying, logged `Copied 100 of 658`, and wrote about 17 more;
- **then, at 21:37-21:38, Windows reported every thread of the PowerShell engine (27 of 27) and five of the wizard's eight threads as `Wait: Suspended`.** The tester calls those five the wizard's original threads; the other three were waiting on an event pair.
- The engine's CPU time was flat at 11.86 s between observations.
- A file it had been writing, `docs\reports\EDGE-COVERAGE-30.md`, was **"being used by another process"** when the observer tried to read it.
- **Windows Defender logged nothing** for that time.
- The clean install into an empty folder, minutes later, finished in 8 s.

**Your question - copying over files in use? No, not by Sutram.**
- v306 deletes the old files and then creates new ones; it does not write into an existing file.
- The file that was in use was one the engine had just created, held open by another process.
- **Nothing in Sutram suspends a thread:** no `SuspendThread`, no debugger, nothing in the engine or the wizard. A suspension of both processes' threads, from outside, is something the system or a security product does.

**What fits, and is still not confirmed:**
- **Behaviour-based anti-ransomware.** One process deleting hundreds of files and then writing hundreds is the pattern such tools watch for. They can suspend the process tree and hold the file being written while they decide.
- The owner's PATH has Acronis's file-protection filter (`Acronis\FileProtector`).
- **Both stalls came right after the mass delete;** the clean install, with no delete, did not stall.
- **Defender's empty log rules Defender out, not the others.**
- **The owner can settle it:** Acronis's Active Protection log (or the console's activity list) for **6 November, 21:32-21:47** and **18:35**.

**What changes it either way:**
- **v307 stopped deleting first.**
- **v308 does not write into the installation while copying at all:** files are staged beside it and renamed in, and the old ones are moved to a backup, not deleted. A mass-delete detector has no mass delete to see.
- **If something still suspends the engine:** the per-file `START`/`DONE` log names the file, and the journal lets the next run finish.

## WS3 - the journal

Built: R134-00, WS2. A private folder beside the target on the same volume; the journal is durable before anything is deleted, truncated or replaced; a rerun completes an interrupted install, and a file the installer did not write is kept and listed.

## WS4 - the 15-minute stop: unchanged, now logged; and why the run could not show it

- **Unchanged:** `ENGINE_WAIT_MS` is still 900,000.
- **When it fires, the wizard appends to the engine's log:** `[setup] The installation engine was still running after 15 minutes (ENGINE_WAIT_MS); setup stopped it and reports a failure.`
- **Why the v306 run could not show it:** the wizard's original threads were suspended too - presumably including the one in `WaitForSingleObject`; which thread is which was not recorded. A suspended thread cannot wake to stop anything.
- **So the bounded wait protects against an engine that hangs, not against a wizard that something outside has frozen.** No code inside a suspended process can. **The release notes say so.**
- **The way to watch it fire:** a stall where only the engine is stuck. The e2e test's interrupted install is a kill, not a stall, so it does not exercise this. **NOT RUN.**

Evidence: `Claude-to-Sarvam/evidence-r134-r135/`.
