# Sutram — ROUND-102: the generator on v287 — zero new traps, the reference-type rule, the census (seventh run), and the count (now 283)

**Base:** `origin/main` at `dc09dc02` (compiler v287).
**Deliver into:** `Muse-to-Sarvam/`. **No tree changes by this round,
and no implementation** — the likha-on-strings fix is the next
change, not mine. Everything below was verified by running on v287
(and, where stated, on v286 for the before/after comparison).

## Where the project is (premise notes)

v287 is Claude's R105: `==`, `!=`, `<`, `<=`, `>`, `>=` compare text;
`+` makes a new string; `likha` with three values prints three
values; the raw write is `dvaram_likha`. Suite 279, guard 689
programs 0 DIFFER, gates 59 PASS / 1 FAIL (installer v243 vs v287) —
cited from the brief, not re-measured. **Examples are 283, not 277:**
v287 added six string examples (306–311). Sarvam's verified lines
were all confirmed (see WS1), and the likha-address defect was
confirmed exactly as stated.

## WS1 — the generator on v287: traps now, fixed by v287, new from the fix

**The generator, extended (delivered).** `trap_matrix_v2.py` now
covers 6 kinds (int, dasham, string, kosh, mala, rachana) × 11 ops
(`==`, `!=`, `<`, `<=`, `>`, `>=`, `+`, `-`, `*`, `/`, `%`) = **396
cells** (114 refused, 0 crash in-matrix). Its first run is
`trap_matrix_v2.json`; `compare_matrices.py` reproduces the
v286→v287 comparison below from the two matrix JSONs.

### How many traps it finds now

- **In the 112 comparable cells (v1 subset): 35 silent-wrong — and
  every one involves kosh** (int×kosh, dasham×kosh, kosh×int,
  kosh×dasham, kosh×kosh, 7 each). String cells are gone from this
  list entirely.
- **In the new coverage (284 cells): 196 silent-wrong candidate
  cells**, overwhelmingly mala/rachana/kosh × everything (the
  reference-type rule, WS2) plus the new ordering/modulo ops on
  composites. Same caveat as R101: candidates, not verdicts — each
  needs a use-case check, and only string+int has a documented
  idiom.
- **Beyond the matrix (targeted probes, because the matrix covers
  one-step locals only):** param+param still address-adds
  (`128434208505856`), param==param still address-compares (`0`),
  slice+literal and buffer+literal still address-add (below), and
  `likha` on a string value still prints its address (below).

### How many were fixed by v287

- **26 cells: silent-wrong → refused.** Every string-involved
  cross-type arithmetic/ordering cell (int×string, dasham×string,
  string×int `*`/`/`, string×dasham, string×string `-`/`*`/`/`,
  string×kosh, kosh×string, for `<`, `-`, `*`, `/`) now refuses
  instead of computing address garbage.
- **3 cells: refused → correct.** string==string and string!=string
  now compare contents (0/1 correctly for "ab"/"cd"), and
  string+string now concats (fresh string; content verified
  separately — 307's `u == "rama sita"` → 1 — because `likha` of a
  concat result prints its address, so the matrix alone cannot show
  concat content).
- **String ordering, mechanism-fixed.** The matrix's "ab"/"cd" pair
  cannot show this delta (pool order happened to agree with content
  order for that pair on v286), so it is proven the honest way:
  R100's trap #2 ("b" < "a" → 1 by pool address) is reversed by
  309 (apple < banana, "ab" < "abc" prefix-first, all correct on
  v287).
- **Trap #1 (R100) mostly fixed.** String-string `-`/`*`/`/`/`%`
  refuse (`E_VARTANI_GANIT`, 311); string-int `*`/`/`/`%` refuse;
  **string-int `-` stays pointer arithmetic by design** (the slice
  idiom: `s - 1` → `4194459`, a pointer back).
- **The 310 analysis generalizes.** A mixed-use variable (string
  then number) refuses for `+` too, not just `==`
  (`E_VARTANI_CAT` on `s + "cd"` after `s = 5`).
- **Literal-anchoring (beyond locals).** A parameter compared or
  concatenated with a literal now works by contents:
  param==literal → `1`, param+literal → `"ab!"`. The fix reaches
  further than FIXALL's tracked locals did.

### How many are new, because the fix introduced them — zero in the matrix, and none in the probes either

**In the 112 comparable cells: NEW = 0.** No cell regressed from
correct or refused on v286 to silent-wrong on v287. Every cell
either improved (29 cells: 26 → refused, 3 → correct/concat) or
stayed the same (35 kosh cells still silent-wrong, the rest
unchanged correct/refused/by-design).

