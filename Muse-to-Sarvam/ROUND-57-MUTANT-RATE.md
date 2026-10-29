# ROUND-57 — The 818 undecided mutants: the rate, not the list

Base: origin/main `f9b281dc`, CHANGELOG v411, compiler v261.
Measurement only. No source changes. Tree left clean.

Note on the base: this rebuild ran on a fresh copy of current
origin/main (`4bfb73d2`), which adds only one docs commit
(`ChatGPT-to-Sarvam/ROUND-131-NIRMMITA-TRACE.md`) on top of
`f9b281dc`. `lib/` is byte-identical between the two commits
(verified by `git diff f9b281dc origin/main -- lib/`, empty), so
all measurements apply to the brief's base unchanged.

## 0. Frame correction: there is no 818-entry list

The brief asks for a rate over "the 818 undecided mutants" and for a
re-check of "the 15 known survivors". Neither list exists in the tree,
in the same way R48 found for the witness file.

- `Claude-to-Sarvam/evidence-r15/proofs/lib-mutant-witness.json`
  (the R15 survivor list) counts **741 NOT-TRIED / 187 NO-WITNESS /
  23 WITNESS** (951 entries).
- The R15 score summary `lib-mutant-score.md` counts **818 NOT-TRIED /
  110 NO-WITNESS** for the same run.
- The two artifacts from the same run disagree by exactly 77 in each
  direction (818 − 741 = 77; 187 − 110 = 77).
- The 818 quoted in `docs/OPEN-ISSUES.md` (A3) and `docs/WHATS-LEFT.md`
  (C3) comes from the summary, not from the list.

The sample below was drawn from the **741 NOT-TRIED entries**, the only
machine-readable population. Every rate in this report is a rate over
that population, and the 77-entry discrepancy between R15's own
artifacts is itself an open item (see §5). Nothing in this report
should be quoted as a rate over "818" without that qualification.

Likewise there is no 15-entry survivor list. The closest well-defined
known-bad set is the **23 R15 WITNESS entries** (13 distinct functions),
re-checked in §3.

## 1. WS1 — the rate: 42 of 120 caught (35%)

### Method

- Sample: 120 distinct NOT-TRIED entries, `random.Random(20261028)`,
  no replacement. Kinds: K 62, D 20, A 14, C 22, R 2. 73 distinct
  functions, 15 modules.
- R15 line numbers are stale (the library has been renamed and edited
  since), so the sampled unit is **function + mutation kind**, and the
  occurrence within the kind is a seeded-random choice
  (`random.Random(20261028 + index)`), recorded per mutant. A tag alone
  does not identify a mutant: several lines carry multiple same-value
  literals, so one tag (e.g. `K:1@L39` in `simpson`) names up to four
  distinct mutants. The exact changed line for every missed mutant is
  in the appendix table.
- 7 sampled functions were renamed since R15 and were mapped through
  Claude's R56 rename commits (v259–v261): `brihat_ank_se_int` →
  `brihat_ank_se_laghu`, `anukram_grah_ashtak` →
  `anukram_grah_aayam_purva`, `roop_varg_mool` →
  `roop_varg_sahaya`, `pehchan` → `ekaka_matrika` (plus
  `pravan2` → `dvitiya_pravan`, `bindu` → `bindu_gunan`,
  `nishan` → `karna_yog`, `nirnaya2` → `saranik2`,
  `nirnaya3` → `saranik3`, `util_chinha` → `ank_chihna` for the
  WS3 re-check). No sample replacements were needed.
- Harness: per mutant, generate all current mutants for the function
  (`tools/lib_mutant_score.mutants`, cap 10^6, generation RNG seeded
  by "module.name"), filter to the sampled kind (+value/op), apply the
  seeded choice over `lib/<module>.smlib`, run `tools/proof_lib.py`
  (226 proofs) with cwd=repo root and the repo-root
  `./sutram_compiler`, restore the original and verify the restore by
  SHA-256.
- Caught = proof_lib exits non-zero with 1–20 tests failing (verified
  genuine catches, not stillborn or compile failures). Two caught
  mutants were caught via timeout rather than a golden mismatch:
  `khand_chhid` D@L340 makes `string_strb_trim_case` hang, and
  `nighantu_apanay` K:0@L208 (can_move 0→1) makes
  `r11_nighantu_edges` hang; in both cases proof_lib exits 1 with a
  TimeoutExpired traceback and no FAIL lines. Both are genuine
  catches; their mechanism is noted here rather than hidden in the
  count.

### Result

**120 sampled → 42 CAUGHT / 78 MISSED. Caught rate 35%.**

| Kind | Sampled | Caught | Missed |
|---|---|---|---|
| K (constant) | 62 | 24 | 38 |
| D (deletion) | 20 | 12 | 8 |
| A (arithmetic) | 14 | 4 | 10 |
| C (comparison) | 22 | 2 | 20 |
| R (return) | 2 | 0 | 2 |

By construction these were R15 survivors: at R15 they were NOT-TRIED,
meaning no proof had ever been run against them, so a 0% caught rate
then was definitional, not a measure of proof strength. The 35% now
caught is therefore a direct measure of proof strengthening since R15:
new proofs (r18, gaps, bounds, edges) now kill a third of a population
the old proof set had never exercised. The remaining 65% is classified
in §2.

The 42 caught mutants, with their failing proofs, are listed in
Appendix B. The two R mutants (return-code changes) were both missed;
see §5 for why the tooling could not even generate them.

## 2. WS2 — why the 78 missed mutants were missed

**Split: (a) proof too weak = 41, (c) behaviourally equivalent = 30,
undecided = 7, (b) no proof covers the function = 0.**

### (b) is empty, and that is a finding

Every sampled function is executed by at least one proof, directly or
indirectly. Four functions have no proof naming them directly
(`nighantu_kunji_gudh`, `suchi_vardh`, `roop_varg_sahaya`,
`nighantu_anwesh`), but all four are reached indirectly: the hash
helper runs on every map operation, the grow helper runs whenever a
list grows, the digit-grouping helper runs through the `roop` wrappers,
and `anwesh` runs through `khip`. Their gap is the distinguishing
input, not coverage, so they are classified on their merits
(`kunji_gudh` and `suchi_vardh` end as (c) for their sampled mutants,
`varg_sahaya` and `anwesh` as (a)). A (b) count of 0 means the
remaining work is strengthening proofs, not adding coverage for
uncovered functions.

### (a) proof too weak — 41, grouped by mechanism

- **Zeroed buffers hide deleted or misplaced terminators.** The
  proofs use zeroed output buffers, so a deleted terminator is
  invisible (the byte after the output is already 0). Affected:
  `khand_bandh` D, `khand_viparyay` D, `varna_viparyay` D,
  `roop_ank` K:1 (terminator at dst[2]), `roop_varg_sahaya` K:0
  (terminator value 0→1), `vakyank` terminators, `ank_tak_aadhar_varna`
  D. Distinguishing input in every case: a pre-filled output buffer.
