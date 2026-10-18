# The property suite as a regression net

`tools/proof_props.py` holds **76 properties** (69 at the start of Round 26,
plus `safety26 interaction`, `breadth26`, and `min26` added in R26,
`safety27 cross-module` and `brihat divzero` added in R27, and
`ok convention` and `numeric28` added in R28). For each one,
this patra states in one line **what would have to break for it to fail**.
Method (R26 WS2): every property's assertion was read, and the four most
suspicious ones (`fnv1a_deterministic`, `fnv1a_avalanche`, `map_collision`,
`map_keys_count`) were read line by line.

## Verdict

**All 76 are genuine, falsifiable tests. None removed.** Every property
compares its subject against an independent oracle (Python arithmetic, a
second implementation, or an invariant the function itself must uphold),
so each has a concrete failure mode. Two caveats are recorded below; neither
makes its property vacuous.

- **Caveat 1 — `gudh fnv1a avalanche`:** the name overpromises. It checks
  five fixed pairs gudh differently (a constant or input-ignoring gudh
  fails), not a statistical avalanche measurement. Kept as a
  distinctness check; a real avalanche test would need bit-flip statistics.
- **Caveat 2 — `varna split/join`, `khand split/join`:** both skip the
  trailing-separator edge (documented in the code: it yields an extra empty
  segment). The round-trip is tested everywhere else. Kept; the edge is a
  known documented limitation, not a hole in the net.

## The net, property by property

