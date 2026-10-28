# ROUND-51 — the writing style, from the codebase side

Base: origin/main at aaaa6655 (v393; ROUND-51 issued in c4577906, compiler v254).
Read first, as instructed: LANGUAGE-PRIORITY.md, docs/LANGUAGE-REFERENCE.md, docs/OPEN-ISSUES.md.
No tree changes. Every number below was counted on this main, not copied from the brief.
Where the brief's premise does not match the tree, the count is given and the premise is
corrected — that is the codebase answer, not a disagreement about taste.

## Counts

- Examples: 245 files, 5421 lines. Library: 24 modules, 305 functions.
- Three-statement print pattern, any string / value / newline triple:
  135 triples in 48 example files. With `=` in the label: 66 triples in 25 files.
  `likha("\n")` alone: 174 lines in examples. So 135 triples = 405 lines that could be 135.
- `vitti` declarations: 362 code lines in 120 example files; 1077 code lines in lib.
- `prati 0`: 9 lines in examples, 0 of them as a mukhya trailer.
  Mukhya files: 232 in examples, 226 in tests/stdlib — 0 end with `prati 0` before the closing brace.
- Counted loops: `chakra` (the counted loop, see P2) 49 lines in examples;
  `yavat` (while) 62 lines. Manual counted loop (`vitti i = 0` + `yavat (i <` + `i = i + 1`):
  21 example files.
- `likha(` lines in examples: 1261. `likha_fmt(` lines: in examples/format_demo.sm,
  examples/multable.sm, examples/full_demo.sm only.
- Library formatting: `roop_` has 23 functions, all buffer-out, none print.
  No variadic print exists in `roop_`. The closest library answer is `likha_fmt`
  (2 arguments: format string, one value), and it still needs a second statement for the newline.
- Output-parameter functions in lib: 74 take an `out` buffer. See P7.

## P1 — printing a labelled value

Before, today (examples/02_arith.sm:6-8, the pattern in 48 files):

```sutram
likha("x + y = ")
likha(z)
likha("\n")
```

After, already in the compiler, measured on this main:

```sutram
likha("x + y = ", z)
```

Measured: `likha("x = ", x)` prints `x = 42` plus a newline; the same form works
for `dasham` (`d = 2.500000`) and for an expression (`sum = 50`). One statement,
one line of output.

- Reason: one line of output should cost one statement.
- Size: small — in fact none. No compiler change: the 2-argument `likha` already
  exists (arity table 1-3 in src/sutram_compiler.asm). What is missing is documentation,
  not code. `likha_fmt` is not the answer: it still needs `likha("\n")` as a second statement.
- Breaks existing programs: no. The 3-statement form still compiles; migration is optional.
  Do not use the 3-argument form: measured on this main, `likha("y = ", x, "\n")`
  prints only `42`, not the label — 3-argument `likha` behaviour is inconsistent and
  should be fixed or forbidden separately, not relied on for style.
- If migrated, this changes the most existing code of any of the six: 135 triples in
  48 files. That is a reason to document the 1-statement form first and migrate
  examples gradually, not a reason to change the compiler.

## P2 — a counted loop

Before, today (the manual form, 21 example files):

```sutram
vitti i = 0
yavat (i < 10) {
    likha(i)
    i = i + 1
}
```

After, already in the language (examples/11_forloop.sm, docs/LANGUAGE-REFERENCE.md:193):

```sutram
chakra i = 0 tak 10 {
    likha(i)
}
```

Note the semantics, because they are not C's: `tak` is inclusive. `chakra i = 0 tak 10`
gives 0 through 10, 11 values. `chakra i = 0 tak 5` in examples/11_forloop.sm prints
0, 1, 2, 3, 4, 5 and the sum 1 tak 10 is 55. So "for i from 0 to 10" in Sutram is
exactly `chakra i = 0 tak 10`, and a programmer coming from C must be told it is
inclusive, or they will be off by one in the other direction.

- Reason: a counted loop should not require manual init and increment, which is where
  off-by-one and infinite loops come from.
- Size: small — in fact none. `chakra` already exists, with ascending and descending
  forms (`chakra j = 5 tak 1`) and `agrim` (continue) / `krama` (break) inside it.
  Migrating the 21 manual loops is optional.
- Breaks existing programs: no. `yavat` remains the while loop; nothing changes.

## P3 — declaring a variable

Before, today, and after: the same code. Leave it as it is.

```sutram
vitti x = 5
```

- Reason: making `vitti` optional would turn a typo into a new variable and lose
  the `E_UNDEFINED_NAME` safety net that currently catches it — measured:
  `x = 42` without a declaration fails with `Sutram Error [E_UNDEFINED_NAME]`
  and a hint suggesting `vitti x = ...`. Explicit declaration is the safety net.
- Size: none. No change.
- Breaks existing programs: no, because nothing changes.
- The narrower meaning already exists: `vitti` is the general declaration,
  `anka x = 5` / `sankhya x = 5` / `dasham x = 2.5` are the typed ones
  (docs/LANGUAGE-REFERENCE.md:169). `vitti` does not need to mean something
  narrower; it already sits beside narrower words. Changing 362 example lines
  and 1077 lib lines to save one word per declaration would buy brevity at the
  cost of the only declaration check the language has.

## P4 — returning from a function

Before, as the brief describes it: every `mukhya` ends with `prati 0`. That is not
true on this main, and the correction matters more than the proposal.

Measured: 232 mukhya files in examples and 226 in tests/stdlib, 0 ending with
`prati 0`. The 9 `prati 0` lines in examples are function returns (a status value,
e.g. examples/248_r23_slices.sm:18, `bhar` returning 0), not mukhya trailers.
A `mukhya` with no `prati` already compiles and exits 0 (measured on this main),
and `prati dosh(c)` in `mukhya` already exits with code c (R25).

