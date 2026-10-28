# Sutram — ROUND-52: the examples teach the wrong form, and it is fixable without the compiler

**Base worked on:** `origin/main` at `7f36172a` (changelog v398, compiler v256, after the R53 compiler
change; the R52 brief was written against v394, but no R52-relevant tree change landed between v394 and
v398 except the R53 compiler work, which does not touch examples or lib text). **Delivered as a patch
plus this report, NOT applied to main.** Apply in order: `ROUND-52.patch`, then the R53 patches.
Verified: all three patches apply cleanly in order to a fresh `HEAD` checkout and reproduce this
round's tree byte-for-byte (diff empty, excluding the committed compiler binary).

**Headline, with a correction to the brief:** the brief's "135 triples" is a naive count. On this main
the true labelled-print triples are **97, in 34 files — all 97 migrated, 0 remain.** The naive count
inflates by counting `likha("\n")` and `likha(" ")` separator lines as labels (see "Skipped" below).
And the migration is NOT byte-identical against the old golden, for a reason the brief missed:
`likha(x)` already prints a newline, so the triple `likha("x = ") / likha(x) / likha("\n")` prints
`x = 42` followed by a *blank* line, while `likha("x = ", x)` prints `x = 42` with one newline.
Every migrated file was checked: the ONLY output difference against its old golden is exactly the
blank lines the redundant third statement produced (multiplied when the triple sits in a loop).
No label, value, or other output changed in any file. Goldens were therefore updated to remove
exactly those blank lines (32 golden files, 112 blank lines), and the suite is green against the
new goldens. Files where any other difference had appeared would have been reverted; none did.

## WS1 — migrate the triples

**Rule used:** a triple is `likha("<label>") / likha(<value>) or lkhb(<value>) / likha("\n")` on three
consecutive lines, where `<label>` contains a real label (at least one non-space, non-newline
character). Middle values accepted: variables (59 in the naive count), calls, expressions, literals
and indices — all measured to work in the 2-argument form in R51 and re-verified here by running
every migrated file. No middle value was a string variable, and no `lkhb` triple printed a float.

**Files changed (34), triples per file — 97 total, 194 lines removed from examples:**

- examples/02_arith.sm: 1
- examples/05_func_params.sm: 2
- examples/06_rachana.sm: 3
- examples/07_module.sm: 1
- examples/08_demo.sm: 4
- examples/10_mathlib.sm: 4
- examples/11_forloop.sm: 2
- examples/13_negatives.sm: 8
- examples/14_strings.sm: 1
- examples/15_sutra_const.sm: 5
- examples/16_advanced.sm: 1
- examples/17_booleans.sm: 3
- examples/19_srijana_enum.sm: 1
- examples/201_madhava_library.sm: 5
- examples/202_brahmagupta_area.sm: 4
- examples/203_meru_with_kosh.sm: 1
- examples/215_r12_wordfreq.sm: 1 (no golden — NO-EXPECTATION in the suite; verified by running the
  HEAD version against the migrated version: 8 blank lines removed, the triple sits in a loop, nothing else)
- examples/217_r12_report.sm: 1 (no golden — same check: 1 blank line removed, nothing else)
- examples/21_break_continue.sm: 1
- examples/23_grahan_input.sm: 2
- examples/25_patterns.sm: 1 (10 blank lines removed — triple in a loop)
- examples/28_compound.sm: 8
- examples/32_bank_interest.sm: 2 (includes 1 `lkhb` triple: `likha(": ") / lkhb(principal) /
  likha("\n")`, principal is an int, so this one IS byte-identical against the old golden)
- examples/34_incdec.sm: 6 (includes 1 `lkhb` triple: `likha(" squared = ") / lkhb(varg) /
  likha("\n")`, varg is an int, byte-identical)
- examples/35_comments.sm: 2
- examples/91_indian_number_theory.sm: 4
- examples/array_demo.sm: 1
- examples/char_ops.sm: 3
- examples/full_demo.sm: 4
- examples/func_demo.sm: 1
- examples/import_demo.sm: 4
- examples/mem_safe.sm: 2
- examples/number_game.sm: 2
- examples/strength_reduction.sm: 6

**Goldens updated (32):** the `.out` for every migrated file that has one, removing only blank lines
(112 lines total). `215_r12_wordfreq` and `217_r12_report` have no golden and keep their
NO-EXPECTATION status.

**Files skipped, with reasons — 14 files, 0 triples migrated in them:**

