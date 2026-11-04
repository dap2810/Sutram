# Sutram — R204: v303 is the release candidate. Sign off or refuse.

**Base:** main at v303 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - v303. Every gate passes.

**68 PASS / 0 FAIL / 1 NOT-RUN (Windows execution). Suite 327. The installer carries the compiler.**
**ChatGPT R203 found three descriptor defects by READING - one SIGSEGV, one silent memory overwrite, one wrong `parimana()`. Claude reproduced all three on v302 and fixed them at v303. My own testing of four cases had all passed.**
**The Windows linker was rebuilt too - its embedded runtime predated v300.**
**36 goldens asserted a compiled size (not 12); they now check the message words, not the number.**
**Muse R129 attacked v302's descriptor and found NO crash and NO silent-wrong defect. One gap: a `kosh` parameter grown inside a function is refused rather than propagated - safe, but a limitation.**
**Memory has no known defect. The alias cliff, the 64 MiB ceiling and the OOM segfault are all closed - I verified the first and third myself.**

## WS1 - your three defects are fixed. Verify them.
**You found them by reading: a SIGSEGV, a silent memory overwrite, a wrong `parimana()`.** **Claude reproduced all three on v302 and fixed them at v303.**

**Read the fix. Are all three actually closed, or did the fix address the symptom?**

**That is the question only reading can answer - and reading is what found them.**

## WS2 - and the release verdict, which is now yours to give
**Your R197 said NO, with five required items.**

**Status:**
1. **Reconcile string contracts** - done at v298/v299
2. **Resolve eager Windows commit** - done at v300
3. **Attack the integrated candidate on both platforms** - done on Linux; Windows execution is the one NOT-RUN
4. **Build the installer from an accepted commit** - **done, the installer carries v303, `installer version` passes**
5. **Publish the capability reference and release notes** - **written, with your R197 corrections applied**

**So: is v303 shippable as v1.0, conditional on the Windows run?**

**Yes or no. And if yes, the exact wording of what the release notes must say is NOT included.**

## WS3 - and the memory model, finally
**The descriptor is built, attacked twice, and three defects found by reading are fixed.** **The alias cliff is gone. The 64 MiB ceiling is gone. Out of memory is a message.**

**Is the memory model finished?** **If there is a defect class nobody has looked for, name it now - this is the last chance before release.**
