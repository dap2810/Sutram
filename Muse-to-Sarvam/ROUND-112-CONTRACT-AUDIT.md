# ROUND-112 — The contract audit: 16 of the 306 promise what they cannot deliver

Base: current main `51eb8266` (v292 + ROUND-112). Count verified: 306 `prakriya` across 24 modules (grep count, not the brief's number — it happens to match). Method: every function read; each flag below was confirmed by source reading, and 15 of 16 by running a probe on v292 (the 16th, `suchi_shreni`, rests on exact code reading — its trigger is allocation failure, which I did not force). I verified 4 flags independently with a combined probe (delivered as `r112_verify.sm`: dvigun(MAX) = -2, patra_asti(loop) = 0, adish_gunan = 14.000000, varna_tak_dashm = 0.000000 with ok = 1). The other 12 were probe-confirmed in the audit and source-checked by me.

## WS1 — the count and the list (one line each): 16 firm flags

1. `ganit.dvigun` — "n doubled" wraps: dvigun(MAX) = -2, a plausible negative, not a refusal.
2. `ganit.trigun` — "n tripled" wraps: trigun(3074457345618258603) = -9223372036854775807 (true value MAX+1).
3. `ganit.vardh` — "n + 1" wraps: vardh(MAX) = MIN.
4. `ganit.nirapeksh_mulya` — "absolute value" returns MIN for MIN (negative), violating non-negativity; the comment admits it.
5. `ganit.mahattam_samapavartak` — "gcd, always non-negative" (its own comment) returns MIN for (MIN, 0).
6. `ank.viparyay_ank` — "digits reversed, sign kept" wraps: reverse of 1999999999999999999 = -8446744073709551625.
7. `ganita.ganita_nirapeksh` — "absolute value" returns MIN for MIN (same gap as #4, in the other module).
8. `ganita.brahmagupta_kshetr` — "Brahmagupta's formula" truncates s with integer division before the product, computing a different formula: (1,1,2,3) and (2,3,4,0) both give 0, true integer part 2 in both cases; large-side product wrap also returns 0 via the p < 0 check.
9. `aadhar.brihat_ank_se` — "parse digits into an n-digit bigint, 1 on success" silently drops overflow past n digits and still returns 1: [9,9,9,9,9] into n = 2 returns 1 with 99 (truncated from 99999); sibling `brihat_ank_se_laghu` returns 0 on truncation.
10. `brihat.brihat_ank_tak_laghu` — "digit array back to int" wraps: 19 nines = -8446744073709551617 (comment warns "only correct if it fits" — a warning, not a check).
11. `patra.patra_asti` — "this path exists" tests "this path opens read-only": a symlink loop (entries exist, open fails ELOOP) returns 0; the comment admits the caller cannot distinguish missing, missing-directory, and permission-denied.
12. `sadhan.yog_seema` — "sum from start to end inclusive" returns the saturation sentinel for a fitting value: single-element range (4611686018427387904, same) returns maxv instead of the element (the `b > maxv - a` check fires even when a == b).
13. `samanvaya.adish_gunan` — "dot product" over min-length entries: ([1,2,3], [4,5]) = 14.000000 — there is no dot of a 3-vector and a 2-vector; documented in the comment, but per R111 a correct dot needs equal length and refuses on mismatch, so documented-but-wrong is still wrong.
14. `sankhyiki.bindu_gunan` — same min-truncation dot as #13: ([1,2,3], [4,5]) = 14.000000.
15. `suchi.suchi_shreni` — "sort in place, return 1" discards `mil_shreni`'s return and unconditionally returns 1: on scratch-allocation failure the list is left unsorted while reporting success (a caller binary-searching it then gets wrong results). Code reading only; trigger is allocation failure.
16. `vakyank.varna_tak_dashm` — "parse a decimal float, ok = 1 on success" returns 0.0 with ok = 1 when leading zeros consume the 18-digit budget: "00000000000000000001" (true 1.0) gives 0.000000, ok = 1 (the header claims "up to 18 significant digits" but `ndig` counts all digits including leading zeros). Note: the ok channel must be a nirmmita pointer (`vitti ok = nirmmita(8)`), as the tests use — passing a mala as ok does not receive the write, which initially masked this flag in my own probe.

## WS2 — rank: WRONG ANSWER vs DIFFERENT answer

**All 16 are WRONG ANSWER (defects). Zero firm flags are merely DIFFERENT (documentation problems).** The distinction matters, so I applied it strictly: a body that is correct for what it actually does, with the difference documented, would be a docs problem — but none of the 16 qualifies, because in each case the returned number is not the promised computation. Documented-but-wrong (flags #13, #14, whose comments state the min behavior) still counts as wrong per R111's principle: a caller who trusts the name gets a number that is not a dot product, and the comment does not change the value. The genuinely docs-only cases found in the audit are listed separately below, not counted.

Within WRONG, ranked by whether a student notices (the brief's framing):
- **HIGH — wrong for ordinary inputs, plausible, student may not notice:** #8 (ordinary triangles give 0 instead of 2), #1/#2/#3/#6/#10 (wrap for large but ordinary integers), #13/#14 (prefix dot for mismatched vectors), #16 (0.0 with ok = 1 for leading-zero numbers), #9 (success + truncated 99 for long digit arrays).
- **MEDIUM — wrong for a specific valid input:** #4/#5/#7 (MIN — valid, but an edge), #12 (single-element large range — valid shape, but an edge).
- **LOW — wrong only in rare conditions:** #11 (exists-but-won't-open — a student may never hit it, but it is still a wrong answer, not a different one), #15 (allocation failure only).

**Not counted (uncertain / docs notes, for judgment, not in the 16):** negative-length inputs to `khand_tul`, `khand_bhed`, `roop_pad_*`, `varna_bhed` (out of contract — the modules do not promise behavior there); `khand_gan_swar` counting lowercase vowels only (documented in the comment — a docs problem if the caller does not read it, not a defect in the body); loop artifacts for out-of-domain inputs (`ghat`/`brihat_ghatmod` negative exponent → 1, `fib` negative → n, `ganita_vargmool` negative → 0, `kuttaka` when gcd ∤ c, `samasa` unchecked, `meru_mala` propagating meru's -1 sentinel, matrix functions on negative dims, `mil_shreni`'s fall-off-the-end return convention). The dominant pattern in the firm 16 is unchecked int64 wrap in trivial functions — the same Tier-2 extreme-input thread, now with names attached — plus three non-wrap defects (#8 wrong formula, #11 wrong predicate, #13/#14/#16 silent partial/wrong results with success signals).

## WS3 — do other old/new alias pairs promise different things? YES, two do

Checked all 22 pairs (old meaning vs new meaning vs body). **20 promise the same thing** (including `sankhya_dot` → `sankhya_bindu`: both promise a dot product, both unmet — the rename did not change the meaning, the body is the defect, so it is NOT a WS3 flag). **2 change the meaning:**

1. **`kosh_cap` → `kosh_ksham` — the clearest case, and worse than sankhya.** The old name was CORRECT: cap = capacity, a number, which the body delivers. The new name is thin: ksham = capable, a property, not a number — so the new name promises something different from what the body returns (a number). The rename degraded a correct name into a misleading one. This is a rename that changes the meaning for the worse.
2. **`likha_fmt` → `likha_rup` — the promise changed without fixing the body.** The old name promised printf-style formatting (substitution), which the body never did (it does label+value sequential printing). The new name promises form (rup), which the body also does not do (it does not format either). Both names mislead, but differently — the rename replaced one unmet promise with another instead of fixing the body or naming what it actually does (label+value).

Notes, not flags: `kosh_kship` (kship = throw/cast — "throw into" reads as push in context, but alone it could be misread as throw away; docs should state it); `kosh_shodh` (Sanskrit reading = cleanse/clear, but modern Hindi readers may read it as "search" — docs should state clear, not search); `kosh_hri`/`kosh_apanay` (front-vs-top is not in the names — docs must state the ends, as R107 noted). These are documentation notes, not meaning changes: the intended reading matches the body.

NOT RUN: Windows, browser, implementation (none authorized — this round audits and recommends, it does not fix), native-speaker review (the Sanskrit readings above are the auditors' — a native speaker should confirm `ksham`/`rup`/`kship`/`shodh` before any rename decision), full suite (no tree changes; R111's v292 numbers stand: suite 295/299, gates 60/1/1, guard 705 0 DIFFER).
