# ROUND-92: the README sentence, corrected — and why not as the brief corrected it

Base: origin/main at v282 (commit `c6c572b8`,
compiler `Sutram 1.0 (v282)`), tree reset before work.
No tree changes. Deliverables in `Muse-to-Sarvam/`:
this report, `README-SENTENCE.txt` (the corrected
sentence alone, one line, ready to paste), and
`r92_loop_table.json` (the WS3 table in machine form
plus the WS2 census counts).

## WS1 — the corrected sentence

> Still open, and stated plainly so you are not caught by them: a decimal number grown too large silently turns into infinity, and a loop that counts up to a decimal never stops — anything else that surprises you is worth reporting as a bug.

Also in `README-SENTENCE.txt`, alone, one line.

## A note on the brief's verified behaviour — it does not reproduce on main v282

This has to come before WS2 and WS3, because it
changes what the corrected clause can honestly say.
The brief reports, run on v282: `chakra i = 0 tak 3.0`
gives `0 1 2 3 4`, and `dasham d = 3.0; chakra i = 0
tak d` gives the same — "it stops, one iteration
late". On main v282 as committed, and as freshly
built from source, neither does. Measured here, with
`likha(i)` in the body, both run away: `tak 3.0`
printed 447,475 lines in 2 seconds under timeout
(rc=124, last line 447474) and `tak d` (3.0) printed
432,256 lines in 2 seconds, same timeout. With an
empty body and a `likha("done")` after the loop,
`done` never prints (rc=124, 0 lines) — the loop does
not stop at 4, it does not reach the statement after
it. With an indented `mukhya` instead of a braced
one, `tak 3.0` printed 476,549 lines in 2 seconds.
With a freshly built compiler from `src/`
(`nasm -f elf64`, `ld`, reports v282), `tak 3.0` and
`tak d` (3.0) run away identically (432,939 and
446,093 lines in 2 seconds). So the committed binary
is not stale, and the form of `mukhya` is not the
difference.

I therefore did **not** adopt the "one iteration
late" wording. On the evidence of main v282 it would
replace one false clause with another for the normal
ascending case. What was wrong with the R91 clause
was its scope, not its verb: it said "a loop whose
end number is a decimal never stops", without saying
"counts up". Descending cases do stop (by never
running, see WS3), so the blanket version overstates.
The correction in WS1 scopes it to counting up,
where "never stops" is what was measured in every
tested form. If the brief's `0..4` run used a
different binary, flag, or body, send that exact
program and I will re-run it exactly — on main v282
as it stands, the cases above run away.

One part of the brief's correction is right, and it
is confirmed here: the v437 "hang" was an invalid
syntax. `chakra vitti i = 0 tak 3` and `chakra
dasham i = 0.0 tak 3.0` are both compile-refused on
v282 (`Sutram Error: vyakaran dosh, pankti 2:12,
shabd 'vitti'` / `'dasham'`, no binary). A test
written that way prints nothing because it never
compiles — not because the loop hangs. The valid
syntax (no type prefix in the `chakra` header) is a
different question, and its answer is the table
below.

## WS2 — census: does any program in the tree have a `dasham` loop bound?

**Zero.** That is the answer, and it makes this a
documentation error, not a library bug.

