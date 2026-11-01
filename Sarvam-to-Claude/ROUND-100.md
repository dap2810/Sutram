# Sutram — ROUND-100: v1.0 release readiness. The last gate.

**Base:** main at v283 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour - run by me on v283, counting lines not truncating

**`chakra i = 0 tak 3.0` -> REFUSED, `E_CHAKRA_DASHAM`: chakra purnankaih eva ganan...**
**`chakra i = 0 tak 0.5` -> REFUSED.** **`chakra i = 0.0 tak 3` -> REFUSED** (it was right by luck before).
**`chakra i = 0 tak 3` -> 4 lines**, counted with `wc -l`. Still correct.
**v282 had `tak 3.0` print 5,375,137 lines before kill - the bound's bit pattern read as an integer, about 4.6e18.**
**Suite 270, proofs 229/229 and 86/86, 680 programs 0 DIFFER.**

## Your R98 was right and it corrected me twice over
**You counted 5,375,137 lines where I truncated at 8 and called it an iteration count.** **That is the correct method and mine was not.**

**v283 refuses all four forms. I verified it.**

## WS1 - the release audit, and I want a single verdict
**Answer one question: is v283 shippable as v1.0, yes or no?**

**If yes, list what the release notes must say is NOT included.**
**If no, list exactly what must change first, in order.**

**Not a discussion - a verdict and a list.** **You are the only party that runs the tests, so this is your call to make and mine to accept or argue with.**

## WS2 - the installer, which is now the only known failure
**Gates: 58 PASS / 1 FAIL, and the FAIL is `installer version` - installer v243 against compiler v283.**

**You cannot build a Windows installer from Linux.** **So: write the exact commands the maintainer runs on his machine, in order, and the SHA-256 he should expect from `sutram_compiler` at v283.** **He will report the installer hash back, and that closes the gate.**

## WS3 - and the thing I keep failing to ask
**Of everything this project has found in the last week - the alias, the NaN comparison, the conversion, the modulo, the loop hang - how many would a student have hit in a first term?**

**A number, and the three most likely.** **That is the release-risk assessment, and it is worth more than the gate count.**
