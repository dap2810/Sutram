# Sutram — ROUND-93: the guard on the conversion, and the installer that keeps falling behind

**Base:** main at v281 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour - run by me on v281, output pasted

**`dasham d = 3.7; vitti i = d` -> REFUSED, `E_DASHAM_VITTI`: dashama-phalam purnanka-seemayam na bhavati.** Conversion blocker CLOSED.
**`dasham d = 3.0; vitti i = d` -> `3`.** Exactly integral converts.
**`dasham h = 1e20; h = h*h; h = h*h` -> `1.000000e+80`.** Large dasham prints in scientific notation - a third behaviour nobody had documented.
**`0.0 / 0.0` -> REFUSED, `E_SHUNYA_BHAJAN`.**
**Zero of 306 library functions are marked `parikshita`.** Muse R89 confirms 63 are eligible.

## Your R91-92 merged the conversion patch and I verified it
**`3.7` refuses with `E_DASHAM_VITTI`. `3.0` gives `3`.** **That is the right rule and the right error.**

## WS1 - the guard on the conversion, which is the work
**A conversion that now refuses will break any program that relied on truncating.** **Muse counted 5 real sites.**

**Run the guard. For every DIFFER, run the old binary and the new one, and say whether the OLD answer (a truncated integer) or the NEW one (a refusal) is right.**

**My expectation is the refusal is right in all five. Say it from the evidence, not from my expectation.**

## WS2 - and the one thing I found that nobody documented
**`dasham h = 1e20; h = h*h; h = h*h` prints `1.000000e+80`.** **Scientific notation.** **Is that in the reference? Does any golden cover it?**

**If not, that is a gap - a student meeting `1.000000e+80` has no way to know it means a hundred trillion trillion.**

## WS3 - and the installer process
**The installer has fallen behind twice: v279 while the compiler is v281.** **That is not a build failure, it is a missing step.**

**Add the step: whatever command builds the installer becomes part of the release gate, and `gates.sh` fails if the `.exe` version does not match the compiler's.** **That is a small change that prevents a whole class of release error.**

**And rebuild at v281, reporting the SHA-256.**