Method: every `chakra … tak …` and `chakra …
arabhya … paryantam` loop in `examples/` (recursive)
and `lib/` was listed and its bound classified by
hand after a script pass — 51 loops total, all in
examples, none in the library (the only `chakra`
hits in `lib/` are the substring in `chakravala`, a
function name). Every bound is an integer: integer
literals (the large majority, e.g. `tak 5`, `tak 10`,
`tak 40`), integer variables (`tak n`, `tak lo`,
`tak hi`, `tak i` where `i` is an outer integer
counter), one integer constant (`tak LIMIT` where
`sutra LIMIT = 10` in 16_advanced), and three
`pankti_len(s) - 1` bounds (246, 248) where
`pankti_len` is an integer length — and those
programs pass the suite on v282, so they terminate
in practice. Zero `dasham` literals as bounds, zero
`dasham` variables as bounds, zero `dasham` counter
starts. A strict search for `tak <digits>.<digits>`
across `examples/`, `lib/`, and `tests/` returns
nothing (the one loose hit is comment prose, "tak
0..9", not a loop). The suite on v282 is
`PASS=267, NO-EXPECTATION=4, 0 fail`, including the
three new R94 examples (297, 298, 299).

So no program in the tree relies on `dasham`-bound
behaviour, and no program is currently running one
iteration too many — or running away — because of a
`dasham` bound. No program relies on the descending
`dasham` behaviour either, since every descending
loop in the tree (`36_descending`, `115`, `46`, and
others) has an integer bound and behaves correctly.
When the loop fix lands (Claude R96), nothing in the
tree needs to change for it.

## WS3 — loop forms against bound types, on v282

A table of outputs, as asked. Every run used the
committed v282 compiler unless noted; runaway cases
were run under `timeout 2` with stdout to a file,
so the line counts below are "lines in 2 seconds"
(rc=124), not full outputs. All other cases exited
normally (rc=0). `likha(i)` is the body in every
`chakra` row; `yavat` rows use `likha(i); i = i + 1`.

| loop | bound / form | observed on v282 |
|---|---|---|
| `chakra i = 0 tak 3` | integer literal, ascending | `0 1 2 3`, stops |
| `chakra i = 0 tak 3.0` | `dasham` literal (whole), ascending | runs away: 447,475 lines in 2 s, timeout; `done` after the loop never prints |
| `chakra i = 0 tak 3.5` | `dasham` literal (not whole), ascending | runs away: 472,567 lines in 2 s, timeout |
| `chakra i = 0 tak n`, `n = 3` | `vitti` variable, ascending | `0 1 2 3`, stops |
| `chakra i = 0 tak d`, `d = 3.0` | `dasham` variable (whole), ascending | runs away: 432,256 lines in 2 s, timeout |
| `chakra i = 0 tak d`, `d = 3.5` | `dasham` variable (not whole), ascending | runs away: 466,788 lines in 2 s, timeout |
| `chakra i = 0.0 tak 3` | `dasham` counter start, integer bound, ascending | `0 1 2 3`, stops (prints as integers, not `0.000000`) |
| `chakra i = 0.0 tak 3.0` | `dasham` start, `dasham` bound, ascending | runs away: 412,828 lines in 2 s, timeout |
| `chakra i = 0.0 tak 3.5` | `dasham` start, `dasham` bound, ascending | runs away: 474,645 lines in 2 s, timeout |
| `chakra i = 0.0 tak n`, `n = 3` | `dasham` start, `vitti` bound, ascending | `0 1 2 3`, stops |
| `chakra i = 0.0 tak d`, `d = 3.0` | `dasham` start, `dasham` bound, ascending | runs away: 416,642 lines in 2 s, timeout |
| `chakra i = 0.0 tak d`, `d = 3.5` | `dasham` start, `dasham` bound, ascending | runs away: 387,362 lines in 2 s, timeout |
| `chakra i = 3 tak 0` | integer, descending | `3 2 1 0`, stops |
| `chakra i = 3 tak 0.0` | integer start, `dasham` bound, descending | zero iterations, exits normally (0 lines) |
| `chakra i = 3.0 tak 0` | `dasham` start, integer bound, descending | zero iterations, exits normally (0 lines) |
| `chakra i = 3.0 tak 0.0` | both `dasham`, descending | zero iterations, exits normally (0 lines) |
| `chakra i = 5 tak 3` | integer, start past the bound | `5 4 3`, stops |
| `chakra i = 5 tak 3.0` | integer start, `dasham` bound, start past it | counts up forever: `5 6 7 …`, 486,487 lines in 2 s, timeout |
| `chakra i = 3 tak 1.0` | integer start, `dasham` bound, start past it | counts up forever: `3 4 5 …`, 443,179 lines in 2 s, timeout |
| `chakra i = 1 tak 0.0` | integer start, `dasham` bound zero, start past it | zero iterations, exits normally (0 lines) |
| `chakra i = 0 arabhya 3 paryantam` | integer, ascending | `0 1 2 3`, stops |
| `chakra i = 0 arabhya 3.0 paryantam` | `dasham`, ascending | runs away: 425,601 lines in 2 s, timeout |
| `chakra i = 0 arabhya d paryantam`, `d = 3.0` | `dasham` variable, ascending | runs away: 431,659 lines in 2 s, timeout |
| `chakra i = 0.0 arabhya 3 paryantam` | `dasham` start, integer bound, ascending | `0 1 2 3`, stops |
| `chakra i = 3 arabhya 0 paryantam` | integer, descending | `3 2 1 0`, stops |
| `yavat (i < 3.0)`, `i` from 0 | `dasham` comparison, not a `tak` bound | `0 1 2`, stops |
| `yavat (i < d)`, `d = 3.0` | `dasham` variable comparison | `0 1 2`, stops |
| `chakra vitti i = 0 tak 3` | invalid syntax | compile refused: `vyakaran dosh, pankti 2:12, shabd 'vitti'`, no binary |
| `chakra dasham i = 0.0 tak 3.0` | invalid syntax | compile refused: `vyakaran dosh, pankti 2:12, shabd 'dasham'`, no binary |

Read the table as three robust findings, not as a
mechanism (the mechanism was not determined here,
and the fix belongs to the owner, Claude R96):
first, counting up to a `dasham` end — `tak` or
`arabhya`, literal or variable, whole or not — never
stops on v282, which is exactly the WS1 clause as
corrected; second, integer bounds always behave
(ascending inclusive, descending inclusive, start
past the bound descending inclusive); third,
`dasham` in a descending or start-past position
behaves inconsistently (zero iterations when the
bound is `0.0` or the start is `dasham` with an
integer bound of 0, counting up forever when the
bound is a non-zero `dasham` and the start is past
it) — the table gives each case, and no single
"one extra" sentence covers them. The `yavat` rows
matter for the fix: a `dasham` comparison in a
`yavat` condition works correctly, so the defect is
specific to `chakra` bound handling, not to
`dasham` comparison generally. Windows behaviour
was not tested here — ChatGPT's Windows sweep is
the second source, as the brief says, and if Windows
gives `0..4` for the ascending `dasham` case, that
would itself be a Linux/Windows divergence worth
reporting back, because Linux v282 as committed and
as freshly built gives runaway.

## NOT RUN

Windows, browser, implementation. The loop
mechanism (why a `dasham` bound runs away ascending
and gives zero or counts up in the other positions)
was not traced in the compiler source; the fix,
including any decision about what a `dasham` bound
should mean, belongs to the owner. The corrected
sentence is the only README change proposed here.
