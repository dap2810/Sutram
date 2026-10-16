# The property suite as a regression net

`tools/proof_props.py` holds **76 properties** (69 at the start of Round 26,
plus `safety26 interaction`, `breadth26`, and `min26` added in R26,
`safety27 cross-module` and `bigint divzero` added in R27, and
`ok convention` and `numeric28` added in R28). For each one,
this file states in one line **what would have to break for it to fail**.
Method (R26 WS2): every property's assertion was read, and the four most
suspicious ones (`fnv1a_deterministic`, `fnv1a_avalanche`, `map_collision`,
`map_keys_count`) were read line by line.

## Verdict

**All 76 are genuine, falsifiable tests. None removed.** Every property
compares its subject against an independent oracle (Python arithmetic, a
second implementation, or an invariant the function itself must uphold),
so each has a concrete failure mode. Two caveats are recorded below; neither
makes its property vacuous.

- **Caveat 1 — `hash fnv1a avalanche`:** the name overpromises. It checks
  five fixed pairs hash differently (a constant or input-ignoring hash
  fails), not a statistical avalanche measurement. Kept as a
  distinctness check; a real avalanche test would need bit-flip statistics.
- **Caveat 2 — `string split/join`, `strb split/join`:** both skip the
  trailing-separator edge (documented in the code: it yields an extra empty
  segment). The round-trip is tested everywhere else. Kept; the edge is a
  known documented limitation, not a hole in the net.

## The net, property by property

