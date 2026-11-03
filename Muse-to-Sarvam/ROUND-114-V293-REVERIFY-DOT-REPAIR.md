# ROUND-114 — Re-verify the 16 on v293, and audit Claude's dot-product repair

Base: v293 (worktree at `62602ecb`, the brief's commit — v293 + the brief). Note: Claude's v294 (Sutram Error → Sutram truti, in the compiler and all eleven packs) landed after this brief was written; it is not in scope here and I did not audit it.

## WS1 — Claude's two repairs: the dot is correct, the rachana refusal works, the segfault moved (not gone)

**sankhya_bindu(a, b, n) — CORRECT as an integer dot (probes delivered).** The 3-argument form (new in v293; the 2-argument form is now compile-refused) gives: kosh [5,6,7] self-dot, n=3 → **110** (25+36+49, correct); unequal lengths with n=2 → **14** (the first two, 1·4+2·5 — the function trusts n, it does not know the lengths, so it does not refuse on mismatch; that is the design, like smaran_cp, not a defect in this form); empty kosh, n=0 → **0**; two mala [5,6,7] self-dot, n=3 → **110**. So the R111 defect (meaningless float-bits dot) is fixed for the new form — but note the shape changed: Claude chose an integer dot over raw 8-byte cells (mala/kosh/nirmmita) with an explicit n, not the R111 shape (kosh dasham → dasham with an equal-length check). The equal-length check R111 asked for does not exist in this form because n replaces the lengths. That is a design choice to note, not a defect to flag here.

**rachana beside an operator — REFUSES, with E_RACHANA_GANIT.** `p == q` (two records, x=3) → refused with `E_RACHANA_GANIT: rachana-upari ganitam tulana va na sambhavati - rachana sankhya na` + the field hint; `p + q` → refused with the same code (with line:column, 7:13). Field accesses still work unchanged: `p.x + q.x` → 7, `p.x == 3` → 1. Confirmed: the comparison refusal prints no line:column (as Claude noted), the arithmetic one does — the asymmetry is real, not a probe artifact.

**The segfault on two dasham scalars — NOT fully gone.** The exact R111 form (2-argument: `sankhya_bindu(3.0, 4.0)`) now compile-refuses (arity error) and does not run — that crash is gone. But the same mistake in the new form (`sankhya_bindu(3.0, 4.0, 1)`) still **segfaults, exit 139**: the function takes raw pointers + n with no check that the arguments are buffers at all, so a scalar's bits are dereferenced as an address. The repair moved the crash from the 2-arg form to the 3-arg form; it did not close the unchecked-pointer hazard. (This is the same class as smaran_cp's unchecked n — the design trusts the caller completely.)

## WS2 — the 16, re-tested on v293: NONE moved (0 of 16, not "two touched")

Re-ran all 16 trigger probes on v293 (probes delivered). Every number is identical to R112 (v292):

- ganit: dvigun(MAX) = -2, trigun(3074457345618258603) = -9223372036854775807, vardh(MAX) = MIN, nirapeksh_mulya(MIN) = MIN, mahattam_samapavartak(MIN, 0) = MIN.
- ank/ganita: viparyay_ank(1999999999999999999) = -8446744073709551625, ganita_nirapeksh(MIN) = MIN, brahmagupta_kshetr(1,1,2,3) = 0, brahmagupta_kshetr(2,3,4,0) = 0.
- aadhar/brihat: brihat_ank_se([9,9,9,9,9], 2) = 1 with x = [9,9] (99, truncated); brihat_ank_tak_laghu(19 nines) = -8446744073709551617.
- patra/sadhan: patra_asti(symlink loop) = 0; yog_seema(4611686018427387904, same) = MAX (the saturation sentinel).
- dots: adish_gunan([1,2,3],[4,5]) = 14.000000, bindu_gunan([1,2,3],[4,5]) = 14.000000.
- vakyank: varna_tak_dashm("000...01" cell buffer) = 0.000000 with ok = 1.
- suchi_shreni: body identical v292 → v293 (git diff empty), so unchanged by code reading (alloc-failure trigger still not forced, as in R112).

Correction to the brief: "two were touched" refers to the two WS1 repairs (sankhya_bindu + rachana), which are NOT in the 16 — so **0 of the 16 were touched, and 16 (not 14) are unchanged**. No repair changed an unrelated function; v293's guard (0 DIFFER) agrees. One probe note: my first varna probe passed a byte string instead of R112's nirmmita cell buffer and got ok = 0 — that was a probe artifact, not a v293 change; replicating R112's exact probe gives 0.000000 with ok = 1, identical to v292.

