# Sutram — ROUND-129: the last gap, and then stop.

**Base:** main at v303 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is - v303. Every gate passes.

**68 PASS / 0 FAIL / 1 NOT-RUN (Windows execution). Suite 327. The installer carries the compiler.**
**ChatGPT R203 found three descriptor defects by READING - one SIGSEGV, one silent memory overwrite, one wrong `parimana()`. Claude reproduced all three on v302 and fixed them at v303. My own testing of four cases had all passed.**
**The Windows linker was rebuilt too - its embedded runtime predated v300.**
**36 goldens asserted a compiled size (not 12); they now check the message words, not the number.**
**Muse R129 attacked v302's descriptor and found NO crash and NO silent-wrong defect. One gap: a `kosh` parameter grown inside a function is refused rather than propagated - safe, but a limitation.**
**Memory has no known defect. The alias cliff, the 64 MiB ceiling and the OOM segfault are all closed - I verified the first and third myself.**

## WS1 - the one gap Muse found
**A `kosh` parameter grown inside a function is refused rather than propagated.** **It is safe - no crash, no wrong answer - but a student who passes a `kosh` to a function that pushes to it will be surprised.**

**Two questions:**
1. **What does the refusal say?** **If it says the function cannot grow a parameter, that is honest. If it says something opaque, it is not.**
2. **Is propagating the growth possible now that `kosh` is a descriptor?** **The header never moves - so a parameter holding the header address should see the growth, the same way an alias does.**

**If it is possible, build it.** **If it is not, make the message say why.**

## WS2 - and then stop
**Everything else on the release list is done: the installer carries v303, the gates pass, the release notes are written, the memory model survived an attack.**

**So this round: close the gap, run the full suite and gates, and then do not start anything new.**

**Report: the final gate line, the final suite line, and the version string.** **That is the release candidate.**

## WS3 - and one thing for the record
**ChatGPT found three defects by reading that my testing missed.** **That is worth writing down somewhere a future reader will see it - not as an apology, but as a fact about how this project found its bugs: reading and testing catch different things, and neither alone was enough.**
