# ROUND-84: the assumptions page, finished and verified

Base: origin/main at v278 (compiler `Sutram 1.0 (v278)`), tree reset
to `07d1f23b` before work. No tree changes. Deliverables in
`Muse-to-Sarvam/`: this report, `R84-REFERENCE-SECTION-ASSUMPTIONS.md`
(the section, in the reference's voice), and `r84_misread.json`
(the WS3 audit data: file → traps).

## WS1 — the section, and the fifth

`R84-REFERENCE-SECTION-ASSUMPTIONS.md` is the R83 page rewritten
as what the reference needs: a section a student finds before
they are confused. Each entry gives the assumption, what Sutram
actually does, and one line of code showing the difference.

**The fifth is string ordering: `"b" < "a"` is true.** A Python
student assumes strings compare lexicographically; Sutram
compares addresses. Verified twice, with the contents swapped to
prove the mechanism: `s = "b", t = "a"` gives `s < t` true, and
`s = "a", t = "b"` gives `s < t` true as well — the order is
declaration order, not alphabetical order. The reference says
nothing about string ordering (0 hits), so this is genuinely new,
not a restatement of the R83 page's string-`==` item (equality
and ordering are different operators, and a student who learned
"`==` compares addresses" would not necessarily guess that `<`
does too).

Two more new findings came out of the same hunt and are in the
section's second half:

- **The loop variable does not survive the loop.** `likha(i)`
  after a `chakra` loop is a compile error (`'i' … not visible
  outside`). A Python student assumes it leaks with the last
  value; it does not. Not stated in the reference.
- **A `tak` loop counts down.** `chakra j = 5 tak 1` runs
  5, 4, 3, 2, 1. This one is already stated (reference line 317,
  with the ascending example beside it), so it is marked STATED
  in the section rather than claimed as new.

Checked and *not* the fifth (so Sarvam does not re-derive them):
mixed integer/`dasham` division promotes correctly (`7 / 2.0`
and `7.0 / 2` are both 3.5); `yadi (2)` is true and `yadi (0)` is
false (non-zero is true, as in C and Python). Neither differs
from what a competent programmer assumes.

## WS2 — verification: 19/19, nothing wrong

Every line of the section was run on v278 (19 cases: the 18
entries plus the braced-`mukhya` control for the trailing-
statement entry). **All 19 pass; no line was wrong, so no wording
was adjusted to match a guess.** The full results:

- `tak` 0–3, `nirmmita(64)` + `p[7] = 42`, division `-7/2 = -3`
  and `-7%2 = -1`, the alias obstacle case 41/99, string `<`
  true for `"b" < "a"`, string `==` false for two `"hello"`
  variables, `akshar` 104/101, `dasham` div-zero (`1.0/0.0 > 0`
  true, `0.0/0.0 == 0` true), uninitialized `vitti` 0/99/0 across
  two calls, trailing indented statements 7 then 8, `kosh ==`
  false for identical contents, descending `5 tak 1` — all print
  exactly as the section says.
- Assignment-as-expression, `vitti` as a parameter type,
  `kosh_push` on a parameter, trailing statements after a braced
  `mukhya`, and `likha(i)` after the loop — all refused at
  compile time, as the section says.
- `k[-1]` stops with `mala ank seema atikram`, exit 1, as the
  section says.
- `likha(k)` prints an address (134907625996304 on this run, not
  the contents 10/20), as the section says.

One harness note, owned: the first verification run reported 9
"failures" that were my expected strings, not the language —
`likha(x)` followed by `likha("\n")` prints two newlines, not
one, because a numeric `likha` already appends LF. The values
were right in every case; the expectations were corrected and
the run is 19/19.

## WS3 — the number for the release notes: 28 of 259

**28 of the 259 examples in `examples/` would a Python-or-C
student misread on the first attempt** — read correctly, in the
sense of parsing the code, and get the wrong answer. Denominator
confirmed: `examples/*.sm` is exactly 259 files, matching the
brief.

### Rule (so the number can be checked)

A file counts if it contains at least one *wrong-answer* trap: a
construct whose Sutram semantics differ from Python-or-C
intuition in a way that changes the output. Compile-error and
fault traps are excluded — they give no answer, not a wrong one
(so assignment-not-expression, `vitti` parameters,
`kosh_push` on a parameter, negative indices, and loop scope
do not count here, even though they are on the page). Traps
counted: `tak` loops (Python-exclusive intuition), integer
division/modulo with a literal negative operand, string `==`,
string indexing, `kosh` aliasing, `likha` of a string/`kosh`
variable, `kosh ==`, string ordering, uninitialized-`vitti`
reads, and descending `tak` loops. The audit data
(`r84_misread.json`) maps each counted file to its traps.

### Breakdown

- `tak` loops: **25** files. The most frequent trap by far.
- `kosh` aliasing: **3** files (252, 255, 287 — the census sites).
- Everything else: **0** files. No example compares strings or
  `kosh` with `==`, indexes a string variable, prints a
  string/`kosh` variable with `likha`, divides an integer by a
  literal negative, orders strings, or reads an uninitialized
  `vitti`.

Three false-positive rounds were caught and fixed before the
count, and are recorded here so the number is not taken on
trust: (1) an uninitialized-`vitti` check that matched every
`vitti x = …` declaration (a regex backtrack let the lookahead
pass on the space before `=`); (2) two "negative division"
hits that were `dasham` series with subtractions, not integer
division; (3) four "likha of a variable" hits that were `kosh`
values passed to a function *inside* `likha(...)`, not printed
by it, and two "string ordering" hits that were `>` characters
inside string literals (`"x += 50 -> "`).

Two `tak` files were excluded by hand after reading them:
21 (`1 tak 20` with a break at `i > 10`) and 239 (`0 tak 3`
with a break at `i == 2`) — in both, the break fires before
the endpoint under either model, so inclusive and exclusive
readings give the same output. Every other `tak` file's loop
runs to its endpoint (or counts down), where the models differ.

### The three most likely

1. **11_forloop** — the canonical first loop a student meets.
   It is a `tak` loop; a Python student reads it as `range`
   and gets one iteration too few.
2. **36_descending** — the sharpest single case. A Python
   student reads `5 tak 1` as `range(5, 1)` and predicts
   *nothing* runs; Sutram counts down 5, 4, 3, 2, 1.
3. **255_r42_alias_kosh_push** — the one grow site. A C student
   reads `w = v` as a copy and predicts the push through `w`
   leaves `v` alone; a Python student reads it as an alias and
   gets the no-relocation case right but would miss the
   relocation twist. Its comment explains the alias, so a
   careful reader is warned; a skimmer is not. Excluding the
   three commented probe files, the unwarned count is 25.

## NOT RUN

Windows, browser, implementation. The verification is Linux
only (v278 ELF build). The WS3 count is a static-text count over
the tree as it stands, with the rule and the exclusions above;
it is not a study of actual students.
