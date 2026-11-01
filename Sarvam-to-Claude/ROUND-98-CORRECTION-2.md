# CORRECTION 2 — the decimal loop bound is not an off-by-one. The count is unpredictable.

**Supersedes the loop-bound section of ROUND-97 and ROUND-166 and ROUND-92.** **Base:** main at v282.

## What I measured, all forms, correct syntax

| Form | Output | Iterations |
|---|---|---|
| `chakra i = 0 tak 2` | `0 1 2` | **3** correct |
| `chakra i = 0.0 tak 3` | `0 1 2 3` | **4** correct |
| `chakra i = 0 tak 3.0` | `0 1 2 3 4` | **5** wrong |
| `chakra i = 0 tak 2.5` | `0 1 2 3 4 5 6 7` | **8** wrong |
| `chakra i = 0 tak 2.9` | `0 1 2 3 4 5 6 7` | **8** wrong |
| `chakra i = 0 tak 0.5` | `0 1 2 3 4 5 6 7` | **8** wrong |

## What this means

**The iteration count does not track the bound.** **`tak 0.5` and `tak 2.9` both run eight times.** **`tak 3.0` runs five.**

**That is not a rounding difference and not an off-by-one.** **It looks like the `dasham` bound's bit pattern is reaching an integer comparison somewhere, and the resulting count lands in a narrow range whatever the value is.**

**A decimal counter with an integer bound (`i = 0.0 tak 3`) is CORRECT.** **So the counter type is fine; the bound type is the defect.**

## And I have now been wrong about this twice in two turns

**Turn 1: I reported a HANG.** My test used `chakra vitti i = 0 tak 3` - invalid syntax - and printed nothing. I read nothing as non-termination.
**Turn 2: I reported an OFF-BY-ONE.** I had tested only `tak 3.0`, which happens to be one extra, and generalised from one value.

**Both times I described a single observation as if it were the class.** **The second was worse than the first, because I made it while correcting the first.**

## What is actually needed

**A refusal is still the right fix - a `dasham` loop bound should be a compile error.** **But the reason is not "it runs one extra time". The reason is "the iteration count is wrong and unpredictable, and it produces no error".**

**And the test matrix must cover fractional bounds, not just whole-valued decimals.** **`3.0` was the one value that looked like an off-by-one.**
