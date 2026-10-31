# Sutram — ROUND-55: the English variables in `examples/`, counted and proposed — no file changes

**Base worked on:** `origin/main` at `06a0d6f8` (changelog v406, compiler v258 — the brief said
v404, main has moved on by two doc-sync commits since; the compiler is still v258, so the
measurement base is the same language). **Read first, as instructed:** `docs/WHATS-LEFT.md`
(C7: "~140 English variables", R55 is "table only, no changes") and `docs/vocabulary/VOCABULARY-TABLE.md`
(used for existing-word proposals, e.g. `suchi` for list, `aayam` for length).

**No file in the tree was changed in this round.** The deliverables are this report and the TSV
below it. Everything below is measured from `examples/*.sm` (top-level, 229 files), with the
method stated so Sarvam can re-run it and get the same numbers.

## WS1 — the real number, and why "~140" is not it

**Method (reproducible):** a variable is counted when it is *declared* — `vitti NAME`,
a typed declaration (`dasham NAME`, `satya NAME`, `kosh [dasham] NAME`, `mala NAME`),
a `prakriya` parameter, a `chakra NAME =` loop variable, or a `yadi dosh (NAME =` handler
variable — on one code line, with comments stripped, `yoj` import lines excluded, and one
count per declaration line (a parameter and a local with the same name in the same line are
counted once; that case does not occur in the tree). A name that is only *used* without a
declaration does not exist in Sutram (undefined name is a compile error), so declarations
are the complete set. Subdirectory examples (`examples/r67/`, `r68/`, `r71/`, 16 files)
add no new English distinct names — only `buf` (already counted) and single letters.

**The counts, in all three senses, so there is no ambiguity about what "~140" could mean:**

| Sense | Count |
|---|---|
| **Distinct English-named variables** | **108** |
| **English declarations** (a name declared in a file, per declaration line) | **176** |
| **English identifier uses** in code (comments and string literals stripped, every occurrence) | **774** |
| Files affected (of 229 top-level examples) | **67** |
| All distinct variable names, all languages | 186 (736 declarations) |
| Already Sanskrit distinct names | 11 (16 declarations) |
| Neutral distinct names (single letters + letter+number, see below) | 67 (544 declarations) |

**"About 140" matches none of these.** It sits between distinct names (108) and declarations
(176), which suggests the original grep counted something in between — for example, distinct
names plus a subset of redeclarations, or declarations in a subset of files. It is not
explained by subdirectories (0 new names), by full words only (57 distinct, 94 declarations),
or by lines containing an English variable (560 lines). If the owner wants 140 to be true,
the definition that produces it is not in the tree; the three numbers above are the ones
that are.

**Classification rules, stated so the owner can disagree with a boundary rather than a number:**
- **English** = a full English word, an English abbreviation (`arr`, `xs`, `tmp`, `cnt`),
  or a mixed name (`util_chinha` = English `util` + Sanskrit `chinha`). 108 names.
- **Sanskrit already** = `swa`, `tulana`, `anya_bindu`, `madhya`, `antim`, `mool`, `kramgun`,
  `varg`, `asti_abhajya`, `gun_maap`, `phal` (11 names, 16 declarations). `phal` is also a
  lib module name, but as a variable in `135_r30_float_index_scalar.sm` it is the Sanskrit
  word for result, and it is not a function name, so it is counted as already Sanskrit,
  not as a rename target.
- **Neutral** = single letters (`a`–`z`, 26 names) and letter+number (`f0`–`f39`, `v1`, `c0`).
  67 names, 544 declarations — the bulk is the capacity tests (`237_many_variables.sm`
  declares `f0`–`f39` by design, `204_b11_block_statement_capacity.sm` uses `h` hundreds
  of times). These are not English words, and renaming them to words would change what
  those tests are testing, so they are **not** in the TSV. If the owner wants single letters
  renamed too, that is a separate, much larger decision (544 declarations, and `i`, `x`,
  `n` are the working variables of almost every example).

**Most frequent English names (declarations, files):**
`values` 9/7, `sum` 9/9, `total` 7/7, `xs` 7/5, `st` 6/1, `arr` 5/3, `out` 4/4, `terms` 4/2,
`data` 3/3, `util_chinha` 3/3, `buf` 3/3, `flag` 3/2, then 17 names declared twice
(`lo`, `hi`, `nums`, `rem`, `root12`, `p3`, `term`, `row`, `op`, `rhs`, `cont`, `dx`, `dy`,
`secret`, `guess`, `count`, `whole`), then 79 names declared once. The full list, most frequent
first, is the TSV.

