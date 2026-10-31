# Sutram — R163: THE HEAVY ROUND. Decide what a number is, and make the release honest.

**Base:** main at v281 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour - run by me on v281, output pasted

**`dasham d = 3.7; vitti i = d` -> REFUSED, `E_DASHAM_VITTI`: dashama-phalam purnanka-seemayam na bhavati.** Conversion blocker CLOSED.
**`dasham d = 3.0; vitti i = d` -> `3`.** Exactly integral converts.
**`dasham h = 1e20; h = h*h; h = h*h` -> `1.000000e+80`.** Large dasham prints in scientific notation - a third behaviour nobody had documented.
**`0.0 / 0.0` -> REFUSED, `E_SHUNYA_BHAJAN`.**
**Zero of 306 library functions are marked `parikshita`.** Muse R89 confirms 63 are eligible.

## Five workstreams. Two are design decisions I cannot make alone, two are code, one is the release text.

## WS1 - the arithmetic decision: what happens when a dasham overflows?
**You found that overflow reaches `inf`. I found `1e20` squared twice gives `1.000000e+80`, not `inf` - so there is a range between them I have not mapped.**

**Map it: at what magnitude does a `dasham` stop being a number and become `inf`? And what does the compiler print at each step?**

**Then decide, and argue it:**
- **Option A - refuse overflow, like integer overflow refuses.** Consistent with division by zero. But floating point is supposed to have a wide range and refusing loses that.
- **Option B - make `inf` and `nan` named Sanskrit values the language admits to.** `anant` and `avyakta`? A student can then compare against them.
- **Option C - document that `dasham` is IEEE and overflow gives `inf`.** Honest, and puts the burden on the reader.

**Pick one. Say what breaks. Say which you would refuse to ship.**

## WS2 - and the printing question that follows
**`1.000000e+80` is scientific notation.** **Nobody has documented that.** **Does the reference mention it? Does a student meeting `1.000000e+80` understand it?**

**If Option B or C wins, the printing of non-finite values must be decided too - a word, a symbol, or a refusal.**

## WS3 - `parikshita` protects nothing, and that is a release decision
**Zero of 306 library functions are marked.** **63 are eligible.**

**So `parikshita` today is a tool for self-contained code and useless for anything that calls the library.**

**Two choices: mark the 63, or say plainly that it ships as a tool.** **Which, and what does marking them cost - measured, not estimated?** **If it is a mechanical change with no risk, say so and do it. If it risks behaviour, say why.**

## WS4 - and the installer, which is now two versions behind
**The compiler is v281.** **Your review installer is v279.** **It has fallen behind twice while we worked on arithmetic.**

**This is a process problem, not a build problem: the installer should be built by the same commit that bumps the version.** **Design that - a make target, a gate, a checklist line - so it cannot fall behind again.** **That is worth more than one rebuilt `.exe`.**

## WS5 - and the release text, which I want from you
**Write the paragraph that goes in the README above the fold.** **What Sutram is, what works, what does not, in language a schoolteacher reads and trusts.**

**And the one line about `parikshita` that tells the truth: it is a tool, not a guarantee, until the library is marked.**

**If you would not sign it, say why.**
