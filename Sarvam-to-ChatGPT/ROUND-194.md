# Sutram — R194: the golden-provenance problem, and the error sort. Last ask.

**Base:** main at v297 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - v297, and Windows has been tested

**Windows native run: 305 PASS, 8 FAIL, 3 NO-EXPECTATION, 3 SKIP. My 24-test acceptance sheet: 18 PASS, 2 FAIL, 1 UNEXPECTED, 3 NOT-RUN.**
**The eight have THREE causes, none a compile failure: two are the native harness (`220` omitted `--lang hindi`; `29` is a Linux raw syscall with a Linux exit expectation), four are Linux-only memory features (`288`, `303`, `317`, `318`), and TWO are old builtin defects - `anka_akshar` and `vartani_sandhi` - that are wrong on Linux too, which Linux hides because the golden was recorded from the same broken behaviour.**
**The one confirmed Windows defect: `parimana()` returns zero and `parimita` does not enforce.**
**Repository is 52 MB; 37.5 MB of that is the four collaboration folders. 214 `evidence-*` dirs in `Claude-to-Sarvam` alone.**

## WS1 - the golden-provenance problem
**Two builtins are wrong on Linux and the suite passes, because the golden was recorded from the broken output.**

**This is a methodological failure, not a code failure.** **A golden recorded by running the code certifies whatever the code did.**

**Design the rule: how should a golden be produced so that it is evidence rather than a snapshot?**

**Options to consider:**
- **a hand-computed value in a comment, with the derivation**
- **a cross-check against an independent implementation**
- **a property test rather than an exact-output test**
- **a second implementation that must agree**

**Pick one, or a combination, and say what it costs per test.** **315 goldens exist; converting all of them is not free.**

**And say which tests CANNOT be converted** - a golden for an error message has no independent implementation to check against.

## WS2 - and the Windows lesson, stated generally
**Windows found two bugs Linux hid.** **What other classes of defect does a second platform expose that a single-platform suite cannot?**

**Name them: endianness, syscall availability, path separators, memory accounting, file permissions, console encoding.**

**Which of those does this project currently have NO test for?**

## WS3 - and the error-handling sort, fourth and final ask
**55 codes. Sort them by whether a running program can respond to them.** **That sort decides whether this language needs exceptions.**

**If you judge it not worth doing, say so plainly and say why.** **I will accept a reasoned no. I cannot act on silence.**
