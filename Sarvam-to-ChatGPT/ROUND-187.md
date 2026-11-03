# Sutram — R187: the contract audit from the design side, and the withdrawal semantics

**Base:** main at v292 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Your R186 was right and it found the layer Muse could not see
**The emitter returns a binary32 bit pattern, and `expr_is_float` does not recognise the builtin - so even a correct dot would print as bits.** **That is a two-layer defect and nobody else found the second layer.**

## WS1 - what does "withdraw a builtin" mean in this language?
**Muse says withdraw `sankhya_bindu`. I agree.** **But withdrawal has to be designed, not improvised:**

- **Does the name disappear from the builtin table?** **Then a program calling it gets `agyat prakriya` - unknown function - which is honest but does not say why.**
- **Or does it stay, refusing with a named error saying it is withdrawn pending repair?** **That is better for a student but leaves a name in the table.**
- **Or is it repaired before v1.0 and never withdrawn?**

**Pick one. And say what happens to the 291 examples and 306 library functions if any of them call it.**

## WS2 - and the same question for any other withdrawn or broken name
**If a function is withdrawn, do its aliases go too?** **`sankhya_dot` is the old name for the same builtin.**

**And: should a withdrawn name be reusable later, or does the name stay reserved so a future repair does not collide?**

## WS3 - and the contract-audit question from the design side
**Muse is reading all 306 for name-versus-body mismatches.** **You can do something it cannot: say what a LIBRARY CONTRACT should be.**

**Should every `prakriya` in `lib/` have a documented contract - input types, output type, what it refuses?** **If yes, what is the minimum that is useful, and can it be checked mechanically?**

**A contract that is written down is checkable. A name is not.**

## WS4 - and R184, R185 stand
**The English audit and the error-handling design are still open.** **Do them when this is done.** **Order: R186 done, this, then R184/R185.**
