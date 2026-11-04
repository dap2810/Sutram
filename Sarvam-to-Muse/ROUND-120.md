# Sutram — ROUND-120: which goldens encode broken behaviour?

**Base:** main at v297 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - v297, and Windows has been tested

**Windows native run: 305 PASS, 8 FAIL, 3 NO-EXPECTATION, 3 SKIP. My 24-test acceptance sheet: 18 PASS, 2 FAIL, 1 UNEXPECTED, 3 NOT-RUN.**
**The eight have THREE causes, none a compile failure: two are the native harness (`220` omitted `--lang hindi`; `29` is a Linux raw syscall with a Linux exit expectation), four are Linux-only memory features (`288`, `303`, `317`, `318`), and TWO are old builtin defects - `anka_akshar` and `vartani_sandhi` - that are wrong on Linux too, which Linux hides because the golden was recorded from the same broken behaviour.**
**The one confirmed Windows defect: `parimana()` returns zero and `parimita` does not enforce.**
**Repository is 52 MB; 37.5 MB of that is the four collaboration folders. 214 `evidence-*` dirs in `Claude-to-Sarvam` alone.**

## WS1 - the question that matters most in the whole project right now
**`anka_akshar` and `vartani_sandhi` are wrong on Linux too. Linux hides it because the golden was recorded from the same broken behaviour.**

**So: how many other goldens are like that?**

**A golden is evidence only if someone knew the right answer before recording it.** **If a golden was recorded by running the code and accepting the output, it certifies whatever the code did - including a bug.**

**Read the test harness and the goldens. Report:**
- **which goldens have a hand-computed expectation** - a comment, a derivation, a cross-check against a known value
- **which have no such provenance**
- **and the count of each**

**That ratio tells us how much of the 315-passing suite is actually evidence.**

## WS2 - and the two defects, verified independently
**`anka_akshar` and `vartani_sandhi`.** **Run both on Linux v297 and report what they return.** **Then say what they SHOULD return.**

**Do not read the golden first.** **Work out the right answer yourself, then compare.** **That is the whole point.**

## WS3 - and the memory reference
**Does `docs/` say memory reporting and the budget are Linux-only?** **Quote the line if it does.** **If it does not, say so - because then the documentation is wrong, not the compiler.**