After: the same code as today, without a trailer.

```sutram
mukhya() {
    likha("hi")
    likha("\n")
}
```

- Reason: the end of a program should not require a meaningless return value, and
  it already does not.
- Size: none. No change.
- Breaks existing programs: no, because nothing changes. Do not add a rule
  requiring `prati 0` in `mukhya`, and do not remove the 9 function-level `prati 0`
  lines — those mean something (a status return), unlike the imagined trailer.

## P5 — an error a beginner can act on

Before, today, measured on this main (without `yoj brihat`):

```
Sutram Error: agyat prakriya: brihat_yuj
```

After, the message as it should be printed (Sanskrit, in the existing error style,
with the fix named):

```
Sutram Error: agyat prakriya: brihat_yuj
Sanket: brihat_yuj brihat-pustake asti; yoj brihat likha
```

In words: the function exists in the brihat module; write `yoj brihat`.

- Reason: the beginner's actual mistake is a missing `yoj`, not a misspelled name,
  and the message should name the fix, not just the failure.
- Size: small. One correction to the brief's premise: the compiler does NOT
  already know, at backpatch time, which unimported module defines the name
  (R48: `func_table` holds only expanded imports; unimported lib files are never
  read, and the error is raised in `backpatch_calls`). The small fix is to scan
  `lib/*.smlib` for `prakriya <name>` on the error path only — no cost on a
  successful compile, no runtime, no new tool, and the compiler already reads
  lib files for `yoj`, so the scan reuses that path.
- Breaks existing programs: no for compiling programs. For error goldens: only
  one golden expects this exact text (tests/expect/69_undefined_function.out,
  for `does_not_exist`), and that name is in no module, so no suggestion line
  would be added and that golden stays unchanged. The suggestion line is added
  only when a module is actually found.

## P6 — the speakable test

Before, today:

```sutram
mukhya() {
    vitti x = 5
    yadi (x > 3) {
        likha(x)
    }
}
```

After, as a sentence (hypothetical, not proposed for adoption):

```sutram
mukhya() {
    vitti x = 5
    yadi x 3 se adhik {
        likha x
    }
}
```

Can the second one be read aloud as a sentence? As a list of Sanskrit words, yes.
As natural Sanskrit prose, no. The keywords are already Sanskrit — `mukhya`,
`vitti`, `yadi`, `likha` — so reading today's program aloud in Sanskrit already
gives a sequence of Sanskrit words with symbols. Natural prose would need a
second grammar: no parentheses (measured: `yadi x > 3` without parentheses
fails with a grammar error today), no braces, verb-final word order, and case
markers like `se` as syntax. That is a different language sharing a compiler,
not a style for this one, and it would hide exactly what the current syntax
makes explicit: scope (braces) and grouping (parentheses).

- Reason: code is read by eyes, not ears, and the current keywords already speak Sanskrit.
- Size: large if adopted (a second parser and grammar), none if left as it is (recommended).
- Breaks existing programs: no if left as it is. A prose grammar as an addition
  would not break existing programs either, but it would create two languages
  in one compiler, which is worse than the problem it solves.
- Verdict: leave it as it is. Speakability is already present at the word level;
  prose-level speakability is not a goal worth a second language.

## P7 — the seventh problem: returning a non-scalar result

This pattern appears 74 times in lib and nobody in the style discussion has named it:
a function that must return a value that is not a scalar cannot return it, so it
writes into a caller-allocated buffer and returns a count.

Before, today (tests/stdlib/fmt_min.sm, the usual form):

```sutram
vitti out = nirmmita(70 * 8)
vitti n = roop_ank_aadhar(255, 16, 0, out)
likha(n)
```

That is only the count. To see the formatted value, the test then loops over the
bytes with `akshar(out, i)` — or, shorter and already available, uses the fact
that `roop_` functions NUL-terminate their output:

After, the shortest correct form today (measured: prints `2` then `ff`):

```sutram
vitti out = nirmmita(70 * 8)
vitti n = roop_ank_aadhar(255, 16, 0, out)
shabda(out)
```

- Reason: the out-buffer pattern is the language's answer to "no runtime, no
  garbage collector, no hidden allocation" — the caller owns the buffer, the
  function writes into it, and nothing is allocated behind the programmer's back.
  That is a feature of the constraints, not a style failure.
- Size: none. Returning a string or array from a function would need ownership
  and lifetime rules, which is exactly the runtime machinery the hard rules forbid.
- Breaks existing programs: no, because nothing changes. Document `shabda(out)`
  as the print idiom for `roop_` output instead of the `akshar` loop; that alone
  removes the longest form of this pattern from tests without changing any function.

## Which first, and which changes the most existing code

Do P5 first. It is the only one of the six that helps a programmer at the exact
moment they are stuck, it is small (error path only), it breaks nothing
(including the one error golden, by design), and it uses the existing Sanskrit
error style. Do P1 second: it is documentation only, no compiler change, and it
is the one migration that actually reduces example code (135 triples in 48 files).

Which changes the most existing code, if migrated rather than just added:
P1, 48 files and 405 lines, followed by P2, 21 manual-loop files. P3 would
change 362 example lines and 1077 lib lines if `vitti` were made optional, which
is one more reason to leave it. P4 changes 0 files (no mukhya ends with `prati 0`).
P6, if prose were adopted, would change every program — which is why it is rejected.
P5 changes 0 working programs. P7 changes 0 functions; only its documentation changes.
