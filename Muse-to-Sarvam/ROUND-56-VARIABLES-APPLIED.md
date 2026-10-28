# Sutram — ROUND-56: the 108 English variables, applied

**Base worked on:** `origin/main` at `8236bdd4` (changelog v409, compiler v258 — the brief said
v408, main has moved by one issue commit since; the compiler is still v258). **Read first, as
instructed:** my own `ROUND-55-VARIABLES.tsv` (108 names, counted by my method). **This round
applies it, but not blindly — three corrections below change the TSV, and they are the
reason this round exists instead of a script run.**

**Deliverables, in order:**
- `ROUND-56-patchA.patch` (32,896 bytes): the 12 names declared 3+ times. Apply this alone
  and the suite still passes. This is the recommended patch.
- `ROUND-56-patchB.patch` (40,776 bytes): the 96 names declared 1–2 times, **plus the two
  R55 corrections**. Apply it **after** Patch A (it was generated against the Patch-A tree,
  so it will not apply cleanly on fresh HEAD). This is the churn set — see WS2, the owner
  decides whether to apply it.
- This report. **No file was changed on main directly; the patches are the change.**

## WS1 — batches, and every differ (there are none)

**Method, so the byte-identical claim can be checked:** for each file, only identifiers
declared as a variable in that file were renamed, only in code — never inside a string
literal, never inside a comment. That is what makes the output byte-identical: a variable
name never prints, **except** where the name also appears as an output label string
(`likha("is_ready = ", is_ready)`), and those strings were deliberately left alone (see
"Strings left alone" below). Renames were word-boundary and case-sensitive, so `sum` does
not touch `summary` (no such identifier exists, but the boundary is there), and a name
that is also a field (`p.score`) or a function (`mixed`) in a file was not touched,
because it was not declared as a variable there.

**Batches (about 20 names each, suite run after each, stop-on-differ rule applied):**

| Batch | Names | Files changed in batch | Lines changed in batch | Suite after batch |
|---|---|---|---|---|
| A — count 3+ | `values`, `sum`, `total`, `xs`, `st`, `arr`, `out`, `terms`, `data`, `util_chinha`, `buf`, `flag` (12) | 36 | 274 | PASS=225, 0 FAIL |
| B — count 2 | `lo`, `hi`, `nums`, `rem`, `root12`, `p3`, `term`, `row`, `op`, `rhs`, `cont`, `dx`, `dy`, `secret`, `guess`, `count`, `whole` (17) | 18 | 98 | PASS=225, 0 FAIL |
| C — count 1, part 1 | `asc`, `base`, `both_positive`, `calls`, `check`, `cnt`, `code`, `color`, `cs`, `ct`, `cur`, `day`, `delta`, `denom`, `desc`, `diff`, `doubled`, `empty`, `exp`, `flags` (20) | 15 | 51 | PASS=225, 0 FAIL |
| D — count 1, part 2 | `greeting`, `id`, `interest`, `is_done`, `is_ready`, `kg`, `km`, `lens`, `lower_a`, `mean`, `mid`, `miles`, `mixed` (variable in `92_t12_dasham_float.sm` only), `mn`, `mod3`, `mod5`, `msg`, `mx`, `name`, `neg` (20) | 11 | 51 | PASS=225, 0 FAIL |
| E — count 1, part 3 | `nseg`, `nuniq`, `offset`, `ok`, `once`, `pa`, `parts`, `pat`, `pb`, `pos`, `pounds`, `principal`, `prod`, `ptrs`, `quad`, `rate`, `raw`, `score`, `scores`, `spill` (20) | 13 | 72 | PASS=225, 0 FAIL |
| F — count 1, part 4 | `target`, `text`, `threshold`, `tl`, `tlen`, `tmp`, `tp`, `truth`, `two`, `ulens`, `upper_a`, `uptrs`, `wbuf`, `weight`, `wlen`, `wpos`, `year`, `yes`, `ys` (19) | 8 | 60 | PASS=225, 0 FAIL |
| Extra — R55 corrections | `values` in `122_t18_kosh_param_devanagari.sm`, `third` in `92_t12_dasham_float.sm` (see below) | 2 | 6 | PASS=225, 0 FAIL |

Batch line counts sum to 612, while the final diff is 556 lines — the difference is 56
lines that contain two renamed names (e.g. `vitti mean = sum / n` changed in Batch A
for `sum` and again in Batch D for `mean`), counted once per batch but once in the
final diff. Final diff: **68 files, 556 insertions, 556 deletions** — renames only, no
line added or removed, no golden touched.

**Every differ and why: none.** No batch produced a differ, so no batch was stopped.
The suite is **PASS=225, NO-EXPECTATION=4, 0 FAIL** after every batch, on Patch A alone,
and on Patch A + Patch B. Proofs on the full tree: **226/226**. Patch A + Patch B
applies cleanly in order on a fresh HEAD checkout and reproduces the working tree
byte-for-byte (verified, not assumed).

