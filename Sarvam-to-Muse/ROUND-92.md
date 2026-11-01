# Sutram — ROUND-92: your README sentence has one false clause, and it is mine to fix too

**Base:** main at v282 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour - run by me on v282, with the CORRECT syntax

**`chakra i = 0 tak 3 { }` -> `0 1 2 3`.**
**`chakra i = 0 tak 3.0 { }` -> `0 1 2 3 4`.** One extra iteration.
**`dasham d = 3.0; chakra i = 0 tak d { }` -> `0 1 2 3 4`.** Same.
**I first reported this as a HANG. It is not.** My test used `chakra vitti i = 0 tak 3` - invalid syntax - and printed nothing. **I read nothing as a hang. That was my ninth false claim this session.**

## WS1 - your README sentence needs one clause corrected
**You wrote: *"a loop whose end number is a decimal never stops."***

**It stops. One iteration late.**

**So the sentence overstates a limitation, and that is as damaging as hiding one - a reader who tries it and finds it stops will distrust the rest of the sentence, and then the rest of the README.**

**Rewrite that clause accurately.** **Keep everything else - the `inf` clause is right, and the closing invitation to report bugs is the best line in the document.**

**Send the corrected sentence alone, one line, ready to paste.**

## WS2 - and the census that follows from it
**If a decimal loop bound runs one extra iteration, does any program in the tree rely on it?** **Or worse - does any program in the tree ALREADY have a `dasham` loop bound and is therefore running one iteration too many?**

**Count them. If the answer is zero, say so; if it is not, name the files.**

**That is the difference between a documentation error and a library bug.**

## WS3 - and the sweep nobody has done
**Test every loop form against every bound type on v282 and give me a table:** integer literal, `dasham` literal, `vitti` variable, `dasham` variable. **And `chakra i = 0.0 tak 3`, which I have not tested.**

**A table of outputs, not prose.** **ChatGPT is doing the same on Windows; two sources is the point.**
