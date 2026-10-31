# Sutram — R160: your patch is good, but it may be half-done. Three more patches.

**Base:** main at v279 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour - run by me on v279

**`dasham n = 0.0/0.0; n == 5.0` -> `1`.** NaN compares equal to a number.
**`dasham a = 5.0; dasham b = 0.0; a/b` -> `inf`.** No error.
**`dasham d = 3.7; vitti i = d` -> `i = 3`.** Computed conversion truncates silently.

## WS1 - your R159 patch: is it complete?

**`ROUND-159-NAN-COMPARE.patch` is real work and the reasoning is right:** *"Unordered UCOMISD sets PF, ZF and CF. EQ/LT/LE need !PF; NE needs PF OR the ordinary unequal flag."* That is the correct IEEE 754 approach.

**But it handles `OP_EQ`, `OP_LT`, `OP_LE`, `OP_NE`.**

**What about `>` and `>=`?** **Either they are lowered to `LT`/`LE` with the operands swapped before this code runs, or they have their own emit path - and if their own, NaN still returns true there and the fix is half-done.**

**Answer that first: read `gen_expr` and say whether `OP_GT` and `OP_GE` exist as separate opcodes.** **If they do, patch them. If they are lowered, say where and confirm the lowering happens before this point.**

## WS2 - and a test that would have caught it
**Write a `.sm` program that compares NaN against every operator - `==`, `!=`, `<`, `<=`, `>`, `>=` - and prints all six.** **Give the expected output under IEEE 754: `0 1 0 0 0 0`.**

**That is the golden Claude should add. A fix without that test is a fix nobody can check.**

## WS3 - the computed float-to-integer patch
**`dasham d = 3.7; vitti i = d` gives `3` with no message.** **The literal case is refused; this is not.**

**Write the patch.** **Refuse at compile time where the compiler knows both types; at run time with a named Sanskrit error where it does not.** **Say which is achievable here and what the other costs.**

## WS4 - and the installer
**Your finding stands: the checked-in installer is v243, the compiler is v279.** **Write the exact build commands to regenerate it from the current tree**, and say what the resulting hash should be verified against. **Muse is auditing what the current `.exe` installs; your job is the rebuild recipe.**
