# Sutram — ROUND-72: the census is done; now audit the reference against what the language actually does

**Base:** main at v267 · **Deliver into:** `Muse-to-Sarvam/`

**Your R71 census is the best answer this question has had: 2,189 control sites, 2,181 braced and unaffected, 5 indented multi-statement bodies and all five in the test file.** **So the bug was real for 264 versions and affected no shipped code.** **And no golden locks it in.**

## WS1 — the reference against the language
**`docs/LANGUAGE-REFERENCE.md` was written by hand over many rounds.** **Now that four parser defects have been found in one session, the reference deserves the same treatment the library got.**

**Audit it: for every construct the reference shows, does the language actually do what the reference says?**
- **every syntax example in the reference — compile it and run it**
- **`tak` inclusive — is it stated, or did I only find out by measuring?**
- **the block forms — braces, indentation, same-line — is each stated?**
- **and every claim about memory, which is now the area with the most recent change**

**Give me the count: how many examples in the reference, how many compile, how many run, how many do what the prose says.**

## WS2 — and the one I most want
**I assumed `tak 3` meant three iterations and it means four.** **That cost me a wrong test and a wrong conclusion.**
**So: what else in this language would a competent C or Python programmer assume wrongly?** **List them.** **That is the list that belongs at the top of the reference, and nobody has written it.**

## WS3 — and the examples
**231 examples, and the suite covers 230 tests.** **Which examples have no test?** **If an example can rot without a test noticing, name it.**
