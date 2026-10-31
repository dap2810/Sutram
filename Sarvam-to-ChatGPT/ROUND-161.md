# Sutram — R161: finish the two you left open. Runtime conversion, and the installer actually rebuilt.

**Base:** main at v279 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour - run by me on v279, output pasted

**NaN against all six operators: `==` 1, `!=` 0, `<` 1, `<=` 1, `>` 0, `>=` 0.** IEEE 754 requires `0 1 0 0 0 0`. So `>` and `>=` are ALREADY correct (`seta`/`setae` test CF, unordered sets CF=1); only EQ/NE/LT/LE are wrong, and those are what R159 patches.
**`dasham d = 3.7; vitti i = d` -> `i = 3`.** Computed float-to-integer still truncates silently.
**`vitti p = nirmmita(10); p[1] = 5` -> REFUSED, `E_NIRMMITA_SEEMA`.**

## Your R160 answered a question better than I asked it

**`>` and `>=` were never broken.** **I suspected half a patch; the real reason is that `seta`/`setae` test CF and unordered sets CF=1.** **I verified all six operators myself and your analysis was exact.**

**And you named what you had not done, which is why this round is short and specific.**

## WS1 - the untyped runtime conversion case
**You wrote: *"the untyped runtime case and other conversion sites remain unimplemented."***

**Implement it.** **`vitti i = d` where `d` is a `dasham` must not silently give `3`.**

**A named Sanskrit error at run time is acceptable; a wrong answer is not.** **And list the other conversion sites you found, so I know the full set rather than the one I tested.**

## WS2 - and the installer, actually rebuilt
**Your R160 said the manifest and an execution-policy failure prevented calling it rebuilt.**

**So this round: state exactly what blocks it, and whether any of it is something I can do.** **If the blocker is a Windows execution policy, that is the maintainer's machine and I will do it - tell me the command.**

**If it cannot be done from where you are, say that plainly and give me the step-by-step for the person who can.**

**Do not write a third recipe. Either rebuild it or tell me the one thing that stops it.**
