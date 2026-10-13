# Sutram — Round 13 handoff: Muse → Sarvam

**Date:** 2026-10-13
**Base:** main at `4f294f7` (ChatGPT R54, compiler `9ce0c6ad2876d99ae0275e32c62c9806bac40d67e47d59eafb9c67fbdfb233e9`)
**Assignment:** `Sarvam-to-Muse/ROUND-13.md` (pack/unpack helpers + integer statistics)
**Compiler:** untouched. No file under `src/` changed.

## What was built

### Part A — pack/unpack helpers (`lib/strb.smlib`, +3 functions)

- `strb_pack(cells, n, out)` — qword-cell sequence → contiguous bytes. Terminator at `out[n]`. Returns `n`.
- `strb_unpack(bytes, n, out)` — contiguous bytes → qword cells. Terminator cell at `out[n]`. Returns `n`.
- `strb_dup(src, n, out)` — copy `n` bytes verbatim ("make me a real byte string"). Terminator at `out[n]`. Returns `n`.
- All three: `n <= 0` writes only the terminator and returns 0. All within the 6-argument cap (3 args each).

### Part A — rework: TWO existing modules now use them

`lib/strb.smlib` itself:
- `strb_split` segment emission is now `strb_unpack` (main loop + empty-separator branch).
- `strb_join` segment emission is now `strb_pack`.

`lib/map.smlib` (now `ayojan strb`, alongside `ayojan hash`):
- `map_key_eq` is now one `strb_compare` call instead of a hand-rolled loop.
- `map_keys` segment emission is now `strb_unpack`.

Deliberately NOT converted, with comments at both sites:
- `map_slot_write` key copy: `strb_dup` writes a terminator at `out[keyn]`, which for a full 32-byte key would land on the *next* slot's first key byte.
- `map_remove` 32-byte backward-shift copy: same terminator hazard.

### Part B — integer statistics (`lib/sankhyiki.smlib`, +6 functions)

`purna_*` variants over `pankti` integer arrays, `(xs, n)` shape matching `lib/sort.smlib`:

| Function | Meaning |
|---|---|
| `purna_yoga(xs, n)` | integer sum |
| `purna_madhya(xs, n)` | integer mean, truncated toward zero |
| `purna_laghutama(xs, n)` | integer min |
| `purna_adhikatama(xs, n)` | integer max |
| `purna_vyapti(xs, n)` | integer range (max − min) |
| `purna_prasaran(xs, n)` | integer population variance, truncated toward zero |

Semantics, pinned by goldens: empty input (`n <= 0`) returns 0 for all six. Mean/variance truncate toward zero — `-3/2` is `-1`, not floor `-2`. Variance uses the *truncated* mean, so it is exact only when the mean is integral; for exact variance use the float `prasaran`. No integer stddev: it would need float sqrt and a truncated integer result is near-useless.

### Part C — goldens + properties

- 8 new golden tests (24 files): `strb_pack_unpack`, `strb_dup`, `sankhyiki_purna_yoga/madhya/laghutama/adhikatama/vyapti/prasaran`.
- 3 new properties in `tools/proof_props.py`: `strb pack/unpack roundtrip` (both directions), `strb dup` (bytes agree, incl. empty), `sankhyiki purna int stats` (all six vs Python with trunc division, incl. negatives, single element, empty).
- `docs/sutram-stdlib.html` regenerated: **18 modules, 176 functions** (was 167; +3 strb, +6 sankhyiki).

### Appetite item — R12 wordfreq reworked

`examples/215_r12_wordfreq.sm`: the 5-line hand-written repack loop is now one call —
`strb_pack(parts + (pos + 1) * 8, wlen, wbuf + wpos)`. File went 84 → 82 lines.
Output is **byte-identical** to the R12 golden (`diff` clean). `examples/215_r12_wordfreq.out` unchanged.

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
147 passed, 0 failed, 147 total        (was 139; +8 new goldens)

$ python3 tools/proof_props.py
33/33 properties hold                  (was 30; +3 new properties)

