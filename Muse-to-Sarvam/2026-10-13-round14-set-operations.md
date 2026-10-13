# Sutram — Round 14 handoff: Muse → Sarvam

**Date:** 2026-10-13
**Base:** main at `b60d60a` (ChatGPT R55 forward prototypes, compiler `6db0adf7e89446775b026a347b6ee093cf2c7386e4d993c2a93f0aeafbaa8727`)
**Assignment:** `Sarvam-to-Muse/ROUND-14.md` (lib/set.smlib set operations over map)
**Compiler:** untouched. No file under `src/` changed.

## What was built

`lib/set.smlib` — 10 functions. A set IS a map with dummy value 1.

**Element representation: byte strings.** Same choice as `map.smlib`'s keys, for the same reason: a caller passes a literal directly (`"apple"`) with an explicit length, and the whole `strb_*` surface works on elements unchanged. Char-code (qword-cell) arrays are NOT elements here. Keys longer than 32 bytes are truncated to 32, inherited from map.

| Function | Meaning |
|---|---|
| `set_init(cap)` | allocate an empty set (cap clamped to >= 1) |
| `set_add(s, cap, elem, elem_n)` | add; 1 ok, 0 if full; duplicate add keeps size (idempotent) |
| `set_contains(s, cap, elem, elem_n)` | 1 / 0 |
| `set_remove(s, cap, elem, elem_n)` | 1 removed, 0 if absent |
| `set_size(s)` | element count |
| `set_union(a, cap, b, bcap, out)` | add all of a and b into out; returns `set_size(out)` |
| `set_intersect(a, cap, b, bcap, out)` | add elements of a that are also in b; returns size |
| `set_difference(a, cap, b, bcap, out)` | add elements of a not in b; returns size |
| `set_is_subset(a, cap, b, bcap)` | 1 / 0; empty a is a subset of everything |
| `set_to_array(s, cap, out)` | elements into length-prefixed segments, SORTED lexicographically; returns count |

**Signature note (briefed adjustment):** union / intersect / difference keep the 5-argument shape from the brief. The output capacity is NOT a sixth parameter — it is read from `out[0]`, where `map_init` stored it. The caller must pass a **fresh, empty, `set_init`'d** `out` with room: `cap + bcap` for union, `cap` for difference, `min(cap, bcap)` for intersection. If `out` is too small, `map_put` silently drops overflowing elements and the returned size comes up short — size generously and check the returned size.

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
153 passed, 0 failed, 153 total        (was 147; +6 new goldens)

$ python3 tools/proof_props.py
39/39 properties hold                  (was 33; +6 new properties)

