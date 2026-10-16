# The error convention, stated

Charter item 12 (explicit, convenient error handling) is partial:
the checked library functions take an `ok` out-parameter and return a
defined value on failure rather than wrapping — a real, tested
convention. There is no result type, no propagation operator, and no
exhaustiveness checking. This page states the convention as it exists
today, audits every function that follows it, and names what is not
covered.

## The contract

1. **The `ok` parameter is a 1-cell `pankti` (integer array) supplied
   by the caller.** The function writes `ok[0] = 1` on success and
   `ok[0] = 0` on failure, on **every** return path.
2. **On failure the function returns a defined value, never a
   wrapped one.** For integer functions the failure value is `0`;
   for `str_to_float` and `bahu_mula` it is `0.0`.
3. **The caller must check `ok[0]` before trusting the return.**
   A return of `0` with `ok[0] = 0` means "failed"; a return of `0`
   with `ok[0] = 1` means "the answer really is zero".
4. **The caller owns the `ok` cell.** It is not allocated by the
   function; the function only writes `ok[0]`. (The cell may be
   shared across calls, but it is overwritten by each call.)
5. **Saturating functions do not take `ok`.** `ganita_sat_*` always
   succeeds by clamping, so there is nothing to report. Plain
   functions (e.g. `math`'s `power`) wrap silently — that is their
   documented contract; use the checked form when wrapping is not
   acceptable.

## The audit (R28 WS2)

Every function with an `ok` parameter was read line by line. **No
violations found**: all 18 set `ok` on every return path and return a
defined failure value.

| Function | Module | Failure value | Failure cases |
|---|---|---|---|
| `ganita_checked_add` | ganita | `0` | signed overflow |
| `ganita_checked_sub` | ganita | `0` | signed overflow |
| `ganita_checked_mul` | ganita | `0` | signed overflow, incl. `MIN * -1` |
| `ganita_checked_div` | ganita | `0` | divisor 0; `MIN / -1` |
| `ganita_checked_mod` | ganita | `0` | divisor 0; `MIN % -1` |
| `ganita_checked_pow` | ganita | `0` | negative exponent; overflow |
| `ganita_checked_fact` | ganita | `0` | negative `n`; overflow |
| `ganita_checked_abs` | ganita | `0` | `MIN` (no positive form) |
| `str_to_int` | strconv | `0` | empty, malformed, overflow (R26 guard) |
| `str_to_int_base` | strconv | `0` | empty, bad digit, digit ≥ base, overflow |
| `str_to_float` | strconv | `0.0` | empty, malformed, overflow (`> ~1.8e308`) |
| `list_min` / `list_max` | list | `0` | empty list |
| `stack_pop` / `stack_peek` | list | `0` | empty stack |
| `queue_dequeue` / `queue_peek` | list | `0` | empty queue |
| `bahu_mula` | kalana | `0.0` | no sign change on `[lo, hi]` |

Notes:

- `bahu_mula` is the one exception to "integer `ok`": its `ok` is a
  `kosh dasham` (float array) holding `1.0` / `0.0`, because its
  result is `dasham`. Same shape, float cell.
- `str_to_float` returns `0.0` with `ok` **1** in two success cases:
  the input really is zero (`"0"`, `"0e999"`), and extreme underflow
  (`"1e-999"`, as `strtod`). Both are correct values, not failures.
- `ganita_checked_pow` / `ganita_checked_fact` propagate the inner
  `ganita_checked_mul` failure: the loop returns `0` with `ok` 0 as
  soon as a multiplication overflows.

## What is NOT covered by `ok`

- **Sentinels.** Some functions signal "absent" with a documented
  return value instead of `ok`: `map_get` returns `-1` for a missing
  key (use `map_contains` to disambiguate; `map_get_default` takes an
  explicit default), `str_find` / `strb_find` / `strb_find_char`
  return `-1` for not found, `list_remove_at` returns `1` ok / `0`
  out of bounds, `map_remove` / `set_remove` return `1` removed /
  `0` absent.
- **Defined total functions.** `bigint_divmod(a, 0)` returns
  `q = 0, r = a`; `bigint_mod_2n(num, 0)` applies no reduction;
  `lcm(0, 0)` is `0`; `ganita_isqrt` of a negative is `0`;
  `fmt_digits_base` with base outside 2–36 returns `0` (empty).
  These take no `ok` because they never fail — their edge behaviour
  is defined in the function comment and in
  `docs/NUMERIC-CONTRACT.md`.
- **No result type, no propagation, no exhaustiveness.** The
  charter names these as missing. Until they exist, the discipline
  is: check `ok[0]` after every checked call; never read a checked
  return without it.

## The Result type (R29 WS3) — one value instead of two cells

`lib/result.smlib` (layer: core) provides a `Result`: a 2-cell
pankti `[ok, value]` supplied by the caller. `ok` = 1 means
success and `value` holds the answer; `ok` = 0 means failure
and `value` is 0.

| Function | Meaning |
|---|---|
| `result_ok(out, v)` / `result_err(out)` | Write `[1, v]` / `[0, 0]` into `out`. |
| `result_is_ok(r)` / `result_value(r)` | Inspect. `result_value` on a failure returns 0 — check `is_ok` first. |
| `result_value_or(r, def)` | Value if success, else `def` — both branches in one expression. |
| `result_from_ok(out, v, ok)` | Bridge the `ok` convention into a Result. |
| `result_checked_add/sub/mul/div/mod(out, a, b)` | The `ganita` checked operation, producing a Result. Overflow, div/mod by zero, and `MIN / -1` give failure `[0, 0]`. |
| `result_checked_pow(out, a, e)` | `ganita_checked_pow` as a Result (R30). Failure on `e < 0` or overflow. |
| `result_checked_fact(out, n)` | `ganita_checked_fact` as a Result (R30). Failure on `n < 0` or overflow (21! overflows). |
| `result_checked_abs(out, a)` | `ganita_checked_abs` as a Result (R30). Failure on `abs(MIN)`. |

The checked producers pass `out` itself as the `ok` cell to the
`ganita` checked form, so the module allocates nothing and stays
core.

### What a Result buys over the `ok` convention

- **One value carries both.** A Result can be stored, passed,
  and returned from a function without threading a separate `ok`
  cell through every call.
- **Both branches in one expression** via `result_value_or`.
- **The failure is visible in the value itself** — there is no
  separate cell to forget to pass.

### What it still cannot do without compiler support

- **Nothing forces the check.** The caller can still read
  `result_value` without calling `result_is_ok` — exactly like
  ignoring `ok`. There is no exhaustiveness checking.
- **No propagation operator.** The caller still branches by
  hand; there is no `?` / `try` that returns early on failure.
- **No chaining.** `map` / `and_then` need callbacks, which the
  language does not have.
- **No ownership.** A Result is a caller-owned mutable array;
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
    result_checked_add(t, a, b)
    yadi (result_is_ok(t) == 0) {
        result_err(out)
        pratiyati 0
    }
    result_checked_mul(out, result_value(t), c)
    pratiyati result_is_ok(out)
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
  from ignoring `result_is_ok` mid-chain, and there is no
  exhaustiveness check. The chain is only as disciplined as the
  code that writes it.

## Test pinning

`prop_ok_convention` asserts the container half of this contract
(empty → return 0 + `ok` 0; non-empty → `ok` 1 + correct value for
`stack_pop`/`stack_peek`/`queue_dequeue`/`queue_peek`/`list_min`/
`list_max`). The `ganita` and `strconv` halves are pinned by
`prop_ganita_checked_*`, `prop_ganita_sat`, `prop_safety25`,
`prop_safety26`, `prop_safety27`, and `prop_breadth26`.
