# Sutram — R159: WRITE THE CODE. Four fixes, as patches I can hand to Claude.

**Base:** main at v279 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour - run by me on v279 (Linux ELF), output pasted

**`dasham n = 0.0 / 0.0` -> `n = nan`; then `n == 5.0` -> `1`.** NaN compares EQUAL to a number.
**`dasham a = 5.0; dasham b = 0.0; a / b` -> `inf`.** No error, no message.
**`dasham d = 3.7; vitti i = d` -> `i = 3`.** Computed float-to-integer conversion still truncates silently - the v279 refusal catches literals only.
**`vitti f = 3.5` -> REFUSED, `E_DASHAM_VITTI`.** Literal refusal works.
**ChatGPT R158 on Windows: the checked-in installer hash matches a historical v243 package, not v279.**

## You are being given coding work from now on, not only audits

**You can write code. You cannot merge it. So write it, and Claude applies it.** **That is faster than me asking Claude to design and build while you audit.**

**Deliver actual patches, not descriptions.** **If you cannot produce a patch for one of these, say which and why - that is a useful answer, not a failure.**

## WS1 — NaN comparison. The worst bug in the language.

**`0.0/0.0` gives `nan`, and `nan == 5.0` returns `1`.** **A comparison that lies is worse than a crash, because the program keeps running.**

**Write the fix.** **The semantics I want: any comparison involving NaN is FALSE, except `!=` which is TRUE.** **That is IEEE 754 and it is what a student should learn.**

**Show: the emitted-code change, the operand order, and the exact instruction sequence.** **If the current comparison is a single `ucomisd` + `sete`, say what it actually is and what it must become.**

## WS2 — computed float-to-integer conversion
**`vitti i = d` where `d` is a `dasham` truncates to `3` silently.** **The literal case is refused at v279; this is not.**

**Write the fix: refuse at COMPILE TIME when the compiler can see the types, and at RUN TIME with a named Sanskrit error when it cannot.** **Say which of the two is achievable in this compiler and what the other costs.**

## WS3 — `inf` and `nan` as printed values
**`5.0/0.0` prints `inf`.** **Is that acceptable, or should it be a named error?**

**My view: `inf` and `nan` are not answers, and a teaching language should refuse the division rather than print a word the student has not met.** **Argue me out of it if you disagree - but write the code either way.**

## WS4 — and the installer
**The checked-in installer is v243. The compiler is v279.** **Write the build steps to regenerate it from the current tree**, and say what the hash should be verified against. **This is the one that decides whether anyone installs the right thing.**
