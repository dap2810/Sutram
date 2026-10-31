# Sutram — ROUND-80: does the library overflow on ordinary inputs?

**Base:** main at 55540ced, compiler v275
· **Deliverable:** this report (the table is the deliverable)
· **No tree changes.** The language findings at the end are evidence for
Claude's parallel R80 language brief, not fixes from this round.

## The premises, re-verified on v275

`9223372036854775807 + 1` → `-9223372036854775808`. `4000000000 *
4000000000` → `-2446744073709551616`. `1 / 0` → SIGFPE, exit 136, no
message from the program. All three as stated. Raw `5 % 0` in user code
also traps (exit 136) — the language has no divide story, as stated.

## WS1 — the table: does the library lie?

Every row below was run on the v275 binary built from source. "Smallest
input" means the smallest input verified to overflow for that function
(exact minima for the single-argument functions, verified by the
boundary value below them; for two-argument functions, the smallest
verified ordinary-scale case). A negative or wildly wrong positive in
the last column is a lie: the function returns it with no error, no
sentinel, no crash.

### Tier 1 — lies on inputs a student would plausibly write (11 functions)

| Function | Smallest input | True answer | Sutram's answer |
|---|---|---|---|
| `ganit.kramgun` (factorial) | 21 | 51090942171709440000 | -4249290049419214848 |
| `chandas.matra_meru` (Fibonacci) | 93 | 12200160415121876738 | -6246583658587674878 |
| `ganit.ghan` (cube) | 2097152 (2^21) | 9223372036854775808 | -9223372036854775808 |
| `ganit.varg`, `ganit.vargit` (square) | 3037000500; e.g. 4000000000 | 16000000000000000000 (for 4e9) | -2446744073709551616 |
| `ganit.ghat` (power) | (2, 63); also (10, 19) | 9223372036854775808; 10000000000000000000 | -9223372036854775808; -8446744073709551616 |
| `chandas.dwi_ghat` (2^n) | 63 | 9223372036854775808 | -9223372036854775808 |
| `ganit.laghuttam_samapavartya` (lcm) | (4000000000, 4000000001) | 16000000004000000000 | **2446744069709551616** (wrong *positive* — see note) |
| `sankhyiki.purna_prasaran` (int variance) | [2147483648, -2147483648] (2^31) | 4611686018427387904 | **-4611686018427387904** (a negative variance) |
| `ganit.yog_tak` (sum 1..n) | 4294967296 (2^32) | 9223372039002259456 | -9223372034707292160 |
| `sadhan.yog_seema` (range sum) | (0, 4294967296) | 9223372039002259456 | 2147483648 |

Notes on the Tier-1 rows:

- The lcm row is the nastiest in the table. The implementation computes
  `(a / g) * b` and then takes the absolute value of the result. The
  product wraps to a negative, and the absolute value un-negates it
  into a *plausible-looking positive* — 2446744069709551616 instead of
  16000000004000000000. A negative lcm would at least look wrong.
- The variance row is the same shape at a smaller scale: for
  [2^31, -2^31] each squared deviation fits (2^62), but their sum
  (2^63) wraps to MIN and halving gives a negative variance. The
  [4000000000, -4000000000] case also fails (per-cell squares wrap
  there too).
- `yog_tak` / `yog_seema` are the weakest Tier-1 rows: they need
  2^32-scale inputs. They are included because 2^32 is a famous
  boundary a student tests, and the closed form makes the call instant
  (no 4-billion-iteration loop stands in the way). Without them the
  Tier-1 count is 9.
- Plain sums do NOT make Tier 1: `mala_yog` and `purna_yoga` on
  [4000000000, 4000000000, 4000000000] return the correct 12000000000.
  A sum overflows only with MAX-scale values or billions of entries.
  It is the *products* (squares, cubes, powers, factorials, lcm,
  variances) that overflow on ordinary magnitudes, because
  multiplication amplifies.