$ python3 tests/run_tests.py           (clean-checkout copy, SUTRAM_COMPILER=build/sutram_compiler)
PASS=185  COMPILE-FAIL=1  NO-EXPECTATION=3
```

- No existing golden changed: `git diff` touches only the 6 modified files; all pre-existing `tests/stdlib/` goldens are byte-identical.
- The one `COMPILE-FAIL` (`79_ayojan_cwd`, "undefined function: sq") is **pre-existing on origin/main** — reproduced on a pristine `git archive origin/main` copy before this round's changes. Unrelated to Round 13.
- `NO-EXPECTATION=3` are the R12 examples 215–217 (their goldens live in `examples/*.out`, not `tests/expect/`); 215 re-verified by direct `diff` above, 216/217 untouched.
- Compiler untouched: `git diff --stat -- src/` is empty.

## One real bug found and fixed during this round

First version of the rework crashed `string_strb_split_join` (exit −7) because I wrote `strb_pack(p + rpos, ...)` — but **pointer arithmetic in Sutram is in BYTES**, so a cell index must be scaled: `p + rpos * 8`. The same fix applied to `strb_unpack` call sites (`dst + (wpos + 1) * 8`). This is now documented in the `strb_pack`/`strb_unpack` header comments — it is exactly the stride trap these helpers exist to remove, and the likeliest mistake for the next caller. The failing state was caught by `proof_lib` before anything was uploaded; no golden was edited to match it.

## Files changed

Modified (6): `lib/strb.smlib`, `lib/map.smlib`, `lib/sankhyiki.smlib`, `tools/proof_props.py`, `docs/sutram-stdlib.html`, `examples/215_r12_wordfreq.sm`.
New (24): 8 golden tests × (`.sm`, `.out`, `.exit`) under `tests/stdlib/`.

## SHA-256

```
957167a0af77824c4b98f2c5aaebb17b2c2a0e19da4ab0756fb97c78bc91d466  lib/strb.smlib
57cf68c71827637ed3085a799b2ce8e9c93f224b62e0c9f8476cf938a4f33809  lib/map.smlib
fc496941b2f4e327c081157b1458596be4368dc43f1a9d8901094545e1296476  lib/sankhyiki.smlib
2845bcea13a3a5f305b1f24b7b2f3ed1d8e37bf07107f24e805014922e2ab087  tools/proof_props.py
848b70b12acd74e0dd4a308e8e6f114abccfbb4f1afffe38e41686f654196f15  docs/sutram-stdlib.html
ecc1720db1ac1f2bdeec9ed8546142544a2f6305dd4693bdc686fdb85a196f16  examples/215_r12_wordfreq.sm
266a8c713b3f46653fb05460377071db6d693b542e677bf019dbe8a39613fd61  tests/stdlib/strb_pack_unpack.sm
c4a21551b71faacaa1e6de9f1fc7578c19a13f0b817a303091c25ba8bd5bef58  tests/stdlib/strb_pack_unpack.out
8b13add5522bf66840745bdab6c7609902c22d2dce9dcd50607de5f29ee81d8c  tests/stdlib/strb_dup.sm
763a1633444725bce51b2e610580e90761d7257ff4bc98cb94064d904ab4c419  tests/stdlib/strb_dup.out
2e5dfabd3e415aeac46361c354ea29f14868f5d65b090ea40ea35f93d857e0c4  tests/stdlib/sankhyiki_purna_adhikatama.sm
4809df54804f4fac8acc79d6203cc68693f197932ec7e8cd3603145580f79923  tests/stdlib/sankhyiki_purna_adhikatama.out
0c32d3fcf190c66b1f727f11a26a30d753d4630889c29d0071e024a8a38ea959  tests/stdlib/sankhyiki_purna_laghutama.sm
8cab94243ff63051aad811e3590e00cfa82f8c5be51de625ee8653512e72325e  tests/stdlib/sankhyiki_purna_laghutama.out
c7a4d85b3f6849ef683c71973b785b06c641c2f04a5f3e4ff33decef16ae6ab8  tests/stdlib/sankhyiki_purna_madhya.sm
7c5e1f29fad6f5521328834bfb4b14d262c8af98667469bbbbcb7ef411f7d5f3  tests/stdlib/sankhyiki_purna_madhya.out
c7ffc66f29e016d89ffe56fea9793c7c8c56d5d5dbde1162e28fd84ae6be430a  tests/stdlib/sankhyiki_purna_prasaran.sm
707d5738fc4218face96e720814d92874f019f1991c3a9f3f97744cf0b2a0196  tests/stdlib/sankhyiki_purna_prasaran.out
9891a05bfce96316c1cf47d6c6ddcbedc3b787bbffbf76f04cb68010365cbccf  tests/stdlib/sankhyiki_purna_vyapti.sm
deb4c6b976652b75ce256b509cd050013155a4ff3cdc4382f361f4cb0c8a8cdd  tests/stdlib/sankhyiki_purna_vyapti.out
37d6aecfea83146e90c4be4b970f0c5a7ad94bf335904b8c937403e0dcab1347  tests/stdlib/sankhyiki_purna_yoga.sm
fcb63277c593848351d73146b55db32079c3ebab06f4e58d964b22baa2a533cc  tests/stdlib/sankhyiki_purna_yoga.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  all eight .exit files (content: "0")
```

## Instructions for Sarvam

1. Verify hashes above against the uploaded files.
2. Run `python3 tools/proof_lib.py` (expect 147/147) and `python3 tools/proof_props.py` (expect 33/33).
3. Known pre-existing issue, not from this round: `tests/run_tests.py` reports `79_ayojan_cwd` COMPILE-FAIL ("undefined function: sq") on clean origin/main too.
4. Review the two deliberate non-conversions in `lib/map.smlib` (comments at `map_slot_write` and `map_remove`): if you prefer a non-terminating `strb_dup` variant for fixed-size slots, say so and it can be added as a separate helper rather than changing `strb_dup` semantics.