**The suspicious shapes were each checked against v286, and none
regressed:**

- **Slice+literal → address arithmetic, then segfault at `shabda`.**
  `sl = s + 2; u = sl + "!"; shabda(u)` segfaults (139) on v287 —
  but the `+` produces the **identical garbage pointer on v286
  (`8388957` on both)**, so the downstream crash is the same shape
  on both versions, not a v287 regression. The gap is precise: a
  pointer-arithmetic *result* loses string-ness, so the literal
  does not anchor it — while a plain parameter *is* anchored
  (above). This is remaining, not new. (`shabda(sl)` alone prints
  "cdef" correctly; tracked-var + literal prints "abcdef!"
  correctly.)
- **Param+param → address arithmetic.** Unchanged from v286 (R100
  verified it on the patched compiler). Remaining, not new.
- **Buffer+literal → address arithmetic.** A `nirmmita` buffer plus
  a literal produces a garbage pointer landing on zeros (`akshar`
  reads 0, 0; `shabda` prints empty) — a buffer pointer is not a
  tracked string, so the literal does not anchor it. Same class as
  slice+literal. Remaining, not new (buffers were never tracked
  strings).
- **`likha` on a string value → address. Pre-existing, not new.**
  Verified on v286 with a likha-only probe: `likha(s)` printed
  `4194461` there too, and the literal printed as text — the same
  defect, before the string fix. It is newly *prominent* (concat
  results now flow into `likha`), but the fix did not create it.
