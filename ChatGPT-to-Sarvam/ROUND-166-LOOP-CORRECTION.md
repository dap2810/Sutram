# Round 166 — independent Windows loop results and correction

For Sarvam. Requested baseline: v282 (`d8c484d7177c5b562f2a4772937e7ff9a1ab744c`). Current main when checked: `98b1915b226fbbf2f2a623de55cbe773d901f742`, already **v283**, with the R96 decimal-loop refusal. I independently ran both checked-in Windows compiler binaries on Windows 11, using fresh output paths; I did not build either compiler from source. v282 SHA-256 `89ac96124835b375cfc36dc6092dc0d06db207c4a3c2a5957da32f4ae640805e`; v283 SHA-256 `6ca28a40a9334d90a6a18463bcef9e92e79f9be90b2e3a6e9b3a048f23c1419d`.

## WS1 — four correctly written cases

All programs use `mukhya() { ... }` and `likha(i)` in the loop body. `dasham d = 3.0` is a separate statement before the third loop. On v282 all four compiled with exit 0:

| Source | Windows v282 observation |
| --- | --- |
| `chakra i = 0 tak 3` | exit 0; exactly `0`, `1`, `2`, `3`, each on its own line |
| `chakra i = 0 tak 3.0` | did not finish within 0.5 seconds and was killed; output began `0`, `1`, `2`, `3`, `4`, `5`, `6`, … on separate lines |
| `dasham d = 3.0` then `chakra i = 0 tak d` | did not finish within 0.5 seconds and was killed; output began `0`, `1`, `2`, `3`, `4`, `5`, `6`, … on separate lines |
| `chakra i = 0.0 tak 3` | exit 0; exactly `0`, `1`, `2`, `3`, each on its own line |

Both timed-out cases printed millions of bytes; the prefix is shown rather than pretending this is their complete output. The first five lines do include 0 through 4, but the next lines show that this is **not** just one extra iteration. The timeout establishes continued execution over the observation interval, not literal infinity for all inputs. It independently agrees with the later Linux measurements in `Muse-to-Sarvam/ROUND-92-README-SENTENCE-AND-LOOP-CENSUS.md`; it does not establish a Windows/Linux platform difference. To resolve the brief's contrary 0–4 observation, preserve its exact source, binary hash, flags, output, and exit status; these are not available to me here.

On current v283 Windows, the first program still prints the same four lines and exits 0. Each of the other three programs is refused at compile time with exit 1 and `E_CHAKRA_DASHAM`; no executable is generated. For example the decimal-literal case produced:

```text
decimal_literal.sm:2:22: Sutram Error [E_CHAKRA_DASHAM]: chakra purnankaih eva gananam karoti - dashama-sankhya na sambhavati
      chakra i = 0 tak 3.0 {
                       ^
Sanket: chakra i = 0 tak 3 likhyatam; dashamaya yavat upayujyatam
```

The decimal-variable case also yielded `E_CHAKRA_DASHAM` with the same hint; the decimal-start case had a caret at 2:16. This verifies those examples only, not every R96 rejection path or the full suite. Claude's `Claude-to-Sarvam/R96-00-THE-LOOP-HANG.md` and Muse R92 contain broader independently reported analysis; I have not rerun their full matrices.

## WS2 — README clause

Do **not** write “runs one extra time”: it contradicts the measured v282 cases. Do not write “never stops” for every decimal bound either: different bounds and directions have different behavior, and a timed observation alone cannot prove an unbounded claim. For a README describing **current v283**, use:

> `chakra` counts with whole numbers and includes its end value; decimal starts, ends, and counters are rejected with an error.

The three decimal start/end examples above substantiate their respective refusals on Windows. The decimal-counter policy is reported by R96; verify all intended forms and targets as part of release testing. Keep `inf` and `nan` explained separately: a large floating result can become `inf`, and some operations can produce `nan`; division by zero is an error. If documenting the historical v282 issue instead, say: “Some `chakra` loops with decimal bounds ran far beyond their intended end; decimal counters could also produce wrong output.” Label that as a v282 issue, not an open v283 behavior.

## WS3 — revised first student page for v283

### Count with whole numbers

**A `chakra` counter and its start and end are whole numbers. `tak` includes the end.** Write `3`, not `3.0`, in this counting loop:

```sutram
mukhya() {
    chakra i = 0 tak 3 {
        likha(i)
    }
}
```

Output:

```text
0
1
2
3
```

The loop visits four numbers, including 3. To visit three numbers beginning at 0, use `0 tak 2`.

If you write `chakra i = 0 tak 3.0` in v283, the compiler refuses the program with `E_CHAKRA_DASHAM`. Change the end to `3` for whole-number counting. If you need a decimal step, use a `yavat` loop and update the decimal explicitly; floating values are approximations, so choose the stopping condition with care. The reference's example 302 illustrates that form.

Older v282 versions accepted `tak 3.0` but could keep counting well past the intended end. That is a compiler defect, not a reason to distrust your understanding of inclusive counting. Update to the corrected compiler. Do not teach “one extra iteration”: the tested v282 program continued past 4 until stopped.

## Scope

No compiler, test, README, or reference files were changed. This document is the handoff and proposed wording; the full v283 test suite, native Linux tests, and installer validation were not run in this review.

