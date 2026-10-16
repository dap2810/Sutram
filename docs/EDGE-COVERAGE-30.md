# R30 WS1 edge-coverage ledger — all 23 modules

Systematic edge-driven defect hunt across every module in `lib/`
(excluding `file`, which did not exist until WS4 of this round).
Probe classes per export: normal values, zero, negative, `MIN` /
`MAX`, empty (length 0 / count 0), huge (capacity / exponent /
magnitude), and invalid (bad base, negative length, out-of-range
index). A defect is listed with the exact probe that exposed it and
the fix. "Clean" means every probe in the classes above returned the
documented (or, where the contract was silent, the sane) result.

Fixes are pinned by `prop_edge30_int`, `prop_edge30_text`,
`prop_edge30_conv`, `prop_edge30_cont`, `prop_edge30_float` in
`tools/proof_props.py`, plus the corrected `madhava_atan` golden.
Two investigated behaviours were deliberately KEPT (see `chandas`,
`math`): they are pinned by an earlier round's contract.

## Defects found and fixed (51, counted per function)

### `array` (8 exports) — 1 fixed
- `array_new(2^60)`: byte-size overflow returned a bogus pointer.
  Fixed: `sz < 0` returns 0.
- Others clean: safe access, bounds, zero/negative counts.

### `baseconv` (2 exports) — 3 fixed
- `bigint_to_digits` base 0 → SIGFPE; base 1 → SIGSEGV (infinite
  loop writing past the buffer). Fixed: base outside 2..16 returns 0.
- `bigint_to_digits` on a 30-digit all-9 bigint in base 2 returned
  100 digits into a fixed 70-cell `rev` — heap overflow. Fixed:
  `rev` sized `4*n` cells (base 2 needs `ceil(3.33*n)`), caller
  rule updated to `>= 4*n`.
- `bigint_from_digits` base 0/1/negative silently mis-parsed.
  Fixed: base outside 2..16 returns 0.

### `bigint` (12 exports) — 1 fixed
- `bigint_from_int(MIN)`: negation wrapped, emitting negative
  digits (`-8`, …, `-9`), violating "digits must be 0-9". Fixed:
  convert `MAX`, then add 1 to the digit array (magnitude
  9223372036854775808, all digits 0-9).
- Others clean, incl. `bigint_divmod` / `mod_2n` by zero (R27),
  `powmod`, `cmp`, `is_zero`, round-trips.

### `chandas` (6 exports) — 1 fixed, 1 kept
- `is_guru(5, 64)`: SIGFPE (divisor shifted to 0). Fixed: index
  outside `[0, 64)` returns 0. `is_guru(5, -1)` (was 1, bit 0)
  now 0.
- `guru_count` negatives: investigated, KEPT at 0 — mirrors
  `bit_count`'s R28-pinned contract (defined for `n >= 0`).
- Others clean: pattern classification, metre checks.

### `fmt` (23 exports) — 1 fixed
- `fmt_fixed(NaN, …)`: returned garbage (`-9223372036…`).
  Fixed: NaN guard via the double comparison `v == 0.0` AND
  `v < 0.0` (the only value satisfying both). Note: this
  language's dasham `!=` treats NaN as equal to itself
  (`NaN != NaN` is false), so `v != v` does NOT detect NaN —
  compiler-side comparison quirk, documented here and in the R30
  report. Overflow → 0 was already correct (R29).
- Others clean: grouping, padding, fixed/float formatting.

### `ganita` (22 exports) — 0 WS1 defects (WS5 items below)
- `sum_to` rewritten O(1) closed form (WS5): the loop took `n`
  iterations, so `sum_to(4294967296)` was ~4.3e9 iterations.
  Pinned: `sum_to(4294967296) == -9223372034707292160`.
- `chakravala` limitation pinned (WS5): for
  `n = 9223372030926249006`, the better above-sqrt candidate
  `m = 3037000501` exceeds `isqrt(MAX)`, so its square overflows
  int64 and the code picks the worse below-sqrt `m = 3037000496`;
  the call returns 0. See `tools/chakravala_model.py`.
- `ganita_checked_*` / `ganita_sat_*` FROZEN, untouched.
  Others clean.

### `hash` (2 exports) — clean
- `fnv1a` returns unsigned 32-bit values as documented; earlier
  "mismatches" were oracle representation mistakes.

### `kalana` (6 exports) — 2 fixed
- `slope` / `slope2` on duplicate x coordinates: division by zero
  → inf / blank formatted output. Fixed: zero spacing (either
  side, or `hl == -hr`) returns 0.0.
- Others clean: trapezoid, Simpson, `bahu_ganana`, empty cases.

### `list` (34 exports) — 2 fixed
- `list_init(2^60)`: returned a handle whose data pointer was
  bogus (size overflow); first `list_push` segfaulted. Fixed:
  overflow → 0. Same guard added to `queue_init`.
- Others clean: push/get/set/insert/remove, stack, queue
  wrap/growth, clear/reuse, min/max, swap/reverse.

