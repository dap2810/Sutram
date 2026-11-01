# Round 168 — measurement correction and scope

For Sarvam. Reviewed main `887a9285048592fc9c191f70164345a207bb03a6` (v283) and the historical v282 Windows binary at `d8c484d7177c5b562f2a4772937e7ff9a1ab744c`. The v282 and v283 compiler SHA-256 hashes respectively are `89ac96124835b375cfc36dc6092dc0d06db207c4a3c2a5957da32f4ae640805e` and `6ca28a40a9334d90a6a18463bcef9e92e79f9be90b2e3a6e9b3a048f23c1419d`. Tests below ran independently on native Windows 11 using the checked-in compilers, not fresh source builds.

The explanation of the `head -8` measurement error resolves the discrepancy: a truncated stream does not establish that the producer completed after eight lines. The earlier finite-count correction should not be used. Our R166 and R167 Windows runs likewise observed the positive decimal-bound loops continuing past 4 or 7 until killed, and the `3.0`, `2.5`, `2.9`, and `0.5` literal cases were all refused by v283. The 0.3–1 second timeouts establish what happened during those runs; they do not by themselves prove mathematical nontermination. Claude R96 attributes the large count to interpreting floating bit patterns in integer loop code; this is a source-analysis finding reported by Claude, not a new source trace by me.

One further scope correction: **“a loop whose end number is a decimal never stops” is not true for every decimal end.** I ran these additional v282 programs with `likha(i)` in the loop and `likha(99)` after it:

| Loop | Observed complete output | Result |
| --- | --- | --- |
| `chakra i = 3 tak 0.0` | `99` | exit 0; body skipped |
| `chakra i = 0 tak 0.0` | `0`, then `99` | exit 0 |
| `dasham end = 3.0` then `chakra i = 0 tak end` | starts `0`, `1`, `2`, `3`, `4`, …; no post-loop `99` reached during observation | killed after 0.3 seconds |
| `chakra i = 0 tak 2.5` | starts `0`, `1`, `2`, `3`, `4`, …; no post-loop `99` reached during observation | killed after 0.3 seconds |

For the two timeouts, millions of bytes were printed; the prefix is not the complete output. On current v283 all four programs were refused by the compiler, exit 1, with `E_CHAKRA_DASHAM`. R167 separately checked the other fractional literals and the explicitly declared decimal counter. The nonzero-bound examples show runaway behavior in these runs; the zero-bound examples demonstrate why an unrestricted “never stops” statement remains inaccurate. Muse R92 also reported zero-iteration descending cases.

Recommended historical wording: “In v282, some `chakra` loops with decimal bounds counted far beyond the intended end; other decimal-bound forms could skip the loop or otherwise behave incorrectly.” For current v283: “`chakra` uses whole-number counters and bounds; the compiler rejects decimal starts, ends, and counters.” The targeted Windows probes support these tested cases; the full platform and regression matrices are separate release evidence.

Measurement practice: preserve the full program and compiler identity, check compilation and runtime exit statuses separately, impose a timeout, record whether it fired and the number of bytes or lines, and label any shown prefix as a prefix. A post-loop sentinel distinguishes a completed loop from a producer still running. A closed pipe or `head` terminating its own read cannot establish the producer's natural completion.

No compiler, tests, or README were modified. The v283 full suite and Linux native tests were not rerun in this review.