**Strings left alone, deliberately (so the byte-identical claim holds, and so the owner
can see what still prints in English):** output labels that match a variable name were
NOT renamed, because renaming them would change the golden. Examples: `17_booleans.sm`
still prints `"is_ready = "`, `"is_done = "`, `"both_positive = "` while the variables
are now `sajj`, `sampanna`, `ubhay_dhan`; `34_incdec.sm` still prints `"count = "`
while the variable is `ganan`; `array_demo.sm` still prints `"  arr["` while the
variable is `ank_mala`; `33_unit_conversion.sm` still prints `" km = "`, `" kg = "`,
`" miles"` (units, as they should be). This is not a miss — it is the byte-identical
rule applied correctly, and it is the reason WS3's answer is "yes, but" (below).

## WS2 — the three that need care, plus the corrections the TSV needed

**`xs` → `pratham_suchi` is wrong, and I did not apply it.** `pratham` means "first".
`xs` is a generic numeric list in 4 of its 5 files (`135_r30_float_index_scalar.sm`,
`144_xmm_cache_fallback.sm`, `148_stage2_array_mutation_call.sm`,
`206_sankhyiki.sm` — statistics data, not a first anything) and x-values only in
`208_kalana.sm`, where it is the independent variable, not "the first list".
**Applied instead: `xs` → `ank_suchi`** (number list — existing words, correct in all
5 files, including 208 where the list is numbers). **`ys` → `dvitiya_suchi` is wrong
for the same reason** (ys is not "second", it is the dependent values, `x * x`, in the
only file that uses it, 208). **Applied instead: `ys` → `phal_suchi`** (result list),
which is distinct from `ank_suchi` in the same scope in 208, which `pratham`/`dvitiya`
would also have been, but with the right sense.

**`st` → `avastha` — kept, as the brief says.** Parser state array (ptr, len, pos) in
`216_r12_expr.sm`; `avastha` = state/condition, and the note in the TSV was right.

**Count 1–2 names — listed separately, as the brief asks, and put in Patch B, not Patch A,
so the owner can skip them with one decision.** That is 96 names: Batch B (17 names,
count 2) + Batches C–F (79 names, count 1). Their files are listed at the end of this
report ("Files still English if Patch B is skipped"). If Patch B is skipped, 46 files
still contain English variable names; if it is applied, 0 files do (see "Skipped"
for the two non-variable exceptions).

**A correction to my own TSV, found by the post-rename verification (this is why the
verification step exists): `terms` → `pada` breaks `95_t12_madhava_functions.sm`.**
In that file, `terms` is a *count* parameter (`madhava_pi(terms)`, `madhava_sin(x, terms)`,
`madhava_cos(x, terms)` — the loop bound) and `term` is a *value* local
(`dasham term = 1.0 / ...` inside the loop). Renaming both to `pada` would put a
parameter and a local with the same name in the same function, shadowing the count
with the value. **Applied instead, per file:** `terms` in 95 → `pada_ganana` (term
count), `terms` in `205_madhava_pi_kosh.sm` (where it is a kosh *list* of terms) →
`pada_kosh`, `term` (value, in 95 and 200) → `pada`. All three are collision-free,
and the suite proves the semantics did not change.

**A correction to R55's count, also found by verification: R55 missed Devanagari-keyword
declarations, because its extractor only matched Latin keywords.** Two English
declarations were missed: `values` in `122_t18_kosh_param_devanagari.sm`
(`कोश दशम values[1]`) and `third` in `92_t12_dasham_float.sm`
(`दशम third = 0.1 + 0.2`). Both are renamed in Patch B (`values` → `mulya`, same as
the other `values`; `third` → `tritiya`, Sanskrit ordinal, collision-free). The
corrected R55 totals are therefore **109 distinct English names, 178 declarations**
(not 108 / 176). A full re-scan for non-Latin keyword declarations found no others:
the only other non-Latin declarations are single letters (`b`, `a`, `q`, `i` in
Devanagari/Hindi/Tamil files, neutral) and Devanagari variable names (`योग`, `इ` in
218, already Sanskrit).

**Longer names, per the added rule (if a suggested name is longer, say so and give the
shorter correct alternative — or say why there is none):** most proposals are longer
than the abbreviations they replace (`sum` 3 → `sankalan` 8, `xs` 2 → `ank_suchi` 9,
`st` 2 → `avastha` 7, `arr` 3 → `ank_mala` 8, `buf` 3 → `koshtha` 7). In each case the
shorter form was checked and rejected for a stated reason: `yog` (3) collides with
`shreni.yog`, `mala` alone is the array keyword, `sthan` (5) means place, not state,
`kosh` alone is a container type, not a buffer. Where a shorter correct form existed,
it was used (`util_chinha` 11 → `chinha` 6, `values` 6 → `mulya` 5, `both_positive`
13 → `ubhay_dhan` 10). No proposal was kept long when a shorter correct alternative
existed.

**Skipped, with reasons (not in either patch, and not counted as differs):**
- `score` as a *field* in `08_demo.sm` (`rachana Person = { age, score }`, `p.score`).
  Fields are not variables; R55 counted variables only, and renaming a field would
  change the rachana's public shape. Listed here so the owner can ask for a field
  round if they want it.
