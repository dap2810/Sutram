# Sutram — ROUND-139: v308 claims the class is closed. Test all eight, then find the ninth.

**Base:** main at v308 · **Deliver into:** `Muse-to-Sarvam/`

## v308 is out: three fixes, all three unverified on Windows

**`gates: 73 PASS / 0 FAIL / 1 NOT-RUN` · `suite: PASS=327 (331 run)` · `Sutram 1.0 (v308)` · installer `e737086849052a7a42076734b28a183b0ba329f9727ab9a5a9da09e89a7b9686`, `--self-test` exit 0 under Wine.**

**1. THE STACK OVERFLOW, EXPLAINED.** *"The stack overflow comes after the message: the commit limit that refused the page also leaves the thread's stack no room to grow while the process exits. Whether that happens depends on how much commit the failed request left over, which is why 512 MiB fails and 640 passes."* **v308 keeps 64 KiB of commit from the start and gives it back before writing the message.**

**2. THE SLICE CLASS, CLOSED BY STRUCTURE.** Five doors reproduced on v307 - a cell store, an untyped call, a global, a builtin's argument, and a slice forwarded through a `vibhag` parameter - all compiled and a write through the kept slice was lost. **Now every door calls `r134_holds_kosh`, and only it calls `r126_is_kosh_value`. Gate `R134 one predicate` fails if a new door asks the old question.**

**3. THE INSTALL IS A JOURNALED TRANSACTION** in a folder beside the target, in the order ChatGPT R207 WS3 gives, with each file logged when its copy starts and when it is done.

**And the hang is named: a commit says `identify Acronis upgrade suspension`. Acronis suspended the installer's threads - something outside Sutram.** **Claude's own limitation: *"the 15-minute stop now writes to the log - and it cannot fire if the wizard thread that waits is itself suspended."***

**NOT VERIFIED NATIVELY: *"Wine cannot impose a commit limit."***

## WS1 - eight shapes on v308
**You found eight escape shapes. v308 says every door now asks one predicate.**

**Run all eight:**
1. cell store into `mala`
2. untyped parameter
3. untyped return
4. function value
5. a global `vitti`
6. a `rachana` field
7. raw `nirmmita` memory
8. a `dasham` parameter

**For each: compile refusal, correct value, stale read, or crash?**

**If any still reads stale or loses a write, the class is not closed.**

## WS2 - and the ninth, which you were asked for and have not reported
**You found four more after being asked about four.** **Is there a ninth?**

**Try: a `kosh` element holding a slice; a parameter passed by reference; a `yantra` inline-assembly buffer; a module-level `kosh` holding a slice; a slice returned from a builtin that takes one.**

**If you find a ninth, the fix is not structural enough and that is the most important thing you can report.**

## WS3 - and the gate itself
**`R134 one predicate` fails if a new door asks the old question.** **Read it.**

**Can a door be added that does not go through the gate?** **Name the place a future contributor would add a store and forget.**

**A gate that can be bypassed is not a gate.**
