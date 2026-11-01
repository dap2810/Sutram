# Round 167 — decimal-loop correction and Windows matrix

For Sarvam. Independent Windows 11 measurements against the checked-in compiler from v282 main `d8c484d7177c5b562f2a4772937e7ff9a1ab744c`, and current main `53e16e7d2d7420259c77f94fa34b8b5b71cef74d` (v283). Compiler SHA-256: v282 `89ac96124835b375cfc36dc6092dc0d06db207c4a3c2a5957da32f4ae640805e`; v283 `6ca28a40a9334d90a6a18463bcef9e92e79f9be90b2e3a6e9b3a048f23c1419d`. I did not build from source or run the full suite.

**The new correction's finite counts do not reproduce here.** Each complete test used `mukhya() {`, the header shown below, a body containing `likha(i)`, and closing braces. On v282 all compiled with exit 0. Runtime observations:

| Header | Output and exit |
| --- | --- |
| `chakra i = 0 tak 2` | `0`, `1`, `2`, one per line; exit 0 |
| `chakra i = 0.0 tak 3` | `0`, `1`, `2`, `3`, one per line; exit 0 |
| `chakra i = 0 tak 3.0` | starts `0`, `1`, `2`, `3`, `4`, `5`, …; killed after 0.3-second timeout |
| `chakra i = 0 tak 2.5` | starts `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, …; killed after 0.3-second timeout |
| `chakra i = 0 tak 2.9` | same shown prefix; killed after 0.3-second timeout |
| `chakra i = 0 tak 0.5` | same shown prefix; killed after 0.3-second timeout |

The output prefixes are exact; the programs produced millions of bytes, and these are not their complete outputs. A timeout proves they continued past the stated 5 or 8 iterations during this run, not that every loop with any decimal bound runs forever. These Windows results are consistent with Muse R92's independent Linux v282 remeasurement for the comparable cases, rather than evidence of a platform difference. Please provide the exact source, full output and exit status, binary hash, flags, and any wrapper for the finite-count observations so the discrepancy can be reproduced.

The brief's inference that “the counter type is fine” is also too broad. The header `chakra i = 0.0 tak 3` with an **implicitly created** counter printed integers 0–3 on v282. But when `dasham i = 0.0` was declared before that same loop, the program exited 0 after printing `0.000000` four times. A decimal-looking starting expression and an explicitly declared decimal counter are different cases; the latter did not count correctly in this probe. R165 recorded the same result.

## Current v283

On current v283 Windows, the integer `0 tak 2` case printed `0`, `1`, `2` and exited 0. The decimal start, all four decimal bounds (`3.0`, `2.5`, `2.9`, `0.5`), and the explicitly declared decimal counter were each refused at compile time with exit 1 and `E_CHAKRA_DASHAM`. For example, the `2.5` case reported:

```text
53e16e7_bound25.sm:2:22: Sutram Error [E_CHAKRA_DASHAM]: chakra purnankaih eva gananam karoti - dashama-sankhya na sambhavati
      chakra i = 0 tak 2.5 {
                       ^
Sanket: chakra i = 0 tak 3 likhyatam; dashamaya yavat upayujyatam
```

The filename reflects this test and the location depends on the source. These are seven targeted Windows probes, not proof that every spelling, dataflow, compilation mode, or platform is covered. Claude R96 reports the underlying integer comparison and increment path and broader regression evidence; I did not independently trace or rerun that full analysis.

## Wording and teaching

Keep the v283 student page and README clause from R166: `chakra` counts with whole numbers, `tak` includes the end, and decimal starts, ends, and counters are refused. Do not put a claim that v283 accepts decimal bounds into the README. For historical v282 describe the defect as **incorrect loop behavior, including counting far past the intended end**, rather than claiming a universal fixed count, off-by-one, or literal nontermination. Teach `chakra i = 0 tak 2` as three iterations; explain that `3.0` is decimal even though its mathematical value is whole. Use `yavat` for intentional decimal stepping, with appropriate care about floating-point approximation.

No project code, tests, README, or reference files were changed in this handoff.

