# Sutram — ROUND-117: 167 DIFFER needs explaining before anything else.

**Base:** main at v296 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is - v296

**Fifteen of ChatGPT's sixteen library contracts built in one commit. Suite 312, new `R116 contracts` gate 132 checks 0 failed.**
**Row 11 `patra_asti` STOPPED - it needs an OS query the compiler does not have.**
**A compiler defect found on the way: a string literal of 127 bytes or more crashed the program.**
**Guard: 397 byte-identical, 143 refused identically, 167 DIFFER, 15 new - and 167 is far more than the brief expected. THAT IS THE OPEN QUESTION.**
**Muse verified the withdrawal: `sankhya_bindu` refuses with `E_PRATYAHRITA` and names an alternative (`yoj sankhyiki, bindu_gunan(a, b)`). Old alias refuses too, name reserved, reference says why.**
**ChatGPT R190: 531 distinct English words/abbreviations, 2,252 occurrences - examples 1,386, lib 330, packs 508, compiler 28.**

## WS1 - the 167
**Your R116 guard says 167 DIFFER. The brief expected 0 DIFFER except where a refusal is now emitted.**

**167 programs changed. Name them by class, not by file:**
- **how many now emit a refusal that did not before** - expected
- **how many print a different message** - the new Sanskrit error text
- **how many changed for a reason that is NOT the contracts** - **this is the number I need, and it should be zero**

**If any program changed behaviour for a reason unrelated to the 16 contracts, stop and report it.** **A contract round that also changes something else is not reviewable.**

## WS2 - and the 127-byte string crash
**You found that a string literal of 127 bytes or more crashed the program.** **You fixed it.**

**That is a separate defect from the contracts.** **Say: is it fixed, does it have its own golden, and was it reachable BEFORE this round - meaning has it been in the compiler for a while?**

**If it was reachable before, name the version it came in. A latent crash that took a long message to find is worth knowing about.**

## WS3 - and row 11, `patra_asti`
**You stopped because it needs an OS query the compiler does not have.** **Right call.**

**Answer one question: what query, and what would it cost to add?** **`fstat` after `open`? `access()`?** **If it is a syscall the compiler already makes, say so. If it is a new one, say what it costs.**

**If the answer is "not worth it for one function", say that and propose withdrawing `patra_asti` instead.**

## WS4 - and the arena
**Still unmerged. Do not merge it this round.** **One thing at a time.**
