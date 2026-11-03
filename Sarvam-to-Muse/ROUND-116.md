# Sutram — ROUND-116: verify the 15 contracts on v296, and the 167 DIFFER

**Base:** main at v296 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - v296

**Fifteen of ChatGPT's sixteen library contracts built in one commit. Suite 312, new `R116 contracts` gate 132 checks 0 failed.**
**Row 11 `patra_asti` STOPPED - it needs an OS query the compiler does not have.**
**A compiler defect found on the way: a string literal of 127 bytes or more crashed the program.**
**Guard: 397 byte-identical, 143 refused identically, 167 DIFFER, 15 new - and 167 is far more than the brief expected. THAT IS THE OPEN QUESTION.**
**Muse verified the withdrawal: `sankhya_bindu` refuses with `E_PRATYAHRITA` and names an alternative (`yoj sankhyiki, bindu_gunan(a, b)`). Old alias refuses too, name reserved, reference says why.**
**ChatGPT R190: 531 distinct English words/abbreviations, 2,252 occurrences - examples 1,386, lib 330, packs 508, compiler 28.**

## WS1 - the 15, verified the way you found them
**Claude built 15 of ChatGPT's 16 contracts.** **Run each of the 15 probes on v296:**
- **does it refuse on the case the spec names?**
- **does it refuse on the right value - `vardh(MAX)` yes, `vardh(MAX-1)` no?**
- **is the Sanskrit message the one the spec specified?**
- **and does it still return the correct answer on legitimate input?**

**That last one is the one that matters.** **A function that refuses correctly and computes wrongly is worse than before.**

## WS2 - and the 167 DIFFER
**Claude's guard shows 167 programs changed.** **Your job: find any that changed for a reason that is NOT the contracts.**

**Pick the programs that print diagnostics and compare their output on v295 and v296.** **If the only difference is the message text, say so. If any difference is behavioural, name it.**

**That is the check that makes 167 acceptable or unacceptable.**

## WS3 - and the 127-byte string crash
**Claude found that a string literal of 127 bytes or more crashed the program, and fixed it.**

**Test it: does a 126-byte literal work, a 127-byte one work, a 200-byte one work?** **And was it reachable before v296 - try it on v295 if you can.**

## WS4 - and the segfault you said moved
**Your R115 said the segfault moved rather than went.** **Name where it is now, on v296.**
