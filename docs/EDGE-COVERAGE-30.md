# R30 WS1 edge-coverage ledger — all 23 modules

Systematic edge-driven defect hunt across every module in `lib/`
(excluding `patra`, which did not exist until WS4 of this round).
Probe classes per export: normal values, zero, negative, `MIN` /
`MAX`, empty (length 0 / count 0), huge (capacity / exponent /
magnitude), and invalid (bad base, negative length, out-of-range
index). A defect is listed with the exact probe that exposed it and
the fix. "Clean" means every probe in the classes above returned the
documented (or, where the contract was silent, the sane) phal.

Fixes are pinned by `prop_edge30_int`, `prop_edge30_text`,
`prop_edge30_conv`, `prop_edge30_cont`, `prop_edge30_float` in
`tools/proof_props.py`, plus the corrected `madhava_atan` golden.
Two investigated behaviours were deliberately KEPT (see `chandas`,
`ganit`): they are pinned by an earlier round's contract.

## Defects found and fixed (51, counted per function)

### `mala` (8 exports) — 1 fixed
- `mala_nava(2^60)`: byte-size overflow returned a bogus pointer.
  Fixed: `sz < 0` returns 0.
- Others clean: safe access, bounds, zero/negative counts.

### `aadhar` (2 exports) — 3 fixed
- `brihat_ank_tak` base 0 → SIGFPE; base 1 → SIGSEGV (infinite
  loop writing past the buffer). Fixed: base outside 2..16 returns 0.
- `brihat_ank_tak` on a 30-digit all-9 brihat in base 2 returned
  100 digits into a fixed 70-cell `rev` — heap overflow. Fixed:
  `rev` sized `4*n` cells (base 2 needs `ceil(3.33*n)`), caller
  rule updated tak `>= 4*n`.
- `brihat_ank_se` base 0/1/negative silently mis-parsed.
  Fixed: base outside 2..16 returns 0.

### `brihat` (12 exports) — 1 fixed
- `brihat_ank_se_int(MIN)`: negation wrapped, emitting negative
  digits (`-8`, …, `-9`), violating "digits must be 0-9". Fixed:
  convert `MAX`, then add 1 tak the digit mala (magnitude
  9223372036854775808, all digits 0-9).
- Others clean, incl. `brihat_bhajshesh` / `mod_2n` by zero (R27),
  `powmod`, `cmp`, `is_zero`, round-trips.

### `chandas` (6 exports) — 1 fixed, 1 kept
- `asti_guru(5, 64)`: SIGFPE (divisor shifted tak 0). Fixed: index
  outside `[0, 64)` returns 0. `asti_guru(5, -1)` (was 1, bit 0)
  now 0.
- `guru_gan` negatives: investigated, KEPT at 0 — mirrors
  `bit_gan`'s R28-pinned contract (defined for `n >= 0`).
- Others clean: pattern classification, metre checks.

### `roop` (23 exports) — 1 fixed
- `roop_sthir(NaN, …)`: returned garbage (`-9223372036…`).
  Fixed: NaN guard via the dvigun comparison `v == 0.0` AND
  `v < 0.0` (the only value satisfying both). Note: this
  language's dasham `!=` treats NaN as equal tak itself
  (`NaN != NaN` is false), so `v != v` does NOT detect NaN —
  compiler-side comparison quirk, documented here and in the R30
  report. Overflow → 0 was already correct (R29).
- Others clean: grouping, padding, fixed/float formatting.

### `ganita` (22 exports) — 0 WS1 defects (WS5 items below)
- `yog_tak` rewritten O(1) closed form (WS5): the loop took `n`
  iterations, so `yog_tak(4294967296)` was ~4.3e9 iterations.
  Pinned: `yog_tak(4294967296) == -9223372034707292160`.
- `chakravala` limitation pinned (WS5): for
  `n = 9223372030926249006`, the better above-sqrt candidate
  `m = 3037000501` exceeds `isqrt(MAX)`, so its vargit overflows
  int64 and the code picks the worse below-sqrt `m = 3037000496`;
  the call returns 0. See `tools/chakravala_model.py`.
