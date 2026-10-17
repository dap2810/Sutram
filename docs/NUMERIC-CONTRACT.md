# The numeric contract, tabulated

Charter item 10 (strong static typing) requires integer sizes,
conversions, overflow, initialisation and comparison tak be defined
precisely. This page tabulates, for each numeric operation across
`ganita`, `ganit`, `roop` and `vakyank`: the operand types, the
behaviour on overflow, and whether a checked and/or saturating form
exists. Operations whose behaviour is **not** pinned by a test are
marked — that gap suchi is as valuable as the table.

## Ground rules (whole library)

- Integers are signed 64-bit (`vitti`): range
  `[-9223372036854775808, 9223372036854775807]` (`MIN`, `MAX`).
- Plain arithmetic (`+`, `-`, `*`, `/`, `%`) wraps silently on
  overflow, as in C. Division by zero traps (SIGFPE) at the hardware
  level — library functions must never let it happen (see `laghuttam`).
- `dasham` is the float type. `varna_tak_dashm` overflows only past
  `~1.8e308`.
- "Pinned" means a property or golden asserts the stated behaviour.
  Property names are `tools/proof_props.py` entries unless noted.

## `ganita` — checked and saturating arithmetic (R18)

| Operation | Operands | Overflow | Checked | Saturating | Pinned by |
|---|---|---|---|---|---|
| `ganita_janchit_yuj/sub/mul` | `vitti, vitti` | returns `0`, `ok` 0 | itself | `ganita_paripurna_yuj/sub/mul` | `prop_ganita_checked_add_sub`, `prop_ganita_checked_mul`, `prop_safety25/26/27` |
| `ganita_janchit_bhaj/shesh` | `vitti, vitti` | divisor 0 or `MIN / -1` → `0`, `ok` 0 | itself | `ganita_paripurna_bhaj/shesh` (`MIN/-1` → `MAX` / `0`) | `prop_ganita_checked_divmod`, `prop_safety25/26` |
| `ganita_janchit_ghat` | `vitti, vitti` | negative exp or overflow → `0`, `ok` 0 | itself | `ganita_paripurna_ghat` (seemit) | `prop_safety25/26` |
| `ganita_janchit_kramgun` | `vitti` | negative `n` or overflow → `0`, `ok` 0 | itself | `ganita_paripurna_kramgun` (seemit) | `prop_safety25/26` |
| `ganita_janchit_nirapeksh` | `vitti` | `MIN` → `0`, `ok` 0 | itself | `ganita_paripurna_nirapeksh` (`MIN` → `MAX`) | `prop_safety25/26` |
| `ganita_nirapeksh` | `vitti` | **wraps**: `MIN` → `MIN` | `ganita_janchit_nirapeksh` | `ganita_paripurna_nirapeksh` | `prop_numeric28` (pins the wrap) |
| `ganita_vargmool` | `vitti` | negative → `0`; binary search, no overflow | — | — | `prop_numeric28` (`MAX` → `3037000499`), golden `numeric_hangfix` |
| `kuttaka`, `chakravala`, `samasa`, `brahmagupta_kshetr` | mixed | **wraps** (plain arithmetic; no checked forms) | — | — | `prop_numeric29` pins wrapping: `kuttaka` (wrapping vs exact differ — pinned against a Python wrapping simulation), `samasa` (2^80 → 0), `brahmagupta_kshetr` (2^64 sum → 0); `chakravala` pinned separately below |

## `ganit` — plain arithmetic (wraps by design)

