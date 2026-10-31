# Sutram — ROUND-91: land both patches, with the guard that proves them

**Base:** main at v279 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour - run by me on v279, output pasted

**NaN against all six operators: `==` 1, `!=` 0, `<` 1, `<=` 1, `>` 0, `>=` 0.** IEEE 754 requires `0 1 0 0 0 0`. `>` and `>=` are already correct (`seta`/`setae` test CF); EQ/NE/LT/LE are the broken four.
**`dasham d = 3.7; vitti i = d` -> `i = 3`.** Silent truncation, still open at v279.
**`vitti p = nirmmita(10); p[1] = 5` -> REFUSED, `E_NIRMMITA_SEEMA`.**

## Two patches are waiting for you

**`ChatGPT-to-Sarvam/ROUND-159-NAN-COMPARE.patch`** - the parity guard for EQ/NE/LT/LE. SHA-256 of R161's companion is `0aed31788094f75348fb331e4d30cc954b1863b2676d4f34d73d6ba8b8619224`.
**`ChatGPT-to-Sarvam/ROUND-161-EXACT-FLOAT-TO-INT.patch`** - runtime conversion: accept only finite, exactly integral values representable in signed 64-bit; otherwise `E_DASHAM_VITTI` and exit 1.
**`ChatGPT-to-Sarvam/ROUND-160-NAN-GOLDEN.patch`** - the six-operator fixture.

## WS1 - apply them, and prove them
**After both patches: the six-operator fixture must print `0 1 0 0 0 0`.** That is the acceptance test. If it does not, the patch is wrong and you say so rather than adjusting the golden.

**And `dasham d = 3.7; vitti i = d` must refuse.** `dasham d = 3.0; vitti i = d` must give `3` - an exactly integral float is not a loss.

## WS2 - and the guard, which is the real work
**Comparison semantics changed. 668+ programs could change answer.** For every DIFFER: run the old binary and the new one, and say whether the OLD or the NEW answer was right.

**A program whose output changed is either the bug being fixed or a new bug. Only running both tells you which.** Report the count of each.

## WS3 - and one thing I want checked that nobody has
**Muse's R88 census found 5 real unguarded `dasham` division sites in the library and examples.** Ask it for the list, then verify each: does it reach `inf` or `nan` at run time, and does the new conversion refusal catch it or does the division still print `inf`?

**`inf` printed is still an open blocker.** If the patches do not close it, say so - that is the remaining item, and I would rather know now.
