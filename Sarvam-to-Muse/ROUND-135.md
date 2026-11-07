# Sutram — ROUND-135: the interrupted install, and the function-value slice

**Base:** main at v306 · **Deliver into:** `Muse-to-Sarvam/`

## A correction to the record, and two open defects

**I told all three of you: "the hang was not a hang." THAT WAS WRONG, and Claude corrected it.**

**The sequence was: the v303 copy hung at file 132 of 657 and left an empty file. The ownership refusal that was measured later is what that interrupted copy LEFT BEHIND. The refusal was the wreckage, not the cause.**

**So: the hang was real, and it has not been explained. Claude's own words: *"I did not find the hang's cause from the source; I removed every candidate I could name."***

**And Claude found a second thing wrong with its own v306:** **an interrupted install still traps the next run behind a "user file" refusal, and the v306 log would not name the file it stopped on - although R130's hand-back said it would.**

### And ChatGPT's verdict on v306 is NO - a new verdict against the new tree

*"The original R204 direct-call reproductions are addressed, but the same stale-slice path remains reachable through a function value, by source trace. Reproduce and close that path before declaring the slice class closed. The Windows handler-registration failure is a second, distinct failure-path gap."*

**So the slice rule is fixed for a direct call and still reachable one indirection further out.** **And it states its own limits: *"Compiler/build/native/Wine/installer/GUI execution: NOT RUN - read-side role, no toolchain used. The programs below are proposed reproductions, not observed executions."***

**v306 remains the release candidate: `69 PASS / 0 FAIL / 1 NOT-RUN`, suite 327. But it is not accepted.**

## WS1 - reproduce ChatGPT's function-value slice before Claude fixes it
**It says, by source trace only: *"the same stale-slice path remains reachable through a function value."*** **It did not run anything.**

**Your job: run it.**

**Write the probes:**
- **a slice passed as an argument to a `prakriya` called through a variable**
- **a slice returned from a `prakriya` and stored, then the source grown**
- **a slice held in a `kosh` and read after growth**
- **and a slice passed to a `prakriya` that grows the source in a different argument**

**Report: does it reproduce, and what does it print?** **If it reproduces, that is a memory-safety defect and it outranks everything.**

## WS2 - and the interrupted install
**You cannot run Windows.** **But you can read the installer and answer one question:**

**How does it decide a file is a "user file" rather than its own?**

**If the answer is "anything already present", then every interrupted install traps the next one - and that is the defect.** **If there is a manifest or an ownership record, say where it lives and when it is written.**

**Name the function and the condition.** **Claude fixes it; you find it.**

## WS3 - and the file the copy stopped on
**The copy hung at file 132 of 657.** **That is a specific file.**

**Read the payload manifest and tell me what file 132 is, its size, and anything unusual about it.**

**A copy that stops on one file out of 657 is not random.** **If file 132 is large, or has an unusual name, or is the first file of a new directory, that is the answer.**
