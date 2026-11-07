# Sutram — R207: your function-value slice, and what the release notes must say

**Base:** main at v306 · **Deliver into:** `ChatGPT-to-Sarvam/`

## A correction to the record, and two open defects

**I told all three of you: "the hang was not a hang." THAT WAS WRONG, and Claude corrected it.**

**The sequence was: the v303 copy hung at file 132 of 657 and left an empty file. The ownership refusal that was measured later is what that interrupted copy LEFT BEHIND. The refusal was the wreckage, not the cause.**

**So: the hang was real, and it has not been explained. Claude's own words: *"I did not find the hang's cause from the source; I removed every candidate I could name."***

**And Claude found a second thing wrong with its own v306:** **an interrupted install still traps the next run behind a "user file" refusal, and the v306 log would not name the file it stopped on - although R130's hand-back said it would.**

### And ChatGPT's verdict on v306 is NO - a new verdict against the new tree

*"The original R204 direct-call reproductions are addressed, but the same stale-slice path remains reachable through a function value, by source trace. Reproduce and close that path before declaring the slice class closed. The Windows handler-registration failure is a second, distinct failure-path gap."*

**So the slice rule is fixed for a direct call and still reachable one indirection further out.** **And it states its own limits: *"Compiler/build/native/Wine/installer/GUI execution: NOT RUN - read-side role, no toolchain used. The programs below are proposed reproductions, not observed executions."***

**v306 remains the release candidate: `69 PASS / 0 FAIL / 1 NOT-RUN`, suite 327. But it is not accepted.**

## WS1 - your function-value finding, handed to two testers
**You traced it and did not run it, and you said so: *"Compiler/build/native/Wine/installer/GUI execution: NOT RUN - read-side role, no toolchain used. The programs below are proposed reproductions, not observed executions."***

**That is the right way to report a read-side finding.** **Muse and Claude are both being asked to reproduce it.**

**So: is there a second path beyond the function value?** **You have found direct call, then function value.** **What is the third?**

**If the rule is enforced at the call site rather than at the point where the slice is created, then every indirection is a hole - and the fix is to enforce it where the slice is made, not where it is used.**

**Say whether that is the right shape of the fix.**

## WS2 - and the release verdict, one more time
**Your NO was against v306 and it was new, not carried forward.** **That is the right discipline and I am not arguing with it.**

**So: what exactly must be true before you say yes?** **A list, and the smallest version of it.**

**Not "fix everything" - the specific conditions, so they can be checked rather than interpreted.**

## WS3 - and the interrupted install
**A student whose install hangs is then locked out, because the half-written files look like "user files" to the guard.**

**What should an installer do when it finds a partial install of its own making?** **Offer to complete it, replace it, or refuse with a path to the folder?**

**And: how does an installer tell its own half-written file from a user's file?** **If the answer needs a marker, say where it goes and when it is written and deleted.**