- `ganita_checked_*` / `ganita_sat_*` FROZEN, untouched.
  Others clean.

### `gudh` (2 exports) — clean
- `fnv1a` returns unsigned 32-bit values as documented; earlier
  "mismatches" were oracle representation mistakes.

### `kalana` (6 exports) — 2 fixed
- `pravan` / `pravan2` on duplicate x coordinates: division by zero
  → inf / blank formatted output. Fixed: zero spacing (either
  side, or `hl == -hr`) returns 0.0.
- Others clean: kalana_trapiz, Simpson, `bahu_ganana`, empty cases.

### `suchi` (34 exports) — 2 fixed
- `suchi_srij(2^60)`: returned a handle whose data pointer was
  bogus (size overflow); first `suchi_khip` segfaulted. Fixed:
  overflow → 0. Same guard added tak `avali_srij`.
- Others clean: push/get/sangrah/insert/remove, stack, queue
  wrap/growth, clear/reuse, min/max, vinimay/reverse.

### `madhava` (5 exports) — 5 fixed
- `madhava_vargmool(-4)` → `6.07…`. Fixed: `v <= 0` returns 0.0.
- `madhava_vargmool` fixed 40 iterations failed for extreme
  magnitudes (`sqrt(1e300)` → `1e288`). Fixed: 1000 iterations
  (Newton from `v` needs ~512 halvings for `1.8e308`).
- `madhava_atan(1)` → `0.784773` (off by 6e-4); `atan(2)` inf;
  `atan(10)` garbage. Fixed: halving identity for `|x| <= 1`
  (`atan(x) = 2*atan(x/(1+sqrt(1+x^2)))`, 60 terms) +
  reciprocal identity for `|x| > 1`
  (`atan(x) = PI/2 - atan(1/x)`). The `madhava_atan` golden
  encoded the old wrong value and was corrected tak `0.785398`.
- `madhava_sin(100)` / `madhava_cos(100)` overflowed tak inf.
  Fixed: argument reduction tak `[-PI, PI]` (exact tak ~1e15).
- `madhava_pi` clean.

### `nighantu` (17 exports) — 3 fixed
- `nighantu_srij(2^60)`: allocation-size overflow → SIGSEGV writing
  past a small buffer. Fixed: overflow → 0 (plus null check).
- `nighantu_khip` / `nighantu_anwesh` with caller `cap = 0`: SIGFPE (`h % 0`).
  Fixed: `cap < 1` → 0 / -1.
- `nighantu_khip` with negative key length: stored keylen `-1`, which
  `nighantu_kunjika_ashtak` emitted as length byte 255. Fixed: `keyn < 0`
  → 0 / -1.
- Others clean: full-table, removal (backward-shift), update,
  `nighantu_kunjika` / `nighantu_kunjika_ashtak` FROZEN, untouched.

### `ganit` (18 exports) — 2 fixed, 1 kept
- `kramgun(100000)`: SIGSEGV (recursive call-stack exhaustion).
  Fixed: iterative loop. Same values (multiplication commutes
  shesh 2^64); `kramgun(21)` wrap unchanged.
- `yog_tak`: O(1) closed form (see `ganita` above).
- `bit_gan` negatives: investigated, KEPT at 0 — R28 pinned
  "defined for `n >= 0`; negative returns 0" (`prop_numeric28`).
- Others clean: wrapping `varg`/`ghan`/`ghat`/`fib` (R29-pinned),
  `asti_abhajya` (R28), `seemit`, `rand`.

### `ank` (10 exports) — 4 fixed
- `ank_gan(MIN)` → 1, `ank_yog(MIN)` → 0 (wrapped
  negation). Fixed: explicit MIN cases (19, 89).