### `madhava` (5 exports) — 5 fixed
- `madhava_sqrt(-4)` → `6.07…`. Fixed: `v <= 0` returns 0.0.
- `madhava_sqrt` fixed 40 iterations failed for extreme
  magnitudes (`sqrt(1e300)` → `1e288`). Fixed: 1000 iterations
  (Newton from `v` needs ~512 halvings for `1.8e308`).
- `madhava_atan(1)` → `0.784773` (off by 6e-4); `atan(2)` inf;
  `atan(10)` garbage. Fixed: halving identity for `|x| <= 1`
  (`atan(x) = 2*atan(x/(1+sqrt(1+x^2)))`, 60 terms) +
  reciprocal identity for `|x| > 1`
  (`atan(x) = PI/2 - atan(1/x)`). The `madhava_atan` golden
  encoded the old wrong value and was corrected to `0.785398`.
- `madhava_sin(100)` / `madhava_cos(100)` overflowed to inf.
  Fixed: argument reduction to `[-PI, PI]` (exact to ~1e15).
- `madhava_pi` clean.

### `map` (17 exports) — 3 fixed
- `map_init(2^60)`: allocation-size overflow → SIGSEGV writing
  past a small buffer. Fixed: overflow → 0 (plus null check).
- `map_put` / `map_find` with caller `cap = 0`: SIGFPE (`h % 0`).
  Fixed: `cap < 1` → 0 / -1.
- `map_put` with negative key length: stored keylen `-1`, which
  `map_keys_bytes` emitted as length byte 255. Fixed: `keyn < 0`
  → 0 / -1.
- Others clean: full-table, removal (backward-shift), update,
  `map_keys` / `map_keys_bytes` FROZEN, untouched.

### `math` (18 exports) — 2 fixed, 1 kept
- `fact(100000)`: SIGSEGV (recursive call-stack exhaustion).
  Fixed: iterative loop. Same values (multiplication commutes
  mod 2^64); `fact(21)` wrap unchanged.
- `sum_to`: O(1) closed form (see `ganita` above).
- `bit_count` negatives: investigated, KEPT at 0 — R28 pinned
  "defined for `n >= 0`; negative returns 0" (`prop_numeric28`).
- Others clean: wrapping `sq`/`cube`/`power`/`fib` (R29-pinned),
  `is_prime` (R28), `clamp`, `rand`.

### `num` (10 exports) — 4 fixed
- `digit_count(MIN)` → 1, `digit_sum(MIN)` → 0 (wrapped
  negation). Fixed: explicit MIN cases (19, 89).
- `reverse_num(-123)` → 0, `reverse_num(MIN)` → 0 (loop only
  ran for `x > 0`). Fixed: negatives reverse with the sign;
  MIN returns `-8085774586302733229`. `is_palindrome` on
  negatives now 0 (was 1 for `-121`).
- Others clean: `fib`, `gcd`/`lcm` (R28), `isqrt`, `collatz`.

### `result` (11 exports before WS3) — WS3 additions
- Added `result_checked_pow` / `result_checked_fact` /
  `result_checked_abs` (14 exports now) + documented/tested
  early-return chain. See WS3.

### `samanvaya` (10 exports) — clean
- Proper-size matrix operations pass. Empty `nirnaya2` exits
  through kosh bounds checking because the contract requires four
  elements (caller error, not a defect).

### `sankhyiki` (16 exports) — 1 fixed
- `sankhyiki_sqrt(1e12)` → `1279996.5…` (20 iterations).
  Fixed: 1000 iterations, as `madhava_sqrt`. Negative input
  already returned 0.
- Others clean; integer-overflow results are deterministic
  wrapping under the current contract.

### `serial` (5 exports) — clean
- LE i64 + length-prefixed bytes, bounds-checked, `-1` on
  overrun (R29). Round-trips pass.

### `set` (14 exports) — clean
- All operations pass with fresh outputs (the documented
  contract). Reusing a non-empty output set is caller error,
  not a defect — re-verified.

### `sort` (14 exports) — 2 fixed
- `min_of(…, 0)` / `max_of(…, 0)`: SIGSEGV reading `a[0]` on an
  empty buffer. Fixed: `n <= 0` returns 0 (as `list_min` does).
- Others clean: sort, merge, swap, reverse, binary search.

### `strb` (22 exports) — 9 fixed
- `strb_upper` / `strb_lower` with `sn = -1`: wrote the
  terminator at `out[-1]`, corrupting the byte before `dst`.
  Fixed: empty output, return 0.
- `strb_replace` with negative find length: SIGSEGV. Fixed:
  verbatim copy (as empty find).
- `strb_split` with negative separator length: hang. Fixed:
  one segment (as empty separator).
- `strb_count` with negative needle length: hang. Fixed: 0.
- `strb_find` with negative needle length: returned 0. Fixed: -1.
- `strb_starts` / `strb_ends` with negative prefix/suffix
  length: returned 1. Fixed: 0.