These files contain patterns that LOOK like triples to a naive counter but are not labelled prints.
In each, the "label" line is `likha("\n")` or `likha(" ")` — a separator, not a label — and the
sequence is really `value, newline, value, newline, ...` (e.g. `examples/61_stdlib_math.sm` prints
one value per line with a blank line between). Migrating them would produce nonsense such as
`likha("\n", nirapeksh_mulya(0 - 5))` and would change the output in a way that is not a labelled
print. I initially migrated 30 of these by mistake, caught it in review, and reverted all 30; the
files below are back to their exact HEAD text (they do not appear in the patch at all):

- examples/116_perf_reg_destination.sm, examples/117_perf_constant_literals.sm,
  examples/20_pankti_array.sm, examples/216_r12_expr.sm, examples/22_precedence.sm,
  examples/61_stdlib_math.sm, examples/62_stdlib_num.sm, examples/63_stdlib_string.sm,
  examples/81_stdlib_num2.sm, examples/83_stdlib_sort.sm, examples/84_stdlib_string2.sm,
  examples/85_stdlib_shellsort.sm, examples/86_b8_multi_modules.sm, examples/88_pingala_chandas.sm

The remaining gap between the naive 135 and the true 97 (38) is these 30 separator patterns plus
8 double-counts: a naive counter that filters out blank/comment lines counts a `likha("\n")` line
both as the end of one triple and as the "label" of the next.

**`lkhb` float triples skipped:** none. The only two exact `lkhb` triples in the tree are the int
cases in `32_bank_interest` and `34_incdec` above, both migrated. (Other `lkhb` uses in those files
are not exact triples — e.g. `lkhb(year) / likha(": ") / lkhb(principal)` — and were left alone.)

## WS2 — the 88 functions with no usage comment

**Definition that reproduces 88:** a comment must sit *directly* above the `prakriya` line, with no
blank line between. Under that strict definition there are exactly 88: **81 with no comment at all,
plus 7 whose comment exists but is separated by a blank line.** All 88 are now commented in the
patch; **no code line changed.**

**81 new comments written (one line each, from the function body, not from the name):**

- lib/ank.smlib (9): asti_visham — 1 if n is odd; ank_gan — number of decimal digits in n (MIN = 19);
  ank_yog — sum of decimal digits (MIN = 89); viparyay_ank — n with digits reversed, sign kept;
  asti_vilom — 1 if n is a palindrome (negatives never are); seemit(n, lo, hi) — n clamped to
  [lo, hi]; fib — nth Fibonacci, iterative; asti_sampurna — 1 if n is perfect; collatz_charan —
  Collatz steps to 1, -1 if n < 1 or 3x+1 would overflow.
- lib/chandas.smlib (5): meru(n, k) — binomial C(n, k), 0 for k < 0 or k > n; matra_meru — nth
  Fibonacci; asti_guru(pat, i) — 1 if bit i of pat is set (0 for i < 0 or >= 64); guru_gan — set-bit
  count, negatives return 0; meru_mala(a, n) — fills a[0..n] with Pascal row n.
- lib/ganit.smlib (15): vargit — n squared; ghan — n cubed; nirapeksh_mulya — absolute value;
  laghu2 — smaller of a, b; adhik2 — larger of a, b; mahattam — GCD, non-negative; laghuttam — LCM,
  non-negative, 0 for (0, 0); ghat(base, e) — base^e; kramgun — n! (1 for n < 2); asti_abhajya — 1
  if prime; yog_tak — 1+...+n closed form, 0 for n <= 0; dvigun — n*2; trigun — n*3; vardh — n+1;
  bit_gan — set-bit count, negatives return 0.
- lib/ganita.smlib (1): ganita_nirapeksh — absolute value (the ganita spelling).
- lib/khand.smlib (3): khand_maap — byte length of s; khand_avanat(src, sn, out) — copy with
  A-Z lowercased, NUL-terminated, returns sn (0 for sn < 0); khand_ant(src, sn, suf, sn2) — 1 if
  src ends with suf.
- lib/mala.smlib (7): mala_sangrah — store at arr[i], no bounds check, returns 0; mala_grah — load
  arr[i]; mala_purn — fill arr[0..n-1] with val; mala_pratilip — copy n qwords dst <- src;
  mala_yog — sum of arr[0..n-1]; mala_sangrah_surakshit — bounds-checked store, 1/0;
  mala_grah_surakshit — bounds-checked load, arr[i] or 0.