- `viparyay_ank(-123)` → 0, `viparyay_ank(MIN)` → 0 (loop only
  ran for `x > 0`). Fixed: negatives reverse with the util_chinha;
  MIN returns `-8085774586302733229`. `asti_vilom` on
  negatives now 0 (was 1 for `-121`).
- Others clean: `fib`, `mahattam`/`laghuttam` (R28), `isqrt`, `collatz`.

### `phal` (11 exports before WS3) — WS3 additions
- Added `phal_janchit_ghat` / `phal_janchit_kramgun` /
  `phal_janchit_nirapeksh` (14 exports now) + documented/tested
  early-return chain. See WS3.

### `samanvaya` (10 exports) — clean
- Proper-size matrix operations pass. Empty `nirnaya2` exits
  through kosh bounds checking because the contract requires four
  elements (caller error, not a defect).

### `sankhyiki` (16 exports) — 1 fixed
- `sankhyiki_vargmool(1e12)` → `1279996.5…` (20 iterations).
  Fixed: 1000 iterations, as `madhava_vargmool`. Negative input
  already returned 0.
- Others clean; integer-overflow results are deterministic
  wrapping under the current contract.

### `anukram` (5 exports) — clean
- LE i64 + length-prefixed bytes, bounds-checked, `-1` on
  overrun (R29). Round-trips pass.

### `sangrah` (14 exports) — clean
- All operations pass with fresh outputs (the documented
  contract). Reusing a non-empty output sangrah is caller error,
  not a defect — re-verified.

### `shreni` (14 exports) — 2 fixed
- `laghu(…, 0)` / `adhik(…, 0)`: SIGSEGV reading `a[0]` on an
  empty buffer. Fixed: `n <= 0` returns 0 (as `suchi_laghu` does).
- Others clean: shreni, merge, vinimay, reverse, binary search.

### `khand` (22 exports) — 9 fixed
- `khand_unnat` / `khand_avanat` with `sn = -1`: wrote the
  terminator at `out[-1]`, corrupting the byte before `dst`.
  Fixed: empty output, return 0.
- `khand_pratisthap` with negative find length: SIGSEGV. Fixed:
  verbatim copy (as empty find).
- `khand_bhed` with negative separator length: hang. Fixed:
  one segment (as empty separator).
- `khand_gan` with negative needle length: hang. Fixed: 0.
- `khand_anwesh` with negative needle length: returned 0. Fixed: -1.
- `khand_aadi` / `khand_ant` with negative prefix/suffix
  length: returned 1. Fixed: 0.
- `khand_asti_sarv_ank(…, -1)`: returned 1. Fixed: 0.
- Others clean: pack/unpack, dup, trim, join, compare, reverse,
  count/vowels/char, anwesh_akshar, equals.

### `vakyank` (6 exports) — 2 fixed
- `ank_tak_aadhar_varna(10, 0, …)`: SIGFPE. Base 1: SIGSEGV
  (infinite loop past the buffer). Base `-2`: returned `"0"`.
  Fixed: base outside 2..36 → terminator only, return 0.
- `varna_tak_dashm("9e308")` / `"2e308"`: returned `ok = 1` with
  inf, violating the documented overflow contract. Fixed: the
  `val / 2 == val` inf test after scaling (`1e309` already
  returned `ok = 0`; `1.7e308` still returns `ok = 1`).
- Others clean: `ank_tak_varna`, `varna_tak_ank` (overflow → 0),
  `float_to_str`, base rendering.

### `varna` (27 exports) — 8 fixed
- Eight negative-length defects, mirroring `khand`'s (khand has one
more: `khand_asti_sarv_ank`), same fixes:
  `varna_unnat` / `varna_avanat` (`sn = -1` overwrote `dst[-1]`),
  `varna_pratisthap` (SIGSEGV), `varna_bhed` (hang), `varna_gan`
  (hang), `varna_anwesh` (returned 0 → now -1), `varna_aadi` /
  `varna_ant` (returned 1 → now 0).
- Others clean: find/replace/split/join/trim/upper/lower/
  starts/ends/compare, `varna_sam`, vowels, digits.