### Tier 2 — lies only on extreme int64 inputs (11 more functions)

| Function | Smallest input | True answer | Sutram's answer |
|---|---|---|---|
| `ganit.dvigun` (2n) | 4611686018427387904 (2^62) | 9223372036854775808 | -9223372036854775808 |
| `ganit.trigun` (3n) | 3074457345618258603 | 9223372036854775809 | -9223372036854775807 |
| `ganit.nirapeksh_mulya` (abs) | MIN | 9223372036854775808 | -9223372036854775808 (still negative) |
| `ganit.vardh` (n+1) | MAX | 9223372036854775808 | -9223372036854775808 |
| `ank.viparyay_ank` (reverse digits) | 1000000000000000039 | 9300000000000000001 | -9146744073709551615 |
| `sankhyiki.purna_vyapti` (range) | [-1, MAX] | 9223372036854775808 | -9223372036854775808 |
| `mala.mala_yog`, `sankhyiki.purna_yoga` (sum) | [MAX, 1] | 9223372036854775808 | -9223372036854775808 |
| `sankhyiki.purna_madhya` (int mean) | [MAX, 1] | 4611686018427387904 | -4611686018427387904 |
| `ganita.kuttaka` (modular solution) | (2, 0, 5) — modulus 0, no solution | no solution | 2 (wrong: 2×2≠5) |
| `sadhan.shesh` (remainder) | (MIN, -1) | 0 | SIGFPE, exit 136 (crash, not a value) |

The reversal minimum (1000000000000000039) was found by greedy search
and confirmed against its predecessor, whose reversal (8300000000000000001)
still fits. The kuttaka row is a degenerate modulus, not an overflow:
with b = 0 the function returns `c / a` truncated, so (2, 0, 5) claims
x = 2 where no solution exists (while (2, 0, 4) = 2 is genuinely
correct). The shesh row is the x86 `idiv` trap: the function guards
`b == 0` (returns 0) but not the MIN/-1 pair.

## What does NOT lie (and why the count is not larger)

The tree has already fixed a large part of this audit's surface, and
the report would be dishonest if it counted those functions. Verified
safe on v275, by run or by source:

- **The checked and saturating families are the answer, working as
  designed.** `ganita_janchit_*` return ok = 0 on overflow and on
  divide-by-zero (including MIN/-1, verified for both `bhaj` and
  `shesh`); `ganita_paripurna_*` saturate to MAX (21! → MAX,
  10^19 → MAX) and return 0 on divide-by-zero (including MIN/-1).
- **Combinations and Fibonacci-adjacent functions that look dangerous
  are already fixed.** `meru(70, 35)` → -1 (not a wrap); `meru_mala`
  row 70 has -1 at position 35; `meru(60, 30)` = 118264581564861424
  (correct). `collatz_charan` refuses x < 1 and x > (MAX-1)/3 with -1
  (the overflow is documented in its own comment). `asti_abhajya`
  uses a division bound (`i <= x / i`) with a comment explaining the
  `i * i` overflow it avoids.
- **Ceiling division was rewritten, not patched.** `bhaj_urdhva`
  uses `q = a / b` plus a remainder adjustment (not `(a + b - 1) / b`),
  returns the correct 4611686018427387904 for (MAX, 2), and returns 0
  for b = 0.
- **Empty and zero cases are guarded across the statistics module.**
  `madhya` / `prasaran` on an empty array → 0.0; `purna_madhya` /
  `purna_prasaran` on n ≤ 0 → 0; `shesh(x, 0)` → 0;
  `laghuttam_samapavartya(0, 0)` → 0; `vichalan` and `manak` on empty
  inputs compose to 0.0 through those guards.