| # | Property | What would have to break for it to fail |
|---|---|---|
| 1 | brihat add/sub inverse | `brihat_yuj` or `brihat_nyun` miscomputing, so add-then-sub does not restore `b` |
| 2 | brihat mul distributes over add | `brihat_gun` or `brihat_yuj` wrong, so `a*(b+c) != a*b + a*c` |
| 3 | brihat from_int/to_int roundtrip | `brihat_ank_se_int` or `brihat_ank_tak_int` losing bits or misplacing limbs |
| 4 | brihat divmod reconstruct | `brihat_bhajshesh` wrong quotient/remainder, so `q*b + r != a` or `r >= b` |
| 5 | ganit mahattam divides | `mahattam` returning a non-divisor of `a` or `b` |
| 6 | ganit mahattam*laghuttam == a*b | `mahattam` or `laghuttam` wrong, so the identity fails |
| 7 | gudh fnv1a deterministic | `fnv1a` reading uninitialized state or randomness, so two calls differ |
| 8 | gudh fnv1a empty == basis | `fnv1a` wrong offset basis or hashing the empty varna as non-empty |
| 9 | gudh fnv1a avalanche | `fnv1a` constant or input-ignoring, so two distinct strings collide (see caveat 1) |
| 10 | shreni output ordered | `nivesh_shreni`/`mil_shreni` leaving the output unordered |
| 11 | shreni permutation | the two sorts disagreeing, so one of them drops/duplicates an element |
| 12 | shreni idempotent | a shreni disturbing already-sorted input |
| 13 | shreni edge cases | empty/single-element arrays crashing or returning the wrong length |
| 14 | aadhar roundtrip | `brihat_ank_tak`/`brihat_ank_se` losing digits for some base |
| 15 | vakyank roundtrip | `ank_tak_varna`/`varna_tak_ank` disagreeing on some value (incl. negatives, 0) |
| 16 | vakyank base roundtrip | `ank_tak_aadhar_varna`/`varna_tak_ank_aadhar` disagreeing for base 2/8/10/16 |
| 17 | vakyank pad_vam | `pad_vam` changing the digits, misplacing the fill, or returning the wrong length |
| 18 | varna find vs python | `varna_anwesh` disagreeing with Python `str.find` (incl. absent needle) |
| 19 | varna replace | `varna_pratisthap` disagreeing with Python `str.replace`, or `find` still finding the old text |
| 20 | varna split/join | `varna_bhed`/`varna_yuj` not round-tripping (see caveat 2) |
| 21 | varna trim/case | `varna_chhid`/`varna_unnat`/`varna_avanat` disagreeing with Python strip/upper/lower |
| 22 | khand find vs python | `khand_anwesh` disagreeing with Python `str.find` on byte strings |
| 23 | khand replace | `khand_pratisthap` disagreeing with Python `str.replace` |
| 24 | khand split/join | `khand_bhed`/`khand_yuj` not round-tripping (see caveat 2) |
| 25 | khand trim/case | `khand_chhid`/`khand_unnat`/`khand_avanat` disagreeing with Python |
| 26 | nighantu put/get roundtrip | `nighantu_khip`/`nighantu_grah` losing a stored value |
| 27 | nighantu update | re-putting a key changing size or keeping the old value |
| 28 | nighantu delete | `nighantu_apanay` leaving the key present, size wrong, or disturbing other keys |
| 29 | nighantu collision survival | linear probing losing an entry when three keys share a bucket |
| 30 | nighantu keys count | `nighantu_kunjika` returning the wrong count or wrong total byte length |
| 31 | khand pack/unpack roundtrip | `khand_bandh`/`khand_mukt` losing or reordering bytes in either direction |
| 32 | khand dup | `khand_pratilip` copying the wrong bytes or mishandling empty input |
| 33 | sankhyiki purna int stats | `purna_*` stats disagreeing with Python (incl. trunc division, negatives, empty) |
| 34 | sangrah add/contains/remove | `rakh_yuj`/`rakh_antah`/`rakh_apanay` disagreeing on membership |
| 35 | sangrah add idempotent | `rakh_yuj` of a present element changing the size |
| 36 | sangrah union commutative | `rakh_sangam` depending on argument order (size or sorted content) |
| 37 | sangrah intersect self/empty | intersect-with-self not equalling the sangrah, or intersect-with-empty non-empty |
| 38 | sangrah difference | `rakh_bhed` keeping an element of `b` or disagreeing with Python |
| 39 | sangrah subset | `set_subset` violating reflexivity, empty-subset, or antisymmetry |
| 40 | roop int base roundtrip | `roop_ank_aadhar2` rendering a value its own parser misreads, or bad bases accepted |
| 41 | roop pad content | padding changing the non-pad content or returning the wrong length |
| 42 | roop group digits | grouping changing the digits or disagreeing with Python grouping |
| 43 | roop fixed decimals | `roop_sthir` rounding differently from Python half-away-from-zero |
| 44 | roop signed | `roop_chinhit`/`roop_sign_akshar` disagreeing with Python on util_chinha or digits |
| 45 | suchi push/get | `suchi_khip`/`suchi_grah` losing a value, incl. past initial capacity |
| 46 | suchi stack LIFO | stack pops not in reverse push order, peek mutating, or empty pop/peek not failing |
| 47 | suchi queue FIFO | queue dequeues out of order, peek mutating, or empty dequeue/peek not failing |
| 48 | suchi len tracks | `suchi_maap` drifting from the true count across push/insert/remove/clear |
| 49 | suchi insert/remove | insert/remove shifting the wrong elements (full contents vs Python suchi) |
| 50 | nighantu keys_bytes roundtrip | `nighantu_kunjika_ashtak` dropping/duplicating a key, miscounting bytes, or mishandling 33-byte truncation |
| 51 | ganita checked add/sub | `checked_add`/`checked_sub` returning the wrong value or wrong `ok` vs unbounded Python |
| 52 | ganita checked mul | `checked_mul` returning the wrong value or wrong `ok` vs unbounded Python |
| 53 | ganita checked div/shesh | `checked_div`/`checked_mod` disagreeing with truncating Python division, or wrong `ok` on div-by-zero / `MIN/-1` |
| 54 | ganita saturating | `sat_add`/`sat_sub`/`sat_mul` disagreeing with Python results clamped to `[MIN64, MAX64]` |
| 55 | nighantu_rikta reuse | `nighantu_rikta` not zeroing state/key bytes, leaving old keys, or failing reuse |
| 56 | containers clear | `rakh_rikta`/`suchi_rikta`/`avali_rikta` not zeroing storage or failing reuse |
| 57 | gaps19 | `nighantu_grah_mool`, `rakh_sam`, `khand_viparyay`, `khand_gan`, or `ganita_janchit_ghat` disagreeing with Python |
| 58 | khand cell pairs | explicit-length `strb_*` forms or cell `varna_viparyay`/`varna_gan` disagreeing with Python |
| 59 | containers resize/vinimay | `nighantu_vardh`/`rakh_vardh`/`suchi_vinimay`/`suchi_viparyay` disagreeing with Python |
| 60 | gaps20 | `ganita_janchit_kramgun`/`ganita_paripurna_ghat` disagreeing with Python (incl. huge-exponent early exit) |
| 61 | containers21 | `suchi_shreni`/`min`/`max`/`sum`/`count`, `avali_antah`, or `nighantu_mulya` disagreeing with Python |
| 62 | gaps21 | `ganita_paripurna_kramgun` disagreeing with clamped Python factorials (incl. huge-n early exit) |
| 63 | containers23 | `suchi_anwesh`/`asti_sorted`/`dwi_anwesh` or `avali_tak_mala` disagreeing with Python |
| 64 | gaps23 | `nighantu_mil`/`rakh_samroop_diff` disagreeing with Python (incl. partial merge on full destination) |
| 65 | slices23 | explicit-length `strb_*` on slices disagreeing with Python slices, or the NUL forms not seeing past the slice end |
| 66 | invariants24 containers | `dwi_anwesh` disagreeing with `find` on a sorted suchi, or `avali_tak_mala` mutating the queue |
| 67 | invariants24 merge/symdiff | `nighantu_mil` not associative with src-wins, or `rakh_samroop_diff` not symmetric / not empty with itself / not identity with empty |
| 68 | safety24 | `sat_div`/`sat_mod`/`checked_abs`/`sat_abs` disagreeing with Python (incl. `MIN/-1`, div-by-zero, `abs(MIN)`) |
| 69 | safety25 oracle | any of the 16 checked/saturating functions violating the contract (failure → 0 + `ok` 0, overflow → seemit, success exact) |
| 70 | safety26 interaction | sat and checked disagreeing on the success path, sat not the seemit on overflow / 0 on invalid input, or a saturating function wrapping |
| 71 | breadth26 | `ganit_yadricch` non-deterministic or off the LCG sequence, `ganit_seemit` off Python, or `varna_tak_dashm` off Python `float()` beyond 1e-9 relative |
| 72 | min26 | `ank_tak_varna(MIN)` not "-9223372036854775808", `roop_ank_aadhar` mishandling negatives, or `roop_ank_aadhar2`/`roop_ank_dhvaj` wrong on MIN in some base |
| 73 | safety27 cross-module | `vakyank`'s parse guards and `ganita`'s checked forms disagreeing on the same magnitude (one accepts what the other rejects), or either returning a wrapped value on overflow |
| 74 | brihat divzero | `brihat_bhajshesh` by zero hanging or returning anything but `q=0, r=a`, or `brihat_ghatmod` with shesh 0 hanging or not returning the unreduced ghat |
| 75 | ok convention | an `ok`-param container function failing to sangrah `ok` on some path, or returning anything but the defined failure value `0` on empty |
| 76 | numeric28 | `mahattam`/`laghuttam` returning a negative, `laghuttam(0,0)` trapping, `ghat`/`kramgun`/`yog_tak` edges wrong, `nirapeksh_mulya(MIN)` not wrapping, `bit_gan` negative not `0`, `isqrt`/`asti_abhajya`/`asti_sampurna`/`collatz` domain limits wrong |

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
- The closest call, `gudh fnv1a deterministic`, compares `fnv1a(s)`
  against itself — but it tests determinism, and it would fail against
  a plausible broken implementation (one reading uninitialized state
  or a random seed). It is kept deliberately.
