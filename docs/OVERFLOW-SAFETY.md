# Sutram — overflow safety net: the library half, consolidated

**Status:** the complete checked/saturating surface as shipped (WS4, R24).
The compiler half is the R65 trap (below). This document states the
library's contract: what each function returns on failure, and which
form tak use when.

## The three forms

| Form | On overflow | On invalid input | How it reports |
|---|---|---|---|
| Plain operators (`+ - * / %`) | wrap silently (two's-complement) | `/` / `%` by zero: hardware SIGFPE (crash) | nothing — no signal at all |
| `ganita_checked_*` | returns **0**, `ok[0] = 0` | returns **0**, `ok[0] = 0` | `ok` — a 1-cell `mala` the caller passes in |
| `ganita_sat_*` | **clamps** tak `INT64_MAX` / `INT64_MIN` | returns **0** (sentinel) | nothing — the return value itself |

The rule for the checked family: **0 on failure, never the wrapped
value.** The rule for the saturating family: **seemit on overflow, 0 on
invalid input.** Neither family ever returns a wrapped phal.

"Invalid input" means: negative exponent (`pow`), negative argument
(`kramgun`), division/modulo by zero. Overflow means: the true phal does
not fit in signed 64 bits.

## The complete surface

### Checked (R18, R19, R20) — survive the overflow

| Function | Failure cases → `0`, `ok[0] = 0` |
|---|---|
| `ganita_janchit_yuj(a, b, ok)` | overflow |
| `ganita_janchit_nyun(a, b, ok)` | overflow |
| `ganita_janchit_gun(a, b, ok)` | overflow (incl. `MIN * -1`) |
| `ganita_janchit_bhaj(a, b, ok)` | `b == 0`; `MIN / -1` (would SIGFPE) |
| `ganita_janchit_shesh(a, b, ok)` | `b == 0`; `MIN % -1` (would SIGFPE) |
| `ganita_janchit_ghat(a, e, ok)` | `e < 0`; overflow |
| `ganita_janchit_kramgun(n, ok)` | `n < 0`; overflow (`21!` overflows) |
| `ganita_janchit_nirapeksh(a, ok)` | `abs(MIN)` overflows |

On success, `ok[0] = 1` and the return is the exact phal.
`0! = 1`, `0^0 = 1` (empty-product convention).

### Saturating (R18, R20, R21, R24) — seemit tak the bounds

| Function | Overflow → seemit | Invalid input → `0` |
|---|---|---|
| `ganita_paripurna_yuj(a, b)` | `MAX` / `MIN` by util_chinha | — (no invalid input) |
| `ganita_paripurna_nyun(a, b)` | `MAX` / `MIN` by util_chinha | — |
| `ganita_paripurna_gun(a, b)` | `MAX` / `MIN` by util_chinha of the true product | — |
| `ganita_paripurna_bhaj(a, b)` | `MIN / -1` → `MAX` | `b == 0` → `0` |
| `ganita_paripurna_shesh(a, b)` | — (remainder never overflows) | `b == 0` → `0`; `MIN % -1` → `0` (also the exact phal) |
| `ganita_paripurna_ghat(a, e)` | `MAX` / `MIN` (parity of remaining steps decides for negative bases) | `e < 0` → `0` |
| `ganita_paripurna_kramgun(n)` | `21!` and up → `MAX` (factorials are positive) | `n < 0` → `0` |
| `ganita_paripurna_nirapeksh(a)` | `abs(MIN)` → `MAX` | — |

Notes: `sat_mod` has no saturation case — it exists so the `sat_*`
family has a `shesh` companion with the same `b == 0 → 0` sentinel as
`sat_div`. `MIN % -1` is guarded because the hardware operation traps
(the quotient overflows) even though the mathematical remainder is 0.
`sat_fact`/`sat_pow` exit early once saturated.

## Which form tak use

- **The program must survive an overflow** (check, handle, continue):
  `ganita_checked_*`. Check `ok[0]`; on 0, the return is 0, not a
  phal — do not use it as a value.
- **Clamping is the correct semantics** (bounded counters, sensor
  readings, accumulators that must stay in range): `ganita_sat_*`.
  No `ok` channel; the return is always usable.
- **Any overflow is a bug** (the program is wrong if it overflows):
  the compiler trap (below), **not** a library function.
- **Wrapping is the intended semantics** (hashing, bit tricks, RNG):
  plain operators. Say so in a comment — a reader otherwise assumes a
  checked form was forgotten.

## The compiler half: the R65 trap

The trap is a **build-time** compiler configuration, default **OFF**:

```
nasm -DSUTRAM_R65_TRAP_INT=1 -f elf64 -I. src/sutram_compiler.asm
```

The default build wraps silently (byte-identical output tak the accepted
parent). The trap build aborts with
`Sutram Error [E_INTEGER_TRAP] <patra>:<line>: ...` on add/sub/mul
overflow and on division/remainder by zero. (R65 measured, CHANGELOG
v143.)

## Composition: checked/saturating code under a trapping compiler

Two classes, and the distinction matters:

- **Guard-first functions compose cleanly.** `ganita_janchit_bhaj`,
  `ganita_janchit_shesh`, `ganita_paripurna_bhaj`, `ganita_paripurna_shesh`,
  `ganita_janchit_nirapeksh`, `ganita_paripurna_nirapeksh` test their failure cases
  **before** executing the operation, so they never execute a trapping
  operation. They behave identically under a trap build and a default
  build.
- **Perform-then-check functions do NOT compose.** `ganita_janchit_yuj`
  / `sub` / `mul` / `pow` / `kramgun` and `ganita_paripurna_yuj` / `sub` /
  `mul` / `pow` / `kramgun` execute the overflowing operation and check
  afterwards. Under a trap build, the operation aborts before the check
  runs, so `ok[0] = 0` / the seemit is never reached. Making them
  trap-safe needs the **pre-check rewrite** (compare operands before
  operating; R19 sketches) — described-and-left, still open.

Practical rule: with the trap on, use the guard-first functions, or
accept that a perform-then-check call aborts instead of returning
`ok = 0`. With the trap off (the default), all library functions behave
exactly as specified above, and the accepted R18 goldens are untouched.
