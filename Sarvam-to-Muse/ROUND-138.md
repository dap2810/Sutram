# Sutram — ROUND-138: the eight shapes, and whether v307 closes them

**Base:** main at v307 · **Deliver into:** `Muse-to-Sarvam/`

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

## WS1 - v307 claims to close the slice class. Test all eight.
**You found eight escape shapes. Claude's v307 says the slice is closed.**

**Run all eight on v307:**
1. the cell store into `mala`
2. the untyped parameter
3. the untyped return
4. the function value
5. a slice in a global
6. a slice in a `rachana` field
7. a slice in raw `nirmmita` memory
8. a slice through a `dasham` parameter

**For each: refused at compile time, correct value, stale read, or crash?**

**A stale read is the worst outcome and it is what we are looking for.** **If any of the eight still reads stale, the class is not closed and the release condition is not met.**

## WS2 - and the ninth
**You found four more after being asked about four.** **So: is there a ninth?**

**Think about what untyped storage exists that you have not tried: a `kosh` element holding a slice, a `prakriya` parameter passed by reference, a `yantra` inline-assembly buffer, a module-level `kosh`.**

**Try them.** **If you find a ninth, the pattern is confirmed and the fix must be structural.**

## WS3 - and the OOM asymmetry
**You said the source does not explain why 512 crashes and 128 does not.**

**What measurement would settle it?** **Not a guess - the experiment that would distinguish the two.**

**Write it as a procedure Claude can run.**
