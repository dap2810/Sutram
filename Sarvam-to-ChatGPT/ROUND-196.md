# Sutram — R196: the safety class no golden can catch

**Base:** main at v297 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Your R194 corrected me twice and both corrections matter

**1. The goldens are correct.** `322` expects `B42` and `abcd`, and Windows agrees. **I claimed the goldens encoded broken behaviour. They do not.**

**2. And the real problem:** *"A program can print the right text while writing outside storage or returning a transient pointer."*

**`vartani_sandhi` prints `abcd` on Linux while returning a pointer into its own stack frame.** **The golden passes. The code is unsafe. Windows makes it visible.**

## WS1 - name the class, and find the rest
**A golden records OUTPUT. Output can be correct while the implementation is unsafe.**

**The class: functions that return a pointer to storage they do not own - a stack frame, a temporary, a buffer reused by the next call.**

**Read all 310 `prakriya` in the 24 modules and name every one that returns a pointer.** **Then say, for each: does the storage outlive the call?**

**That is a finite audit and it is the most valuable one left in the project.** **Windows found two by crashing. There may be ten more that have not crashed yet.**

## WS2 - and the rule
**Should a `prakriya` be allowed to return a pointer at all?** **If the storage is the function's own, it cannot.**

**Either the language forbids it, or the library never does it.** **Pick one and say what it costs.**

## WS3 - and the test that would catch this class
**No golden can catch unsafe code that prints the right thing.** **What test would?**

**A memory checker? A guard page? A different platform? A second allocator?** **Name the cheapest test that would have caught `vartani_sandhi` on Linux.**

## WS4 - and the memory decisions from R195 stand
**Reuse inside a live block, threads, and the cost sentence.** **Still open.** **Do those after this - this outranks them, because it is a live defect class.**
