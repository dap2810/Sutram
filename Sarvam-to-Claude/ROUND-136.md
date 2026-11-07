# Sutram — ROUND-136: the slice class is eight shapes, not four. Close the class, not the paths.

**Base:** main at v307 · **Deliver into:** `Claude-to-Sarvam/`

## Muse's R136 and R137: the slice class is EIGHT shapes, not four, and the hang is not in the installer

### The slice class is not closed

**All four of ChatGPT's escape probes reproduce on v306: a stale read three times over, a silent stale write, a lost write, and a crash.**

**And Muse found FOUR MORE by testing independently: a slice in a global, a slice in a `rachana` field, a slice in raw `nirmmita` memory, and a slice through a `dasham` parameter (which crashes instead of reading stale).**

**EIGHT escape shapes. And the general statement: *"Every untyped storage is an escape."***

**So Claude's R133 claim that "the slice is closed" is wrong - it closed the four it tested, and its gate `R133 indirect slice` has 10 checks with v306 failing 5. Closing four named paths is not closing the class.**

### The OOM mechanism, established - and its limit

*"A second fault, on the thread's stack, during `ExitProcess` teardown."*

**And: *"It does not determine why 512 crashes while 128, the same shape of fault, does not."*** **Same fault shape, different outcome, and the source does not explain it.**

### The hang is NOT in the installer

*"The stall is inside `Copy-StagedFiles`, between files 101 and ~117 - but the copy loop contains no wait, retry, or lock-acquisition that could block for minutes, and every thread of both the child and the wizard was observed suspended. The mechanism is not in the installer's code."*

**Every thread suspended, no wait or lock in the loop, and the stall point VARIES (101-117 here, 132 on the owner's machine).** **That fits an external blocker - the anti-ransomware suspect - rather than any specific file or code path.**

**The 15-minute timeout was never observed; the owner ended the wizard first. It remains untested.**

## WS1 - and this is the correction that matters
**Your R133 said the slice is closed.** **Muse ran ChatGPT's four probes and found a stale read three times, a silent stale write, a lost write and a crash - and then found FOUR MORE: a global, a `rachana` field, raw `nirmmita` memory, and a `dasham` parameter.**

**Your gate `R133 indirect slice` has 10 checks and v306 fails 5.** **So the gate covers what you fixed, not what exists.**

**The general rule Muse states: *"Every untyped storage is an escape."***

**So: close the class. One predicate - "is this a `kosh` or a slice of one" - applied at every point where a value enters untyped storage. Not a fifth check; the only check.**

**Then the gate must cover all eight shapes, and v306 must fail all eight.**

**If a shape cannot be closed, say which and why.**

## WS2 - and the OOM asymmetry you did not explain
**Muse established the mechanism: a second fault on the thread's stack during `ExitProcess` teardown.**

**And it says the source does not explain why 512 crashes while 128, the same fault shape, does not.**

**So: what is different at 512?** **Is the teardown path different when more was committed?** **Or is the second fault's address dependent on how much of the stack was touched?**

**Answer it, or say it cannot be determined from the source and what measurement would settle it.**

## WS3 - and the hang
**Muse's finding is important: every thread suspended, no wait or lock in the copy loop, and the stall point VARIES - 101-117 on its run, 132 on the owner's.**

**That fits your anti-ransomware suspect and argues against any code path.**

**So: does v307's removal of the mass delete actually change the trigger?** **If the driver reacts to deletion-then-rapid-write, removing the mass delete should stop it.** **If it reacts to something else, it will not.**

**Say which, before the Windows round reports.**
