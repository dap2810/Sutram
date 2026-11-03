# ADDENDUM to ROUND-115 — do not stop, do not restart

**Read this after R115. It does not replace it and it does not change its scope.**

## The addition

**Muse R111 has proven `sankhya_bindu` is TOTAL, not partial:** `kosh` self-dot gives 0 instead of 110, `mala` gives 0 instead of 110, `rachana` gives 0 instead of 61, and **two `dasham` scalars SEGFAULT with exit 139.**

**ChatGPT R186 found the second layer: the emitter returns a binary32 BIT PATTERN rather than a numeric value, and `expr_is_float` does not recognise the builtin as returning a float - so even a correct dot would print as bits.**

## What to do

**If it is cheap after the R115 work: withdraw `sankhya_bindu` and `sankhya_dot` from the builtin table in the same commit.** **A function that cannot be right is worse than a missing one.**

**If it is not cheap, or if it would make the commit hard to bisect: do not do it.** **Queue it and say so. The arena defect outranks this.**

**Do not restart R113 or R114. Do not stop what you are doing. This is a note on work already queued.**

## And the withdrawal, if you do it

**A named Sanskrit message when someone calls it, not a silent absence.** **Something that says the function is withdrawn pending repair.** **And a line in the reference saying why.**