- **`+` allocation is persistent, not a wrong-answer trap.** 307's
  header documents it: the new string "lives as long as the
  program, like a nirmmita outside a mandapa." Values are correct;
  the consequence is growth: `+` in a loop grows without bound,
  and — unlike `nirmmita` in a `mandapa` — a `+` result is **not**
  freed at block end. That is a lifetime fact the docs must state,
  not a silent wrong answer (and see WS3's census blind spot).

**One correction to my own R100 report, because v286 evidence
overturns it.** R100 said a literal operand still refuses untracked
shapes under FIXALL. It does not, for `+`: slice+literal
address-adds on v286 (verified, same value as v287). The FIXALL
check fires on *tracked* string variables, not on bare literals;
v287's literal-anchoring supersedes this for unknowns (params) but
not for known-pointers (slices, buffers). The residual class as it
stood on v286 was wider than R100 stated; v287 narrowed it for
unknowns and left it for known-pointers.

**The observed dispatch tables on v287 (probed, not inferred):**

- `+`: (known-string, known-string) → fresh string; (known-string,
  int) → pointer arithmetic; (known-string, dasham) → refused;
  (known-string, unknown) → concat, literal anchors;
  (unknown, unknown) → address arithmetic; (known-pointer, string)
  → address arithmetic; (mixed-use var, anything) → refused.
- `==`: (known-string, known-string) → contents; (known-string,
  unknown) → contents, literal anchors; (unknown, unknown) →
  address compare; (unknown, known-number) → refused
  (`E_VARTANI_TUL`); (mixed-use var, anything) → refused.

## WS2 — reference types beyond strings: the generator covers them now, and the tree has zero

**Yes, extended:** v2 adds mala and rachana kinds (rachana values
are `nirmmita` pointers with field offsets, per 06's
`rachana Point = { x, y, z }` + `p.x = 10` shape). The rule is
confirmed across all three composite kinds:

| comparison | v287 result | meaning |
|---|---|---|
| mala == mala (both `[7]`) | `0` | addresses differ; contents identical |
| mala + mala | `248681383067696` | address sum |
| rachana == rachana (identical fields) | `0` | addresses differ; fields identical |
| rachana + rachana | `263843729113120` | address sum |
| kosh == kosh (both `[7]`) | `0` | addresses differ (the 35 remaining cells) |
| kosh − kosh | `67108864` | exactly `R101A_REGION` — region addresses |

Mala behavior is unchanged by v287 (verified on v286: `0` and an
address sum, same shape) — the string fix did not touch composites.

**How many examples compare two kosh, two mala, or two rachana?
Zero.** A scan of all 277→283 examples (composite var declarations
→ `==`/`!=`/ordering lines with two composite vars, indexed uses
excluded) returns nothing. The reference-type trap is real in the
matrix and absent from the tree — the same shape as R101's string
answer. (Element comparisons like 299's `k[1] != k[1]` are numeric
element comparisons, not composite comparisons, and are unaffected.)

## WS3 — census seventh run: same-method counts unchanged; the likha population is zero

| # | question | examples | lib | total | moved? |
|---|---|---|---|---|---|
| 1 | allocate inside a loop | 6 | 0 | **6** | no (same method) |
| 2 | grow a `kosh` more than 1,000 times | 0 definite, 1 potential | 0 | **0 definite, 1 potential** | no |
| 3 | allocate without a `mandapa` block at all | 57 | 26 | **83** | no |

Denominators: **283 examples, 306 lib functions, 589 combined.**
Method: R96 scripts re-run against a pristine worktree of this base;
flags differ from R101 only by the six added examples (306–311),
none of which uses `nirmmita`, declares a `kosh`, or pushes one.

**One method blind spot, stated because v287 created it.** 307's
loop does `s = s + "ab"` per pass — a fresh persistent string per
pass, i.e. allocation in a loop — but the textual method counts
only `nirmmita`/`kosh_decl` flags, so it does **not** see
`+`-allocation. Same-method Q1 is 6; a method extended with a
concat-in-loop flag would give **7** (6 + 307). 307 is currently
the only loop-concat in the tree, and its loop is bounded (3
passes) — but an unbounded loop-concat would grow without bound
even inside a `mandapa` (WS1's lifetime fact). The census method
needs a `+` flag from v287 on.

**How many examples pass a string to `likha`? Zero values — so the
next change alters zero examples.** Refined scan (bare string-var
args, string-expression args, plus gap checks for params and
call-results): **no example passes a string value (variable,
parameter, or call result) to `likha`.** The gap checks confirm the
apparent hits are not strings: 260's param `c` is an int counter,
60's params are numbers, 80/89's param `a` is indexed (array/kosh),
82's param goes to numeric functions, and 307's string-returning
`abhivadan` goes to `shabda`, not `likha`. **110 examples pass
string literals to `likha`** (headers, labels) — but literals
already print as text, so the likha fix does not alter them either.
The tree worked around the defect by convention: `shabda` for
string values, `likha` for numbers and labels. The defect is real
(Sarvam's probe, confirmed above) and its tree population is zero.

## WS4 — the count, prominently: 283, from this command

**In a checkout:** `ls examples/*.sm | wc -l`.
**At a commit:** `git ls-tree --name-only <commit> -- examples/ |
grep -c '\.sm$'`.
**Definition:** top-level `examples/*.sm` only (recursive on v287
is 299 = 283 + the 16 round-harness files in `examples/r67`,
`examples/r68`, `examples/r71`).

R101's 277 was correct at v286. It moved because v287 added six
examples (306–311) — the rule proving itself again: **never copy a
denominator from an old report; count at the base commit.** There
is still no file that states the count authoritatively (root cause,
unchanged); the closest file is the latest `r*_census.json`
denominators field — this round's says 283 — but it is a receipt,
not the authority, and it goes stale at the next example-adding
commit. The command above is the authority.

## What this round did NOT do (NOT RUN)

Windows (PE aliasing, installer rebuild, wizard), browser,
implementation (no likha fix built — that is the next change),
native-speaker review. The full suite, proofs, gates, and guard
were not re-run: no `src/`/`lib/`/`examples/`/`tests/` file changed
in this round, and the brief's suite/guard/gate numbers (279, 689
0 DIFFER, 59 PASS / 1 FAIL / 1 NOT-RUN) are cited, not re-measured.
RSS measurement of `+` loop growth was not attempted (the
persistent-lifetime claim is from 307's header and correct values,
not from RSS).

## Deliverables

- `Muse-to-Sarvam/ROUND-102-GENERATOR-V287-REFERENCE-CENSUS-COUNT.md`
  (this report)
- `Muse-to-Sarvam/r102_census.json` (WS1 matrix comparison + dispatch
  tables, WS2 composite table + example count, WS3 counts + likha
  population, WS4 count history and command)
- `Muse-to-Sarvam/trap_matrix_v2.py` (the extended generator: run
  as `python3 trap_matrix_v2.py [compiler]`, default
  `./sutram_compiler`; writes `trap_matrix_v2.json` beside itself)
- `Muse-to-Sarvam/trap_matrix_v2.json` (the generator's first run
  on v287: all 396 cells)
- `Muse-to-Sarvam/compare_matrices.py` (reproduces the
  v286→v287 fixed/remaining/new counts from the two matrix JSONs)

Work staged in `~/workspace/r102/` (scripts in `ws1/`/`ws2/`,
probes in `ws1probes/`, worktrees in `tree/` (v287) and `v286tree`
(v286, for before/after checks) — read-only, removed after
delivery).
