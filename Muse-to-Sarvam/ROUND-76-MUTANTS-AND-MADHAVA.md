# Sutram — ROUND-76: the 15 mutants, and the sign error in the Madhava series

**Base:** main at v273 (commit 3f365564) · **Compiler:** v273, built from `src/r68_compiler_entry.asm`
· **Deliverable:** this report + `r76_madhava_sign.sm/.out/.exit` (a test for
`tests/stdlib/`, placed here in the outbox for Sarvam to land — this round
authorizes no direct-to-main change) · **No tree changes.**

## The headline, first

**The shipped Madhava code has no sign error.** I swept all five functions
against Python's `math` at 16 points — every value matches to all 6 printed
decimals (table in WS1). The "sign error" is a **mutant**: a sign flip no
proof killed at R15. **12 of the 15 are killed today by the R18 tests, 1 is
moot (its function no longer exists), and 2 still survive** — the two
`suchi`/`avali_srij` size mutants, with a current witness below.

Provenance of the "15": R15-03's witness search found 23 mutants an input
tells apart; 15 of them are clear defects inside the function's contract, in
8 functions (`Claude-to-Sarvam/R15-03-PROOF-STRENGTH.md`, "The 23 witnesses").
The other 8 were out-of-contract inputs and are not counted here.

## WS1 — the Madhava sign error

### 1. Which function, which term, which sign

There is not one sign flip but one sign-error *class* in three functions,
all in the argument reduction / sign-return, never in the series terms:

| Function | The flip | Effect |
|---|---|---|
| `madhava_sin`, `madhava_cos` | Negative-branch adjustment: `y = y + pi2` → `y = y - pi2` (R15 `A:+@L56` / `A:+@L76`) | `sin(-18)`: **0.750987 → 0.770223**; `cos(-18)`: **0.660317 → 0.606488** |
| `madhava_sin`, `madhava_cos` | Positive-branch adjustment: `y = y - pi2` → `y = y + pi2` (verified by construction this round) | `sin(10)`: **-0.544021 → -0.544127**; `sin(4)`: **-0.756802 → -0.757068** |
| `madhava_atan` | Negative-branch return: `nivartanam 0.0 - r` → `nivartanam r` (R15 `A:-@L104`) | `atan(-20)`: **-1.520838 → +1.520838 — the sign lost entirely** |
| `madhava_atan` | Same return via `neg == 1` → `neg == 2` (R15 `K:1@L104`, verified by construction this round) | `atan(-20)`: **-1.520838 → +1.520838** |

The purest "sign error" is atan's: the answer is exactly right in magnitude
and exactly wrong in sign. The sin/cos ones are reduction errors: the series
is evaluated at an unreduced argument, so the answer is close but wrong
(2e-2 off for sin(-18), 5e-2 off for cos(-18)).

Why the R15 proofs missed them: no proof took `x` below -pi (sin/cos
negative branch) or atan's negative branch for `|x| > 1`. The R18 test
(`tests/stdlib/r18_madhava_reduction.sm`) now covers exactly those inputs,
and it matches its golden on v273 (verified by run this round) — so all
nine Madhava mutants of the 15 are killed today.

Two further sign-shaped mutants survive the *golden* tests but not the full
proof set, and the distinction matters:

- sin/cos positive-reduction flip (`y - pi2` → `y + pi2`): no golden test
  calls sin/cos with `x > pi` (r18's `sin(3.0)` sits just below pi), so it
  survives every golden — but `proof_props` edge30_float tests sin(10) and
  cos(10), which kill it. Golden-surviving, prop-killed.
- atan's `|x| <= 1` negative-return flip (`nivartanam 0.0 - res` →
  `nivartanam res`): no golden tests atan of a negative `|x| <= 1` value
  (r18's atan(-1.5) takes the `|x| > 1` branch), so it survives every golden
  — mutant `atan(-0.5) = +0.463648` vs true `-0.463648` — but edge30_float
  tests atan(-1.0), which kills it. Golden-surviving, prop-killed.

The lesson is narrow: the golden suite still has no positive-reduction
sin/cos test and no negative-small atan test. The delivered test closes
both without depending on the props.

### 2. The test that would have caught it

`r76_madhava_sign.sm` (delivered alongside this report, golden verified on
v273). Eight known values, each independently computed, not recorded from
the implementation:

| Call | Golden | Kills |
|---|---|---|
| `madhava_sin(pi/2)` | 1.000000 | term-sign flips (see below) |
| `madhava_cos(0)` | 1.000000 | regression anchor only — see note |
| `madhava_sin(4.0)` | -0.756802 | positive-reduction flip (mutant -0.757068) |
| `madhava_sin(10.0)` | -0.544021 | positive-reduction flip (mutant -0.544127) |
| `madhava_sin(-18.0)` | 0.750987 | negative-reduction flip (mutant 0.770223) |
| `madhava_cos(-18.0)` | 0.660317 | negative-reduction flip (mutant 0.606488) |
| `madhava_atan(-0.5)` | -0.463648 | small-negative return flip (mutant +0.463648) |
| `madhava_atan(-20.0)` | -1.520838 | sign-loss flip (mutant +1.520838) |

Wrong output before the fix / right output after, on the killing inputs
("before" = the mutant's output, "after" = the shipped code's output — the
shipped code is already right, so there is no code fix to report; the fix
this round delivers is the test):

- `sin(-18)`: mutant 0.770223 → shipped 0.750987 (true: 0.750987…)
- `cos(-18)`: mutant 0.606488 → shipped 0.660317 (true: 0.660317…)
- `atan(-20)`: mutant +1.520838 → shipped -1.520838 (true: -1.520838…)
- `sin(10)`: mutant -0.544127 → shipped -0.544021 (true: -0.544021…)
- `atan(-0.5)`: mutant +0.463648 → shipped -0.463648 (true: -0.463648…)

Note on the brief's suggested values: `sin(pi/2) = 1` catches a term-sign
flip in any term down to about y^11/11! at 6 printed decimals, and the
reduction caps |y| at pi, so higher-term flips are below float precision
and exactly equivalent, not missed bugs. `cos(0) = 1` catches **nothing**:
every series term vanishes at 0, so any sign flip still prints 1.000000.
It is in the test as a regression anchor, not as a sign detector — a test
that only checked cos(0) would pass a completely sign-broken cosine.

### 3. The rest of `lib/madhava.smlib` — does every alternating series alternate correctly?

Yes. Verified term by term against the mathematical series, and numerically
at the sweep points below (shipped output vs Python `math`, all equal to
6 decimals):

| Function | Series | Check |
|---|---|---|
| `madhava_pi` | sqrt(12)·Σ(-1)^k/((2k+1)·3^k) | sign alternates via util_chinha; pi = 3.141593 ✓ |
| `madhava_sin` | y - y³/3! + y⁵/5! - … | recurrence negates each term; division (2n)(2n+1) correct |
| `madhava_cos` | 1 - y²/2! + y⁴/4! - … | recurrence negates each term; division (2n-1)(2n) correct |
| `madhava_atan` | x - x³/3 + x⁵/5 - …, with 2·atan(x/(1+√(1+x²))) reduction and pi/2 - atan(1/x) for \|x\| > 1 | sign alternates via util_chinha; both identities exact, both sign branches correct |
| `madhava_vargmool` | Newton, not alternating | (g + v/g)/2; sqrt(2) = 1.414214 ✓ |

Sweep (shipped → Python): sin(pi/2) 1.000000, sin(3) 0.141120, sin(-3)
-0.141120, sin(10) -0.544021, sin(100) -0.506366, cos(pi/2) 0.000000, cos(3)
-0.989992, cos(-3) -0.989992, cos(10) -0.839072, atan(0.5) 0.463648, atan(1)
0.785398, atan(-1) -0.785398, atan(20) 1.520838, atan(-20) -1.520838, pi
3.141593, sqrt(2) 1.414214 — all match.

## WS2 — the other 14

Each row: what the mutant changes, whether any existing test notices it
**today on v273**, and severity — WRONG (a materially incorrect answer,
crash, or corruption) vs DIFFERENT (the same value to the precision the
library prints, or a last-digit rounding difference).

| # | Mutant | What it changes | Test notices today? | Severity |
|---|---|---|---|---|
| 1 | `sadhan.util_chinha` K:0 | sign(1): 1 → 0 | **MOOT** — the function no longer exists; madhava now uses local `util_chinha` variables, and the pi/atan tests pin the alternation | was WRONG |
| 2 | `ank.ank_gan` K:0 | digit count of -9: 1 → 2 | **KILLED** — `r18_sign_digits_kramgun` tests ank_gan(-9) → 1 | was WRONG |
| 3 | `ganita_paripurna_kramgun` K:MAX | 1e9! : MAX (saturated) → crash | **KILLED** — `r18_sign_digits_kramgun` tests kramgun(1e9) → MAX | was WRONG (crash) |
| 4 | `suchi_srij` A:* | byte size `c*8` → `c+8`; 3037000499: 0 → a handle | **NO — STILL SURVIVES** (see below) | **WRONG, dangerous** |
| 5 | `avali_srij` A:* | same shape; 3037000499: 0 → a handle | **NO — STILL SURVIVES** (see below) | **WRONG, dangerous** |
| 6 | `avali_srij` K:0 | MAX: 0 → 1 | **KILLED** — `r18_srij_overflow_guard` tests avali_srij(MAX) → 0 | was WRONG |
| 7 | `madhava_sin` N@L56 | negated reduction condition; sin(3): 0.141120 → 0.141111 | **KILLED** — r18 tests sin(3.0) → 0.141120 | was WRONG (small, 9e-6) |
| 8 | `madhava_sin` A:-@L56 | negative-branch sign; sin(-18): 0.750987 → 0.770223 | **KILLED** — r18 tests sin(-18) | was WRONG |
| 9 | `madhava_sin` A:+@L56 | negative-branch sign (same witness) | **KILLED** — r18 tests sin(-18) | was WRONG |
| 10 | `madhava_cos` N@L76 | negated reduction condition; cos(2): -0.416147 → -0.416148 | **KILLED** — r18 tests cos(2.0) | DIFFERENT (1 last-digit ulp; the mutant path is the periodic identity, truncated, not a wrong value at 5 decimals) |
| 11 | `madhava_cos` A:-@L76 | negative-branch sign; cos(-18): 0.660317 → 0.606488 | **KILLED** — r18 tests cos(-18) | was WRONG |
| 12 | `madhava_cos` A:+@L76 | negative-branch sign (same witness) | **KILLED** — r18 tests cos(-18) | was WRONG |
| 13 | `madhava_atan` N@L98 | negated `ax < 0` test; atan(-20): -1.520838 → -1.520817 | **KILLED** — r18 tests atan(-20) | was WRONG (small, 2.1e-5 — the reduction identity is exact, so the mutant nearly works) |
| 14 | `madhava_atan` K:1@L104 | `neg == 1` → `neg == 2`; atan(-20) → +1.520838 (verified by construction this round) | **KILLED** — r18 tests atan(-20) → -1.520838 | was WRONG (sign lost) |

(The 15th is atan's `A:-@L104`, the sign loss in WS1.)

**The two that still survive, in detail.** The R18 guard test
(`r18_srij_overflow_guard`) uses wrap-values (2^61+1, 2^60, 2^60-1, MAX),
for which the mutant also returns 0 — a mutant buffer of `c+8` bytes at
those capacities still cannot be allocated, so the test cannot tell it
apart. Verified by construction this round: a `suchi_srij` copy with
`sz = c + 8` returns 0 on all four r18 inputs (matching the golden) but
returns a handle for 3037000499, where the shipped code returns 0 (24 GB
refused, 3 GB granted, on this machine). Worse, the mutant is wrong even
where allocation succeeds: a list claiming capacity `c` backed by `c+8`
bytes corrupts memory on any fill past ~c/8 cells, silently — the handle
is indistinguishable from a valid list. The R18 test pins the *wrap*
guard; it does not pin the *size computation*. A test with the R15
witness input (3037000499, expecting 0) would kill both mutants — but the
r18 comment records why that input was dropped: on a machine that grants
24 GB it is flaky. A machine-independent kill needs a capacity where the
real size fails and the mutant size succeeds on every machine, which does
not exist for this shape; the honest fix is a test that fills a small
list to capacity and reads it back, which the size mutant corrupts.

**Count:** of the 15 — 12 killed by R18, 1 moot, 2 still surviving.

## WS3 — the library against known values

### How many have a known-value test?

For the four audited modules, all of them. The census below counts a test
as known-value only if its expected output can be checked without running
the implementation — a mathematical constant, a closed form, a published
identity, or a documented spec (saturation, guard, ok-channel). A golden
recorded from an arbitrary input with no independent check would count as
golden-only; **no function in these four modules falls in that bucket**.

| Module | Functions | With a test | Known-value test | Golden-only |
|---|---|---|---|---|
| madhava | 5 | 5 | 5 | 0 |
| ganita | 22 | 22 | 22 | 0 |
| sankhyiki | 16 | 16 | 16 | 0 |
| chandas | 6 | 6 | 6 | 0 |
| **Total audited** | **49** | **49** | **49** | **0** |

Coverage notes: ganita's 22 include 6 functions covered only through the
shared checked/saturating files (`gaps19`, `gaps20`, `safety24`,
`safety25`, `result_chain`) rather than dedicated files — `janchit_ghat`,
`paripurna_ghat`, `paripurna_bhaj`, `paripurna_shesh`,
`janchit_nirapeksh`, `paripurna_nirapeksh`. Their goldens are spec-derived
under the same overflow/saturation rules verified below, not
implementation-recorded, so they count as known-value; I verified the
family's rules, not every line of those five files.

For the full 305: this round does not give that number, and I will not
invent it. The census above is the method (per function: does a test
assert a value checkable without the implementation?), and it extends
mechanically to the other 20 modules. What this round does establish is
the pattern for the mathematical core: 49/49.

### Are there goldens here that record wrong answers?

**No — not one, in the four modules audited.** Every golden I checked
against an independent value matches. The checks, by module:

- **madhava:** all 5 functions vs Python `math` (16 sweep points + all
  dedicated goldens + r18's 9 values) — all match to 6 decimals.
- **ganita:** kuttaka (3,7,1)→5, (10,6,4)→4, (2,4,2)→1 — each solves
  ax ≡ c (mod b) ✓; chakravala(2)→(3,2), (3)→(2,1) — both satisfy
  x² - ny² = 1 minimally ✓; samasa(1,1,2,1,2)→(4,3) — Brahmagupta's
  composition: 4² - 2·3² = -2 = (1-2)(4-2) ✓; brahmagupta_kshetr
  (3,4,5,0)→6 (Heron, 3-4-5 triangle) and (4,4,4,4)→16 (square) ✓;
  isqrt 16→4, 15→3, 0→0, 100→10 ✓; abs -5→5, 7→7, 0→0 ✓; the checked
  family (overflow → 0 + ok 0; MIN·-1 and MIN/-1 reported, not SIGFPE;
  -7/2 → -3, -7%2 → -1, truncation toward zero) ✓; the saturating family
  (MAX/MIN saturation at every edge, 6·7 → 42) ✓; factorials 5! → 120,
  20! → 2432902008176640000, 21! and 100! → MAX, 0! → 1, (-1)! → 0 ✓.
- **sankhyiki:** sum [1,2,3,4] → 10, mean → 2.5, min/max/range on
  [1,5,3] and [2,2] ✓; population variance [1..5] → 2 (not the sample
  variance 2.5 — the golden pins the population convention explicitly),
  stddev → √2 = 1.414214 ✓; dot [1,2,3]·[4,5,6] → 32,
  [1.5,2.5]·[2,4] → 13 ✓; norm [3,4] → 5, [1,2,2] → 3 ✓; integer
  variants (mean truncates toward zero: [1,2] → 1, [-3,0] → -1, not
  floor) ✓.
- **chandas:** meru(5,2) → 10, (6,3) → 20, (4,0) → 1, (3,5) → 0 —
  binomial coefficients ✓; matra_meru 1 → 1, 2 → 1, 10 → 55 —
  Fibonacci, Pingala's mora-count ✓; guru_gan popcount 0 → 0, 7 → 3,
  8 → 1 ✓; asti_guru bits of 5: 1, 0, 1 ✓; meru_mala row 4 →
  [1,4,6,4,1] ✓; dwi_ghat 2^n: 0 → 1, 5 → 32, 10 → 1024 ✓.

One caution for the reader: `proof_lib` passes 226/226 on v273, but that
only proves the goldens match the current code. The audit above is the
separate step — goldens matched against values computed without the
implementation — and it is that step which finds nothing wrong here. The
parser question from before got the same answer; the mathematics gets it
again. The two surviving srij mutants in WS2 are the counterexample that
keeps the distinction honest: a behaviour can pass every golden and
still be wrong, which is why the known-value check, not the golden, is
the unit that matters.

## Verification status

- Built v273 from `src/r68_compiler_entry.asm`; `proof_lib` 226/226 on
  v273.
- All mutant constructions run as standalone programs (functions copied
  before a braced mukhya — note: nothing may follow a *braced* mukhya's
  closing brace on v273, per the 261 rule; an indented mukhya still
  accepts trailing definitions, which is why the reference §6 example
  still compiles).
- R15 witness values re-confirmed by construction where the code path
  still exists: sin(-18) negative-branch mutant = 0.770223 exactly as
  R15 recorded; atan neg==2 mutant = +1.520838 for atan(-20).
- NOT RUN: Windows, browser, implementation (no code fix is proposed
  here — the deliverable is the test and the list; the srij size fix and
  the test landing belong to their owners).