- **Return codes and ok flags never asserted.** `brihat_bhajshesh` R,
  `brihat_shesh` R (proofs check the out-arrays, never the return
  code), `ganita_janchit_nyun` K:0 (wrong-cell ok write, masked by
  call order — see below), `varna_tak_ank_aadhar` D (deleted ok
  assignment), `varna_tak_dashm` K:0 (ok flag flipped).
- **Untested boundary, empty, and first-byte cases.** `khand_ant`
  first-byte-only suffix mismatch, `varna_chhid` no-leading-space
  (drops the first character) and all-spaces (hangs),
  `roop_sthir_mool` v==0.0 printing "-0…", `anukram_grah_i64` top
  byte exactly 128 (= i64 MIN), `aadhar` base 17, `chakravala`
  exact-boundary and shifted-candidate cases, `ganita_janchit_gun`
  (−1, MIN), `roop_ank` negatives (only covered via `roop_ank_aadhar`),
  `roop_pad_dakshin`/`madhya` w<=cnt branch (madhya's real gap is
  w<cnt, where a negative pad count writes out of bounds).
- **Even-count Simpson.** `kalana.simpson` K:1 is equivalent (see (c));
  the real gap is A:-, which makes the parity expression negative for
  every n, so an even point count is never dropped. Distinguishing:
  4 points of x^2 on 0..3 — real 2.666667, mutant 7.000000. R48's
  4-point witness (real 2.000000) is the same family.
- **Allocation shrink masked because proofs check outputs, not heap
  bounds.** `brihat_ghatmod` A:* (bcur c×8 → c+8 bytes; proofs use
  c=8 and the result stays correct because the overflow lands in
  scratch rewritten before use), same family `rakh_samroop_diff` /
  `rakh_tak_mala` A:* with small-set tests.
- **2×2-only matrix tests.** `matrika_yoga` m×n → m+n is invisible
  at 2×2, where m+n == m×n; `ekaka_matrika` n×n → n+n is invisible
  at n=2.
- **Miscellaneous singletons.** `rekha_manak` skips row 0 (proofs
  never put the maximum in row 0); `vakyank` K:102 ('g' accepted as
  digit 16 — distinguishing is a base-17+ input containing 'g'; the
  mutant is mathematically correct for bases 17–36, the real
  limitation is the letter range); `varna_tak_dashm` C18 (any exponent
  containing '0', e.g. "1e10", rejected); `anukram_grah_aayam_purva`
  K:1 (inner-read-failure return −1 → −2; proofs never trigger an
  inner-read failure); `brihat_ank_se_laghu` A:- (MIN constant
  becomes MAX−1; proofs test neither boundary); `brihat_ank_tak`
  K:16 (base 17 accepted) and A:* (allocation shrink);
  `nighantu_anwesh` K:1 (kn<0 return −1 → −2).

The `ganita_janchit_nyun` case deserves its own sentence because it
looks like a proof success: the proof does call exactly the mutated
branch (`nyun(max, -1)`), but the preceding `nyun(min, 1)` call
already left ok[0] = 0, so the mutant's wrong-cell write (ok[1]
instead of ok[0]) is invisible. Distinguishing: `nyun(max, -1)` as
the first call, or with ok[0] preset to 1.

### (c) behaviourally equivalent — 30, grouped by mechanism

- **Dead initialisations** (value overwritten before use):
  `khand_gan_swar` ch, `khand_pratisthap` k (two sample draws, same
  mutant), `nighantu_khip` start, `nighantu_mil` seglen,
  `roop_pad_madhya` npad, `avali_pravesh` nd/old.
- **Converging branches** (changed case reaches the same outcome):
  `khand_mukt`, `khand_viparyay` C1, `khand_avanat` (slen==0),
  `varna_unnat` (slen==0, terminator written by the final line either
  way), `roop_ank` C3 (val==0 handled by the earlier return),
  `purna_vyapti`.
- **Changed case already handled earlier**: `bahu_mula` C5 (fhi==0.0
  returns earlier) and C10 (flo==0.0 returns earlier).
- **Overwritten extra byte**: `roop_pad_dakshin` C4,
  `roop_pad_vam` C3, `rakh_tak_mala` C6.
- **Value-not-index comparisons**: `laghutama` < → <=,
  `ganita_janchit_yuj` y>=0 → y>0 (dead at y==0),
  `ganita_janchit_nirapeksh` x<0 → x<=0 (abs(0) = 0 either way).
- **API-unobservable**: `nighantu_rikta` stale key byte (slots marked
  empty, inserts overwrite), `suchi_apanay` extra shift past the
  logical length, `varna_gan` window extension (extra bytes are
  terminators that cannot match a string needle),
  `nighantu_kunji_gudh` cap==1 (h%1 == 0, identical to the branch
  return), `suchi_vardh` capacity 3× instead of 2× (no program
  asserts capacity).
- **Parity-equivalent Simpson**: `simpson` K:1 changes the second
  (n−1) to (n−2), giving (n−1) − ((n−2)/2)·2, which equals 1 exactly
  when n is even — the same as the real expression. Verified by
  direct run: the harness-chosen mutant gives 2.666667, identical to
  real, on the 4-point x^2 program. (A different same-tag occurrence,
  n = n−2, does differ; the appendix records the harness-chosen
  occurrence.)
- **`brihat_ank_se_laghu` K:8**: the stride j×8 → j×9 sits in the
  MIN-only carry loop, and carry clears at j=0 because MIN's least
  digit is 7 (7+1 = 8, not 10), so the misaligned read at j>=1 is
  never reached. R48's reasoning, reconfirmed against the actual
  changed line.

### Undecided — 7

All require inputs outside the proof set's reach rather than merely
untested ones: allocation-failure branches (`rakh_asti_upasamuh`
K:0, `avali_pravesh` K:0@L418 twice — both draws chose the same
return-flip occurrence, alloc failure returning 1 instead of 0,
`roop_ank_aadhar` K:0@L80, `ank_tak_aadhar_varna` K:0@L148) and
out-of-contract-only differences (`khand_aadi` K:0, plen<0 error
return flipped; `khand_avanat` K:0@L389, slen<0 return flipped).
By the R48 rule, out-of-contract-only differences are neither counted
as proof gaps nor proven equivalent.

### Classification method, stated plainly

