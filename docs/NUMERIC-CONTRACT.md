# The numeric contract, tabulated

Charter item 10 (strong static typing) requires integer sizes,
conversions, overflow, initialisation and comparison to be defined
precisely. This page tabulates, for each numeric operation across
`ganita`, `math`, `fmt` and `strconv`: the operand types, the
behaviour on overflow, and whether a checked and/or saturating form
exists. Operations whose behaviour is **not** pinned by a test are
marked — that gap list is as valuable as the table.

## Ground rules (whole library)

- Integers are signed 64-bit (`vitti`): range
  `[-9223372036854775808, 9223372036854775807]` (`MIN`, `MAX`).
- Plain arithmetic (`+`, `-`, `*`, `/`, `%`) wraps silently on
  overflow, as in C. Division by zero traps (SIGFPE) at the hardware
  level — library functions must never let it happen (see `lcm`).
- `dasham` is the float type. `str_to_float` overflows only past
  `~1.8e308`.
- "Pinned" means a property or golden asserts the stated behaviour.
  Property names are `tools/proof_props.py` entries unless noted.

## `ganita` — checked and saturating arithmetic (R18)

| Operation | Operands | Overflow | Checked | Saturating | Pinned by |
|---|---|---|---|---|---|
| `ganita_checked_add/sub/mul` | `vitti, vitti` | returns `0`, `ok` 0 | itself | `ganita_sat_add/sub/mul` | `prop_ganita_checked_add_sub`, `prop_ganita_checked_mul`, `prop_safety25/26/27` |
| `ganita_checked_div/mod` | `vitti, vitti` | divisor 0 or `MIN / -1` → `0`, `ok` 0 | itself | `ganita_sat_div/mod` (`MIN/-1` → `MAX` / `0`) | `prop_ganita_checked_divmod`, `prop_safety25/26` |
| `ganita_checked_pow` | `vitti, vitti` | negative exp or overflow → `0`, `ok` 0 | itself | `ganita_sat_pow` (clamp) | `prop_safety25/26` |
| `ganita_checked_fact` | `vitti` | negative `n` or overflow → `0`, `ok` 0 | itself | `ganita_sat_fact` (clamp) | `prop_safety25/26` |
| `ganita_checked_abs` | `vitti` | `MIN` → `0`, `ok` 0 | itself | `ganita_sat_abs` (`MIN` → `MAX`) | `prop_safety25/26` |
| `ganita_abs` | `vitti` | **wraps**: `MIN` → `MIN` | `ganita_checked_abs` | `ganita_sat_abs` | `prop_numeric28` (pins the wrap) |
| `ganita_isqrt` | `vitti` | negative → `0`; binary search, no overflow | — | — | `prop_numeric28` (`MAX` → `3037000499`), golden `numeric_hangfix` |
| `kuttaka`, `chakravala`, `samasa`, `brahmagupta_area` | mixed | **wraps** (plain arithmetic; no checked forms) | — | — | `prop_numeric29` pins wrapping: `kuttaka` (wrapping vs exact differ — pinned against a Python wrapping simulation), `samasa` (2^80 → 0), `brahmagupta_area` (2^64 sum → 0); `chakravala` pinned separately below |

## `math` — plain arithmetic (wraps by design)

