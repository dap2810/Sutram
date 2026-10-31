# Sutram — ROUND-92: one blocker left, and it is the one with real sites

**Base:** main at v280 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour - run by me on v280, output pasted

**`dasham n = 0.0 / 0.0` -> REFUSED, `E_SHUNYA_BHAJAN`: shunye vibhajanam na sambhavati.** Float division by zero is now a named error, so `inf` and `nan` cannot be produced that way.
**`dasham d = 3.7; vitti i = d` -> `3`.** Silent truncation, STILL OPEN on v280.
**`dasham d = 3.0; vitti i = d` -> `3`.** An exactly integral float converts correctly.
**`yadi` needs parentheses: `yadi (n == 5.0)`, not `yadi n == 5.0`.** I got a syntax error before working that out.
**Compiler v280, 509,768 B, 28,165 lines. 265 examples, 24 library modules. Changelog split at v424.**

## Your R91 closed two of three, and I verified both

**`0.0/0.0` now refuses with `E_SHUNYA_BHAJAN`.** **That is the right answer - a teaching language should refuse the division rather than print a word the student has not met.** **And it makes the NaN comparison hard to reach from a division.**

**The changelog is split, the docs are in four folders, the compiler is v280 and healthy.**

## WS1 - and the one that is still open
**`dasham d = 3.7; vitti i = d` gives `3`.** **ChatGPT's R161 patch is written and NOT merged.**

**Merge it.** **Its policy: accept only finite, exactly integral values representable in signed 64-bit; otherwise `E_DASHAM_VITTI`.** **`3.0` converts because it is `3`. `3.7` refuses. `nan` and `inf` refuse.**

**And test the case the patch was written for: after it lands, does `dasham d = 3.7; vitti i = d` refuse, and does `3.0` still give `3`?**

## WS2 - and the guard on the conversion
**A conversion that now refuses will break any program that relied on truncating.** **Muse found 5 real sites.** **Run the guard, and for every DIFFER say whether the old answer (a truncated integer) or the new one (a refusal) is right.**

**My expectation: the refusal is right in all five, because a silent truncation is never what the programmer meant. But say it from the evidence, not from my expectation.**

## WS3 - and the installer, which is the last gate
**You have a rebuilt v279 review installer from ChatGPT, and the compiler is now v280.** **So the installer is one version behind again.**

**Rebuild it at v280, and report the SHA-256 of the `.exe` you produce.** **That hash is what the maintainer verifies on Windows, and it is the only way he can tell whether he installed the right thing.**

**If you cannot build it, say exactly what blocks it and what the maintainer must run instead.**
