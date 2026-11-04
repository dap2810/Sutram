# Sutram — R192: the trust-the-count rule, and the error sort. Both overdue.

**Base:** main at v296 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - v296

**Fifteen of sixteen library contracts built. Suite 313. `R116 contracts` gate: 133 checks, 0 failed.**
**The 167 DIFFER are the LIBRARY and nothing else - 0 changed for a reason that is not the contracts. Importing a module changes every program that links it, whether or not it calls the changed function.**
**The 127-byte string crash is OLD - present in v244, the oldest runnable compiler. Found because a 300-character Sanskrit refusal message hit it. Now has its own golden.**
**`patra_asti` stopped: needs `access()`, which the compiler does not make. Claude estimates a day and a half and recommends building it.**
**ChatGPT R191: of 531 English words, 33 are STUDENT-FACING. 135 source-only, 357 example identifiers, 6 preserved.**
**`sankhya_bindu` withdrawn with `E_PRATYAHRITA` and a named alternative. `Sutram truti` live everywhere except the linker.**

## Your R191 gave the number I needed: 33, not 531
**That is a round, not a programme.** **Claude is renaming them as aliases; Muse is auditing each before it is built.**

## WS1 - the trust-the-count rule, third request
**Muse found Claude's `sankhya_bindu` repair took a count `n` and trusted it - `n=2` on [1,2,3]·[4,5,6] gave 14, the first two, silently.**

**The function is withdrawn now, but the rule applies to all 306.**

**Should a library function with a length or count parameter trust it, or verify it?**

**One rule.** **And if the answer is "depends", give the test that decides.** **This is the last unwritten convention in the library and I have asked twice.**

## WS2 - and the error-handling sort, third request
**55 codes, no `try`/`catch`.** **Sort the 55 by whether a running program could respond to them.**

**`E_SHUNYA_BHAJAN` is preventable by checking first.** **`E_PARSE` is not a runtime event at all.** **That sort is the answer to whether this language needs exceptions.**

**If you believe it is not worth doing, say so and say why.** **Two rounds of silence is not an answer, and a reasoned "not worth it" is.**

## WS3 - and one thing you can do that nobody else can
**The 127-byte string crash was present since v244 and nobody found it for fifty versions.** **It took a 300-character Sanskrit message to expose it.**

**What other limits in this compiler have no test because nothing has ever been long enough to hit them?** **Name the candidates: identifier length, nesting depth, module count, literal length, parameter count.**

**A limit nobody has probed is a crash waiting for the right input.**
