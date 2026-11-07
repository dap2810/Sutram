# Sutram — ROUND-133: the interrupted-install trap, and the hang you did not find.

**Base:** main at v306 · **Deliver into:** `Claude-to-Sarvam/`

## A correction to the record, and two open defects

**I told all three of you: "the hang was not a hang." THAT WAS WRONG, and Claude corrected it.**

**The sequence was: the v303 copy hung at file 132 of 657 and left an empty file. The ownership refusal that was measured later is what that interrupted copy LEFT BEHIND. The refusal was the wreckage, not the cause.**

**So: the hang was real, and it has not been explained. Claude's own words: *"I did not find the hang's cause from the source; I removed every candidate I could name."***

**And Claude found a second thing wrong with its own v306:** **an interrupted install still traps the next run behind a "user file" refusal, and the v306 log would not name the file it stopped on - although R130's hand-back said it would.**

### And ChatGPT's verdict on v306 is NO - a new verdict against the new tree

*"The original R204 direct-call reproductions are addressed, but the same stale-slice path remains reachable through a function value, by source trace. Reproduce and close that path before declaring the slice class closed. The Windows handler-registration failure is a second, distinct failure-path gap."*

**So the slice rule is fixed for a direct call and still reachable one indirection further out.** **And it states its own limits: *"Compiler/build/native/Wine/installer/GUI execution: NOT RUN - read-side role, no toolchain used. The programs below are proposed reproductions, not observed executions."***

**v306 remains the release candidate: `69 PASS / 0 FAIL / 1 NOT-RUN`, suite 327. But it is not accepted.**

## WS1 - the trap, which is the one a student will hit
**An interrupted install still leaves the next run refusing behind a "user file" guard.**

**A student whose install hangs, or whose machine sleeps, or who closes the window, is then locked out of installing at all.** **That is worse than the original hang, because it is permanent until they find and delete a folder they do not know exists.**

**Build the fix:**
- **the installer must recognise a partial install of its own making and offer to complete or replace it**
- **the "user file" guard must not fire on a file the installer itself wrote and did not finish**
- **and the log must name the file it stopped on**

**If a partial install cannot be told apart from a user file, say why - and then the answer is a marker file the installer writes at the start and deletes at the end.**

## WS2 - and the hang itself, which is still unexplained
**You removed every candidate and said so.** **That was honest and it is not a fix.**

**Two things that would find it:**
- **does the copy loop write file by file?** **If so, file 132 of 657 is a specific file - name it.** **If that file is large, empty, or has a name that sorts oddly, that is the clue.**
- **and is there a per-file step that can block - a hash, a reparse check, an antivirus interaction, a `Set-Content` on a locked path?**

**You have the owner's machine state.** **The interrupted copy stopped at a specific file. That is the strongest evidence in the whole report and it has not been used.**

## WS3 - and ChatGPT's function-value slice
**It says the stale-slice path is still reachable through a function value.**

**Reproduce it: a `kosh` slice passed to a `prakriya` value, or returned from one, or stored in a variable that is then called.**

**If it reproduces, close it the same way the direct call was closed.** **If it does not, say so with the probe - a refuted finding is worth as much as a confirmed one.**
