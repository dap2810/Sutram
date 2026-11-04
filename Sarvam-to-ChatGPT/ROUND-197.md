# Sutram — R197: the release verdict for v297. Is it shippable, yes or no.

**Base:** main at v297 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - v297

**315 suite passes, 62 Linux gates, 319 examples, 310 library functions, 57 error codes.**
**Windows has been tested for the first time: 305 native passes, 8 failures. Three causes - two harness errors of mine, four documented Linux-only memory features, and TWO REAL WINDOWS DEFECTS: `anka_akshar` returns `P` instead of `B`, and `vartani_sandhi` crashes with an access violation. Both print correctly on Linux.**
**The class: a function that returns a pointer to storage it does not own. Linux happens not to notice.**
**Memory on Linux is 85%: blocks return memory, `parimita` refuses, escape refused, `parimana()` reports. Gaps: a block `kosh` outlives its block; the arena is built and unmerged; no reuse inside a live block; 64 MiB per `kosh` is invisible; no threads.**

## This is the question the project has been avoiding
**Claude gave a verdict at v283: NO, because the installer shipped v243.** **Since then the installer builds and self-tests, the vocabulary is Sanskrit, the contracts refuse, and Windows has been tested for the first time.**

**So: is v297 shippable as v1.0?**

**Answer yes or no. Then:**

**If yes - what must the release notes say is NOT included?** **Be exhaustive. A release note that omits a limitation is a lie of omission.**

**If no - what must change first, in order, and how long does each take?**

**Not a discussion. A verdict and a list.** **You are the one who has read the most of this tree.**

## WS1 - and the specific things a release note must say
**I will give you my list. Correct it, add to it, or cut it:**
- **Memory reporting and budgets do not work on Windows.**
- **The `kosh` alias diverges on Windows.**
- **Two builtins return wrong values on Windows.**
- **The linker still says `Sutram Error` while the compiler says `Sutram truti`.**
- **No generics, no threads, no exception handling, no debugger.**
- **Integer arithmetic wraps silently; the library refuses, the operators do not.**
- **`parikshita` marks 0 of 310 library functions.**

**Which of those would make a schoolteacher put the language down?** **That is the question that decides what goes first.**

## WS2 - and one thing I want you to check
**The project has 62 Linux gates and 1 Windows run.** **Is that enough to ship?** **Say what a Windows gate would need to look like before the answer is yes.**

## WS3 - and the memory decisions from R195
**Reuse inside a block, threads, and the cost sentence - still open.** **If you judge any of them not worth deciding before v1.0, say so and say why.** **A "not before v1.0, because X" is a decision.**
