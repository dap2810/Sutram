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

## Test pinning

`prop_ok_convention` asserts the container half of this contract
(empty → return 0 + `ok` 0; non-empty → `ok` 1 + correct value for
`stack_pop`/`stack_peek`/`queue_dequeue`/`queue_peek`/`list_min`/
`list_max`). The `ganita` and `strconv` halves are pinned by
`prop_ganita_checked_*`, `prop_ganita_sat`, `prop_safety25`,
`prop_safety26`, `prop_safety27`, and `prop_breadth26`.
