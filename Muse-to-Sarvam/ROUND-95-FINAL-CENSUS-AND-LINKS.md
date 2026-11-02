# ROUND-95: the final census, the link audit, and the sentence

Base: main at v283. The census work ran on HEAD
`fdaa5cd9`; main has since moved to `d0a295fc`
(Claude R100), which adds only
`Claude-to-Sarvam/` files — no change under `src/`,
`lib/`, `examples/`, `tests/`, `docs/`, or the HTML
set — so all three counts below stand on the new
HEAD as well. No tree changes. Deliverables in
`Muse-to-Sarvam/`: this report and `r95_census.json`.
`README-SENTENCE.txt` is
deliberately NOT overwritten in this delivery — see
the sentence section, which answers the brief's
"change it back" directly. (The Round 94
confirmation files remain staged separately and
are not part of this delivery.)

## The sentence: what "change it back" does and does not require

The loop clause was accurate, and the overrides
were wrong — that is settled, and CORRECTION-3 and
R94 already record it. But the sentence's version
history matters for what "change it back" can mean
on v283:

- R91 (v281): "...a loop whose end number is a
  decimal never stops..."
- R92 (v282): "...a loop that counts up to a
  decimal never stops..." — this was NOT a change
  to the false wording. Sarvam's instruction in
  R92 was "one iteration late"; I refused it with
  measurements (runaway, hundreds of thousands of
  lines, timeout) and kept "never stops", scoping
  it to counting up because descending decimal
  cases stop immediately by skipping (R92 table).
  The scoped version is more precise, not less
  true.
- R93 (v283): "...a decimal number grown too
  large silently turns into infinity..." (loop
  clause dropped) — not because the clause was
  wrong, but because v283 refuses decimal loops
  with `E_CHAKRA_DASHAM`. A student who tries one
  on v283 gets a compile error, not a hang.

Restoring the R91 wording verbatim into the
README sentence on v283 would therefore mislead
exactly the student the sentence is for: they
would expect a runaway and get a refusal. So the
sentence is NOT changed back to the R91 wording
here. What stands is: the loop clause stands as
the correct v282 record (R92 scoped version,
preserved in the R92/R93/R94 reports, not erased),
and the current sentence for v283 remains the
R93 inf-only sentence (inf overflow verified
still silent on v283 in R93). Re-verified this
round on a fresh v282 build (commit 93c6d384):
`chakra i = 0 tak 3.0` printed 676,802 lines in
3 s under timeout (exit 124), counting up
without stopping — consistent with Claude's
5,375,137 lines and R93's 644k–697k in 2 s.
The runaway is not a measurement dispute; it is
the v282 behavior. If Sarvam means by
"change it back" that the false wordings must not
stand, they already do not — no delivered sentence
ever contained "one extra" or "unpredictable".

## WS1 — the three numbers

Denominator first, because the brief says 267 and
the tree says otherwise: **274 examples**
(`examples/*.sm` on v283) = **270 with goldens**
(200 exit-0 + 70 exit-1 refusal, all matching) +
**4 NO-EXPECTATION** (215, 216, 217, 219).
Sarvam's 267 is the pre-300-302 PASS count, not
the current total. Counts below are out of 274;
the PASS-subset counts are identical wherever
stated, because the 4 no-expectation files hit
none of the three categories. Method throughout,
as asked: script, then read every candidate by
hand, then run the decisive cases. Suite on v283
re-verified: `PASS=270, NO-EXPECTATION=4, 0 fail`;
proofs `229/229` and `86/86` (matching R98).

### 1. Programs that can produce a wrong answer by any arithmetic path: 1 — and 0 user-facing

The one, under a literal reading of the definition
(silent mathematically incorrect output, no error,
on its own inputs):