| Operation | Operands | Overflow / edge | Checked | Saturating | Pinned by |
|---|---|---|---|---|---|
| `sq`, `square`, `cube`, `double`, `triple`, `inc` | `vitti` | **wraps** | `ganita_checked_mul` (for products) | `ganita_sat_mul` | `prop_numeric29` (pins wrap cases: `sq(2^32)=0`, `square(3037000500)`, `cube(2^21)=MIN`, `double(MAX)=-2`, `triple(MAX)`, `inc(MAX)=MIN`) |
| `abs_val` | `vitti` | **wraps**: `MIN` → `MIN` | `ganita_checked_abs` | `ganita_sat_abs` | `prop_numeric28` (pins the wrap) |
| `min2`, `max2` | `vitti, vitti` | n/a | — | — | goldens |
| `gcd` | `vitti, vitti` | non-negative result; `gcd(0,0)=0`; `gcd(MIN,0)=MIN` (wrapping abs) | — | — | `prop_math_gcd`, `prop_math_gcd_lcm`, `prop_numeric28`, golden `math_gcd_lcm_edge` |
| `lcm` | `vitti, vitti` | non-negative result; `lcm(0,0)=0`; `lcm(MIN,2)=MIN` (wrapping) | — | — | `prop_math_gcd_lcm`, `prop_numeric28`, golden `math_gcd_lcm_edge` |
| `power` | `vitti, vitti` | **wraps**; `e <= 0` → `1` | `ganita_checked_pow` | `ganita_sat_pow` | `prop_numeric28` (edges); `prop_numeric29` (`power(2,63)=MIN`, `power(3,40)` wrap) |
| `fact` | `vitti` | **wraps** for `n >= 21`; `n < 2` → `1` | `ganita_checked_fact` | `ganita_sat_fact` | `prop_numeric28` (edges); `prop_numeric29` (`fact(21)` wrap) |
| `is_prime` | `vitti` | n/a; `n < 2` → `0` | — | — | `prop_numeric28` (edges + `is_prime(97)`); one-off: `is_prime(9223372036854775783) = 1` (largest 63-bit prime, verified vs Python Miller-Rabin) |
| `sum_to` | `vitti` | **wraps** for large `n`; `n < 1` → `0` | — | — | `prop_numeric28` (edges) — **OPEN GAP**: wrapping is defined but not pinned — pinning needs `n ≈ 4.3e9` iterations, impractical in a test |
| `bit_count` | `vitti` | defined for `n >= 0`; negative `n` → `0` (not two's-complement popcount) | — | — | `prop_numeric28` (pins it) |
| `math_rand` | 1-cell state | wraps by design (LCG) | — | — | `prop_breadth26` |
| `math_clamp` | `vitti, vitti, vitti` | n/a; requires `lo <= hi` (`lo > hi` → returns `lo`) | — | — | `prop_breadth26` |

## `strconv` — conversions

| Operation | Operands | Overflow / edge | Checked | Saturating | Pinned by |
|---|---|---|---|---|---|
| `str_to_int` | bytes, `vitti` | malformed/overflow → `0`, `ok` 0 (R26 guard) | itself (`ok`) | — (use `ganita_sat_*` on the parsed value) | `prop_strconv_roundtrip`, `prop_safety27`, golden `strconv_overflow` |
| `str_to_int_base` | bytes, `vitti`, base | bad digit, digit ≥ base, overflow → `0`, `ok` 0 | itself (`ok`) | — | `prop_strconv_base_roundtrip`, `prop_safety27`, golden `strconv_overflow` |
| `str_to_float` | bytes, `vitti` | malformed/overflow → `0.0`, `ok` 0; underflow → `0.0`, `ok` 1 | itself (`ok`) | — | `prop_breadth26` |
| `int_to_str` | `vitti` | n/a; `MIN` → `"-9223372036854775808"` (R26 fix) | — | — | `prop_min26`, `prop_safety27`, golden `strconv_overflow` |
| `int_to_base_str` | `vitti`, base | requires `n >= 0`; negative → `0` (empty) | — | — | `prop_numeric28` (pins it) |
| `pad_left` | bytes | n/a (padding) | — | — | `prop_strconv_pad_left` |

## `fmt` — formatting

| Operation | Operands | Overflow / edge | Checked | Saturating | Pinned by |
|---|---|---|---|---|---|
| `fmt_int_base` / `fmt_int_flags` | `vitti`, base | n/a; `MIN` handled (R26 fix) | — | — | `prop_fmt_int_base_roundtrip`, `prop_min26` |
| `fmt_digits` / `fmt_digits_base` | `vitti`, base | base `< 2` or `> 36` → `0` (empty); `MIN` handled | — | — | `prop_min26`, `prop_numeric28` (base limits) |
| `fmt_dec/hex/hex_upper/oct/bin` | `vitti` | n/a (fixed-base forms of `fmt_int_base`) | — | — | `prop_fmt_int_base_roundtrip` |
| `fmt_group*` / `fmt_group_int` | bytes / `vitti` | n/a; grouping is digit-preserving | — | — | `prop_fmt_group_digits`, golden `fmt_group` |
| `fmt_fixed` / `fmt_fixed_signed` | `dasham`, places | requires `\|x\| * 10^places` fits in int64; overflow input returns `0` (empty) — R29 guard (was a segfault: the dasham→int conversion is indefinite past 2^63) | — | — | `prop_numeric29` (overflow → 0, negative overflow → 0, largest fixed output `9223372036854774784` = 2^63 − 1024, 19 chars) |
| `fmt_signed` / `fmt_sign_char` | `vitti` | n/a | — | — | `prop_fmt_signed` |
| `fmt_pad_left/right/center` | bytes | n/a (padding) | — | — | `prop_fmt_pad_content` |

## `num` — found by the same sweep (R28)

Not in the R28 WS3 module list, but the same overflow-hang pattern
(`d * d <= x`) was found there by grep and fixed in this round.

| Operation | Operands | Overflow / edge | Pinned by |
|---|---|---|---|
| `is_perfect` | `vitti` | `n < 2` → `0`; division bound (the old `d * d` loop hung near MAX) | `prop_numeric28`, golden `numeric_hangfix` |
| `collatz_steps` | `vitti` | `-1` means "does not reach 1": `n < 1`, or the `3x+1` step would overflow int64 (`n > 3074457345618258602` and odd) | `prop_numeric28`, golden `numeric_hangfix` |
| `fib` | `vitti` | **wraps** for large `n` (loop is bounded by `n`, so it terminates); `n < 2` → `n` | — | — | `prop_numeric29` (`fib(93)` wrap) |
| `digit_count`, `digit_sum`, `reverse_num`, `is_palindrome`, `clamp`, `is_even`, `is_odd` | `vitti` | `reverse_num` **wraps** for reversals past MAX; the rest are exact | — | — | `prop_numeric29` (`reverse_num` wrap); goldens |

## Gap list (behaviour not pinned by a test)

1. `sum_to` wrapping: defined (wraps) but not pinned — pinning
   needs `n ≈ 4.3e9` iterations, impractical in a test. **OPEN GAP.**

## R29: chakravala fixes and compiler-side findings

`chakravala` (Pell's equation) had two defects, both fixed in
`lib/ganita.smlib`:

- **Perfect-square input crashed** (`chakravala(4)` → SIGFPE:
  the search divided by `|k| = 0`). Now returns the trivial
  solution `(1, 0)` with return `1`.
- **Large `|k|` hung.** The old scan `m = 0, 1, 2, ...` needs
  `m ~ 2.9e9` for `n = MAX`. Now solves `b*m = -a (mod |k|)`
  with `kuttaka` and compares the two divisible candidates
  bracketing `sqrt(n)`. `chakravala(61)` still gives the
  minimal `(1766319049, 226153980)`.
- **Return contract made explicit:** `1` = solution in `out`,
  `0` = failure (`out` untouched) — overflow in the update
  step, no divisible `m`, or the 1000-iteration guard.
  `chakravala(MAX)` returns `0` (its minimal solution does
  not fit in int64) instead of hanging.
- **Approximation:** candidates with `m > isqrt(MAX)` are
  skipped (their `nk` would not fit). The below-`sqrt(n)`
  candidate is always exact, so one always exists. For
  `n > MAX/2` this can pick a suboptimal `m` — still a valid
  divisible `m`, never a wrong answer.

Three compiler-side findings (in `src/`, not fixable from the
library side) surfaced while pinning this contract:

- **Scientific-notation literals are broken.** `dasham x = 1e18`
  parses as `1.0` (exponent dropped), and `fmt_fixed(1e18, ...)`
  with the literal inline in a call argument segfaults.
  `1e18` written out (`1000000000000000000.0`) works. Use full
  decimal literals until the lexer is fixed.
- **~29+ locals across nested blocks miscompile.** A function
  with ~29 locals in nested blocks segfaults at runtime even
  when the offending branch never executes (verified by
  bisection: 28 locals fine, 29 crashes in `chakravala`).
  The fix reuses dead variables (`g1`, `g2`, `gt`, `r`) in
  the nested branch instead of declaring fresh locals.
- **64 KiB expanded-source cap.** The compiler caps total
  `ayojan`-expanded source at 65536 bytes (`IMPORT_BUF_CAP`).
  The `gaps19` property program (which ayojans
  `map` + `set` + `strb` + `ganita`) now sits ~130 bytes under
  it — the chakravala rewrite had to be compacted to fit.
  The library is growing into this cap; raising it is
  compiler-side work.

None of these is a crash: the plain functions wrap deterministically,
and the crash/hang-class inputs (`lcm(0,0)`, `bigint_divmod` by zero,
`ganita_isqrt`/`is_prime`/`is_perfect` near MAX, `collatz_steps`
overflow) were fixed in R27/R28 and are pinned. The gaps are
contract coverage, not defects.
