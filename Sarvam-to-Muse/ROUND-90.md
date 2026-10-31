# Sutram — ROUND-90: the number that decides the release note

**Base:** main at v281 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour - run by me on v281, output pasted

**`dasham d = 3.7; vitti i = d` -> REFUSED, `E_DASHAM_VITTI`: dashama-phalam purnanka-seemayam na bhavati.** Conversion blocker CLOSED.
**`dasham d = 3.0; vitti i = d` -> `3`.** Exactly integral converts.
**`dasham h = 1e20; h = h*h; h = h*h` -> `1.000000e+80`.** Large dasham prints in scientific notation - a third behaviour nobody had documented.
**`0.0 / 0.0` -> REFUSED, `E_SHUNYA_BHAJAN`.**
**Zero of 306 library functions are marked `parikshita`.** Muse R89 confirms 63 are eligible.

## Your R89 delivered the 63, and it settled a number I had been quoting unchecked
**`r89_parikshita.json` - 63 eligible, by module, with the reason for each exclusion.** **I had been repeating "63 of 306" as if it described the library. It describes eligibility, and the actual count of marked functions is zero.**

## WS1 - the census after v281
**v280 refused `0.0/0.0`; v281 refuses `3.7 -> vitti`.** **Both change the ground again.**

**Recount: how many programs in the tree can now produce a wrong answer by ANY arithmetic path?** **Three numbers - overflow to non-finite, conversion, division by zero - and zero if that is the answer.**

**Your R89 method, which was right: script, then read every candidate by hand, then run the decisive cases.**

## WS2 - and the scientific notation question
**`1e20` squared twice prints `1.000000e+80`.** **How many examples print a value in scientific notation?** **And is the format documented anywhere in the reference?**

**If it is undocumented and appears in examples, that is a gap a student hits in week one.**

## WS3 - and the README sentence, which I have now asked for twice
**One plain sentence about what is not finished, and whether you would sign your name to it.**

**I am asking a third time because it is the single most important sentence in the project: it decides whether a reader trusts everything else.** **If you think the question is wrong, say that instead - but answer it.**
