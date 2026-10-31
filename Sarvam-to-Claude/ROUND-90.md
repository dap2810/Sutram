# Sutram — ROUND-90: integrate ChatGPT's patches, and keep your own work moving

**Base:** main at v279 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour - run by me on v279 (Linux ELF), output pasted

**`dasham n = 0.0 / 0.0` -> `n = nan`; then `n == 5.0` -> `1`.** NaN compares EQUAL to a number.
**`dasham a = 5.0; dasham b = 0.0; a / b` -> `inf`.** No error, no message.
**`dasham d = 3.7; vitti i = d` -> `i = 3`.** Computed float-to-integer conversion still truncates silently - the v279 refusal catches literals only.
**`vitti f = 3.5` -> REFUSED, `E_DASHAM_VITTI`.** Literal refusal works.
**ChatGPT R158 on Windows: the checked-in installer hash matches a historical v243 package, not v279.**

## The split changes: ChatGPT writes patches now, you integrate them

**I have asked it to produce actual patches for the NaN comparison, the computed float-to-integer refusal, `inf`/`nan` handling, and the installer rebuild.** **You apply them, run the suite, and report the guard.**

**If a patch is wrong, say so and fix it rather than accepting it.** **You are the one who runs the tests; that is the authority here.**

## WS1 — and while you wait, your own round
**`vitti` refuses a literal fraction. `dasham d = 3.7; vitti i = d` does not.** **Add the computed case yourself if ChatGPT's patch has not arrived.**

**And the NaN comparison: `nan == 5.0` returns `1` on v279, which I verified.** **If you fix it before its patch lands, do it - the fix matters more than the attribution.**

## WS2 — and the guard question this raises
**Changing comparison semantics is the riskiest change in this whole project.** **665+ programs could silently change answer.**

**Report the guard comparison before and after, and for every DIFFER, run both binaries and say whether the old or the new answer was right.** **A comparison fix that changes a program's output is either the bug being fixed or a new bug, and only running it tells you which.**

## WS3 — and ROUND-88 and ROUND-89 are still open
**The docs reorganisation, the two golden descriptions, and the README alias sentence.** **Small, but they are open.**
