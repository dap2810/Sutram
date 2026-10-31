# Round 164 — four student pages and release wording

For Sarvam. Reviewed against main `ea19b12e0714102612c0b2b2aa09b842c4b5b669`, v281. Each complete program below was compiled and run on native Windows with the checked-in v281 compiler (SHA-256 `51bbb8ed0e83853acca52c16c554bc054ae2742a45ed45d7ca80a83bb8ec1284`). Output blocks are observed program output; diagnostics are identified separately. No source, tests, or README was changed by this handoff.

## Page 1 — Whole numbers and decimal numbers

Use `vitti` for a whole number such as `3`. Use `dasham` when you need a decimal value such as `3.7`. A `dasham` is stored as a binary floating-point approximation, so not every decimal fraction is represented exactly.

```sutram
mukhya() {
    vitti whole = 3
    dasham fraction = 3.7
    dasham exact = 3.0
    vitti converted = exact
    likha(whole)
    likha(fraction)
    likha(converted)
}
```

Output:

```text
3
3.700000
3
```

`3.0` can be stored in a `vitti` because it represents an exact whole number in range. A fractional value cannot: Sutram stops instead of silently discarding the fraction. Try this separate program:

```sutram
mukhya() {
    dasham fraction = 3.7
    vitti whole = fraction
    likha(whole)
}
```

This program compiled, but when run it stopped with exit status 1 and printed:

```text
Sutram Error [E_DASHAM_VITTI]: dashama-phalam purnanka-seemayam na bhavati
```

The message tells you that the decimal result cannot be stored as a whole number. Keep the value in a `dasham` if you need the fraction. A written fractional literal can be diagnosed at compile time; a value calculated or held in a variable may be checked when the program runs. Non-finite and out-of-range values cannot be stored in `vitti` either.

## Page 2 — Very large results, `inf`, and `nan`

Scientific notation is a short way to write a large number. For example, `1.000000e+80` means approximately 1 times 10 to the power 80. Here the `e+80` is output notation. In v281, do not write `1e20` as a source literal; write the decimal value instead.

```sutram
mukhya() {
    dasham h = 100000000000000000000.0
    likha(h)
    h = h * h
    likha(h)
    h = h * h
    likha(h)
    h = h * h
    likha(h)
    h = h * h
    likha(h)
    dasham n = h - h
    likha(n)
    likha(h == h)
    likha(n == n)
    likha(n != n)
}
```

Output:

```text
1.000000e+20
1.000000e+40
1.000000e+80
1.000000e+160
inf
nan
1
0
1
```

After four squarings the finite result is too large for the `dasham` representation, so it prints `inf` (positive infinity). `inf - inf` produces `nan`, meaning “not a number”: the result is undefined, not a useful ordinary answer. Negative infinity prints `-inf`.

The last three lines are comparison results: `1` means true and `0` means false. Infinity equals itself; NaN does **not** equal itself, so `n == n` is false and `n != n` is true. Ordered comparisons involving NaN are false. Do not use `n == n` as a test that a value is an ordinary number. When `inf` or `nan` appears, revisit the calculation and its range. Division by zero is a separate rule: Sutram stops with `E_SHUNYA_BHAJAN`, rather than producing an infinity or NaN from that division.

## Page 3 — Allocation counts bytes; indexing counts cells

`nirmmita` asks for a number of **bytes**. In this example each `p[i]` selects an eight-byte cell, so two cells need 16 bytes. The first cell is index 0, and the second is index 1.

```sutram
mukhya() {
    vitti p = nirmmita(16)
    p[0] = 11
    p[1] = 22
    likha(p[0])
    likha(p[1])
}
```

Output:

```text
11
22
```

To hold three cells, request at least `nirmmita(24)`. What if we request only 16 bytes and try the third cell?

```sutram
mukhya() {
    vitti p = nirmmita(16)
    p[2] = 33
}
```

This was refused by the compiler, with exit status 1:

```text
Sutram Error [E_NIRMMITA_SEEMA]: pankti 3:8 - p[2] nirmmita(16) bahih
Sanket: nirmmita bhaita-sankhyam ganayati, p[i] ashta-bhaita-ekakaih: p[2] hetu nirmmita(24) avashyakam
```

The hint says that `p[2]` needs 24 bytes. The position in a diagnostic depends on the source layout. For this recognized pattern—a literal-sized allocation assigned to `p` and not reassigned—a computed index is checked at runtime: with `vitti i = 2` and `likha(p[i])`, the program compiled and then stopped with `Sutram Error: mala ank seema atikram` and exit status 1. **Do not assume this protection covers every pointer, alias, or allocation form.** For ordinary indexed collections, prefer `mala` when appropriate.

## Page 4 — `tak` includes the last number

`chakra i = 0 tak 3` visits 0, 1, 2, **and 3**. Both endpoints are included in this ascending example.

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

That is four iterations. If you have four cells numbered 0 through 3, those are their indices; index 4 is outside them. If your loop needs to stop before 3, use 2 as the last endpoint instead. Do not transfer assumptions about a different language's exclusive end to `tak`.

## README copy — ready to review

> Sutram is a programming language with Sanskrit keywords that compiles programs into native executables. Students can learn variables, arithmetic, conditions, loops, functions, and numeric lists using its documented subset. Whole numbers use `vitti`; `dasham` values are binary floating-point approximations. Integer calculations can wrap; large decimal calculations can produce `inf` or `nan`, and floating-point division by zero stops with an error. Some advanced memory features have limits: legacy `kosh` aliases can diverge when a buffer grows, and `mandapa` reclamation differs on Windows. Generics and threads are outside v1. The Windows installer and classroom package have not yet been accepted for release.

> `parikshita` is a tool that checks the compiler's documented function and call restrictions; the standard library is not yet marked, and it is not a whole-program safety guarantee.

This is the requested paragraph and line, proposed for the README, not a claim that the README was changed. I would not sign a release-ready claim until current-source installation and supported-platform gates have evidence. Sarvam reports a v281 suite of PASS=263, NO-EXPECTATION=4, 0 fail; I did not independently rerun that suite, and four cases without expectations are not four passing output checks.

## Decision — checked functions

Ship the scoped tool with the explicit library limitation, rather than automatically mark the 63 for v1.0 without the missing audit and compatibility checks. R163's measured Windows scratch experiment applied Muse R89's v280 candidate list to 63 declarations in 11 v281 modules: 24 of 24 import-and-print probes compiled in both variants and each output executable was byte-identical. Sequential compile sweeps took 0.810 s and 0.667 s; they are too noisy and limited to establish overhead. One checked `ank` call was refused before marking and compiled and ran after marking. These measurements do not establish the total cost of marking, safety of all bodies, runtime performance, separate compilation, or other platforms. A fresh v281 classification and full checked-call and platform regression are still needed.

What should a student do today? Put a small self-contained function and its caller under `parikshita`, use the permitted subset, and respond to the compiler's diagnostic if a call is not checked. For example:

```sutram
parikshita prakriya twice(x) {
    nivartanam x + x
}
parikshita mukhya() {
    likha(twice(3))
}
```

Observed output: `6` (compile and run exit 0). A checked function cannot simply call an unmarked library function; either keep the checked part self-contained or call the library from ordinary, unchecked code and understand that this boundary is outside the checked guarantee. Do not tell students to mark library functions themselves as a substitute for auditing them. The checker enforces its documented subset; it does not prove that the answer is mathematically correct or that the entire program is safe.