- lib/nighantu.smlib (1): nighantu_maap — entry count of map m.
- lib/phal.smlib (4): phal_janchit_nyun/gun/bhaj/shesh(out, a, b) — checked subtract/multiply/
  divide/remainder: out[0] = ok flag, out[1] = result if ok else 0, returns out[0].
- lib/roop.smlib (4): roop_shodash — lowercase hex into out, returns digit count;
  roop_shodash_unnat — UPPERCASE hex (flag 2 = uppercase, no prefix); roop_asht — octal;
  roop_dwi — binary.
- lib/sadhan.smlib (6): yog_seema(start, end) — sum start..end inclusive, 0 if end < start;
  shesh(a, b) — remainder as a - (a/b)*b, 0 if b == 0; bhaj_urdhva — ceiling division, 0 if
  b == 0; util_chinha — sign: 1/0/-1; satya_tak_ank(b) — boolean to int; ank_adhik() — max int64.
- lib/shreni.smlib (11): budbud_shreni — bubble sort in place; viparyay_mala — reverse in place;
  laghu — smallest, 0 if n <= 0; adhik — largest, 0 if n <= 0; yog — sum; anwesh_sarak — first
  index of target or -1; gan — count of target; asti_sorted — 1 if non-decreasing;
  dwi_anwesh — binary search, index or -1; shankh_shreni — shell sort; nivesh_shreni — insertion sort.
- lib/varna.smlib (15): akshar_sanket(s, i) — byte code of s[i]; asti_ank_akshar — 1 if digit;
  asti_unnat_akshar — 1 if A-Z; asti_avanat_akshar — 1 if a-z; asti_akshar_akshar — 1 if any
  letter; asti_avakash_akshar — 1 if space; gan_swar — count of lowercase vowels; gan_akshar(s,
  code) — count of code in s; anwesh_akshar — first index of code or -1; asti_sarv_ank — 1 if
  non-empty and all digits; unnat_sanket — code to uppercase; avanat_sanket — code to lowercase;
  varna_sam — 1 if strings byte-identical; varna_avanat(src, sn, out) — copy with A-Z lowercased,
  returns sn (0 for sn < 0); varna_ant(src, sn, suf, sn2) — 1 if src ends with suf.

**7 gap fixes (comment already existed, blank line removed so it sits directly above):**
lib/ank.smlib asti_yugm, lib/chandas.smlib dviguna, lib/ganit.smlib varg, lib/mala.smlib mala_nava,
lib/sadhan.smlib antargam, lib/shreni.smlib vinimay, lib/varna.smlib varna_maap. No comment text
changed for these seven.

**Functions I could not describe: none.** Every one of the 81 was described from its body. The two
that needed a body check rather than a name guess: `roop_shodash_unnat` is uppercase hex *without*
a prefix (flag 2 in `roop_ank_dhvaj` is the uppercase bit, not the prefix bit), and `khand_avanat`
/ `varna_avanat` are byte/qword-cell copies respectively with the same lowercasing — the names
alone would not say which.

**After WS2, strict re-count: 0 functions without a directly-above comment.**

## WS3 — re-count and confirm

- Labelled print triples: **97 before, 0 after.**
- `likha("\n")` lines in examples: **174 before, 77 after.** The drop is exactly 97 — one per
  migrated triple. The 77 that remain are not triples: standalone blank-line prints, section
  separators, and the reverted separator patterns in the 14 skipped files above. If a number "did
  not move as much as expected", that is why: `likha("\n")` is also used on its own, and those
  uses are correct and untouched.
- Suite after WS1+WS2: **PASS=225, NO-EXPECTATION=4** (215, 216, 217, 219 — all with no golden). No test changed from PASS to FAIL.

## Delivery and one warning that belongs to R53, not R52

`ROUND-52.patch` (51,566 bytes) covers 78 files: 34 examples, 32 goldens, 12 lib files
(178 insertions, 410 deletions). **Warning:** this patch alone pushes one library proof over the
compiler's 64 KiB expanded-source cap (see the R53 report for the exact numbers: the R52 comments
in khand/nighantu/shreni add 1,169 bytes to the program that already sat 986 bytes under the cap).
That is a compiler-limit problem, not a comment problem — the comments are correct and the suite
stays green. Do not drop the comments to fit the cap; raise the cap (Claude's open item, R29
finding 3). The R53 report gives the full arithmetic.

**NOT RUN:** Windows/WSL execution (owner's test, as always). No Windows claim is made.
