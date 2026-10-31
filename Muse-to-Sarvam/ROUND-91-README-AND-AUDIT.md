# ROUND-91: the README sentence, and the last audit

Base: origin/main at v281 (compiler `Sutram 1.0 (v281)`),
tree reset before work. No tree changes. Deliverables in
`Muse-to-Sarvam/`: this report, `README-SENTENCE.txt`
(the sentence alone, one line, ready to paste above the
fold), and `r91_audit.json` (probe outcomes, library
counts, and link-audit results).

## WS1 — the sentence

> Still open, and stated plainly so you are not caught by them: a decimal number grown too large silently turns into infinity, and a loop whose end number is a decimal never stops — anything else that surprises you is worth reporting as a bug.

I would sign my name to it.

## WS2 — the release audit

### Q1. Is there any claim in `docs/LANGUAGE-REFERENCE.md` that is FALSE on v281?

Yes — three, in two places. The rest of the reference,
checked section by section, is correct on v281 (list
below). On the "three in R86": the printer and
`nirmmita` claims that were stale then are now correct
(§15 and §6c, both updated since); what is false now is
a different set, and it is in the parts of the page a
reader meets first.

**False 1 — the status block at the top of the page
(§1 header).** It reads "Status at v411, 29 October
2026", "Compiler v261", "Suite PASS=225", "library
proofs 226/226", "gates 48 PASS", and, two lines
below, "Compiler: v29 source line · Package: v35" and
"Generated from the compiler source and the language
packs, so it cannot drift from the code." On v281 the
compiler is v281, the suite is PASS=263 (verified in
R90 and again in this round's brief), and the library
is 306 functions (counted below). A status block dated
to v261 is not false as history — but presented at the
top of the reference, without a "historical" label, it
is what a reader takes as current, and it is wrong.
And the "cannot drift" sentence is disproved by the
page itself: the block has drifted, and so has §4b
below.

**False 2 — the same block's memory sentence.** " `nirmmita`
emits `mmap` per allocation on Linux" is false on v281.
Since Step 1 (v263) `nirmmita` is a bump allocator in
one reserved arena: the compiler source carries
`src/r65_arena.inc` ("the arena bump", "the bump
cursor (0 until the arena is reserved)") and grows a
`kosh` in place "when the `kosh` ends at the arena
cursor". One reservation, bumped within — not one
`mmap` per allocation. The second half of the sentence
("no `munmap` anywhere — nothing ever returns memory")
remains true.

**False 3 — §4b, the library table, in three ways.**
§4b says `lib/` ships "60 functions across six
modules" and lists them: ganit 15, ank 10, shreni 11,
ganita 6, madhava 5, varna 13. Counted on v281 (every
`prakriya` definition in `lib/*.smlib`): **306
functions across 24 modules** — ganit 18, ganita 23,
varna 27, shreni 14 (ank 10 and madhava 5 happen to be
right). §4b then says "a program can currently include
at most two modules — the inliner's buffer overflows at
three or more". Probed on v281, a program including
three modules (`yoj ganit`, `yoj ank`, `yoj madhava`)
compiles and prints `120`, `55`, `3.141593` — three
modules work, so the limit and its mechanism are both
wrong (the real limit is higher, a procedure-list cap
at around ten modules, not an inliner buffer at three).
§4b then says "Every library function copies its
parameters into locals before changing them, because
the compiler currently faults on assignment to a
parameter." Probed on v281, assigning to a parameter
works: `prakriya f(x) { x = x + 1; nivartanam x }`
called with 5 prints 6, exit 0. The reason is gone,
whatever the library's current style is.

**Checked and true on v281** (read section by section;
behavioral claims tested where they could be tested on
Linux, and the rest checked against the tree): §3a
integer edges (wrap, `E_ATIPRAVAH` on written
overflow, div/mod-zero stops — including that a
written integer `/ 0` is compile-refused, probed —,
`/` and `%` by −1, the −1/saturate library list); §4a
`likha`/`lkhb`/`likha_fmt` newline rules; §5 types
(including `vitti a[10]` as a `mala` declaration,
probed); §6 syntax; §6a `tak`/`arabhya … paryantam`
inclusive (both forms probed, 0–4); §6a-2 indentation
rules; §6c raw memory (constant-index compile refusal
and run-time bounds check, as corrected in R87); §7
command line (including `-i`, probed — the REPL
starts, compiles input, exits 0); §7b danda (probed);
§7c Devanagari (the section's own example, probed
with `--lang sanskrit`, prints 15); §15 floating
point (printer threshold at 2⁶³, `d.dddddde+N`,
`inf`/`-inf`/`nan`, division-by-zero stop, IEEE NaN
comparisons, and "the `E_DASHAM_VITTI` message does
not yet give the line" — still true on v281, probed);
§16 `kosh` (including aliasing: in-place growth only
without an intervening allocation, Windows always
moves, old buffer never freed, wrong value not a
crash); §17 function values, methods, slices (including
both refusals probed: slicing a `kosh dasham` gives
`vibhag: mala, kosh va vibhag apekshita`, returning a
slice gives `vibhag prakriyayah na pratyarpaniyah`);
§18 `siddhi`/`dosh`/`prasar`; §19 `mandapa`
(scratch contents, `E_SCRATCH_ESCAPE`, what it does
not see, `kosh` made inside the block); §20
`parikshita` (allowed/refused table, transitivity,
"63 of 306 could be marked, none marked yet" —
re-verified on v281 with the R82 marking tests:
`kramgun` and `madhava_atan` mark and run, `mala_yog`
refused for `pad8`); the string-variable section
(`likha` of a literal vs a variable, and the `s + "cd"`
address example). Windows-only claims (a growing
`kosh` always moving on Windows, the `.exe` target
name) were **not** verified here and are not counted
as false — they are unverified on Linux, as before.

**Two wording items, not headline falsehoods.**
(1) §16 says "the three that alias — 252, 255, 287 —
never grow it afterwards". The alias count is four
including 288, the section's own pinning example,
which aliases and grows deliberately; and 255 grows
via its alias (safely, in place). The core claim —
"nothing in the standard examples relies on a second
name after a move" — holds, but the parenthetical
should say four, including 288. (2) §3a's "Written as
`/ 0`, it is refused when compiled" is true for an
integer literal (probed, compile-refused with a
caret) but a written `dasham` division by `0.0`
compiles and stops at run time (probed in R89, same
message and exit 1). The outcome is the same; the
timing differs, and the row — which explicitly
includes the `dasham` case — should say so.
**One omission, not a falsehood:** §15 documents the
`vitti` and `kosh` conversion refusals but not the
v281 refusal for a non-whole `dasham` passed to an
untyped function parameter (probed in R90). It is
true as far as it goes; it does not go that far.

### Q2. Does any example produce output that contradicts the reference?

No, in the areas checked — and the check was
claim-driven, not a line-by-line reading of all 267
programs, which is stated here so the verdict is not
over-read. The suite passes 263/263 on v281 (4
no-expectation, 0 fail), so every example's actual
output matches its golden; the question is whether
any golden contradicts a reference statement, and for
each feature area where the reference makes a strong
claim the examples exercising it were checked:
conversion (93, 94, 112, 295, `r71/conversion`) all
match §15 (whole converts, fraction refuses);
division (293 refuses, 118 prints 2.0 on its own
inputs) matches §15; NaN (291, 294) matches the IEEE
paragraph; aliasing (252, 255, 287, 288) matches §16;
printer (289) matches §15; `parikshita` (282–285)
matches §20; `mandapa` (263–272) matches §19
(including the refusal examples, whose goldens are
the refusals §19 describes). Two further sweeps
found nothing: **no** example uses a decimal `tak`
bound (so no example runs away against §6a), and the
only `prati` in `examples/` is inside a comment and a
function name (`vartani_pratilip`, 256) about the
lexer reading a name that begins with the keyword —
not a legacy-`prati` program, and §2's "legacy alias"
statement is not contradicted by it (the alias itself
was probed in this round: a `prati` function prints
42). No example contradicts the reference.

### Q3. Is the `docs/` structure complete — does every file a reader needs exist, and does any link point at something that moved?

The files a reader needs exist: the reference,
`BUILDING.md`, `INSTALLATION-ROUTES.md`,
`WINDOWS-SETUP.md`, `CHANGELOG.md`, `MEMORY-MODEL.md`,
`NUMERIC-CONTRACT.md`, `OVERFLOW-SAFETY.md`,
`OPEN-ISSUES.md`, `WHATS-LEFT.md`, `SPECIFICATION.md`,
`LIBRARY-BOUNDARY.md`, `ERROR-CONVENTION.md`,
`SANDESH.md`, `sutram-philosophy.html` (the §13
pointer resolves), `WINDOWS-PORT-PLAN.md`, and the
nine `sutram-book*.html` teaching books.

**Links: no broken markdown link in `docs/*.md`.**
All 36 markdown links in `docs/` (including subdirs)
resolve when resolved relative to their own file's
directory. (Two apparent breaks in a first pass were
my own errors, corrected here: a `](x)` inside code
in §17 is not a link, and the negative-corpus link
resolves to `tests/negative/r70/manifest.json`,
which exists.) **But two mentions do point at files
that moved**, both in older docs rather than in the
reference: `docs/decisions/MEMORY-DECISION.md` cites
`docs/VOCABULARY-RULE.md`, now at
`docs/vocabulary/VOCABULARY-RULE.md`; and
`docs/rounds/CHANGELOG-ARCHIVE.md` cites
`docs/R68-INSTALLATION-ROUTES.md`, now
`docs/INSTALLATION-ROUTES.md`. Neither blocks a
reader of the reference, but both are links pointing
at moved files, as asked.

Three further structural notes. (1) The reference's
section numbers jump from §8 to §13 — there is no
§9–§12, no table of contents, and no cross-reference
to them, so nothing is broken, but a reader looking
for §9–§12 finds nothing and no explanation.
(2) The reference cites examples in two styles —
full paths (`examples/289_r87_float_print.sm`) and
bare numbers (`examples/288`). All seven bare-number
pointers resolve to an existing example by number,
but a reader copying `examples/288` as a path gets a
missing file; the style should be one or the other.
(3) The authoritative page is itself stale: the
reference (§1) says "The authoritative page is
`docs/WHATS-LEFT.md`. Where this page disagrees with
it, that page is right" — but `WHATS-LEFT.md` still
opens "Compiler v258 · changelog v404 · suite
PASS=225 · proofs 226/226 · gates 48", and its body
never mentions `parikshita`, conversion, NaN, or
division. A reader following the reference's own
pointer to the authoritative page gets numbers two
compiler versions old. The books, likewise, exist as
files but none of them mentions the scientific
format or `1.000000e` — they predate the v281 printer
documentation, a content gap rather than a missing
file.

### Verdict

The audit does **not** come back clean, so the
condition for "ready for the maintainer's Windows
test" is not met by this report alone. That is a
narrow verdict, and it should be read narrowly: the
language's behaviour sections (§3a–§20) are correct
on v281, and no example contradicts them — the
failures are the page's own header (§1), its library
section (§4b), and the currency of the page it calls
authoritative (`WHATS-LEFT.md`), plus two moved
mentions in older docs and three wording nits.
Fixing the §1 header (current version, suite, and
allocator sentence), rewriting §4b from the counted
library (306/24, three modules working, parameter
assignment working), and updating the `WHATS-LEFT.md`
header would make the reference clean on the evidence
of this audit. One note outside WS2's scope, because
it decides what a Windows test would actually test:
the checked-in installer is unchanged since R87
(same sha256, still the v243 package) — a maintainer
who installs from it tests v243, not v281.

## NOT RUN

Windows, browser, implementation. Windows-only
reference claims were left unverified rather than
counted false; the full 267-program line-by-line
comment audit was not done (claim-driven checks
instead, as stated in Q2); the §19 memory figures
(62 MB, 7.8 MB, 78 MB, 2 MB) are earlier measurements
and were not re-run on v281. Marking the 63, the
`tak`-bound refusal, an overflow message, and the
§1/§4b/`WHATS-LEFT.md` rewrites belong to the owners.
