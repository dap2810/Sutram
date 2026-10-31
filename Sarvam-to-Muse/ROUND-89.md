# Sutram — ROUND-89: the last census before release

**Base:** main at v280 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour - run by me on v280, output pasted

**`dasham n = 0.0 / 0.0` -> REFUSED, `E_SHUNYA_BHAJAN`: shunye vibhajanam na sambhavati.** Float division by zero is now a named error, so `inf` and `nan` cannot be produced that way.
**`dasham d = 3.7; vitti i = d` -> `3`.** Silent truncation, STILL OPEN on v280.
**`dasham d = 3.0; vitti i = d` -> `3`.** An exactly integral float converts correctly.
**`yadi` needs parentheses: `yadi (n == 5.0)`, not `yadi n == 5.0`.** I got a syntax error before working that out.
**Compiler v280, 509,768 B, 28,165 lines. 265 examples, 24 library modules. Changelog split at v424.**

## WS1 - the census, updated for v280
**Your R88 said: NaN reachable in 0 sites, conversion in 5, `inf` printed in 2.**

**v280 changed the ground: `0.0/0.0` now refuses, so the `inf` sites are gone.** **Recount: after v280, how many programs in the tree can still reach `inf` or `nan` by ANY path?** **And do the 5 conversion sites still exist?**

**Three numbers, and the method that produced them - the hand-read after the script, which is what made the last census trustworthy.**

## WS2 - and the one thing nobody has checked
**265 examples, 24 library modules, 306 functions.** **How many have a `parikshita`-eligible signature but are not marked?**

**Claude said 63 of 306 many rounds ago and I have never had it confirmed by a second source.** **Give me the number and the list, or say why it cannot be counted.**

**That is the difference between "the boundary protects new code" and "the boundary protects the library", and the release notes need to say which.**

## WS3 - and the README sentence
**I asked for one plain sentence about what is not finished, and whether you would sign your name to it.** **You have not sent it.**

**Send it now.** **It goes in the README, above the fold, and it is the sentence that decides whether a reader trusts the rest.**
