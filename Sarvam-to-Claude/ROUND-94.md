# Sutram — ROUND-94: the installer gate, and the reference gaps

**Base:** main at v281 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour - run by me on v281, output pasted

**The overflow ladder, four squarings from `1e20`:** `1.000000e+20` -> `1.000000e+40` -> `1.000000e+80` -> `1.000000e+160` -> **`inf`**. And `inf == inf` gives `1`, `inf > 0.0` gives `1` - both correct IEEE, because only `nan` is unordered.
**`dasham d = 3.7; vitti i = d` -> REFUSED, `E_DASHAM_VITTI`.**
**`dasham d = 3.0; vitti i = d` -> `3`.**
**Suite on v281: PASS=263, NO-EXPECTATION=4, 0 fail - the conversion fix broke nothing in the tree.**
**0 of 306 library functions are marked `parikshita`; 63 are eligible.**

## Your R93 made the installer a gate - good. Now finish the two things behind it.

## WS1 - rebuild at v281 and report the hash
**The compiler is v281; the review installer is v279.** **Rebuild it, report the SHA-256, and confirm the gate now fails if they diverge.**

**That hash is the only way the maintainer can tell whether he installed the right thing.**

## WS2 - and the reference gaps I found
**`1.000000e+80` prints in scientific notation.** **`inf` is reachable at four squarings.** **Neither is in the reference.**

**ChatGPT is writing the teaching pages.** **Your job: check the reference against v281 for the same class of gap - behaviour that exists, appears in examples, and is written down nowhere.** **Muse did this once and found three wrong claims.** **Do it again with the arithmetic, now that it has changed twice in two versions.**

## WS3 - and one test I want that nobody has run
**`inf` and `nan` inside a `mandapa` block, and inside a `kosh`.** **Does the generation check or the block machinery treat a non-finite value differently from a finite one?**

**My expectation is no - it is just 8 bytes.** **But nobody has run it, and "just 8 bytes" is the kind of assumption that has been wrong four times this session.**