- `mixed` as a *function* in `93_t12_float_functions.sm` / `94_t12_float_functions.sm`
  (`prakriya mixed(dhvaj)` — the parameter was renamed, the function name was not).
  Function names were a previous round's scope, not this one.
- Strings and comments, everywhere, by design (see "Strings left alone" above).
- Negative/capacity examples were **not** skipped: `values` in
  `121_t18_kosh_param_push_reject.sm`, `total` in `223_undefined_name.sm`,
  `225_undeclared_array.sm`, `227_assign_undeclared.sm`, and `raw` in
  `120_t18_kosh_param_mismatch.sm` were renamed like any other variable. Their tests
  still fail for the same reason (suite PASS=225 includes them), because the rename
  does not change the failure — the undefined name, the undeclared array, and the
  param mismatch are all still there. If the owner prefers failure fixtures pristine,
  those 5 declarations are the ones to revert.

## WS3 — is it worth it? Plainly

**If the owner applies Patch A + Patch B, a beginner reading any example meets no
English variable name.** That is the round's job, and it is done — 0 English variable
names remain in `examples/*.sm` code, apart from the field and function above.

**If the owner applies Patch A only, 46 files still have English variables** (the
Patch-B files, listed below). Patch A covers the names a beginner actually meets
repeatedly (`sum`, `total`, `values`, `xs`, `arr`, `out`, `data`, `buf`, `flag` in
36 files), but it does not finish the job — a beginner reading `17_booleans.sm`
(`is_ready`, `is_done`, `both_positive`), `24_guess_game.sm` (`secret`, `guess`),
`32_bank_interest.sm` (`principal`, `rate`, `interest`), or `215_r12_wordfreq.sm`
(`text`, `parts`, `pos`, `tmp`, and the rest) still meets English variables, because
those are all count-1 names.

**But: a beginner reading `examples/01_hello.sm` meets no English word as a variable
either way — before this round, or after it.** `01_hello.sm` has no variables at all,
and the tutorial sequence `01`–`09` uses only single letters (`x`, `y`, `i`), which
were never English words. The English variables were never in the first files; they
were in the later, advanced examples. So this round does not change the beginner's
first reading — it changes the later reading.

**And: a beginner reading any example still meets English, full stop.** Comments in
most examples are English prose, and output strings are English (`"Sum: "`,
`"Temperature: "`, `"Guess the secret number"`, `" km = "`). Those were left alone
on purpose, to keep output byte-identical. If the owner's goal is "a beginner meets
no English word in the file at all", that is a different round — comments and output
strings, with golden changes — not this one, and this round does not claim it.

**My plain assessment:** Patch A is worth it — 12 names, 36 files, the names that
repeat. Patch B is worth it only if the goal is completeness ("no English variable
anywhere") rather than tutorial readability, because 96 names for 79 once-used
variables in 46 files, many of them test/perf files a beginner never reads first
(`215_r12_wordfreq.sm`, `217_r12_report.sm`, `115_perf_loop_bottom.sm`), is a
556-line diff for no behaviour change. It is mechanical, it is verified, and it is
reversible (Patch B is separate), so the cost is review time, not risk — but the
owner should decide that trade-off knowingly, which is why Patch B is separate.

## Files still English if Patch B is skipped (46 files)

`115_perf_loop_bottom.sm`, `118_t18_kosh_param.sm`, `120_t18_kosh_param_mismatch.sm`,
`12_elif.sm`, `133_perf_float_scalar_call_rhs.sm`, `135_r30_float_index_scalar.sm`,
`138_r30_float_comparison_index.sm`, `139_r30_float_mixed_fallback.sm`,
`13_negatives.sm`, `140_r30_index_side_effect.sm`, `15_sutra_const.sm`,
`16_advanced.sm`, `17_booleans.sm`, `18_guna_switch.sm`, `19_srijana_enum.sm`,
`200_madhava_series.sm`, `203_meru_with_kosh.sm`, `205_madhava_pi_kosh.sm`,
`208_kalana.sm`, `209_samanvaya.sm`, `20_pankti_array.sm`, `215_r12_wordfreq.sm`,
`216_r12_expr.sm`, `217_r12_report.sm`, `236_guna_once.sm`,
`246_r23_comparator_sort.sm`, `247_r23_methods.sm`, `24_guess_game.sm`,
`32_bank_interest.sm`, `33_unit_conversion.sm`, `34_incdec.sm`, `41_recursion.sm`,
`44_shabda.sm`, `46_language_reference.sm`, `78_do_while.sm`, `82_b7_stack_spill.sm`,
`88_pingala_chandas.sm`, `92_t12_dasham_float.sm`, `93_t12_float_functions.sm`,
`94_t12_float_functions.sm`, `95_t12_madhava_functions.sm`, `char_ops.sm`,
`fizzbuzz.sm`, `import_demo.sm`, `number_game.sm`, `prime.sm`.

**NOT RUN:** Windows/WSL, as always. **No goldens changed, no suite run claimed beyond
the ones above (PASS=225 after every batch, proofs 226/226 on the full tree).**
