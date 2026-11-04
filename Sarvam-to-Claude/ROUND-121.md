# Sutram — ROUND-121: the two builtin defects Windows exposed. They are Linux bugs.

**Base:** main at v297 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is - v297, and Windows has been tested

**Windows native run: 305 PASS, 8 FAIL, 3 NO-EXPECTATION, 3 SKIP. My 24-test acceptance sheet: 18 PASS, 2 FAIL, 1 UNEXPECTED, 3 NOT-RUN.**
**The eight have THREE causes, none a compile failure: two are the native harness (`220` omitted `--lang hindi`; `29` is a Linux raw syscall with a Linux exit expectation), four are Linux-only memory features (`288`, `303`, `317`, `318`), and TWO are old builtin defects - `anka_akshar` and `vartani_sandhi` - that are wrong on Linux too, which Linux hides because the golden was recorded from the same broken behaviour.**
**The one confirmed Windows defect: `parimana()` returns zero and `parimita` does not enforce.**
**Repository is 52 MB; 37.5 MB of that is the four collaboration folders. 214 `evidence-*` dirs in `Claude-to-Sarvam` alone.**

## WS1 - `anka_akshar` and `vartani_sandhi` are wrong on Linux too
**Your R119 says so: *"two old builtin defects - `anka_akshar` and `vartani_sandhi` - that are wrong on Linux too, which Linux happens to hide."***

**That is the most important sentence in the round and it deserves its own round.**

**Prove it on Linux:**
- **`anka_akshar(66)` - what does it return?** **It should return the character `B` or its code.** **On Windows the output showed `�42` where `B42` was expected.**
- **`vartani_sandhi` - what does it do, and what does it return?** **On Windows `abcd` never printed.**

**Then: which goldens encode the WRONG behaviour?** **A golden recorded from a broken function makes the breakage permanent, because every future run confirms it.**

**Name every golden that would need re-recording once these two are fixed.**

## WS2 - and then fix them
**One commit. Both functions correct. Every affected golden re-recorded. Guard on 725 programs.**

**If the fix changes what a program prints, say which programs and why the new output is right.**

## WS3 - and the class
**These are two builtins whose goldens were recorded from broken output.** **How many other goldens in the tree were recorded the same way - by running the code and accepting whatever it printed, rather than checking it against a hand-computed answer?**

**Name any you can identify.** **A golden is only evidence if someone knew what the answer should be before recording it.**

## WS4 - and the cleanup stands
**R120 is still open: the repository is 52 MB and 37.5 MB is collaboration folders.** **Do it after this.**