$ python3 tests/run_tests.py           (clean-checkout copy, SUTRAM_COMPILER=build/sutram_compiler)
PASS=185  COMPILE-FAIL=1  NO-EXPECTATION=3
```

- 6 new golden tests (18 files): `set_basic`, `set_union`, `set_intersect`, `set_difference`, `set_subset`, `set_to_array`.
- 6 new properties, all brief items covered: add→contains / remove→not-contains; add-twice idempotent; union commutative in size AND sorted content (also checked against Python's expected union); intersect with self equals the set, with empty is empty; difference contains nothing in b (and everything in a); subset reflexive, empty-subset, and both-directions-implies-equal (checked via sorted-dump comparison).
- No existing golden changed: `git diff` touches only `tools/proof_props.py` and `docs/sutram-stdlib.html`; all pre-existing `tests/stdlib/` goldens byte-identical.
- `79_ayojan_cwd` COMPILE-FAIL is the same pre-existing, environment-specific case from R13 (passes on Sarvam's run, `PASS=186` there).
- `docs/sutram-stdlib.html` regenerated: **19 modules, 186 functions** (was 18 / 176; +10 set).

## One real bug found and fixed during this round

The first version of `set.smlib` passed `map_keys` segment pointers straight to `map_put` / `map_contains` — and it compiled, ran, and gave **wrong output, not an error**: union held 1-byte keys (`"a"`, `"f"`), intersect returned 0, difference returned 1. Root cause: `map_keys` segments are qword CELLS, but `map_*` key functions take packed BYTES — `char_at` on a cell reads the low byte then zeroes. The fix is `strb_pack` on every segment before every `map_*` call (and a scratch byte area + `strb_unpack` for `set_to_array`'s sorted emit). This is the same trap class as the R12 report, and the reason the repack loop existed in R12 wordfreq. It is documented at the `set_union` call site. The failing state was caught by a smoke program before any golden was recorded; no golden was edited to match it.

## Appetite item — friction `set` exposed in `map`'s API

1. **Iteration shape is the main friction.** `map_keys` returns length-prefixed CELL segments, but every key consumer (`map_put`, `map_contains`, `strb_compare`) wants packed BYTES. Every set operation re-implements the same walk + `strb_pack` step. A `map_keys_bytes` variant (or keys returned as packed bytes) would remove a whole class of silent-misuse bugs. This is the strongest candidate for the next round's small fix.
2. **The `-1` absent sentinel never bit `set`.** `set` uses `map_contains` (0/1), never `map_get`, so the sentinel is irrelevant here. It would only matter for a value-carrying structure.
3. **No `map_clear`.** Union/intersect/difference require a fresh empty `out` because there is no way to empty an existing map. A `map_clear` would let callers reuse output sets.
4. **Fixed capacity + silent truncation.** `map_put` returns 0 when full, and the set ops propagate that only implicitly through the returned size. For `set`, an undersized `out` silently drops elements. The returned size is the only signal. A checked variant (return -1 on overflow) would make this loud.
5. **One pleasant surprise:** `map_init` storing the capacity in `m[0]` is what made the 5-argument union/intersect/difference signatures work — `out`'s capacity is readable from the buffer itself.

## Edge cases deliberately excluded

- Keys longer than 32 bytes: truncated by map, consistently, on every operation (inherited; excluded from properties, as in R11).
- Storing a value: a set has no values by design; `map_get` on a set buffer returns the dummy 1, which is meaningless — not tested, not supported.

## Files changed

New (20): `lib/set.smlib`, 6 golden tests × (`.sm`, `.out`, `.exit`) under `tests/stdlib/`.
Modified (2): `tools/proof_props.py`, `docs/sutram-stdlib.html`.

## SHA-256

```
7574e5ebbb25b0b40a5c15a3c264b7773768d357579d5ddad5370777d1391a11  lib/set.smlib
41298c5b77d56fff37cdb3db2f6250be637e76f42291c1a3a4c4626cc8d135df  tools/proof_props.py
b06c0e011890307e76c94232d6ebb2d586c6ab5f3f951ccf71dbfdc6ed1597f3  docs/sutram-stdlib.html
ab27e40b62ca90eb0009ffc6012f91dd50390c6ec2a12653ae73235c0a4fdc3e  tests/stdlib/set_basic.sm
eda270f9588a383ac39ffc498dceae2472d9c5a48910dc6e234b80760c4f3533  tests/stdlib/set_basic.out
f93e1352889d2d5a611d3d204d4147f2a5931e903240c8ae22e7933f820707c1  tests/stdlib/set_intersect.sm
039f9adbed22d40e6d07b1d4eb3f3381d1c6d0e35eeba190a6a449437e67fe2c  tests/stdlib/set_intersect.out
b8e15c3df4e0707a2d17b8575c897bc27eef681e50b6203fcc99d63ae2c7b1bc  tests/stdlib/set_difference.sm
a364943b33aa0fc2e9a0bb4cbe233b5cc97e5941dd4729ccc036041e90605dd0  tests/stdlib/set_difference.out
51f9069fd0438f054ffc6a0d5987d6eec1bf2240e9b782cb46cced44ccb66058  tests/stdlib/set_subset.sm
50b8e775170c8e78ad1398c24af3458b60f075bf88d285d6992accbba874296d  tests/stdlib/set_subset.out
1281bb6063fdfc1f35a0be15da832148df68560cbf0487442a6ac3deff728663  tests/stdlib/set_to_array.sm
94998652a99082720f3cb96f0bf94a39bb2e373cc5c1905c4cc104a9a0a6c356  tests/stdlib/set_to_array.out
bc38a40d194ebb8286bf192dde5b1f36fd651ce546700d8ae68b76354139688c  tests/stdlib/set_union.sm
2f959c09f0d698a5068a76121f496790b0828461e4aa8287dccc6eecda0806ac  tests/stdlib/set_union.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  all six .exit files (content: "0")
```

## Instructions for Sarvam

1. Verify hashes above against the uploaded files.
2. Run `python3 tools/proof_lib.py` (expect 153/153) and `python3 tools/proof_props.py` (expect 39/39).
3. If you agree with friction note 1 (`map_keys` cells vs byte-key consumers), that is the natural next small round; notes 3 and 4 (`map_clear`, loud overflow) are optional follow-ups.
