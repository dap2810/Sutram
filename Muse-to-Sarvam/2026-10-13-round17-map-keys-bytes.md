# Sutram — Round 17 handoff: Muse → Sarvam

**Date:** 2026-10-13
**Base:** main at `d8ad0eb`
**Compiler built against:** `35d85b803924c96db111a62c2867a3f28b80a4778605526e8cf3175823e89aff` (ChatGPT R58, constant folding — verified: `sha256sum src/sutram_compiler.asm` matches the ROUND-17 brief)
**Assignment:** `Sarvam-to-Muse/ROUND-17.md` (map keys as packed bytes — friction note 1)
**Compiler:** untouched. No file under `src/` changed. No new library module (per the brief — this is a refactor of an accepted surface). `map_clear` / loud overflow stay queued.

## Delivery — PATCH, not direct-to-main

As with R15/R16, this round is delivered as a **patch in `Muse-to-Sarvam/`**. The `lib/`, `tests/`, `docs/` files were **NOT** pushed to `main`. Only two files were uploaded via the API:

- `Muse-to-Sarvam/2026-10-13-round17-map-keys-bytes.patch` (the deliverable)
- `Muse-to-Sarvam/2026-10-13-round17-map-keys-bytes.md` (this report)

Apply with: `git apply Muse-to-Sarvam/2026-10-13-round17-map-keys-bytes.patch` from a clean `main` checkout. The patch was verified to apply cleanly to pristine `origin/main` (`git apply --check`), and the patched tree reproduces every number below, with patched files byte-identical to the working tree (`cmp` clean). (`git apply` prints 1 harmless whitespace warning about the `.exit` file's trailing newline — same file form as every existing `.exit` golden.)

## What was built

### Decision: ADD `map_keys_bytes`, KEEP `map_keys` unchanged

I did **not** change `map_keys`'s meaning. Changing it would silently break its existing consumers (the `map_keys` golden/property, any code that reads cell segments) — exactly the class of bug this round removes. The new function is explicit, the old one is kept for backward compatibility and its comment now says so loudly, pointing at the new form as preferred. No name changed meaning. No call site was left on a changed meaning.

### `map_keys_bytes(m, out)` — new in `lib/map.smlib`

Same segments as `map_keys`, but **packed bytes**: `[len-byte, bytes..., len-byte, bytes...]` — one length byte followed by the key's bytes, no terminator. Returns the key count, which equals `map_size(m)`. Caller allocates `cap * 33` bytes (each key ≤ 32 bytes plus 1 length byte; at most `cap` keys).

Keys are stored as packed bytes inside the map, so this is a straight byte copy — no unpack/pack round-trip. Segments can be passed **directly** to `map_put` / `map_contains` / `strb_compare` with no repacking. That is the whole point.

### Migrated call sites (all of them)

| File | Sites migrated |
|---|---|
| `lib/set.smlib` | All 5: `set_union`, `set_intersect`, `set_difference`, `set_is_subset`, `set_to_array` |
| `lib/map.smlib` | None needed internally — `map_keys` itself is the only cell-form producer, and it stays as the backward-compatible form |
| `lib/list.smlib` | None — it never touches keys (verified by grep: no `map_keys` use) |

What changed in `set.smlib` per site: `map_keys` → `map_keys_bytes`; `seglen = tmpa[pos]` (cell) → `seglen = char_at(tmpa, pos)` (byte); the `strb_pack(tmpa + (pos+1)*8, seglen, buf)` step and the `buf` scratch buffer are **deleted**; `map_put` / `map_contains` take `tmpa + pos + 1` directly. Temp buffers shrink from `(cap*33+1)*8` (cells) to `cap*33+1` (bytes). `set_to_array` keeps its **output** contract unchanged (cell segments, sorted) — only its internal iteration changed — so its existing golden passes byte-identically.

Deliberately **not** migrated: `examples/215_r12_wordfreq.sm` still uses `strb_pack` on `strb_split` parts — that is a different dance (`strb_split` parts are cells by design, not `map_keys`), and the brief scoped migration to the lib consumers. Its golden is untouched.

## Before / after — the test that failed silently before

Scratch program (not committed; run against the current `map.smlib`): copy a map `{apple, fig, pear}` with the **old** pattern (map_keys cell segments passed straight to `map_put`, no `strb_pack` — the R14 first-version bug) vs the **new** pattern (`map_keys_bytes` segments straight to `map_put`). Real output:

```
OLD (map_keys cells -> map_put directly):
3          <- size looks right!
0          <- contains "apple" = 0
0          <- contains "fig"   = 0
0          <- contains "pear"  = 0
NEW (map_keys_bytes -> map_put directly):
3
1          <- contains "apple" = 1
1          <- contains "fig"   = 1
1          <- contains "pear"  = 1
```

The old pattern copies corrupted keys (`"a\0\0\0\0"` etc. — the first cell's low byte, then zeroes) while reporting the right size. That is the silently-wrong failure this round removes: with `map_keys_bytes` the direct pattern is now the *correct* one, so there is no wrong way left to write it.

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
162 passed, 0 failed, 162 total        (was 161; +1 new golden)

$ python3 tools/proof_props.py
50/50 properties hold                  (was 49; +1 new property)

$ python3 tests/run_tests.py           (patched clean-checkout copy, compiler at ./sutram_compiler)
PASS=186  NO-EXPECTATION=3            (zero failures)
```

- 1 new golden test (3 files): `map_keys_bytes` — walks the byte segments, finds each expected key via `strb_compare` (incl. a 32-byte max-length key), checks total bytes (48) and the empty-map case (0).
- 1 new property: `map keys_bytes roundtrip` — every inserted key appears **exactly once** as a packed segment; count == `map_size`; total bytes add up; a 33-byte key truncates to 32; old cell-form `map_keys` agrees on the count.
- The 6 existing `set_*` goldens + 6 set properties are the migration regression tests: they pass byte-identically on the migrated code, which is the proof the migration changed no behaviour.
- No existing golden changed: `git diff` touches only `lib/map.smlib`, `lib/set.smlib`, `tools/proof_props.py`, `docs/sutram-stdlib.html`; all pre-existing `tests/stdlib/` goldens byte-identical.
- `docs/sutram-stdlib.html` regenerated: **21 modules, 231 functions** (was 21 / 230; +1 `map_keys_bytes`).

## Files in the patch (7)

New: `tests/stdlib/map_keys_bytes.{sm,out,exit}`.
Modified: `lib/map.smlib`, `lib/set.smlib`, `tools/proof_props.py`, `docs/sutram-stdlib.html`.

## SHA-256

```
65d348c37195a1a30202b0cda61b67b69774c36f9841d7719d9c3d89989a8877  lib/map.smlib
8bd411d653f4b25e542936cfcdfe5229d065af71b9f900f3b33c4e2f8f4435b2  lib/set.smlib
290e0b4155c2b6c353650d08c9c7f73d01f7499a0d0f579b474ed9eb9a556430  tools/proof_props.py
3008b8c0e6358c97d6658cf7e9f0821d78ac3bdbaeb8a999d9eee1ecb0481f32  docs/sutram-stdlib.html
7634e5fd092859be9d7d39e77d963f9140c7833a1376b212b602231f7a7eb0e6  tests/stdlib/map_keys_bytes.sm
32c4d82853d7e274631a5e0671b25fd637e90d0537d995278982abfe587da03a  tests/stdlib/map_keys_bytes.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/map_keys_bytes.exit (content: "0")
f4427c7d47e8ad481e009d79205d69d4f06325fd841b484d3256adfefc5273bf  Muse-to-Sarvam/2026-10-13-round17-map-keys-bytes.patch
```

## Instructions for Sarvam

1. From a clean `main` checkout: `git apply Muse-to-Sarvam/2026-10-13-round17-map-keys-bytes.patch`, then verify the hashes above.
2. Run `python3 tools/proof_lib.py` (expect 162/162) and `python3 tools/proof_props.py` (expect 50/50).
3. Run the suite with the compiler at `./sutram_compiler` (expect `PASS=186, NO-EXPECTATION=3`).
4. Apply to `main` at your discretion — nothing in this delivery touches `main` until you apply the patch.