Classification is reasoned from reading each function body at the
exact chosen mutant line (R48's method), not individually harness-run
per mutant — except the caught set (full proof_lib runs), the WS3
trig cases (direct runs), and five spot checks run directly against
real and mutant libraries: `khand_ant` first-byte mismatch (real 0,
mutant 1), `varna_chhid` no-leading-space (real "abc", mutant "bc"),
`roop_ank` negative (real "5", mutant ""), `ganita_janchit_nyun`
masking (mutant output identical to golden, confirming the call-order
mask), and the `simpson` K:1 equivalence above. Every (a) entry in
the appendix states its distinguishing input, so each claim is
checkable by one program.

## 3. WS3 — re-check of the known survivors: 11 of 23 now caught

There is no 15-entry list. The re-check below covers all 23 R15
WITNESS entries (13 distinct functions), each re-run fresh with
`tools/lib_mutant_score.py` per function.

### Caught now (no survivor at the witness kind/line)

- `meru` K:0
- `madhava_sin` N, A:-, A:+
- `madhava_cos` N, A:-, A:+
- `madhava_atan` N, A:-, K:1
- `ank_chihna` K:0 (function renamed from `util_chinha`; now 0
  survivors total)

### Still surviving (same or adjacent line, same kind)

- `ank_gan` K:0
- `seemit` C1
- `meru` N, `meru` A:-
- `ganit_seemit` C1
- `kuttaka` C4, `kuttaka` K:0
- `brahmagupta_kshetr` K:0
- `ganita_paripurna_kramgun` K:MAX
- `suchi_srij` A:*
- `avali_srij` A:*, `avali_srij` K:0

### Trig verdict: the sign error was a real wrong answer, and the gap was proof coverage

The `atan` mutants A:-@L104 / K:1@L104 (the `neg == 1` return at
current `lib/madhava.smlib:104`, `nivartanam 0.0 - r`) give
**+1.520838 for atan(−20)** against the real **−1.520838**. At R15 the
only atan proof used 0.0, 0.5, 1.0 — all non-negative, so a sign
error passed every proof. `tests/stdlib/r18_madhava_reduction.sm`
(whose own header says "No proof reached them; a sign error there
passed every proof") now exercises atan(−20) and atan(−1.5) with
goldens −1.520838 / −0.982794, and current score runs confirm the
sign mutants are killed. Verified directly: real compiler output for
sin(3) = 0.141120, cos(2) = −0.416147, atan(−20) = −1.520838.

Do not conflate the surviving trig mutants with the old witness
effect: the current `sin` N@L55 / `cos` N@L75 survivors are
reduction-boundary negations, a different mutant from the R15 sign
witnesses, and they do not reproduce the old witness effect on the
old witness inputs. The old sign error is closed; a new,
narrower reduction-boundary gap remains open for sin/cos.

## 4. What this means for the proof set

Of 120 sampled R15 survivors: 42 are already killed by proof growth
since R15, 41 are still-open proof gaps with a stated distinguishing
input each, 30 are equivalent, 7 are undecided. The single cheapest
proof-strengthening step is pre-filled output buffers: the largest (a)
family (terminators) is invisible only because every proof uses a
zeroed buffer. The second cheapest is asserting return codes and ok
flags on the checked-arithmetic and parsing functions, where the
proofs currently check values and ignore the flag that carries the
error. No new coverage for uncovered functions is needed: (b) is 0.

## 5. Tool gaps found (measurement only, not fixed)

1. `tools/lib_proof_gaps.py` `RET_RE` matches only `\bprati\s+`, so
   R mutants are ungeneratable on the current nivartanam library.
   The 2 sampled R mutants (`brihat_bhajshesh`, `brihat_shesh`) were
   built manually (`nivartanam e` → `nivartanam (e) + 1` on every
   return: 2 and 4 sites changed) and both were MISSED — proofs check
   the out-arrays, never the return code. The witness tool's
   deep-mutant set has the same staleness, and it only handles R/C
   kinds and expects a `survivors` key in its gaps file.
2. The witness grid cannot classify this population, by construction:
   `tools/lib_mutant_witness.py` states it "only tries functions whose
   parameters are all plain numbers" and says NOT-TRIED for the rest.
   111 of the 120 sampled entries carry the R15 reason "a parameter
   is a list, string or record" and the other 9 "no number input runs
   cleanly", so the numeric grid has no inputs to drive them with.
   Body reading (R48's method) was used instead.
3. Same-tag multiplicity: a tag does not identify a mutant. Reports
   and tools must record the exact changed line (as the appendix
   does), not just the tag, or two different mutants will be conflated
   — as nearly happened here with `simpson` K:1.
4. The 77-entry discrepancy between R15's own score summary (818
   NOT-TRIED) and its witness file (741 NOT-TRIED) remains unexplained
   in-tree. Until it is resolved, "818" should not be quoted as the
   size of the undecided population.

## NOT RUN

- Windows / WSL (no Windows environment here; nothing in this round
  touches Windows-specific code).
- Browser automation (no browser component in this round).
- The guard was not re-run: this round made no tree changes, so there
  is nothing new for the guard to compare.

## Files and verification

- Sample: 120 entries, seed 20261028, drawn from the 741 NOT-TRIED
  entries of `Claude-to-Sarvam/evidence-r15/proofs/lib-mutant-witness.json`.
- Harness restores were verified by SHA-256 after every mutant; the
  work copy is a fresh extraction of origin/main and the original
  tree is untouched (only the pre-existing untracked `build/`
  directory, which is never uploaded).
- Per-function score outputs for the WS3 re-check were produced by
  `tools/lib_mutant_score.py` (the whole-madhava-module run is the
  slowest, a few minutes; most single functions take seconds — e.g.
  kuttaka 44 s, brahmagupta_kshetr 2 s in this rebuild).

## Appendix A — all 78 missed mutants (function, chosen mutant, exact change, verdict, reason)

### Verdict (a)

| Function | Mutant | Change | Reason |
|---|---|---|---|
| aadhar.brihat_ank_tak | A:*@L45 | L45: `    vitti rev = nirmmita(c * 4 * 8)` → `    vitti rev = nirmmita(c + 4 * 8)` | Allocation shrink masked: rev = nirmmita(c*4*8) becomes nirmmita(c+4*8). Proofs use small c and check the converted digits, never the allocation size, so the undersized buffer goes unnoticed. Distinguishing: a large c where the buffer must actually hold c digits. |
| aadhar.brihat_ank_tak | K:16@L26 | L26: `    yadi (b > 16) { nivartanam 0 }` → `    yadi (b > 17) { nivartanam 0 }` | Base 17 accepted: the guard b > 16 becomes b > 17, so base 17 (which needs digits beyond the letter range) is accepted instead of rejected. Distinguishing: base 17 input. Proofs test bases up to 16 only. |
| anukram.anukram_grah_aayam_purva | K:1@L118 | L118: `    yadi (p2 == 0 - 1) { nivartanam 0 - 1 }` → `    yadi (p2 == 0 - 1) { nivartanam 0 - 2 }` | Return-value change, not a check change: the chosen mutant flips the inner-read-failure return -1 -> -2 (the p2==-1 check still fires). Distinguishing: a buffer/pos where the inner i64 read fails, asserting the return is exactly -1 rather than merely negative. Proofs never trigger an inner-read failure. |
| anukram.anukram_grah_i64 | C4:>=->>@L77 | L77: `    yadi (top >= 128) {` → `    yadi (top > 128) {` | Top-byte boundary: top >= 128 becomes top > 128, so a top byte of exactly 128 (i64 MIN) is treated as a positive value instead of a negative one. Distinguishing: an 8-byte encoding whose top byte is exactly 128. Proofs test top bytes above and below 128, never exactly 128. |
| brihat.brihat_ank_se_laghu | A:-@L34 | L34: `    vitti minv = (0 - 9223372036854775807) - 1` → `    vitti minv = (0 + 9223372036854775807) - 1` | MIN constant becomes MAX-1: minv = (0-MAX)-1 becomes (0+MAX)-1 = 9223372036854775806. The ismin check then fires for the wrong value (MAX-1, which gets |MIN| digits) and never for true MIN (which keeps the documented negative-digit behaviour). Distinguishing: v = MAX-1 or v = MIN. Proofs test neither boundary for this function. |
| brihat.brihat_bhajshesh | R (manual nivartanam) | manual R: every `nivartanam e` → `nivartanam (e) + 1` | Return code never asserted: every nivartanam e becomes nivartanam (e) + 1 (2 sites). Proofs check the out-arrays, never the return code, so a wrong return value passes. Distinguishing: assert the return value on any call. |
| brihat.brihat_ghatmod | A:*@L331 | L331: `    vitti bcur = nirmmita(c * 8)` → `    vitti bcur = nirmmita(c + 8)` | Allocation shrink masked: bcur = nirmmita(c*8) becomes nirmmita(c+8). Proofs use c=8 and check the result, which stays correct because the overflow lands in scratch rewritten before use. Distinguishing: a larger c where the buffer must actually hold c limbs. |
| brihat.brihat_shesh | R (manual nivartanam) | manual R: every `nivartanam e` → `nivartanam (e) + 1` | Return code never asserted: every nivartanam e becomes nivartanam (e) + 1 (4 sites). Proofs check the out-arrays, never the return code, so a wrong return value passes. Distinguishing: assert the return value on any call. |
| ganita.chakravala | C20:>->>=@L141 | L141: `        yadi (b != 0 && mm > 9223372036854775807 / b) { nivartanam 0 }` → `        yadi (b != 0 && mm >= 9223372036854775807 / b) { nivartanam 0 }` | Overflow-boundary case: mm > MAX/b becomes mm >= MAX/b, so the exact-boundary product mm == MAX/b is newly rejected as overflow. Distinguishing: an input where the product lands exactly on the boundary. Proofs test interior overflow, not the exact boundary. |
| ganita.chakravala | K:1@L109 | L109: `        yadi (d < 0 && r != 0) { t = t - 1 }` → `        yadi (d < 0 && r != 0) { t = t - 2 }` | Exact-boundary case: the adjustment t = t - 1 becomes t = t - 2 in the d < 0 && r != 0 branch, so an exact-boundary candidate is shifted by one extra step. Distinguishing: an input hitting that branch exactly. Proofs sweep interior cases, not the exact boundary. |
| ganita.ganita_janchit_gun | K:1@L291 | L291: `        yadi (x == 0 - 1) {` → `        yadi (x == 0 - 2) {` | MIN-times-minus-one edge: the check x == 0 - 1 becomes x == 0 - 2, so the (-1, MIN) overflow case is no longer recognised and takes the plain-multiply path. Distinguishing: x = -1 with the other operand MIN. Proofs test other overflow pairs, not (-1, MIN). |
| ganita.ganita_janchit_nyun | K:0@L251 | L251: `                okp[0] = 0` → `                okp[1] = 0` | Wrong-cell ok write, masked by call order: the chosen mutant writes the overflow ok flag to ok[1] instead of ok[0] in the x>=0,y<0,d<0 branch (hit by nyun(max,-1)). The proof does call exactly this branch, but the preceding nyun(min,1) call already left ok[0]=0, so the wrong-cell write is invisible. Distinguishing: nyun(max,-1) as the first call, or with ok[0] preset to 1, asserting ok[0]==0. Verified by direct run: mutant output identical to golden. |
| kalana.simpson | A:-@L39 | L39: `    yadi ((n - 1) - ((n - 1) / 2) * 2 == 1) { n = n - 1 }` → `    yadi ((n - 1) - ((n + 1) / 2) * 2 == 1) { n = n - 1 }` | Even-count guard never fires: the chosen mutant changes the second (n-1) to (n+1), so the expression becomes (n-1) - ((n+1)/2)*2, negative for every n>=2 and never ==1. Distinguishing: any even point count, e.g. 4 points of x^2 on 0..3: real 2.666667 (drops to 3 points), mutant 7.000000. Proofs use only odd point counts. |
| khand.khand_ant | K:0@L427 | L427: `    vitti i = 0` → `    vitti i = 1` | First-byte-only suffix mismatch missed: the comparison loop starts at i = 1 instead of i = 0, so a suffix differing only in its first byte is reported as matching. Distinguishing: source and suffix differing only in the first byte (e.g. "ab" vs "xb"). Proofs test matching and fully-different suffixes, never a first-byte-only difference. Verified by direct run: real 0, mutant 1. |
| khand.khand_bandh | D@L52 | L52: `    akshar_rakh(dst, cnt, 0)` → `` | Terminator deleted: akshar_rakh(dst, cnt, 0) is removed, so the joined output is unterminated. Distinguishing: pre-filled output buffer, any input. Proofs use zeroed buffers. |
| khand.khand_viparyay | D@L489 | L489: `    akshar_rakh(dst, n, 0)` → `` | Terminator deleted: akshar_rakh(dst, n, 0) is removed, so the reversed output is unterminated. Distinguishing: pre-filled output buffer, any input. Proofs use zeroed buffers. |
| nighantu.nighantu_anwesh | K:1@L90 | L90: `    yadi (kn < 0) { nivartanam 0 - 1 }` → `    yadi (kn < 0) { nivartanam 0 - 2 }` | Return-value change: the kn<0 branch return -1 becomes -2, so a caller checking for exactly -1 (absent) misreads the result. Distinguishing: a lookup with negative key length, asserting the return is exactly -1. Proofs never pass a negative key length. (No proof names anwesh directly, but it executes indirectly through khip, so this is (a), not (b).) |
| roop.roop_ank | A:-@L53 | L53: `        val = 0 - val` → `        val = 0 + val` | Negation dropped: val = 0 - val becomes val = 0 + val, so negative inputs are printed without their sign (and the digit loop then runs on the still-negative value, producing an empty string). Distinguishing: any negative input (e.g. -5: real "5" with sign handling, mutant ""). Proofs cover negatives only via roop_ank_aadhar, never via roop_ank itself. Verified by direct run: real "5", mutant "". |
| roop.roop_ank | K:1@L44 | L44: `        akshar_rakh(dst, 1, 0)` → `        akshar_rakh(dst, 2, 0)` | Terminator misplaced: the zero-case terminator moves from dst[1] to dst[2], so the output string gains a garbage byte between the digit and the terminator. Distinguishing: pre-filled output buffer with val == 0. Proofs use zeroed buffers. |
| roop.roop_ank_aadhar | K:0@L92 | L92: `        akshar_rakh(dst, 0, 0)` → `        akshar_rakh(dst, 0, 1)` | Terminator value flip, not a move: the chosen mutant changes the b>36 terminator from akshar_rakh(dst, 0, 0) to akshar_rakh(dst, 0, 1), so a null-terminated read gives "\x01" instead of "". Distinguishing: base > 36, reading the output as a null-terminated string. Proofs use zeroed buffers and check the return value, not the output bytes, on this branch. |
| roop.roop_pad_dakshin | D@L292 | L292: `            akshar_rakh(dst, i, akshar(s, i))` → `` | Copy statement deleted in the w<=cnt (no-padding) branch, so output is an empty string instead of the verbatim copy. Distinguishing: width <= length. Proofs test padding cases (w>cnt) only, never the no-padding branch. |
| roop.roop_pad_madhya | C1:<=-><@L324 | L324: `    yadi (w <= cnt) {` → `    yadi (w < cnt) {` | Width-smaller-than-length case: the chosen mutant changes w<=cnt to w<cnt, so for w<cnt the function falls through with npad = w-cnt negative, left negative, and the copy loop writes at negative offsets instead of returning the verbatim copy. Distinguishing: width < length (e.g. w=2, cnt=5). Proofs test padding (w>cnt) and the w==cnt case, where both paths coincide, never w<cnt. |
| roop.roop_pad_madhya | D@L328 | L328: `            i = i + 1` → `` | Hang in the no-padding branch: the deleted i = i + 1 is the increment of the w<=cnt branch's copy loop, so for any non-empty src with width <= length the loop never advances and hangs. Distinguishing: width <= length with non-empty src. Proofs test only w>cnt padding. |
| roop.roop_sthir_mool | C5:<-><=@L504 | L504: `    yadi (v < 0.0) {` → `    yadi (v <= 0.0) {` | Zero-value sign case: v < 0.0 becomes v <= 0.0, so v == 0.0 takes the negative branch and prints "-0..." instead of "0...". Distinguishing: v = 0.0 exactly. Proofs test positive and negative values, never exactly 0.0. |
| roop.roop_varg_sahaya | K:0@L429 | L429: `    akshar_rakh(dst, wpos, 0)` → `    akshar_rakh(dst, wpos, 1)` | Terminator value flip: the final terminator changes from akshar_rakh(dst, wpos, 0) to akshar_rakh(dst, wpos, 1), so the output string is unterminated. Distinguishing: pre-filled output buffer - real terminates, mutant reads past into garbage. Proofs use zeroed buffers. (No proof names this helper directly, but it executes indirectly through the roop digit-grouping wrappers, so this is (a), not (b).) |
| samanvaya.ekaka_matrika | A:*@L46 | L46: `    nivartanam n * n` → `    nivartanam n + n` | 2x2-only invisibility: the size return n*n becomes n+n, which coincides with n*n exactly at n=2. Distinguishing: any n != 2, e.g. n=3 (9 vs 6). Proofs test 2x2 matrices only. (Function renamed from pehchan since R15.) |
| samanvaya.matrika_yoga | A:*@L71 | L71: `    yavat (k < m * n) {` → `    yavat (k < m + n) {` | 2x2-only invisibility: the element loop bound m*n becomes m+n, which coincides with m*n exactly at 2x2 (and 1xn/nx1 edge cases the proofs do not distinguish). Distinguishing: any non-2x2 matrix, e.g. 3x3 (9 vs 6 elements). Proofs test 2x2 matrices only. |
| samanvaya.rekha_manak | K:0@L150 | L150: `    vitti i = 0` → `    vitti i = 1` | Row 0 skipped: the scan starts at i = 1 instead of i = 0, so a maximum sitting in row 0 is never seen. Distinguishing: a matrix whose maximum is in row 0. Proofs never put the maximum in row 0. |
| sangrah.rakh_samroop_diff | A:*@L66 | L66: `    vitti tmpb = nirmmita(b[0] * 33 + 1)` → `    vitti tmpb = nirmmita(b[0] + 33 + 1)` | Allocation shrink masked: tmpb = nirmmita(b[0]*33+1) becomes nirmmita(b[0]+33+1). Proofs use small sets and check the diff output, never the allocation size. Distinguishing: a large set where the buffer must actually hold b[0] entries. |
| sangrah.rakh_tak_mala | A:*@L219 | L219: `    vitti scratch = nirmmita(s[0] * 32 + 1)` → `    vitti scratch = nirmmita(s[0] + 32 + 1)` | Allocation shrink masked: scratch = nirmmita(s[0]*32+1) becomes nirmmita(s[0]+32+1). Proofs use small sets and check the output array, never the allocation size. Distinguishing: a large set where the scratch buffer must actually hold s[0] entries. |
| vakyank.ank_tak_aadhar_varna | D@L180 | L180: `    dst[rlen] = 0` → `` | Terminator deleted: dst[rlen] = 0 is removed, so the converted output is unterminated. Distinguishing: pre-filled output buffer, any input. Proofs use zeroed buffers. |
| vakyank.ank_tak_aadhar_varna | K:0@L153 | L153: `        dst[0] = 0` → `        dst[1] = 0` | Invalid-base zero-write misplaced: the chosen mutant moves the failure-path zero-write from dst[0] to dst[1], so with a pre-filled buffer the output reads garbage at dst[0] instead of empty. Distinguishing: an invalid base with a pre-filled buffer. Proofs use zeroed buffers, so the misplaced write is invisible. |
| vakyank.varna_tak_ank_aadhar | D@L193 | L193: `        okp[0] = 0` → `` | Ok flag assignment deleted: okp[0] = 0 is removed on the error branch, so a failed parse leaves the caller's ok flag at its previous value. Distinguishing: an invalid input with ok[0] preset to 1, asserting ok[0] == 0. Proofs check the parsed value, not the ok flag, on this branch. |
| vakyank.varna_tak_ank_aadhar | K:102@L205 | L205: `            yadi (c <= 102) { d = c - 87 }` → `            yadi (c <= 103) { d = c - 87 }` | Letter-range extension: c <= 102 becomes c <= 103, so 'g' (103) is accepted as digit 16. Distinguishing: a base-17+ input containing 'g'. Note the mutant is mathematically correct for bases 17-36; the real limitation is the letter range. Proofs use bases up to 16 and digits within range. |
| vakyank.varna_tak_dashm | C18:<-><=@L327 | L327: `                    yadi (c2 < 48) {` → `                    yadi (c2 <= 48) {` | Exponent-'0' rejected: c2 < 48 becomes c2 <= 48, so an exponent digit '0' (48) is treated as a non-digit and the parse fails. Distinguishing: any exponent containing '0', e.g. "1e10". Proofs test exponents without '0'. |
| vakyank.varna_tak_dashm | K:0@L434 | L434: `            okp[0] = 0` → `            okp[0] = 1` | Ok flag flipped: okp[0] = 0 becomes okp[0] = 1 on the error branch, so a failed parse reports success. Distinguishing: an invalid dasham input, asserting ok[0] == 0. Proofs check the parsed value, not the ok flag, on this branch. |
| varna.varna_chhid | D@L377 | L377: `            go = 0` → `` | Hang on all-spaces input: the deleted go = 0 is the exit assignment of the leading-space loop's lo >= slen branch, so when the input is all spaces (or empty) the loop never terminates. Distinguishing: an all-spaces input. Proofs trim only inputs containing non-space characters. |
| varna.varna_chhid | K:0@L373 | L373: `    vitti lo = 0` → `    vitti lo = 1` | Leading-space skip starts at lo = 1 instead of lo = 0, so the first character is dropped even when it is not a space. Distinguishing: input with no leading space (e.g. "abc" -> mutant "bc"). Proofs trim only space-padded inputs. Verified by direct run: real "abc", mutant "bc". |
| varna.varna_viparyay | D@L529 | L529: `    dst[n] = 0` → `` | Final terminator deleted. Distinguishing: pre-filled output buffer, any input. Proofs use zeroed buffers, so the byte after the output is already 0. |
| varna.varna_viparyay | K:0@L514 | L514: `        dst[0] = 0` → `        dst[0] = 1` | Terminator value flip: the empty-input terminator changes from dst[0] = 0 to dst[0] = 1, so a null-terminated read gives "\x01" instead of "". Distinguishing: empty input, reading the output as a null-terminated string. Proofs use zeroed buffers and compare by length. |
| varna.varna_viparyay | K:0@L529 | L529: `    dst[n] = 0` → `    dst[n] = 1` | Terminator value flip: the final terminator changes from dst[n] = 0 to dst[n] = 1, so a null-terminated read gives the output plus a 0x01 byte. Distinguishing: reading the output as a null-terminated string. Proofs compare by length or return value, not by terminator byte. |

### Verdict (c)

| Function | Mutant | Change | Reason |
|---|---|---|---|
| brihat.brihat_ank_se_laghu | K:8@L53 | L53: `                vitti d = pad8(a + j * 8) + 1` → `                vitti d = pad8(a + j * 9) + 1` | Equivalent: the stride j*8 -> j*9 sits in the MIN-only carry loop, and carry clears at j=0 because MIN's least digit is 7 (7+1=8, not 10), so the misaligned read at j>=1 is never reached. |
| ganita.ganita_janchit_nirapeksh | C2:<-><=@L543 | L543: `    yadi (x < 0) { nivartanam 0 - x }` → `    yadi (x <= 0) { nivartanam 0 - x }` | Equivalent: x<0 becomes x<=0, but x==0 gives 0 - 0 = 0 either way, identical to abs(0). |
| ganita.ganita_janchit_yuj | C2:>=->>@L223 | L223: `        yadi (y >= 0) {` → `        yadi (y > 0) {` | Equivalent: y>=0 becomes y>0, but the y==0 case is dead: with y==0 the overflow check that follows cannot trigger, and the success path assigns the same result. |
| kalana.bahu_mula | C10:<-><=@L134 | L134: `        yadi ((fm < 0.0) == (flo < 0.0)) {` → `        yadi ((fm < 0.0) == (flo <= 0.0)) {` | Equivalent: flo<0 becomes flo<=0, but flo==0.0 already returns two lines earlier, so the changed case never reaches this line. |
| kalana.bahu_mula | C5:<-><=@L126 | L126: `    yadi ((flo < 0.0) == (fhi < 0.0)) { ok[0] = 0.0; nivartanam 0.0 }` → `    yadi ((flo < 0.0) == (fhi <= 0.0)) { ok[0] = 0.0; nivartanam 0.0 }` | Equivalent: fhi<0 becomes fhi<=0, but fhi==0.0 already returns two lines earlier, so the changed case never reaches this line. |
| kalana.simpson | K:1@L39 | L39: `    yadi ((n - 1) - ((n - 1) / 2) * 2 == 1) { n = n - 1 }` → `    yadi ((n - 1) - ((n - 2) / 2) * 2 == 1) { n = n - 1 }` | Equivalent: the chosen mutant changes the second (n-1) to (n-2) in the parity expression, giving (n-1) - ((n-2)/2)*2, which equals 1 exactly when n is even, the same as the real expression. The ==1 outcome, and hence the drop decision, never differs. Verified by direct run on the 4-point x^2 program: real 2.666667, mutant 2.666667. (A different same-tag occurrence, n = n-2, does differ; the appendix records the harness-chosen occurrence.) |
| khand.khand_avanat | K:0@L387 | L387: `    yadi (slen < 0) {` → `    yadi (slen < 1) {` | Equivalent: slen<0 becomes slen<1, but slen==0 falls through to a 0-iteration loop with terminator at dst[0] and return 0 - identical to the negative branch. |
| khand.khand_gan_swar | K:0@L525 | L525: `    vitti ch = 0` → `    vitti ch = 1` | Equivalent: dead initialisation - ch = 0 becomes ch = 1, but ch is assigned from the input character before the vowel test. |
| khand.khand_mukt | C1:<=-><@L66 | L66: `    yadi (cnt <= 0) {` → `    yadi (cnt < 0) {` | Equivalent: cnt<=0 becomes cnt<0, but cnt==0 falls through to a 0-iteration loop with the same result (empty output, return 0). |
| khand.khand_pratisthap | K:0@L154 | L154: `    vitti k = 0` → `    vitti k = 1` | Equivalent: dead initialisation - k = 0 becomes k = 1, but k is reset before the copy loop that uses it. |
| khand.khand_pratisthap | K:0@L154 | L154: `    vitti k = 0` → `    vitti k = 1` | Equivalent: dead initialisation - k = 0 becomes k = 1, but k is reset before the copy loop that uses it. (Second sample draw, same mutant.) |
| khand.khand_viparyay | C1:<=-><@L473 | L473: `    yadi (n <= 0) {` → `    yadi (n < 0) {` | Equivalent: n<=0 becomes n<0, but n==0 falls through to a 0-iteration loop with terminator at dst[0] and return 0 - identical to the negative branch. |
| nighantu.nighantu_khip | K:0@L135 | L135: `    vitti start = 0` → `    vitti start = 1` | Equivalent: dead initialisation - start = 0 becomes start = 1, but start is reset before the copy loop that uses it. |
| nighantu.nighantu_kunji_gudh | K:1@L39 | L39: `    yadi (cap < 1) { nivartanam 0 }` → `    yadi (cap < 2) { nivartanam 0 }` | Equivalent, and the (b) appearance is misleading: no proof names this helper directly, but every map operation executes it indirectly via anwesh/khip. The mutant itself (cap<1 becomes cap<2) is equivalent because cap==1 gives h%1 == 0, identical to the branch return. |
| nighantu.nighantu_mil | K:0@L339 | L339: `    vitti seglen = 0` → `    vitti seglen = 1` | Equivalent: dead initialisation - seglen = 0 becomes seglen = 1, but seglen is assigned from the segment length before use. |
| nighantu.nighantu_rikta | K:0@L261 | L261: `        k = 0` → `        k = 1` | Equivalent: stale key byte - k = 0 becomes k = 1 in the slot-clearing loop, but slots are marked empty and the next insert overwrites the key bytes, so the stale byte is never read. |
| roop.roop_ank | C3:<-><=@L47 | L47: `    yadi (val < 0) {` → `    yadi (val <= 0) {` | Equivalent: val<0 becomes val<=0, but val==0 is handled by the earlier return (prints "0", length 1) and never reaches this line. |
| roop.roop_pad_dakshin | C4:<-><=@L305 | L305: `    yavat (i < npad) {` → `    yavat (i <= npad) {` | Equivalent: the pad loop runs one extra iteration writing a pad byte at dst[w], but the terminator written immediately after overwrites dst[w] with 0. The extra byte never survives. |
| roop.roop_pad_madhya | K:0@L321 | L321: `    vitti npad = 0` → `    vitti npad = 1` | Equivalent: dead initialisation - npad = 0 becomes npad = 1, but npad is assigned w - cnt before the pad loops. |
| roop.roop_pad_vam | C3:<-><=@L267 | L267: `    yavat (i < npad) {` → `    yavat (i <= npad) {` | Equivalent: the pad loop runs one extra iteration writing a pad byte at dst[w], but the terminator written immediately after overwrites dst[w] with 0. The extra byte never survives. |
| sangrah.rakh_tak_mala | C6:<-><=@L242 | L242: `        yavat (k < seglen) {` → `        yavat (k <= seglen) {` | Equivalent: the copy loop runs one extra iteration, but the extra byte written is immediately overwritten by the terminator that follows. |
| sankhyiki.laghutama | C3:<-><=@L40 | L40: `        yadi (xs[i] < m) { m = xs[i] }` → `        yadi (xs[i] <= m) { m = xs[i] }` | Equivalent: xs[i] < m becomes xs[i] <= m; when equal, m is assigned the same value it already holds. |
| sankhyiki.purna_vyapti | C1:<=-><@L175 | L175: `    yadi (n <= 0) { nivartanam 0 }` → `    yadi (n < 0) { nivartanam 0 }` | Equivalent: n<=0 becomes n<0, but n==0 falls through to a loop that runs zero times with the same result (empty output, return 0). |
| suchi.avali_pravesh | K:0@L410 | L410: `    vitti nd = 0` → `    vitti nd = 1` | Equivalent: dead initialisation - nd = 0 becomes nd = 1, but nd is assigned from the allocation result before use. |
| suchi.avali_pravesh | K:0@L411 | L411: `    vitti old = 0` → `    vitti old = 1` | Equivalent: dead initialisation - old = 0 becomes old = 1, but old is assigned from the previous buffer before use. |
| suchi.suchi_apanay | C3:<-><=@L161 | L161: `    yavat (k < lst[0] - 1) {` → `    yavat (k <= lst[0] - 1) {` | Equivalent: the shift loop runs one extra iteration past the logical length, but the extra shifted cell is beyond lst[0] and is never read as an element. |
| suchi.suchi_vardh | K:2@L74 | L74: `    ncap = lst[1] * 2` → `    ncap = lst[1] * 3` | Equivalent through the list API, and the (b) appearance is misleading: no proof names this grow helper directly, but it executes indirectly whenever a list grows. The mutant (capacity 3x instead of 2x) changes no observable behaviour because no program asserts the exact capacity, only elements and length. |
| varna.gan_swar | C1:<-><=@L67 | L67: `    yavat (i < n) {` → `    yavat (i <= n) {` | Equivalent: the count loop runs one extra iteration, but the extra iteration reads the terminator, which is never a vowel, so the count is unchanged. |
| varna.varna_gan | A:-@L547 | L547: `        f = varna_anwesh(h + pos * 8, hlen - pos, nd, nlen)` → `        f = varna_anwesh(h + pos * 8, hlen + pos, nd, nlen)` | Equivalent under proof conditions: the search window hlen - pos becomes hlen + pos, extending past the haystack's logical end, but the extra bytes searched are terminators that cannot match a non-empty string needle, so no count changes. (With a pre-filled buffer beyond the logical end the mutant could false-positive; proofs use clean buffers.) |
| varna.varna_unnat | C1:<-><=@L410 | L410: `    yadi (slen < 0) {` → `    yadi (slen <= 0) {` | Equivalent: slen<0 becomes slen<=0, but slen==0 falls through to a 0-iteration loop, terminator at dst[0], return 0 - identical to the negative branch. |

### Verdict (undecided)

| Function | Mutant | Change | Reason |
|---|---|---|---|
| khand.khand_aadi | K:0@L412 | L412: `    yadi (plen < 0) { nivartanam 0 }` → `    yadi (plen < 0) { nivartanam 1 }` | Error-return flip, not an empty-prefix change: the chosen mutant flips the plen<0 branch return 0->1, so it differs only for a negative prefix length, which is invalid input. By the R48 rule (out-of-contract-only differences are not counted as proof gaps, nor proven equivalent), left undecided. |
| khand.khand_avanat | K:0@L389 | L389: `        nivartanam 0` → `        nivartanam 1` | Out-of-contract-only difference: the chosen mutant flips the slen<0 branch return 0->1, so it differs only for a negative source length, which is invalid input. By the R48 rule, left undecided. |
| roop.roop_ank_aadhar | K:0@L80 | L80: `        akshar_rakh(dst, 0, 0)` → `        akshar_rakh(dst, 1, 0)` | Alloc-failure terminator moved from dst[0] to dst[1]. Distinguishing requires both an allocation failure (rev==0, essentially untriggerable in proofs) and a pre-filled buffer. Neither is reachable in the proof set. |
| sangrah.rakh_asti_upasamuh | K:0@L196 | L196: `    yadi (tmpa == 0) { nivartanam 0 - 1 }` → `    yadi (tmpa == 1) { nivartanam 0 - 1 }` | Alloc-failure check flipped: tmpa == 0 becomes tmpa == 1, so the allocation-failure branch is taken exactly when allocation succeeded and vice versa. Distinguishing requires an allocation failure, essentially untriggerable in proofs. Left undecided, not counted as a proof gap. |
| suchi.avali_pravesh | K:0@L418 | L418: `        yadi (nd == 0) { nivartanam 0 }` → `        yadi (nd == 0) { nivartanam 1 }` | Alloc-failure return flip (both draws chose this same occurrence): the chosen mutant flips the allocation-failure return 0->1, so a failed allocation reports success. Distinguishing requires an allocation failure, essentially untriggerable in proofs. Left undecided, not counted as a proof gap. |
| suchi.avali_pravesh | K:0@L418 | L418: `        yadi (nd == 0) { nivartanam 0 }` → `        yadi (nd == 0) { nivartanam 1 }` | Alloc-failure return flip (second sample draw, same occurrence as the first): the chosen mutant flips the allocation-failure return 0->1, so a failed allocation reports success. Distinguishing requires an allocation failure, essentially untriggerable in proofs. |
| vakyank.ank_tak_aadhar_varna | K:0@L148 | L148: `        dst[0] = 0` → `        dst[1] = 0` | Alloc-failure + pre-filled-buffer case: the chosen mutant moves the failure-path zero-write from dst[0] to dst[1] (allocation failure, rev==0). Distinguishing requires both an allocation failure, essentially untriggerable in proofs, and a pre-filled buffer. Neither is reachable in the proof set. |

## Appendix B — all 42 caught mutants (function, chosen mutant, failing proofs)

| Function | Mutant | Failing proofs |
|---|---|---|
| varna.varna_unnat | D@L419 | FAIL r8_text_edges:; FAIL string_case_trim: |
| suchi.chay_avalok | K:0@L354 | FAIL list_stack: |
| shreni.mil_shreni_punar | K:0@L184 | FAIL containers21:; FAIL containers23:; FAIL r10_roop_suchi_edges:; FAIL sort_merge: |
| khand.khand_gan | K:0@L505 | FAIL gaps19: |
| suchi.avali_avalok | K:0@L462 | FAIL list_queue: |
| khand.khand_tul | C3:<-><=@L452 | FAIL containers20:; FAIL gaps19:; FAIL gaps23:; FAIL map_basic:; FAIL map_clear:; FAIL map_keys_bytes:; FAIL map_remove:; FAIL r11_nighantu_edges:; FAIL r11_sets_lists:; FAIL r8_map_model:; FAIL set_basic:; FAIL set_difference:; FAIL set_intersect:; FAIL set_subset:; FAIL set_union:; FAIL slices23:; FAIL strb_cell_pairs:; FAIL string_strb_split_join:; FAIL string_strb_starts_compare:; FAIL string_strb_trim_case: |
| anukram.anukram_grah_ashtak | K:0@L119 | FAIL r11_misc_edges:; FAIL r37_bounds:; FAIL serial29: |
| roop.roop_pad_madhya | D@L347 | FAIL fmt_pad: |
| roop.roop_ank_aadhar | D@L125 | FAIL fmt_group:; FAIL fmt_int_base:; FAIL fmt_min:; FAIL fmt_pad:; FAIL fmt_signed: |
| varna.varna_viparyay | D@L527 | FAIL strb_cell_pairs: |
| varna.asti_sarv_ank | K:1@L109 | FAIL string_is_all_digits: |
| khand.khand_unnat | D@L373 | FAIL r8_bytes_edges:; FAIL string_strb_trim_case: |
| vakyank.varna_tak_ank | K:0@L90 | FAIL strconv_int_str: |
| khand.khand_chhid | D@L340 | (timeout; see §1) |
| shreni.mil_shreni_punar | K:0@L183 | FAIL containers21:; FAIL containers23:; FAIL r10_roop_suchi_edges:; FAIL sort_merge: |
| sangrah.rakh_tak_mala | A:+@L258 | FAIL r11_sets_lists:; FAIL set_to_array:; FAIL set_union: |
| nighantu.nighantu_vardh | A:+@L301 | FAIL containers20:; FAIL r11_nighantu_edges: |
| roop.roop_varg_mool | K:3@L412 | FAIL fmt_group: |
| nighantu.nighantu_kunjika_ashtak | K:0@L418 | FAIL containers20:; FAIL gaps19:; FAIL gaps23:; FAIL map_keys_bytes:; FAIL r11_nighantu_edges:; FAIL r11_sets_lists:; FAIL r39_scratch_from_set:; FAIL r8_map_edges:; FAIL set_difference:; FAIL set_intersect:; FAIL set_subset:; FAIL set_to_array:; FAIL set_union: |
| khand.khand_pratilip | K:0@L94 | FAIL slices23: |
| ganita.chakravala | C4:!=->==@L103 | FAIL chakravala29:; FAIL ganita_chakravala:; FAIL r8_chakravala_sweep: |
| sankhyiki.laghutama | K:1@L38 | FAIL sankhyiki_laghutama: |
| nighantu.nighantu_kunjika_ashtak | K:0@L420 | FAIL containers20:; FAIL gaps19:; FAIL gaps23:; FAIL map_keys_bytes:; FAIL r11_sets_lists:; FAIL r8_map_edges:; FAIL set_difference:; FAIL set_intersect:; FAIL set_subset:; FAIL set_to_array:; FAIL set_union: |
| brihat.brihat_gun | A:*@L160 | FAIL bigint_divzero:; FAIL bigint_mul:; FAIL bigint_powmod: |
| nighantu.nighantu_mil | K:0@L337 | FAIL gaps23: |
| khand.khand_yuj | K:0@L288 | FAIL r11_khand_varna:; FAIL string_strb_split_join: |
| shreni.asti_sorted | K:1@L104 | FAIL containers23:; FAIL sort_is_sorted: |
| roop.roop_ank_aadhar | K:1@L118 | FAIL fmt_min:; FAIL r10_roop_suchi_edges: |
| suchi.suchi_vinimay | K:0@L179 | FAIL containers20:; FAIL r8_list_model: |
| nighantu.nighantu_apanay | K:0@L208 | (timeout; see §1) |
| vakyank.ank_tak_aadhar_varna | D@L173 | FAIL r8_base_digits:; FAIL strconv_base: |
| roop.roop_ank_aadhar | D@L139 | FAIL fmt_group:; FAIL fmt_int_base:; FAIL fmt_min:; FAIL fmt_pad:; FAIL fmt_signed: |
| khand.khand_bandh | K:0@L43 | FAIL r11_khand_varna:; FAIL set_difference:; FAIL set_intersect:; FAIL set_to_array:; FAIL set_union:; FAIL strb_pack_unpack:; FAIL string_strb_split_join: |
| anukram.anukram_khip_i64 | A:-@L50 | FAIL serial29: |
| vakyank.varna_tak_dashm | D@L340 | FAIL breadth26: |
| ganita.ganita_janchit_nyun | K:0@L258 | FAIL ganita_checked:; FAIL r8_result_flags:; FAIL safety25: |
| shreni.nivesh_shreni | K:1@L154 | FAIL sort_insertion: |
| khand.khand_yuj | K:1@L307 | FAIL string_strb_split_join: |
| suchi.avali_avalok | D@L465 | FAIL r8_list_model: |
| vakyank.pad_vam | D@L254 | FAIL strconv_pad: |
| nighantu.nighantu_rikta | K:0@L255 | FAIL containers_clear:; FAIL map_clear:; FAIL r11_nighantu_edges:; FAIL r9_guard_cells2: |
| roop.roop_pad_madhya | D@L333 | FAIL fmt_pad: |
