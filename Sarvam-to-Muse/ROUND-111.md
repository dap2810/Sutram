# Sutram — ROUND-111: `sankhya_bindu` is broken. Prove it is TOTAL, not partial.

**Base:** main at v292 · **Deliver into:** `Muse-to-Sarvam/`

## Your R109 finding, confirmed by me

**`sankhya_bindu(k, k)` on a `kosh` holding 5 and 6 returns `0`.** **A dot of a vector with itself cannot be zero.** **Silent wrong answer, no error.**

**Your diagnosis: the body reads 16 bytes as four 32-bit floats, and no Sutram value holds four contiguous 32-bit floats.**

## WS1 - is the defect total or partial?
**Test every input shape and report the output for each:**
- **two `kosh`** - I get 0
- **two `mala`** - you said 2 for [5,6,7]
- **two `rachana`**
- **two `dasham` scalars**
- **two `vitti` scalars**
- **mixed: `kosh` and `mala`**
- **an empty `kosh`**

**For each: does it compile, what does it print, and is that number meaningful or garbage?**

**The question I need answered: is there ANY input for which it returns a correct dot product?** **If there is none, the function is dead code and should be withdrawn. If there is one, it is a narrow function with a misleading name.**

## WS2 - and what a correct one would need
**A dot product needs two sequences of equal length and a numeric type.** **What would the function have to accept to be correct - two `kosh` of `dasham`? Two `mala` of cells?** **And what would it return?**

**Do not design it - ChatGPT is doing that. Tell me what the CORRECT input shape would be, from the language's own types.**

## WS3 - and the withdrawal question
**If no input produces a correct answer, should `sankhya_bindu` and its old name `sankhya_dot` be withdrawn from the library before v1.0?**

**A function that cannot be right is worse than a missing one, because a student will call it and get a plausible number.**

**Give me a yes or no and the reason.**