| Operation | Operands | Overflow / edge | Checked | Saturating | Pinned by |
|---|---|---|---|---|---|
| `varg`, `vargit`, `ghan`, `dvigun`, `trigun`, `vardh` | `vitti` | **wraps** | `ganita_janchit_gun` (for products) | `ganita_paripurna_gun` | `prop_numeric29` (pins wrap cases: `varg(2^32)=0`, `vargit(3037000500)`, `ghan(2^21)=MIN`, `dvigun(MAX)=-2`, `trigun(MAX)`, `vardh(MAX)=MIN`) |
| `nirapeksh_mulya` | `vitti` | **wraps**: `MIN` → `MIN` | `ganita_janchit_nirapeksh` | `ganita_paripurna_nirapeksh` | `prop_numeric28` (pins the wrap) |
| `laghu2`, `adhik2` | `vitti, vitti` | n/a | — | — | goldens |
| `mahattam` | `vitti, vitti` | non-negative phal; `mahattam(0,0)=0`; `mahattam(MIN,0)=MIN` (wrapping abs) | — | — | `prop_math_gcd`, `prop_math_gcd_lcm`, `prop_numeric28`, golden `math_gcd_lcm_edge` |
| `laghuttam` | `vitti, vitti` | non-negative phal; `laghuttam(0,0)=0`; `laghuttam(MIN,2)=MIN` (wrapping) | — | — | `prop_math_gcd_lcm`, `prop_numeric28`, golden `math_gcd_lcm_edge` |
| `ghat` | `vitti, vitti` | **wraps**; `e <= 0` → `1` | `ganita_janchit_ghat` | `ganita_paripurna_ghat` | `prop_numeric28` (edges); `prop_numeric29` (`ghat(2,63)=MIN`, `ghat(3,40)` wrap) |
| `kramgun` | `vitti` | **wraps** for `n >= 21`; `n < 2` → `1` | `ganita_janchit_kramgun` | `ganita_paripurna_kramgun` | `prop_numeric28` (edges); `prop_numeric29` (`kramgun(21)` wrap) |
| `asti_abhajya` | `vitti` | n/a; `n < 2` → `0` | — | — | `prop_numeric28` (edges + `asti_abhajya(97)`); one-off: `asti_abhajya(9223372036854775783) = 1` (largest 63-bit prime, verified vs Python Miller-Rabin) |
| `yog_tak` | `vitti` | **wraps** for large `n`; `n < 1` → `0` | — | — | `prop_numeric28` (edges) — **OPEN GAP**: wrapping is defined but not pinned — pinning needs `n ≈ 4.3e9` iterations, impractical in a test |
| `bit_gan` | `vitti` | defined for `n >= 0`; negative `n` → `0` (not two's-complement popcount) | — | — | `prop_numeric28` (pins it) |
| `ganit_yadricch` | 1-cell state | wraps by design (LCG) | — | — | `prop_breadth26` |
| `ganit_seemit` | `vitti, vitti, vitti` | n/a; requires `lo <= hi` (`lo > hi` → returns `lo`) | — | — | `prop_breadth26` |

## `vakyank` — conversions

| Operation | Operands | Overflow / edge | Checked | Saturating | Pinned by |
|---|---|---|---|---|---|
| `varna_tak_ank` | bytes, `vitti` | malformed/overflow → `0`, `ok` 0 (R26 guard) | itself (`ok`) | — (use `ganita_sat_*` on the parsed value) | `prop_strconv_roundtrip`, `prop_safety27`, golden `strconv_overflow` |
| `varna_tak_ank_aadhar` | bytes, `vitti`, base | bad digit, digit ≥ base, overflow → `0`, `ok` 0 | itself (`ok`) | — | `prop_strconv_base_roundtrip`, `prop_safety27`, golden `strconv_overflow` |
| `varna_tak_dashm` | bytes, `vitti` | malformed/overflow → `0.0`, `ok` 0; underflow → `0.0`, `ok` 1 | itself (`ok`) | — | `prop_breadth26` |
| `ank_tak_varna` | `vitti` | n/a; `MIN` → `"-9223372036854775808"` (R26 fix) | — | — | `prop_min26`, `prop_safety27`, golden `strconv_overflow` |
| `ank_tak_aadhar_varna` | `vitti`, base | requires `n >= 0`; negative → `0` (empty) | — | — | `prop_numeric28` (pins it) |
| `pad_vam` | bytes | n/a (padding) | — | — | `prop_strconv_pad_left` |

## `roop` — formatting

| Operation | Operands | Overflow / edge | Checked | Saturating | Pinned by |
|---|---|---|---|---|---|
| `roop_ank_aadhar2` / `roop_ank_dhvaj` | `vitti`, base | n/a; `MIN` handled (R26 fix) | — | — | `prop_fmt_int_base_roundtrip`, `prop_min26` |
| `roop_ank` / `roop_ank_aadhar` | `vitti`, base | base `< 2` or `> 36` → `0` (empty); `MIN` handled | — | — | `prop_min26`, `prop_numeric28` (base limits) |
| `roop_dash/hex/hex_upper/oct/bin` | `vitti` | n/a (fixed-base forms of `roop_ank_aadhar2`) | — | — | `prop_fmt_int_base_roundtrip` |
| `roop_varg*` / `roop_varg_ank` | bytes / `vitti` | n/a; grouping is digit-preserving | — | — | `prop_fmt_group_digits`, golden `roop_varg` |
| `roop_sthir` / `roop_sthir_chinhit` | `dasham`, places | requires `\|x\| * 10^places` fits in int64; overflow input returns `0` (empty) — R29 guard (was a segfault: the dasham→int conversion is indefinite past 2^63) | — | — | `prop_numeric29` (overflow → 0, negative overflow → 0, largest fixed output `9223372036854774784` = 2^63 − 1024, 19 chars) |
| `roop_chinhit` / `roop_sign_akshar` | `vitti` | n/a | — | — | `prop_fmt_signed` |
| `roop_pad_vam/right/center` | bytes | n/a (padding) | — | — | `prop_fmt_pad_content` |

## `ank` — found by the same sweep (R28)

Not in the R28 WS3 module suchi, but the same overflow-hang pattern
(`d * d <= x`) was found there by grep and fixed in this round.

| Operation | Operands | Overflow / edge | Pinned by |
|---|---|---|---|
| `asti_sampurna` | `vitti` | `n < 2` → `0`; division bound (the old `d * d` loop hung near MAX) | `prop_numeric28`, golden `numeric_hangfix` |
| `collatz_charan` | `vitti` | `-1` means "does not reach 1": `n < 1`, or the `3x+1` step would overflow int64 (`n > 3074457345618258602` and odd) | `prop_numeric28`, golden `numeric_hangfix` |
| `fib` | `vitti` | **wraps** for large `n` (loop is bounded by `n`, so it terminates); `n < 2` → `n` | — | — | `prop_numeric29` (`fib(93)` wrap) |
| `ank_gan`, `ank_yog`, `viparyay_ank`, `asti_vilom`, `seemit`, `asti_yugm`, `asti_visham` | `vitti` | `viparyay_ank` **wraps** for reversals past MAX; the rest are exact | — | — | `prop_numeric29` (`viparyay_ank` wrap); goldens |

## Gap suchi (behaviour not pinned by a test)

1. `yog_tak` wrapping: defined (wraps) but not pinned — pinning
   needs `n ≈ 4.3e9` iterations, impractical in a test. **OPEN GAP.**

## R29: chakravala fixes and compiler-side findings

`chakravala` (Pell's equation) had two defects, both fixed in
`lib/ganita.smlib`:

- **Perfect-vargit input crashed** (`chakravala(4)` → SIGFPE:
  the search divided by `|k| = 0`). Now returns the trivial
  solution `(1, 0)` with return `1`.
- **Large `|k|` hung.** The old scan `m = 0, 1, 2, ...` needs
  `m ~ 2.9e9` for `n = MAX`. Now solves `b*m = -a (shesh |k|)`
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
  parses as `1.0` (exponent dropped), and `roop_sthir(1e18, ...)`
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
  `yoj`-expanded source at 65536 bytes (`IMPORT_BUF_CAP`).
  The `gaps19` property program (which ayojans
  `nighantu` + `sangrah` + `khand` + `ganita`) now sits ~130 bytes under
  it — the chakravala rewrite had tak be compacted tak fit.
  The library is growing into this cap; raising it is
  compiler-side work.

None of these is a crash: the plain functions wrap deterministically,
and the crash/hang-class inputs (`laghuttam(0,0)`, `brihat_bhajshesh` by zero,
`ganita_vargmool`/`asti_abhajya`/`asti_sampurna` near MAX, `collatz_charan`
overflow) were fixed in R27/R28 and are pinned. The gaps are
contract coverage, not defects.