### `sadhan` (7 exports) — 4 fixed
- `shesh(5, 0)` / `shesh(0, 0)`: SIGFPE. Fixed: return 0 on a zero
  divisor (same sentinel as `ganita_paripurna_bhaj`).
- `bhaj_urdhva(5, 0)` / `bhaj_urdhva(0, 0)`: SIGFPE. Fixed: return 0.
  `bhaj_urdhva` was also wrong for negative divisors
  (`bhaj_urdhva(7, -2)` was `-2`, `bhaj_urdhva(5, -3)` was `0`).
  Fixed: true ceiling division for every util_chinha combination.
- `yog_seema` with `end < start`: returned a negative count.
  Fixed: 0 for an empty range.
- Others clean: `antargam`, `util_chinha`, `satya_tak_ank`, `ank_adhik`.

## Totals

- 23 modules, 297 exports (pre-round) exercised.
- 51 function-level defects fixed, counted per function (a defect
  affecting both `varna` and `khand` counts twice, once per
  surface; the hunt's working count of 31 grouped the
  varna/khand mirrors and paired functions like min/max and
  sin/cos). Breakdown:
  - 12 crashes (SIGFPE / SIGSEGV): `sadhan.shesh`, `sadhan.bhaj_urdhva`,
    `vakyank.ank_tak_aadhar_varna`, `aadhar.brihat_ank_tak`,
    `shreni.laghu`, `shreni.adhik`, `nighantu.nighantu_srij`,
    `suchi.suchi_srij`, `ganit.kramgun`, `chandas.asti_guru`,
    `varna.varna_pratisthap`, `khand.khand_pratisthap`.
  - 4 hangs: `varna.varna_bhed`, `khand.khand_bhed`,
    `varna.varna_gan`, `khand.khand_gan` (negative lengths).
  - 6 memory-safety: `aadhar.brihat_ank_tak` (70-cell `rev`
    overflow), `varna.varna_unnat`, `varna.varna_avanat`,
    `khand.khand_unnat`, `khand.khand_avanat` (out-of-bounds write
    at `dst[-1]`), `nighantu` negative key length (keylen corruption).
  - 29 wrong answers / wrong behaviour: the remaining fixes,
    incl. `sadhan.bhaj_urdhva` negative-divisor formula,
    `sadhan.yog_seema` empty range, `ank` MIN/negative cases (4),
    `roop` NaN, `kalana` zero-spacing (2), `suchi.avali_srij` /
    `mala.mala_nava` overflow (bogus handle / pointer),
    `nighantu` zero capacity, `ganit.yog_tak` (loop unusable at scale),
    `madhava` sqrt/atan/sin/cos (5), `sankhyiki_vargmool`,
    `aadhar.brihat_ank_se` base, `brihat_ank_se_int(MIN)`,
    `vakyank.varna_tak_dashm` overflow, `varna`/`khand` negative
    length returns (7).
- 2 behaviours investigated and deliberately kept
  (`bit_gan` / `guru_gan` negatives → 0, R28 contract).
- 2 non-defects re-verified as contract (sangrah fresh-output rule;
  `sankhyiki` integer wrapping).
- Frozen surfaces untouched: `nighantu_kunjika` / `nighantu_kunjika_ashtak`,
  `ganita_checked_*` / `ganita_sat_*`, R19–R29 additions
  (extended beside them, never rewritten).

## Ceiling note

The fixes added code tak 17 modules. Programs near the 64 KiB
expanded-source ceiling (`containers_clear`, `gaps19`,
`containers_resize_swap` properties) exceeded it, so this round
also trimmed the module-header rationale essays in
`khand` / `suchi` / `nighantu` / `sangrah` (5.8 KB of comments removed, 3.7 KB
of shorter comments added, net −2.1 KB; per-function docs untouched;
full rationale lives in the round reports and `docs/`). The hot
closure now sits below its pre-round size, restoring margin.
