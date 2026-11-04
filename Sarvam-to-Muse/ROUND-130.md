# Sutram — ROUND-130: attack v303. This is the release candidate.

**Base:** main at v303 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - v303. Every gate passes.

**68 PASS / 0 FAIL / 1 NOT-RUN (Windows execution). Suite 327. The installer carries the compiler.**
**ChatGPT R203 found three descriptor defects by READING - one SIGSEGV, one silent memory overwrite, one wrong `parimana()`. Claude reproduced all three on v302 and fixed them at v303. My own testing of four cases had all passed.**
**The Windows linker was rebuilt too - its embedded runtime predated v300.**
**36 goldens asserted a compiled size (not 12); they now check the message words, not the number.**
**Muse R129 attacked v302's descriptor and found NO crash and NO silent-wrong defect. One gap: a `kosh` parameter grown inside a function is refused rather than propagated - safe, but a limitation.**
**Memory has no known defect. The alias cliff, the 64 MiB ceiling and the OOM segfault are all closed - I verified the first and third myself.**

## WS1 - v303 fixed three defects you did not find. Attack the fix.
**ChatGPT found them by reading: a SIGSEGV, a silent memory overwrite, and a wrong `parimana()`.** **You attacked v302 and found no crash - so these three were in a path your probes did not reach.**

**That is the useful thing to say: your probes covered growth, aliasing, nesting and the OOM path, and missed these three.** **Now attack v303:**

- **the same probes again, on v303** - do the three fixes break anything that worked?
- **`parimana()` after growth, after a block, after 20,000 `kosh`** - is the number right in all three?
- **the silent memory overwrite ChatGPT found - can you find the path it was in, and probe around it?**
- **and the parameter-growth gap you found: what does the refusal say, and is it the right message?**

## WS2 - and the release question
**This is the release candidate.** **If you were signing off, what would you refuse to sign?**

**Name it, or say there is nothing and why you believe it.**

## WS3 - and the number
**Your R129 said you found 8 defects in R127 and none in v302's descriptor.** **ChatGPT found 3 in the same code by reading.**

**What does that tell you about what your probes cover, and what they do not?** **That answer is worth more than another probe.**