**One caveat on the count:** 5 of the 176 English declarations are in negative/capacity
examples where the variable name is incidental to the test — `values` in
`121_t18_kosh_param_push_reject.sm`, `total` in `223_undefined_name.sm`,
`225_undeclared_array.sm`, `227_assign_undeclared.sm`, and `raw` in
`120_t18_kosh_param_mismatch.sm`. Renaming them would not change those tests' outcomes
(they still fail for the same reason), but the owner may prefer to leave failure fixtures
untouched, as R54 left the pinned negative tests untouched. The TSV includes them with
their file names, so the owner can strike them.

## WS2 — the proposal table (TSV, 108 rows, 0 collisions)

**File:** `ROUND-55-VARIABLES.tsv`, columns `english | count | files | proposed | collides | notes`.
`count` is declarations, `files` is the example basenames (not paths), `collides` is checked
against **keywords + builtins + 305 library functions + 24 module names** (from
`lang/sanskrit.lang` second columns, `prakriya` names in `lib/*.smlib`, and `lib/` basenames).
Every proposal is `NO` — that is the point of the check, and it caught five real collisions
that a naive proposal would have made:

| English | Naive proposal | Why it collides | Proposal used instead |
|---|---|---|---|
| `rem` | `shesh` | `shesh` is a `sadhan` lib function | `avashesh` |
| `mn` (minimum) | `laghu` | `laghu` is a `shreni` lib function (and a local function in `82_b7_stack_spill.sm`) | `kanishth` |
| `mean` | `madhya` | `madhya` is a `sankhyiki` lib function | `madhyaman` |
| `mid` | `madhya` | same | `madhyank` |
| `doubled` | `dvigun` | `dvigun` is a `ganit` lib function | `dvigunit` (the `-it` form, as in R50 `mishr`/`mishrit`) |

Three more proposals were changed for module-name collisions (a variable named the same as
a module it would sit next to): `secret` → `gupt` (not `gudh`, the hash module),
`color` → `rang` (not `varna`, the string module), `base` → `ghat_aadhar` (not `aadhar`,
the base-conversion module). `parts` → `bhed` (not `khand`, the string module imported
by the same file, `215_r12_wordfreq.sm`).

**Rules followed, per the brief, with the hard cases noted:**
- **Complete word or compound, never a fragment:** `purna`, not `purn` — so `cnt` → `ganan`
  (not `cnt` → `gan`), `arr` → `ank_mala` (not `arr` → `mala`, which is also the array
  keyword), `tmp` → `asthayi` (not `tmp` → `asth`).
- **Existing words first:** `suchi` for lists (`xs` → `pratham_suchi`, `ys` →
  `dvitiya_suchi`, `scores` → `praptank_suchi`), `aayam` for lengths (`lens` →
  `aayam_suchi`, `tlen` → `paath_aayam`), `shakti` for power (`p3` → `tri_shakti`),
  `chinha` for the sign variable (`util_chinha` → `chinha`, dropping the English half).
- **Short:** most proposals are one or two words; the longest are `kotijya_yog` /
  `kotijya_pad` (cosine sum/term — `kotijya` is the Indian-maths word for cosine, and
  there is no shorter correct word) and `lekhan_koshtha` (write buffer).
- **Units are the honest exception:** `km`, `kg`, `miles`, `pounds` have no native
  Sanskrit word — they are SI/imperial units. The TSV proposes loanword transliterations
  (`kilomitar`, `kilogram`, `mail`, `paund`) and says so in the notes, so the owner can
  keep the unit symbols instead. Forcing a native word here would be invention, not
  translation.
- **Same proposal for the same meaning, in different files, is intentional:** `count` and
  `cnt` both → `ganan`, `offset` and `delta` both → `antar`, `sum` in one file and
  `total` in another stay distinct (`sankalan` vs `sarva_yog`) because the originals
  were distinct names in the same file (`217_r12_report.sm` uses both `sum` and `mean`,
  and `28_compound.sm` uses `total` where other files use `sum`).

**Not in the TSV, by design:** the 11 already-Sanskrit names, the 67 neutral names, and
function names (the 44 renames the brief mentions are already done — this round is
variables only, as briefed).

## WS3 — the short print form, and whether R52 left any triple

**Short form, as it stands now (top-level examples, `likha("label", value)`):**
**102 occurrences in 36 files.** R52 migrated 97 of those, in 34 files. The other
**5 occurrences, in 2 files, were already short before R52 and were not triples, so R52
correctly did not count them:**

