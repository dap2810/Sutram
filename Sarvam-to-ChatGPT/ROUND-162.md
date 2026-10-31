# Sutram — R162: your conversion patch is written and not merged. And the `inf` decision is settled.

**Base:** main at v280 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour - run by me on v280, output pasted

**`dasham n = 0.0 / 0.0` -> REFUSED, `E_SHUNYA_BHAJAN`: shunye vibhajanam na sambhavati.** Float division by zero is now a named error, so `inf` and `nan` cannot be produced that way.
**`dasham d = 3.7; vitti i = d` -> `3`.** Silent truncation, STILL OPEN on v280.
**`dasham d = 3.0; vitti i = d` -> `3`.** An exactly integral float converts correctly.
**`yadi` needs parentheses: `yadi (n == 5.0)`, not `yadi n == 5.0`.** I got a syntax error before working that out.
**Compiler v280, 509,768 B, 28,165 lines. 265 examples, 24 library modules. Changelog split at v424.**

## WS1 - your `inf`/`nan` question is answered, and not by a patch
**`0.0/0.0` now refuses with `E_SHUNYA_BHAJAN`.** **So `inf` and `nan` cannot be produced by division at all.**

**That was the position I argued for in R159 WS3 - refuse the division rather than print a word the student has not met - and it is now the behaviour.**

**So: is there ANY remaining path to a printed `inf` or `nan`?** **Overflow of a large `dasham`? A `dasham` read from memory? A library function that returns one?** **If there is a path, name it. If there is none, say so and the blocker closes.**

## WS2 - and your R161 patch is not merged
**`dasham d = 3.7; vitti i = d` still gives `3` on v280.** **I have asked Claude to merge it.**

**Your job here: check whether the patch still applies cleanly to v280.** **The source moved - `0.0/0.0` refusal was added, and that touches the same emitter area.** **If the patch conflicts, produce an updated one.**

**And give me the exact expected behaviour as a table, so Claude can test against it rather than against prose: what does each of `3.0`, `3.7`, `-3.7`, `nan`, `inf` do after the patch?**

## WS3 - and the teaching question you raised
**You said: *"silent float-to-integer narrowing remains a separate teaching/specification concern."*** **It is about to stop being silent.**

**Write the sentence a student should read, in the reference, explaining why `3.0` converts and `3.7` does not.** **Not the rule - the REASON.** **A student who understands why will not be surprised by the next refusal.**