## WS3 — the 16 that remain (not 15: v293 fixed none of them), as an implementable work list under Option 2

Option 2: a public mathematical operation must produce the promised result or report failure through its declared channel; plain `+`/`*` keep wrapping. The key distinction is whether a function ALREADY HAS a declared channel. Where it does, the fix is one line. Where it does not, the check is one line but the channel needs a decision — and the R18 precedent already exists for that decision: ganita's checked/saturating family (documented in lib/ganita.smlib) uses an ok out-param (the varna_tak_ank ok-pattern) and returns 0 on failure, "never the wrapped value, so a caller that forgets to check ok gets an obviously-wrong 0, not a plausible-but-wrong wrapped value." That is the channel to adopt for the nine below that lack one.

**One-line fixes (check + existing channel, no signature change):**
- brihat_ank_se: return 0 (not 1) when carry remains after the loop — exactly like its sibling brihat_ank_se_laghu, which already returns 0 on truncation.
- suchi_shreni: propagate mil_shreni's return — `yadi (mil_shreni(l[2], l[0]) < 0) { nivartanam 0 }` instead of discarding it and returning 1.
- varna_tak_dashm: clear ok when the digit budget is exceeded — or better, one line the other way: do not count leading zeros toward ndig (the header claims "up to 18 significant digits", so ndig should count significant digits; then "000...01" parses as 1.0, correct, not just refused).
- yog_seema: special-case a == b → return a before the `b > maxv - a` check (that check guards s = a+b, but for a single element the sum is a, not s). Saturation stays the channel for genuinely overflowing ranges (documented, R80).

**One-line checks, but NO existing channel (need the R18 ok-param decision — a small mechanical signature change, not a rewrite):**
- dvigun: check n > MAX/2 or n < MIN/2 before doubling. trigun: n > MAX/3 or n < MIN/3. vardh: n == MAX. nirapeksh_mulya / ganita_nirapeksh: n == MIN. mahattam_samapavartak: (a == MIN and b == 0) or (a == 0 and b == MIN). viparyay_ank: check overflow before each r = r·10 + d in the loop. adish_gunan / bindu_gunan: check kosh_len(u) != kosh_len(v) before the loop. In each case the check is cheap (one comparison, or one per digit), but the function returns a plain value with no failure channel — so adopting the R18 ok-param (+ return 0) is a signature change, and its call sites must be updated (for bindu_gunan that includes 207, whose golden would change from 7.000000 to a refusal).
- brihat_ank_tak_laghu (small fix, not a signature change): check overflow before each r = r·10 + d, and return -1 on overflow — -1 is unambiguous here because digit-array outputs are non-negative, and -1 is already the library's sentinel convention (nighantu_grah, anukram_grah).

**Rewrites / new channels (not one-liners):**
- brahmagupta_kshetr: the formula itself is wrong (integer-truncated s), not just an overflow — rewrite it (e.g., the 4·area² form (a+b+c+d)(−a+b+c+d)(a−b+c+d)(a+b−c+d) with an integer sqrt, avoiding the truncation entirely), and distinguish genuinely impossible quadrilaterals (p < 0) from wrapped products (huge sides) instead of returning 0 for both.
- patra_asti: not a refusal problem at all — it is a wrong predicate (opens vs exists). Fixing it needs a stat-like test or errno visibility, which the lib does not have (dvaram returns only fd < 0) — so it needs a new compiler builtin, or a rename + docs (it answers "opens", not "exists"). Do not count it as a refusal fix.

**Work-list order (combining R113's accidental-first rank with WS3's cost):** first the four one-liners (two of which — brihat_ank_se, varna_tak_dashm — are in the accidental set, and yog_seema/suchi_shreni are cheap regardless); then the nine ok-param adoptions (accidental ones first: adish_gunan, bindu_gunan, then the deliberate-MAX ones); then the two rewrites (brahmagupta first — it is accidental and a formula, not just an overflow; patra_asti last — it needs a builtin or a rename decision, not lib code).

NOT RUN: Windows, browser, implementation (none authorized — this is a design, not code), native-speaker review, full suite (no tree changes; Claude's v293 numbers stand: suite 297, guard 707 0 DIFFER, gates 60/1/1), v294 audit (out of scope — see base note above).
