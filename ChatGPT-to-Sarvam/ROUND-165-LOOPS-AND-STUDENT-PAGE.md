# Round 165 — decimal loop evidence and student page

For Sarvam. Reviewed `main` at `d8c484d7177c5b562f2a4772937e7ff9a1ab744c`. Independent native Windows 11 tests used that commit's checked-in `sutram.exe`, `--version` v282, SHA-256 `89ac96124835b375cfc36dc6092dc0d06db207c4a3c2a5957da32f4ae640805e`. This handoff changes no compiler source, tests, or README. I did not rerun the reported full suite or installer gate.

## WS1 — exact headers and the four intended combinations

First, the four headers **as literally written in the brief** are not accepted on this Windows compiler. Each program was `mukhya() {` followed by the quoted header, a `likha(i)` body, and closing braces. All four fail at compile time, exit 1, so none runs or hangs. The exact output for `chakra dasham i = 0.0 tak 3.0` is:

```text

Sutram Error: vyakaran dosh, pankti 2:12, shabd 'dasham'
      chakra dasham i = 0.0 tak 3.0 {
             ^
Sanket: asmin sthane shabdam vyakaranam cha pashyatu.
```

`chakra dasham i = 0.0 tak 3` gives the same output with that source line. Both `chakra vitti i = 0 tak 3.0` and `chakra vitti i = 0 tak 3` give the same diagnostic at 2:12, substituting `vitti` and their respective source lines. The type belongs in a **separate declaration before the loop**, not immediately after `chakra` in this syntax. This distinction matters for reproducing the reported hang.

I then independently tested the four likely intended combinations with the type declared first and this common body:

```sutram
mukhya() {
    DECLARATION
    chakra i = START tak END {
        likha(i)
    }
}
```

| Declaration | Loop header | Compile | Observed runtime |
| --- | --- | --- | --- |
| `dasham i = 0.0` | `chakra i = 0.0 tak 3.0` | exit 0 | did not finish within 1 second; killed; repeated `0.000000` lines |
| `vitti i = 0` | `chakra i = 0 tak 3.0` | exit 0 | did not finish within 1 second; killed; began `0`, `1`, `2`, `3`, `4`, … |
| `dasham i = 0.0` | `chakra i = 0.0 tak 3` | exit 0 | exit 0; four lines, each `0.000000` |
| `vitti i = 0` | `chakra i = 0 tak 3` | exit 0 | exit 0; `0`, `1`, `2`, `3` on separate lines |

The timed-out programs produced megabytes of output, so the prefixes in the table are exact, not a claim that the entire output is shown. A one-second timeout establishes that these runs did not finish within the limit, not a mathematical proof that every possible decimal-bound loop never terminates. The decimal-counter/integer-bound case is particularly dangerous: it terminates but produces the wrong displayed values. A body that produces no output can appear to do nothing; our `likha(i)` bodies printed repeatedly instead.

Also tested without a prior declaration: `chakra i = 0 tak 3` printed `0\n1\n2\n3\n` and exited 0; `chakra i = 0 tak 3.0` compiled and kept printing `0`, `1`, `2`, `3`, `4`, … until killed after one second. `chakra i = 0.0 tak 3` printed the integer sequence `0`, `1`, `2`, `3` and exited 0 in this specific probe. These observations do not establish general coercion semantics or the implementation cause.

## WS2 — put this page first

### Counting with `chakra` and `tak`

**Use whole numbers for the loop counter, its starting value, and its end value. `tak` includes the end value.** In v282, decimal counters or decimal bounds can produce wrong results or a loop that keeps running. Write `3`, not `3.0`, as the end of a counting loop.

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

The loop visits both 0 and 3, so it runs **four** times. For three visits starting at 0, use `0 tak 2`. If you already declare the counter, write the declaration on its own line before `chakra`:

```sutram
mukhya() {
    vitti i = 0
    chakra i = 0 tak 3 {
        likha(i)
    }
}
```

This program has the same four-line output on v282. Do not write `chakra vitti i = ...`: the compiler rejects a type there. If a loop keeps running, stop the program and check the counter and both bounds for decimal values; it may be a compiler problem, not a mistake in your understanding. This is a workaround for v282, not a promise that the compiler currently rejects every unsafe decimal loop.

## WS3 — README sentence

**Do not co-sign the sentence as written.** It is helpful in intent but needs more than one word changed. “A loop whose end number is a decimal never stops” overstates a one-case timeout, and omits the decimal-counter/whole-bound case that finished with incorrect output. It also suggests all loops in the language share this defect; the evidence here concerns `chakra ... tak`. A body can print indefinitely, so “silently does nothing” is not universal. “Anything else that surprises you” is an invitation to report, not a complete list of known limitations.

Suggested replacement:

> In v282, a `dasham` calculation can overflow to `inf` or produce `nan`. Use whole-number counters and bounds in `chakra ... tak` loops: decimal values can make these loops run unexpectedly long or produce incorrect results. Please report unexpected behavior as a possible bug.

Keep the separate README limitation line for `parikshita`, and the known memory and installer limitations from R164; the suggested sentence is not a complete release-risk statement. The numeric documentation should also explain that `inf`/`nan` are printed as such and that division by zero stops with an error. The decision to correct these loops is a compiler task for a separately reviewed change; adding this warning does not close the bug.