| File | Occurrences | Evidence it predates R52 |
|---|---|---|
| `examples/43_nested_likha.sm` | 4 (`"2 + 3 = "`, `"7 * 6 = "`, `"5^2 = "`, `"nested = "`) | Present verbatim at the R52 base (`7f36172a`), in a file whose whole point is multi-argument `likha` (v29). This is the file ChatGPT found; Sarvam's "no example did" was wrong about this file, not about the form in general. |
| `examples/46_language_reference.sm` | 1 (`"x = "`, line 31, commented `# two-argument print`) | Present verbatim at the R52 base, with the comment naming the form. |

So the answer to "are there other examples already using the short form" is **yes — two
files, five uses, both pre-existing, both missed by the "no example did" claim, and both
already in the short form, so there is nothing to migrate in them.**

**Did R52 leave any three-statement triple that could be one line? No.**
Re-running the R52 triple detector on the current tree, with the R52 separator rule
(a first argument of `" "` or `"\n"` is a separator, not a label):

- **True labelled triples remaining: 0.** The 23 sequences that look like triples
  (`likha("\n"); likha(value); likha("\n")` in `20_pankti_array.sm`, `22_precedence.sm`,
  `61_stdlib_math.sm` (9), `62_stdlib_num.sm` (4), `63_stdlib_string.sm` (2),
  `83_stdlib_sort.sm` (2), `85_stdlib_shellsort.sm`, `216_r12_expr.sm` (3)) all have
  `"\n"` as the first argument — they are separator sequences, the same class R52
  deliberately skipped in 14 files. Migrating them as labels would be wrong: the first
  `"\n"` is not a label, it is the line break between values.
- **Separator pairs remaining: 28 in 9 files** (`likha(" ")` or `likha("\n")` followed by
  `likha(value)` in the stdlib/perf examples). These are value sequences formatted with
  spaces and newlines, not labelled prints, and R52 left them by design. They are listed
  here so they are not mistaken for missed triples.
- **A different pattern R52 did not scope, listed for the owner, not claimed as a miss:**
  **21 two-statement label+value pairs** that could become one line with **byte-identical
  output** (because `likha(value)` already adds the newline, and the next statement is
  not `likha("\n")`, so no blank line is involved): `11_forloop.sm:25` (`"3 x "`, `k`),
  `14_strings.sm:22` (`"Temperature: "`, `-15`), `16_advanced.sm:7` (`"Primes up to "`,
  `LIMIT`), `200_madhava_series.sm:27/40/52` (`"pi  = "`, `"sin(0.5) = "`,
  `"cos(0.5) = "`), `217_r12_report.sm:30/32/34/36/38` (`"Count: "`, `"\nSum:   "`,
  `"\nMean:  "`, `"\nMin:   "`, `"\nMax:   "`), `26_calculator.sm:16/18/20/23/25`
  (`"Sum: "`, `"\nDifference: "`, `"\nProduct: "`, `"\nQuotient: "`,
  `"\nRemainder: "`), `250_r26_dosh_handler.sm:38` (`"dosh "`, `x`),
  `91_indian_number_theory.sm:10/14/18` (three `"x = "` labels),
  `array_demo.sm:13` (`"  arr["`, `i`, a fragmented label). These are **not** triples —
  R52's scope was three statements, these are two — but if the owner wants the short
  form everywhere, these 21 are the next, safe, byte-identical batch. Excluded from
  that 21, deliberately: `152_namespaced_comment_string_preservation.sm:4`, whose first
  argument is a test-subject string, not a label, and `25_patterns.sm:12` (`" x "`),
  which is an operator separator in a table row, not a label.

**A stale claim carried forward, so it is not repeated:** `docs/WHATS-LEFT.md` still says
"R52 migrated 48 files, 405 lines -> 135" for the triples. The measured R52 result was
97 triples in 34 files (the 135 was the brief's naive count, corrected in the R52 report).
The 102 short-form uses now are 97 (R52) + 5 (pre-existing, above), not 135 + anything.

**Verification in this round (read-only, so the suite is untouched):** the counts were
re-derived from a clean `origin/main` checkout; the collision set was built from
`lang/sanskrit.lang` + `lib/*.smlib` + module names and checked for every one of the
108 proposals (0 collisions); the short-form count was checked against the R52 base
(`7f36172a`) to prove 43/46 predate R52; the triple detector was re-run on the current
tree and on the R52 base, with the same separator rule, and gives 0 labelled triples
in both. **NOT RUN:** Windows/WSL, as always. **No file changes, no goldens touched,
no suite run needed — and none claimed.**