- `strb_is_all_digits(…, -1)`: returned 1. Fixed: 0.
- Others clean: pack/unpack, dup, trim, join, compare, reverse,
  count/vowels/char, find_char, equals.

### `strconv` (6 exports) — 2 fixed
- `int_to_base_str(10, 0, …)`: SIGFPE. Base 1: SIGSEGV
  (infinite loop past the buffer). Base `-2`: returned `"0"`.
  Fixed: base outside 2..36 → terminator only, return 0.
- `str_to_float("9e308")` / `"2e308"`: returned `ok = 1` with
  inf, violating the documented overflow contract. Fixed: the
  `val / 2 == val` inf test after scaling (`1e309` already
  returned `ok = 0`; `1.7e308` still returns `ok = 1`).
- Others clean: `int_to_str`, `str_to_int` (overflow → 0),
  `float_to_str`, base rendering.

### `string` (27 exports) — 8 fixed
- Eight negative-length defects, mirroring `strb`'s (strb has one
more: `strb_is_all_digits`), same fixes:
  `str_upper` / `str_lower` (`sn = -1` overwrote `dst[-1]`),
  `str_replace` (SIGSEGV), `str_split` (hang), `str_count`
  (hang), `str_find` (returned 0 → now -1), `str_starts` /
  `str_ends` (returned 1 → now 0).
- Others clean: find/replace/split/join/trim/upper/lower/
  starts/ends/compare, `str_equals`, vowels, digits.

### `util` (7 exports) — 4 fixed
- `mod(5, 0)` / `mod(0, 0)`: SIGFPE. Fixed: return 0 on a zero
  divisor (same sentinel as `ganita_sat_div`).
- `div_ceil(5, 0)` / `div_ceil(0, 0)`: SIGFPE. Fixed: return 0.
  `div_ceil` was also wrong for negative divisors
  (`div_ceil(7, -2)` was `-2`, `div_ceil(5, -3)` was `0`).
  Fixed: true ceiling division for every sign combination.
- `sum_range` with `end < start`: returned a negative count.
  Fixed: 0 for an empty range.
- Others clean: `lerp`, `sign`, `bool_to_int`, `int_max`.

## Totals

- 23 modules, 297 exports (pre-round) exercised.
- 51 function-level defects fixed, counted per function (a defect
  affecting both `string` and `strb` counts twice, once per
  surface; the hunt's working count of 31 grouped the
  string/strb mirrors and paired functions like min/max and
  sin/cos). Breakdown:
  - 12 crashes (SIGFPE / SIGSEGV): `util.mod`, `util.div_ceil`,
    `strconv.int_to_base_str`, `baseconv.bigint_to_digits`,
    `sort.min_of`, `sort.max_of`, `map.map_init`,
    `list.list_init`, `math.fact`, `chandas.is_guru`,
    `string.str_replace`, `strb.strb_replace`.
  - 4 hangs: `string.str_split`, `strb.strb_split`,
    `string.str_count`, `strb.strb_count` (negative lengths).
  - 6 memory-safety: `baseconv.bigint_to_digits` (70-cell `rev`
    overflow), `string.str_upper`, `string.str_lower`,
    `strb.strb_upper`, `strb.strb_lower` (out-of-bounds write
    at `dst[-1]`), `map` negative key length (keylen corruption).
  - 29 wrong answers / wrong behaviour: the remaining fixes,
    incl. `util.div_ceil` negative-divisor formula,
    `util.sum_range` empty range, `num` MIN/negative cases (4),
    `fmt` NaN, `kalana` zero-spacing (2), `list.queue_init` /
    `array.array_new` overflow (bogus handle / pointer),
    `map` zero capacity, `math.sum_to` (loop unusable at scale),
    `madhava` sqrt/atan/sin/cos (5), `sankhyiki_sqrt`,
    `baseconv.bigint_from_digits` base, `bigint_from_int(MIN)`,
    `strconv.str_to_float` overflow, `string`/`strb` negative
    length returns (7).
- 2 behaviours investigated and deliberately kept
  (`bit_count` / `guru_count` negatives → 0, R28 contract).
- 2 non-defects re-verified as contract (set fresh-output rule;
  `sankhyiki` integer wrapping).
- Frozen surfaces untouched: `map_keys` / `map_keys_bytes`,
  `ganita_checked_*` / `ganita_sat_*`, R19–R29 additions
  (extended beside them, never rewritten).

## Ceiling note

The fixes added code to 17 modules. Programs near the 64 KiB
expanded-source ceiling (`containers_clear`, `gaps19`,
`containers_resize_swap` properties) exceeded it, so this round
also trimmed the module-header rationale essays in
`strb` / `list` / `map` / `set` (5.8 KB of comments removed, 3.7 KB
of shorter comments added, net −2.1 KB; per-function docs untouched;
full rationale lives in the round reports and `docs/`). The hot
closure now sits below its pre-round size, restoring margin.