- **The string parsers refuse instead of wrapping.** With proper
  cell-array buffers (string literals are *not* byte buffers — see the
  method note): `varna_tak_ank("9223372036854775808")` → 0, ok = 0;
  `("9223372036854775807")` → MAX, ok = 1; `("-9223372036854775808")`
  → MIN, ok = 1; base-16 `"FFFFFFFFFFFFFFFFF"` (17 F's) → ok = 0,
  `"7FFFFFFFFFFFFFFF"` → MAX, ok = 1; `varna_tak_dashm` on a 21-digit
  integer string → 1e20, ok = 1 (18-digit mantissa cap plus an
  infinity guard).
- **Formatting is correct at the extremes.**
  `ank_tak_varna(MIN)` and `roop_dash(MIN)` both produce
  "-9223372036854775808"; `roop_shodash(MIN)` gives "-8000000000000000".
  `ank_gan(MIN)` = 19 and `ank_yog(MIN)` = 89, both correct (digit
  loops that never take an absolute value).
- **The fixed-width bigint does not silently truncate.**
  `brihat_yuj` on 999 + 1 returns carry 1 with digits [0, 0, 0];
  `brihat_gun` writes the full 2n-cell product; `brihat_ghatmod`
  carries an R39 width guard. The carry is the signal; ignoring it is
  caller error, not a lie.
- **Slopes, maps, sets, and containers are guarded.**
  `kalana.pravan` / `dvitiya_pravan` return 0.0 on zero x-spacing
  (the old code divided by zero); `nighantu_srij` / `rakh_srij`
  clamp cap ≥ 1 with a width guard; `chakravala` — see below.
- **Chakravala (Pell) never lies, in the range tested.** All 283
  non-square n from 2 to 300 were compared against an exact
  continued-fraction solver in Python: **281 exact, 0 wrong, 2 safe
  failures** (return 0, out = (0, 0)). n = 277 fails because the true
  minimal solution (x ≈ 1.59e20) does not fit int64. n = 181 fails
  although its solution (2469645423824185801, 183567298683461940)
  *does* fit — the iteration's intermediate products overflow, and the
  code returns 0 rather than wrapping (its comment says exactly this).
  The 181 case is a completeness gap (a solvable case refused), not a
  lie. Perfect squares, 0, and 1 all return (1, 0) correctly; negative
  n returns 0 with no hang and no crash.
- **The float modules do not wrap** (they cannot — float64 range):
  `samanvaya` matrices, `kalana`, and the dasham `sankhyiki` functions
  overflow only to `inf`, at ~1e308-scale inputs, which is not an
  ordinary input. The one float caveat is the printer, below.

## WS2 — divide by zero: the brief's examples do not crash

The brief names three cases and says "each one is a crash today." On
v275, **none of the three crashes**:

- Mean of an empty array: `madhya` (dasham) → 0.0, `purna_madhya` →
  0. Both guarded.
- Variance of a single element: population variance divides by n, and
  n = 1 is fine — `purna_prasaran([x])` = 0, correctly. (There is no
  sample-variance (n-1) function in the library to divide by zero.)
- A ratio with a zero denominator: `bhaj_urdhva(x, 0)` → 0,
  `shesh(x, 0)` → 0, `paripurna_bhaj(x, 0)` → 0,
  `janchit_bhaj(x, 0)` → (0, ok = 0), `brihat_bhajshesh` with a zero
  divisor → 0 (golden-verified by `bigint_divzero`).

**The complete library divide-by-zero crash inventory is one
function, on one input pair: `sadhan.shesh(MIN, -1)` → SIGFPE.**
Everything else that divides either guards zero, guards the MIN/-1
pair (the checked and saturating families), or divides by a constant
or a clamped capacity. The remaining divide traps live in *user code*,
not the library: raw `1 / 0` and `5 % 0` both trap with exit 136.
Those are Claude's language brief, not this audit's count.

## WS3 — the count that decides priority

Out of the library's **306** functions (R78 census; the brief's 305
predates `kuttaka_gun_shesh`):

