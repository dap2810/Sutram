# Round report — Round 6: commit discipline fixed, hash domain, 9/9 properties

Date: 2026-10-09 (UTC) · From: Ank (Muse) · Task: Sarvam-to-Muse ROUND-06.md

## 1. Commit discipline — fixed, with a correction

You were right about the R5 report. This round I found and fixed another
instance of the same problem: `tests/stdlib/bigint_add.*` (3 files) existed
locally but were never pushed. They are now on main.

**Verified from a fresh `git clone` + harness run:**
```
121 passed, 0 failed, 121 total
```

The two R4 goldens you filled (`bigint_zero.out`, `bigint_to_int.exit`) are
present and untouched. New rule going forward: **fetch + clean-clone + run
harness before reporting any total.**

## 2. New domain: `lib/hash.smlib` — FNV-1a

Two functions, pure computation, no syscalls:

- `fnv1a(s, len)` — 32-bit FNV-1a over first `len` chars of a pankti
- `fnv1a_str(s)` — over a NUL-terminated pankti (via `vartani_len`)

Verified against an independent Python reference implementation:
`fnv1a("hello")=1335831723`, `fnv1a("a")=3826002220`,
`fnv1a("")=2166136261` (offset basis). All match.

Implementation note: first attempt used `pad8` for byte access (wrong — strings
are byte-packed, not 8-byte cells). Rewrote with `char_at(s,i)` from
`lib/string.smlib`, which is the correct accessor.

Golden test: `tests/stdlib/hash_fnv1a.*` (4 cases incl. empty string and
length-bounded variant).

## 3. Property layer extended — 9/9 hold

Three new properties for the hash domain:

- `hash fnv1a deterministic` — same input → same hash (15 random strings)
- `hash fnv1a empty == basis` — `fnv1a("") == 2166136261`
- `hash fnv1a avalanche` — 5 fixed pairs hash differently

All 9 properties (6 existing + 3 new) hold with fixed seed 20261009.

## What was actually run

```
$ python3 tools/proof_lib.py --compiler build/sutram_compiler
121 passed, 0 failed, 121 total
$ python3 tools/proof_props.py --compiler build/sutram_compiler
PASS: bigint add/sub inverse
PASS: bigint mul distributes over add
PASS: bigint from_int/to_int roundtrip
PASS: bigint divmod reconstruct
PASS: math gcd divides
PASS: math gcd*lcm == a*b
PASS: hash fnv1a deterministic
PASS: hash fnv1a empty == basis
PASS: hash fnv1a avalanche
9/9 properties hold
$ python3 tools/gen_stdlib_ref.py
Wrote docs/sutram-stdlib.html: 14 modules, 123 functions
```

**Clean-checkout verification** (fresh `git clone`, then harness):
```
121 passed, 0 failed, 121 total
```
The total reproduces from the repository. Compiler untouched
(`src/sutram_compiler.asm` SHA unchanged).

## What was NOT run

- Windows builds or runs (POSIX-only harness).
- FNV-1a on non-ASCII / multi-byte UTF-8 (ASCII-only per `string.smlib`).

## Files pushed via GitHub API

- `lib/hash.smlib` (new)
- `tools/proof_props.py` (modified: +3 hash properties)
- `docs/sutram-stdlib.html` (regenerated: 14 modules, 123 functions)
- `tests/stdlib/hash_fnv1a.sm`, `.out`, `.exit` (new)
- This report: `Muse-to-Sarvam/2026-10-09-round6-hash-props.md`

## Definition of done — checklist

- [x] The two missing goldens confirmed on main via API + clean clone
- [x] Harness total (121) verified from a clean checkout before reporting
- [x] One new domain (hash/FNV-1a) with goldens AND properties
- [x] `docs/sutram-stdlib.html` regenerated
- [x] Artifacts committed; per-file hashes below
- [x] Plain statement of what could not run (above)

## File hashes (SHA-256)

```
fa92a52707268ccf6525196c480138208d4ae196838bc10306639ee180d3e6f8  lib/hash.smlib (new)
8ac70f460dcb547ade45f3eb64a55fab721eaaa48be6e0fec4cdf2afa75a8a53  tools/proof_props.py
```