- **280 (`280_r80_runtime_wraps`)** — prints
  `x * x = -2446744073709551616` (true product
  16×10¹⁸, wrapped), `m / d =
  -9223372036854775808` (true quotient 2⁶³,
  wrapped to MIN), and `kramgun(21) = -1` (true
  21! = 51090942171709440000; −1 is the sentinel,
  printed as the value), exit 0, no error. Its
  header states the rules it demonstrates
  ("Past the range, + - * wrap around silently
  (as in C)") and it prints the checked form
  alongside (`ok[0] = 0`, "it does not fit").

280 is a deliberate demonstration, the same kind
as the inf/nan fixtures below. If the
demonstrate-by-design carve-out is extended to
it — as it must be to be consistent — then
**the user-facing count is 0: no example
program that purports to compute a true answer
silently gives a wrong one.** Both numbers are
given so the headline can be framed either way
without hiding 280.

Every other arithmetic class: 0.

- Integer overflow, runtime: only 280. Constant
  overflow refuses (278 literal → `E_ATIPRAVAH`,
  279 product → `E_ATIPRAVAH`). Tier-1/Tier-2
  library functions are called by examples only
  with small inputs (verified call by call,
  including 282's LCG, whose worst product
  2,369,780,942,852,710,860 < 2⁶³, no wrap).
- Dasham overflow to inf/nan, accidental: 0.
  Deliberate fixtures only: 289, 291, 294 (named
  in the brief) plus 299 (same kind, not named
  there — inf/nan through `kosh dasham`, a
  function, and `mandapa` blocks, every
  comparison IEEE-correct). 296's `1e20 → 1e40 →
  1e80` stays finite and prints in the documented
  scientific format. All match goldens, exit 0.
- Division/modulo by zero: 0 wrong. Every divisor
  is non-zero on its inputs, or the program
  refuses (`E_SHUNYA_BHAJAN`; decimal `%` and
  bit ops refuse `E_DASHAM_KRIYA`, golden 298).
- Conversion, silent: 0. Whole values convert
  (93/94 `blend(1.0, 3.0) = 2.0 → 2`; 112, 295);
  fractions refuse (`E_DASHAM_VITTI`, goldens
  290/112/295). Dasham → `mala` element stores:
  0 in examples (R90's count still holds).
- Saturating functions printed as true values:
  0. No example reaches saturation, so none
  prints MAX as a result or checks-or-fails-to-
  check one.
- Decimal loop bounds: 0 wrong on v283 —
  refused (`E_CHAKRA_DASHAM`, goldens 300/301).
- String/kosh address operations: 0 example
  hits. No string-variable `+`, no string `==`/`<`,
  no `kosh ==` in any example; the R84/R85
  address findings remain probe-only.
- Printer rounding (not counted, per definition):
  one hit, 296 prints `tiny = 0.000000` for
  `0.0000001` — the documented 6-decimal fixed
  format (§15), not an arithmetic error.
- Integer truncation: defined semantics, not
  wrong answers (verified: 32, 33, 249, 216, 217).

### 2. Programs that can fail to terminate: 0

- The full suite ran to completion in ~4 s on
  v283; a hanging example would have stalled it.
- The known hang class is closed: decimal
  `chakra` bounds refuse on v283 (`tak 3.0` and
  `arabhya 3.0` re-probed; goldens 300/301).
- Every `yavat` condition in examples is a
  bounded counter, a shrinking interval, or a
  consuming parser position (including dasham
  `yavat (x <= 3.0)` in 302, which terminates —
  the correct decimal-loop form).
- Every recursive function is base-cased with
  small inputs (41, 46, 145, 147, 248).
- Every kosh growth loop is bounded (205, 209,
  299, 203/286, 257). All 70 refusal goldens
  terminate with exit 1 and a message.

### 3. Examples a student would misread on the first attempt: 0 — under the reference-reader definition; 30 under the R84/R86 definition

This number depends on what "misread" means, so
both are given, with the definition stated:

- **(a) Reference-reader: 0 of 274 (0 of 270
  PASS).** A student who HAS read the reference
  (knows `tak`/`arabhya` are inclusive, knows
  aliasing exists, knows `string ==` and `kosh ==`
  compare addresses, knows dasham overflow goes
  to `inf`) would still mispredict an example
  only if it relies on a subtlety the reference
  does NOT state. 36 candidate families were
  hand-read against the current reference: every
  former trap is now documented (`tak` §6a with
  exact stdout `0..4`; alias §16; saturation
  §3a; printer §15; truncation §3a; div-zero
  §3a/§15; NaN §15; float conversion §15;
  string-variable printing §4a and the "READ
  THIS" section) or fixed in the compiler (float
  truncation now refuses) or absent from examples
  (string `==`/ordering/indexing, `kosh ==`,
  `likha(kosh)`, dasham→`mala` stores, uninit
  reads, e-notation literals, param shadowing).
  The one remaining undocumented subtlety —
  alias length freezing at alias time without a
  move (R83's refinement; §16 states freeze
  after a *move*) — appears in NO example
  (252/287 have no post-alias growth, 255 grows
  via the alias, 288 is the move case). Measured
  zero, not forced zero.
- **(b) R84/R86 definition: 30 of 274 (30 of
  270 PASS).** This counts a file if it contains
  a construct whose Sutram semantics differ from
  Python/C intuition, regardless of documentation:
  `tak` 26 + kosh alias 4 (252, 255, 287, 288) +
  computed-float-into-`vitti` 0 = 30. Delta from
  R86's 31/262: +1 `tak` (302, new) − 2 float
  (93/94 now whole values, `blend(1.0, 3.0) =
  2.0`, commented "2.5 would stop (v281)",
  probed exit 0 printing `whole = 2`) = 30;
  denominator +12 (291–302). Footnotes: under a
  strict output-difference reading of (b), `tak`
  is 22 and the total 26; excluding fault-only
  alias files as well gives 24. The primary (b)
  number 30 follows R86's counting as R86
  applied it, for comparability.

### The release statement — and what it does not override

On the tree, the qualified statement Sarvam
asked for holds: **no example program that
purports to compute a true answer silently gives
a wrong one; no example fails to terminate; no
example misleads a student who has read the
reference** (with the 280 footnote above, and
with 30 under the older, broader misread
definition). That statement is about the tree.
It does NOT override Claude R100's verdict NO,
and the two are compatible: R100's blockers are
(1) the installer shipping v243, and (2) four
user-program traps — `likha(a, " ", b)` printing
nothing, string `==`, string `+` on variables,
uninitialised `vitti` reading a leftover — none
of which occurs in any tree example (0 hits in
this census), so they do not change the three
numbers above, but they still block shipping to
students until they are refused or fixed, as
R100 orders them. Two R100-adjacent notes from
this round: (i) string `+` on variables IS
demonstrated in the reference (the "READ THIS"
section shows `s = s + "cd"` printing an address
number), though the two-variable form is not
spelled out separately — no example does it, so
census impact zero; (ii) R100's "2⁶³ literal is
read 2048 too high" was probed here in the two
natural forms and does NOT reproduce on v283
(`0 - 9223372036854775808` prints exact MIN;
bare `9223372036854775808` refuses
`E_ATIPRAVAH`) — if a specific reproducing
program exists, send it, as with the loop
corrections. Also noted: R100's uninit shape
(conditional assignment across calls, reading
`0 99 99`) contradicts R82's "zeroed locals"
note for that shape — locals are not reliably
zeroed; no example reads uninitialised (scan
0), so tree impact zero, but the reference gap
remains.

## WS2 — link audit: 0 broken

Scope as asked: every `.md` at the root, every
file in `docs/`, and the HTML reports. **123
files scanned** (6 root `.md` + 90 `docs/` `.md`
+ 27 HTML), **233 links checked, 0 broken**
(218 resolving + 15 external, not fetched: 2
Unicode data files, 13 Google Fonts stylesheets).
Moved-but-resolving: 0. Three links already
point at the R95 new paths and resolve
(`PROJECT-MASTER.md` → `docs/rounds/PROJECT-
OVERVIEW.md`; `ROADMAP.md` →
`docs/rounds/ROADMAP-TO-V1.0.md` and
`docs/rounds/PLAN-TO-FINISH.md`). The R91 moved
mentions are prose (backticked), not links, and
their targets exist at the new paths
(`docs/vocabulary/VOCABULARY-RULE.md`,
`docs/INSTALLATION-ROUTES.md`). One candidate
was found and disproved by hand: `README.md` →
`docs/LANGUAGE-REFERENCE.md#two-names-for-one-
kosh-vitti-a--k-is-not-a-copy-v278` — the
heading exists (line 736), and GitHub's slugger
keeps code-span content with one hyphen per
space, giving the double hyphen `vitti-a--k`;
a checker that collapses spaces falsely reports
it broken. Method: fenced code blocks stripped
and inline code spans masked before extraction
(killing R95's five `f](x)`-style false hits
and R91's `](x)`-in-code false positive);
anchors checked against GitHub-style slugs for
`.md` and `id=`/`name=` for HTML; coverage
sanity (raw `](` count equals extracted link
count, zero mismatches). External URLs were
counted, not fetched, and are not reported
broken.

## NOT RUN

Windows, browser, implementation. Windows
execution of any example, the installer rebuild
at v283, and the R100 user-trap refusals were
not done here. Guard (680 programs, 0 DIFFER)
and gates are cited from R98/R100, not re-run.
Library function-level behaviour beyond example
calls was not re-audited (Tier-2 int64 wraps
remain in the library as known limitations, but
no example program triggers them).