- **11 functions lie on inputs a student would plausibly write**
  (Tier 1 above). Excluding the two 2^32-boundary rows, 9 lie on
  everyday magnitudes (7-digit cubes, 10-digit squares, 21!,
  Fib(93), 2^63, 4e9-scale lcm and variance).
- **22 functions lie or crash on some int64 input** (Tier 1 + Tier 2).
- **284 functions do not overflow or divide-by-zero on any input**
  in the audit's scope — guarded, checked, saturating, float, or
  structurally incapable (min/max, counts, lookups, formatting with
  correct MIN handling).

That is between the brief's two poles: more than 3 (so "fix 3" is not
the story — 11 plain-arithmetic functions share one shape, and each
needs its own guard, checked twin, or saturation), but far from 60 (so
the library alone does not force a general runtime check — the checked
and saturating families already exist and already work; the plain
functions are the ones a student reaches for first, which is the real
problem). What *does* argue for a general language answer is the last
section: the literal and printer bugs below affect every program, not
just 11 functions.

## Language findings (for Claude's R80 brief — measured here, not fixed here)

These are not library rows, but they change the interpretation of the
audit, and one of them reverses an apparent madhava finding:

1. **Integer literals wrap silently.** `9223372036854775808` as a
   literal → -9223372036854775808; `10000000000000000000` →
   -8446744073709551616. No error. A student writing MAX+1 as a
   literal gets MIN.
2. **Dasham literals accumulate modulo 2^64.** Verified by
   comparison (not by printing, since the printer cannot show these
   values — see 3): `10000000000000000000.0` is negative;
   `100000000000000000000.0` is positive (≈ 7.77e18, the wrapped
   value); `10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000.0`
   (10^100) is **0.0** (10^100 is divisible by 2^64). A student writing
   a 20-digit float literal gets a wrong-sign or zero value.
3. **The dasham printer (`likha`) scales by 10^6 into int64.**
   It prints correctly up to |value| < 9223372036854.775808
   (MAX / 10^6); at 10^13 it prints -9223372036854.775808 (the MIN
   rendering); `+inf` / `-inf` print as 0.000000; NaN prints as
   -9223372036854.775808. Any dasham result ≥ ~9.2e12 prints garbage.
4. **Consequence: madhava is NOT broken at large inputs — the
   literals were.** `madhava_sin(10000000000.0)` = -0.487506, exactly
   Python's value. The 10^100 / 10^308 "failures" (sin → 0.000000,
   cos → 1.000000, atan → 0.000000) are all exactly the values of
   sin(0), cos(0), atan(0) — because the literal parsed to 0.0. With a
   correctly-passed value, the reduction (division-based, not a loop)
   and the series are sound; `madhava_vargmool` guards v ≤ 0 → 0.0.
   Do not "fix" madhava for this; fix the literal parser.

## Method and caveats

- Built from `src/r68_compiler_entry.asm`; probes run on the built
  binary; the tree was reset to `origin/main` after the runs
  (tracked `./sutram_compiler` restored).
- "Smallest input" is the smallest *verified* case. For
  single-argument functions the minimum is exact (the predecessor
  fits: 20! fits, 92nd Fibonacci fits, 3037000499² fits, 2097151³
  fits, 2^62 doubles to MAX-1). For two-argument functions the row
  gives the smallest verified ordinary-scale case, not a proven
  global minimum over all pairs.
- Two method corrections, disclosed: (a) string literals are not byte
  buffers — early `varna_tak_*` probes that passed literals returned
  ok = 0 for that reason, not because the parsers refuse; all parser
  verdicts above were re-run with proper cell-array buffers. (b) A
  first chakravala batch failed to compile with 56 locals in one
  function (the known ~29-local limit); the sweep was re-run in
  batches of 12.
- NOT RUN: Windows, browser, implementation (the 11 guards/fixes and
  the literal/printer fixes belong to their owners). The one
  pre-existing `tests/r66/test_prepare_review.py` failure (58 pack
  rows vs 57 expected) is untouched by this round.