| # | Property | What would have to break for it to fail |
|---|---|---|
| 1 | bigint add/sub inverse | `bigint_add` or `bigint_sub` miscomputing, so add-then-sub does not restore `b` |
| 2 | bigint mul distributes over add | `bigint_mul` or `bigint_add` wrong, so `a*(b+c) != a*b + a*c` |
| 3 | bigint from_int/to_int roundtrip | `bigint_from_int` or `bigint_to_int` losing bits or misplacing limbs |
| 4 | bigint divmod reconstruct | `bigint_divmod` wrong quotient/remainder, so `q*b + r != a` or `r >= b` |
| 5 | math gcd divides | `gcd` returning a non-divisor of `a` or `b` |
| 6 | math gcd*lcm == a*b | `gcd` or `lcm` wrong, so the identity fails |
| 7 | hash fnv1a deterministic | `fnv1a` reading uninitialized state or randomness, so two calls differ |
| 8 | hash fnv1a empty == basis | `fnv1a` wrong offset basis or hashing the empty string as non-empty |
| 9 | hash fnv1a avalanche | `fnv1a` constant or input-ignoring, so two distinct strings collide (see caveat 1) |
| 10 | sort output ordered | `insertion_sort`/`merge_sort` leaving the output unordered |
| 11 | sort permutation | the two sorts disagreeing, so one of them drops/duplicates an element |
| 12 | sort idempotent | a sort disturbing already-sorted input |
| 13 | sort edge cases | empty/single-element arrays crashing or returning the wrong length |
| 14 | baseconv roundtrip | `bigint_to_digits`/`bigint_from_digits` losing digits for some base |
| 15 | strconv roundtrip | `int_to_str`/`str_to_int` disagreeing on some value (incl. negatives, 0) |
| 16 | strconv base roundtrip | `int_to_base_str`/`str_to_int_base` disagreeing for base 2/8/10/16 |
| 17 | strconv pad_left | `pad_left` changing the digits, misplacing the fill, or returning the wrong length |
| 18 | string find vs python | `str_find` disagreeing with Python `str.find` (incl. absent needle) |
| 19 | string replace | `str_replace` disagreeing with Python `str.replace`, or `find` still finding the old text |
| 20 | string split/join | `str_split`/`str_join` not round-tripping (see caveat 2) |
| 21 | string trim/case | `str_trim`/`str_upper`/`str_lower` disagreeing with Python strip/upper/lower |
| 22 | strb find vs python | `strb_find` disagreeing with Python `str.find` on byte strings |
| 23 | strb replace | `strb_replace` disagreeing with Python `str.replace` |
| 24 | strb split/join | `strb_split`/`strb_join` not round-tripping (see caveat 2) |
| 25 | strb trim/case | `strb_trim`/`strb_upper`/`strb_lower` disagreeing with Python |
| 26 | map put/get roundtrip | `map_put`/`map_get` losing a stored value |
| 27 | map update | re-putting a key changing size or keeping the old value |
| 28 | map delete | `map_remove` leaving the key present, size wrong, or disturbing other keys |
| 29 | map collision survival | linear probing losing an entry when three keys share a bucket |
| 30 | map keys count | `map_keys` returning the wrong count or wrong total byte length |
| 31 | strb pack/unpack roundtrip | `strb_pack`/`strb_unpack` losing or reordering bytes in either direction |
| 32 | strb dup | `strb_dup` copying the wrong bytes or mishandling empty input |
| 33 | sankhyiki purna int stats | `purna_*` stats disagreeing with Python (incl. trunc division, negatives, empty) |
| 34 | set add/contains/remove | `set_add`/`set_contains`/`set_remove` disagreeing on membership |
| 35 | set add idempotent | `set_add` of a present element changing the size |
| 36 | set union commutative | `set_union` depending on argument order (size or sorted content) |
| 37 | set intersect self/empty | intersect-with-self not equalling the set, or intersect-with-empty non-empty |
| 38 | set difference | `set_difference` keeping an element of `b` or disagreeing with Python |
| 39 | set subset | `set_subset` violating reflexivity, empty-subset, or antisymmetry |
| 40 | fmt int base roundtrip | `fmt_int_base` rendering a value its own parser misreads, or bad bases accepted |
| 41 | fmt pad content | padding changing the non-pad content or returning the wrong length |
| 42 | fmt group digits | grouping changing the digits or disagreeing with Python grouping |
| 43 | fmt fixed decimals | `fmt_fixed` rounding differently from Python half-away-from-zero |
| 44 | fmt signed | `fmt_signed`/`fmt_sign_char` disagreeing with Python on sign or digits |
| 45 | list push/get | `list_push`/`list_get` losing a value, incl. past initial capacity |
| 46 | list stack LIFO | stack pops not in reverse push order, peek mutating, or empty pop/peek not failing |
| 47 | list queue FIFO | queue dequeues out of order, peek mutating, or empty dequeue/peek not failing |
| 48 | list len tracks | `list_len` drifting from the true count across push/insert/remove/clear |
| 49 | list insert/remove | insert/remove shifting the wrong elements (full contents vs Python list) |
| 50 | map keys_bytes roundtrip | `map_keys_bytes` dropping/duplicating a key, miscounting bytes, or mishandling 33-byte truncation |
| 51 | ganita checked add/sub | `checked_add`/`checked_sub` returning the wrong value or wrong `ok` vs unbounded Python |
| 52 | ganita checked mul | `checked_mul` returning the wrong value or wrong `ok` vs unbounded Python |
| 53 | ganita checked div/mod | `checked_div`/`checked_mod` disagreeing with truncating Python division, or wrong `ok` on div-by-zero / `MIN/-1` |
| 54 | ganita saturating | `sat_add`/`sat_sub`/`sat_mul` disagreeing with Python results clamped to `[MIN64, MAX64]` |
| 55 | map_clear reuse | `map_clear` not zeroing state/key bytes, leaving old keys, or failing reuse |
| 56 | containers clear | `set_clear`/`list_clear`/`queue_clear` not zeroing storage or failing reuse |
| 57 | gaps19 | `map_get_default`, `set_equals`, `strb_reverse`, `strb_count`, or `ganita_checked_pow` disagreeing with Python |
| 58 | strb cell pairs | explicit-length `strb_*` forms or cell `str_reverse`/`str_count` disagreeing with Python |
| 59 | containers resize/swap | `map_resize`/`set_resize`/`list_swap`/`list_reverse` disagreeing with Python |
| 60 | gaps20 | `ganita_checked_fact`/`ganita_sat_pow` disagreeing with Python (incl. huge-exponent early exit) |
| 61 | containers21 | `list_sort`/`min`/`max`/`sum`/`count`, `queue_contains`, or `map_values` disagreeing with Python |
| 62 | gaps21 | `ganita_sat_fact` disagreeing with clamped Python factorials (incl. huge-n early exit) |
| 63 | containers23 | `list_find`/`is_sorted`/`binary_search` or `queue_to_array` disagreeing with Python |
| 64 | gaps23 | `map_merge`/`set_sym_diff` disagreeing with Python (incl. partial merge on full destination) |
| 65 | slices23 | explicit-length `strb_*` on slices disagreeing with Python slices, or the NUL forms not seeing past the slice end |
| 66 | invariants24 containers | `binary_search` disagreeing with `find` on a sorted list, or `queue_to_array` mutating the queue |
| 67 | invariants24 merge/symdiff | `map_merge` not associative with src-wins, or `set_sym_diff` not symmetric / not empty with itself / not identity with empty |
| 68 | safety24 | `sat_div`/`sat_mod`/`checked_abs`/`sat_abs` disagreeing with Python (incl. `MIN/-1`, div-by-zero, `abs(MIN)`) |
| 69 | safety25 oracle | any of the 16 checked/saturating functions violating the contract (failure → 0 + `ok` 0, overflow → clamp, success exact) |
| 70 | safety26 interaction | sat and checked disagreeing on the success path, sat not the clamp on overflow / 0 on invalid input, or a saturating function wrapping |
| 71 | breadth26 | `math_rand` non-deterministic or off the LCG sequence, `math_clamp` off Python, or `str_to_float` off Python `float()` beyond 1e-9 relative |
| 72 | min26 | `int_to_str(MIN)` not "-9223372036854775808", `fmt_digits_base` mishandling negatives, or `fmt_int_base`/`fmt_int_flags` wrong on MIN in some base |
| 73 | safety27 cross-module | `strconv`'s parse guards and `ganita`'s checked forms disagreeing on the same magnitude (one accepts what the other rejects), or either returning a wrapped value on overflow |
| 74 | bigint divzero | `bigint_divmod` by zero hanging or returning anything but `q=0, r=a`, or `bigint_powmod` with mod 0 hanging or not returning the unreduced power |
| 75 | ok convention | an `ok`-param container function failing to set `ok` on some path, or returning anything but the defined failure value `0` on empty |
| 76 | numeric28 | `gcd`/`lcm` returning a negative, `lcm(0,0)` trapping, `power`/`fact`/`sum_to` edges wrong, `abs_val(MIN)` not wrapping, `bit_count` negative not `0`, `isqrt`/`is_prime`/`is_perfect`/`collatz` domain limits wrong |

## R27: is there a property that has never failed and never could?

**No.** Re-checked in R27 (WS2): every property compares its subject
against an independent oracle, so every one has a concrete failure mode
(the table above). "Never failed in CI" is not "could never fail" — a
property guards against a *plausible* regression, and the plausible
regression is the failure mode. Two pieces of evidence that the net can
actually fail:

- Four properties failed during their own development: `safety26`
  (the re-declaration compiler bug made it report a false
  checked/sat disagreement), `breadth26` (statement limit, then a
  literal-format issue), `min26` (a wrong expected value in the
  property itself), `safety27` (a wrong hex expectation in the property
  itself). Three of those four were bugs in the property code, not the
  library — which is still evidence the assertions are evaluated, not
  vacuous.
- The closest call, `hash fnv1a deterministic`, compares `fnv1a(s)`
  against itself — but it tests determinism, and it would fail against
  a plausible broken implementation (one reading uninitialized state
  or a random seed). It is kept deliberately.
