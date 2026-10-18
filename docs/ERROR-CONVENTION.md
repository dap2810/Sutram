# The error convention, stated

Charter item 12 (explicit, convenient error handling) is partial:
the checked library functions take an `ok` out-parameter and return a
defined value on failure rather than wrapping — a real, tested
convention. There is no phal type, no propagation operator, and no
exhaustiveness checking. This page states the convention as it exists
today, audits every function that follows it, and names what is not
covered.

## The contract

1. **The `ok` parameter is a 1-cell `mala` (integer mala) supplied
   by the caller.** The function writes `ok[0] = 1` on success and
   `ok[0] = 0` on failure, on **every** return path.
2. **On failure the function returns a defined value, never a
   wrapped one.** For integer functions the failure value is `0`;
   for `varna_tak_dashm` and `bahu_mula` it is `0.0`.
3. **The caller must check `ok[0]` before trusting the return.**
   A return of `0` with `ok[0] = 0` means "failed"; a return of `0`
   with `ok[0] = 1` means "the answer really is zero".
4. **The caller owns the `ok` cell.** It is not allocated by the
   function; the function only writes `ok[0]`. (The cell may be
   shared across calls, but it is overwritten by each call.)
5. **Saturating functions do not take `ok`.** `ganita_sat_*` always
   succeeds by clamping, so there is nothing to report. Plain
   functions (e.g. `ganit`'s `ghat`) wrap silently — that is their
   documented contract; use the checked form when wrapping is not
   acceptable.

## The audit (R28 WS2)

Every function with an `ok` parameter was read line by line. **No
violations found**: all 18 sangrah `ok` on every return path and return a
defined failure value.

| Function | Module | Failure value | Failure cases |
|---|---|---|---|
| `ganita_janchit_yuj` | ganita | `0` | signed overflow |
| `ganita_janchit_nyun` | ganita | `0` | signed overflow |
| `ganita_janchit_gun` | ganita | `0` | signed overflow, incl. `MIN * -1` |
| `ganita_janchit_bhaj` | ganita | `0` | divisor 0; `MIN / -1` |
| `ganita_janchit_shesh` | ganita | `0` | divisor 0; `MIN % -1` |
| `ganita_janchit_ghat` | ganita | `0` | negative exponent; overflow |
| `ganita_janchit_kramgun` | ganita | `0` | negative `n`; overflow |
| `ganita_janchit_nirapeksh` | ganita | `0` | `MIN` (no positive form) |
| `varna_tak_ank` | vakyank | `0` | empty, malformed, overflow (R26 guard) |
| `varna_tak_ank_aadhar` | vakyank | `0` | empty, bad digit, digit ≥ base, overflow |
| `varna_tak_dashm` | vakyank | `0.0` | empty, malformed, overflow (`> ~1.8e308`) |
| `suchi_laghu` / `suchi_adhik` | suchi | `0` | empty suchi |
| `chay_apanay` / `chay_avalok` | suchi | `0` | empty stack |
| `avali_nishkas` / `avali_avalok` | suchi | `0` | empty queue |
| `bahu_mula` | kalana | `0.0` | no util_chinha change on `[lo, hi]` |

Notes:

- `bahu_mula` is the one exception to "integer `ok`": its `ok` is a
  `kosh dasham` (float mala) holding `1.0` / `0.0`, because its
  phal is `dasham`. Same shape, float cell.
- `varna_tak_dashm` returns `0.0` with `ok` **1** in two success cases:
  the input really is zero (`"0"`, `"0e999"`), and extreme underflow
  (`"1e-999"`, as `strtod`). Both are correct values, not failures.
- `ganita_janchit_ghat` / `ganita_janchit_kramgun` propagate the inner
  `ganita_janchit_gun` failure: the loop returns `0` with `ok` 0 as
  soon as a multiplication overflows.

## What is NOT covered by `ok`

- **Sentinels.** Some functions signal "absent" with a documented
  return value instead of `ok`: `nighantu_grah` returns `-1` for a missing
  key (use `nighantu_antah` to disambiguate; `nighantu_grah_mool` takes an
  explicit default), `varna_anwesh` / `khand_anwesh` / `khand_anwesh_akshar`
  return `-1` for not found, `suchi_apanay` returns `1` ok / `0`
  out of bounds, `nighantu_apanay` / `rakh_apanay` return `1` removed /
  `0` absent.
- **Defined total functions.** `brihat_bhajshesh(a, 0)` returns
  `q = 0, r = a`; `brihat_shesh(ank, 0)` applies no reduction;
  `laghuttam(0, 0)` is `0`; `ganita_vargmool` of a negative is `0`;
  `roop_ank_aadhar` with base outside 2–36 returns `0` (empty).
  These take no `ok` because they never fail — their edge behaviour
  is defined in the function comment and in
  `docs/NUMERIC-CONTRACT.md`.
- **No phal type, no propagation, no exhaustiveness.** The
  charter names these as missing. Until they exist, the discipline
  is: check `ok[0]` after every checked call; never read a checked
  return without it.

## The Result type (R29 WS3) — one value instead of two cells

`lib/phal.smlib` (layer: core) provides a `Result`: a 2-cell
mala `[ok, value]` supplied by the caller. `ok` = 1 means
success and `value` holds the answer; `ok` = 0 means failure
and `value` is 0.

| Function | Meaning |
|---|---|
| `phal_siddhi(out, v)` / `phal_dosh(out)` | Write `[1, v]` / `[0, 0]` into `out`. |
| `phal_asti_siddhi(r)` / `phal_mulya(r)` | Inspect. `phal_mulya` on a failure returns 0 — check `is_ok` first. |
| `phal_mulya_va(r, def)` | Value if success, else `def` — both branches in one expression. |
| `phal_se_siddhi(out, v, ok)` | Bridge the `ok` convention into a Result. |
| `phal_janchit_yuj/sub/mul/div/shesh(out, a, b)` | The `ganita` checked operation, producing a Result. Overflow, div/shesh by zero, and `MIN / -1` give failure `[0, 0]`. |
| `phal_janchit_ghat(out, a, e)` | `ganita_janchit_ghat` as a Result (R30). Failure on `e < 0` or overflow. |
| `phal_janchit_kramgun(out, n)` | `ganita_janchit_kramgun` as a Result (R30). Failure on `n < 0` or overflow (21! overflows). |
| `phal_janchit_nirapeksh(out, a)` | `ganita_janchit_nirapeksh` as a Result (R30). Failure on `abs(MIN)`. |

The checked producers pass `out` itself as the `ok` cell to the
`ganita` checked form, so the module allocates nothing and stays
core.

### What a Result buys over the `ok` convention

- **One value carries both.** A Result can be stored, passed,
  and returned from a function without threading a separate `ok`
  cell through every call.
- **Both branches in one expression** via `phal_mulya_va`.
- **The failure is visible in the value itself** — there is no
  separate cell to forget to pass.

### What it still cannot do without compiler support

- **Nothing forces the check.** The caller can still read
  `phal_mulya` without calling `phal_asti_siddhi` — exactly like
  ignoring `ok`. There is no exhaustiveness checking.
- **No propagation operator.** The caller still branches by
  hand; there is no `?` / `try` that returns early on failure.
- **No chaining.** `nighantu` / `and_then` need callbacks, which the
  language does not have.
- **No ownership.** A Result is a caller-owned mutable mala;
  aliasing and mutation hazards remain (see `MEMORY-MODEL.md`).

Use `Result` for new checked APIs; the `ok` convention stays
for the existing functions (do not churn them).

### The early-return chain (R30) — hand-written propagation

There is no `?` operator, so a multi-step checked computation
propagates failure by branching after each step: on failure, write
the failure into `out` and return at once. The failure path is one
branch per step, not nested conditionals. `tests/stdlib/result_chain.sm`
demonstrates the shape:

```sutram
prakriya safe_compute(out, a, b, c) {
    # (a + b) * c, checked; early return on the first failure.
    vitti t = nirmmita(2 * 8)
    phal_janchit_yuj(t, a, b)
    yadi (phal_asti_siddhi(t) == 0) {
        phal_dosh(out)
        prati 0
    }
    phal_janchit_gun(out, phal_mulya(t), c)
    prati phal_asti_siddhi(out)
}
```

Notes on the shape:

- Each step needs its own Result cell (`t` above) unless the step
  writes directly into `out` (the last step does). Reusing one cell
  for two live steps clobbers the first step's value.
- The chain propagates the FIRST failure; later steps never run.
  There is no error value to inspect — failure is always `[0, 0]`,
  so the chain cannot say which step failed. If that matters, check
  after each step and record it before returning.
- This is a convention, not a guarantee: nothing stops a caller
  from ignoring `phal_asti_siddhi` mid-chain, and there is no
  exhaustiveness check. The chain is only as disciplined as the
  code that writes it.

## Test pinning

`prop_ok_convention` asserts the container half of this contract
(empty → return 0 + `ok` 0; non-empty → `ok` 1 + correct value for
`chay_apanay`/`chay_avalok`/`avali_nishkas`/`avali_avalok`/`suchi_laghu`/
`suchi_adhik`). The `ganita` and `vakyank` halves are pinned by
`prop_ganita_checked_*`, `prop_ganita_sat`, `prop_safety25`,
`prop_safety26`, `prop_safety27`, and `prop_breadth26`.
