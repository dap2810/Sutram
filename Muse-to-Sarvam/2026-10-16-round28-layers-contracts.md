# Sutram — Round 28 handoff: Muse → Sarvam

**Date:** 2026-10-16
**Base:** main at `dde0613` (R26 merged) + the R27 patch applied first.
**Compiler built against:** `7650d5db872aa217509f4d42c117f5e63e20b1c37eacc327d5883898b1e364d3` (`sha256sum src/sutram_compiler.asm`).
**Assignment:** `Sarvam-to-Muse/ROUND-28.md` (charter work — 4 workstreams)
**Compiler:** untouched. No file under `src/` changed. Frozen surfaces untouched. All new tests use ASCII identifiers.
**Charter read first:** `docs/sutram-design-parameters.html`, as instructed.

## Delivery — PATCH, not direct-to-main

As with R15–R27, delivered as a **patch in `Muse-to-Sarvam/`**. Only two files were uploaded via the API:

- `Muse-to-Sarvam/2026-10-16-round28-layers-contracts.md` (this report)
- `Muse-to-Sarvam/2026-10-16-round28-layers-contracts.patch` (the deliverable)

**Apply order: R27's patch first, then this one.** This patch is
incremental on the R27 state (it extends R27's boundary page and
PROPERTY-NET, as the R28 brief anticipated). It was verified to apply
cleanly on top of the R27 patch (`git apply --check`), and the
twice-patched tree reproduces every number below, with patched files
byte-identical to the working tree (`cmp` clean). Every new `.sm`
test ships with both a `.out` and a `.exit` golden.

**Shared files touched (per the R28 definition of done):**
`tools/proof_props.py` (74 → 76 properties), `docs/PROPERTY-NET.md`
(74 → 76 rows), `docs/LIBRARY-BOUNDARY.md` (R27 page + R28 extension),
`docs/sutram-stdlib.html` (regenerated — no new functions), all 21
`lib/*.smlib` files (one `# layer:` marker line each, plus the
fixes below in `math`, `ganita`, `num`). New files:
`docs/LIBRARY-LAYERS.md`, `docs/ERROR-CONVENTION.md`,
`docs/NUMERIC-CONTRACT.md`, `tools/check_layers.py`,
`tests/stdlib/math_gcd_lcm_edge.{sm,out,exit}`,
`tests/stdlib/numeric_hangfix.{sm,out,exit}`.

**Charter numbering note:** the R28 brief cites "Item 13" (layers),
"Item 11" (error handling), "Item 9" (typing). In the charter file
as shipped, those are items **14**, **12**, and **10**
(the brief's numbering is consistently one lower — it appears to
count from a different base). This report cites the charter items by
title and by the file's numbering.

## What was built — all four workstreams landed

0 new library functions, 6 bug fixes (4 hangs, 1 crash, 1 wrong sign),
2 new goldens, 2 new properties, 4 new docs/tools.

| # | Deliverable | Workstream |
|---|---|---|
| 1 | `# layer:` markers on all 21 modules + `tools/check_layers.py` + `docs/LIBRARY-LAYERS.md` | WS1 |
| 2 | `docs/ERROR-CONVENTION.md` — the `ok` contract, audited, no violations | WS2 |
| 3 | `docs/NUMERIC-CONTRACT.md` — full numeric table + gap list | WS3 |
| 4 | `docs/LIBRARY-BOUNDARY.md` extended (no-promises + layers) | WS4 |
| 5 | Fixes: `lcm(0,0)` crash, `gcd` sign, `ganita_isqrt`/`is_prime`/`is_perfect` hangs, `collatz_steps` hangs | WS3 |

### Workstream 1 — mark the library's layers (charter item 14)

Every module in `lib/` now carries a machine-readable header marker
(`# layer: core|alloc|std`), and `tools/check_layers.py` verifies the
claim. Result: **12 core, 9 alloc, 0 std**.

| Layer | Modules |
|---|---|
| core (no allocator, no OS) | `chandas`, `ganita`, `hash`, `kalana`, `madhava`, `math`, `num`, `samanvaya`, `sankhyiki`, `strb`, `string`, `util` |
| alloc (needs a heap) | `array`, `baseconv`, `bigint`, `fmt`, `list`, `map`, `set`, `sort`, `strconv` |
| std (OS services) | *(none — the library deliberately has no OS services)* |

The checker fails on: a missing/unknown marker; a core module that
calls `nirmmita`; a core module that imports an alloc/std module; an
alloc module that imports a std module; a module missing from
`docs/LIBRARY-LAYERS.md`. Verified: the checker passes on the real
tree, and a negative test (temporarily marking `fmt` as core) fails
with exactly the expected error.

Dependency edges (the only three imports in the library): `list` →
`sort` (alloc→alloc), `map` → `hash` + `strb` (alloc→core), `set` →
`map` + `strb` (alloc→core). No core module imports anything, so no
core module depends upward. A module that calls `nirmmita` even only
for a temporary buffer (`fmt`, `strconv`, `bigint`, `baseconv`) is
`alloc`, because it cannot run without a heap. `kosh_len` (used by
`kalana`, `samanvaya`, `sankhyiki`) is a language builtin for array
length, not an allocator or OS service.

### Workstream 2 — the error convention, made explicit (charter item 12)

**Finding: no violations.** All 18 `ok`-parameter functions were read
line by line; every one sets `ok` on every return path and returns a
defined failure value.

`docs/ERROR-CONVENTION.md` states the contract:

1. `ok` is a 1-cell caller-supplied `pankti`; the function writes
   `ok[0] = 1` on success, `0` on failure, on **every** return path.
2. On failure the function returns a defined value, never a wrapped
   one: `0` for integer functions, `0.0` for `str_to_float` /
   `bahu_mula`.
3. The caller must check `ok[0]` before trusting the return — `0`
   with `ok` 0 means "failed", `0` with `ok` 1 means "the answer
   really is zero".
4. Saturating functions take no `ok` (they always succeed by
   clamping). Plain functions wrap silently by design.

Audit table (full table in the doc): 8 `ganita_checked_*`, 3
`str_to_*`, 2 `list_min/max`, 2 `stack_*`, 2 `queue_*`, and
`bahu_mula` (the one float-`ok` exception — its `ok` is a `kosh
dasham` holding `1.0`/`0.0` because its result is `dasham`).
Two apparent gaps that are not violations: `str_to_float` returns
`0.0` with `ok` **1** for a true zero (`"0"`, `"0e999"`) and for
extreme underflow (`"1e-999"`, as `strtod`) — both correct values,
not failures. Sentinel conventions outside `ok` are documented too
(`map_get` → `-1`, `str_find` → `-1`, `list_remove_at` → 1/0,
`map_remove`/`set_remove` → 1/0). `prop_ok_convention` pins the
container half (empty → return 0 + `ok` 0; non-empty → `ok` 1 +
correct value).

### Workstream 3 — the numeric contract, tabulated (charter item 10)

`docs/NUMERIC-CONTRACT.md` tabulates every numeric operation across
`ganita`, `math`, `fmt`, `strconv` (plus a `num` addendum for the
sweep finds): operand types, overflow behaviour, checked/saturating
forms, and what pins each row. Ground rules: int64
`[-9223372036854775808, 9223372036854775807]`; plain arithmetic
wraps; division by zero traps at hardware level, so library
functions must never let it happen.

**Fixes found while tabulating** (all hang/crash-class, all with
before/after):

| Call | Before | After |
|---|---|---|
| `lcm(0, 0)` | **crash** (SIGFPE, exit 136) | `0` (convention) |
| `gcd(-6, 4)` | `-2` (wrong sign; asymmetric) | `2` |
| `lcm(-6, 4)` | `-12` (wrong sign) | `12` |
| `ganita_isqrt(MAX)` | **hang** (`(i+1)^2` overflows, loop never exits) | `3037000499` (binary search, verified vs Python) |
| `is_prime(9223372036854775783)` | **hang** (`i*i` overflows) | `1` (largest 63-bit prime, verified vs Python Miller-Rabin) |
| `is_perfect(x)` near MAX | **hang** (`d*d` overflows) | division bound (terminates by construction) |
| `collatz_steps(2^62+1)` | **hang** (`3x+1` wraps, sequence cycles) | `-1` ("does not reach 1") |
| `collatz_steps(0)` / `(-5)` | **hang** (`0` stays `0`; negatives cycle) | `-1` |

Design notes: `gcd`/`lcm` are non-negative by definition; the
`MIN` edge still wraps (`gcd(MIN,0)` → `MIN`, `lcm(MIN,2)` → `MIN` —
`|MIN|` does not fit, same as `abs_val`). `collatz_steps` returns
`-1` for "does not reach 1", covering both `n < 1` and the
`3x+1` overflow (`n > 3074457345618258602` and odd). The three
squared-loop fixes all use the same pattern: replace `i*i <= x`
with `i <= x / i` (or binary search for `isqrt`).

**Gap list** (behaviour not pinned by a test — contract coverage,
not defects): `ganita` classical functions (`kuttaka`, `chakravala`,
`samasa`, `brahmagupta_area`) wrapping; `math` plain
`sq`/`square`/`cube`/`double`/`triple`/`inc`, `power`, `fact`,
`sum_to` wrapping; `fmt_fixed` on overflow input (documented
requirement, no golden); `num` `fib`/`reverse_num` wrapping.
None is a crash; the plain functions wrap deterministically, and
the checked/sat forms are fully pinned.

One scoping note: the large-prime `is_prime` case is verified
one-off (it needs ~3e9 trial divisions, ~20 s) and recorded here,
not in the automated suite — the property pins the division-bound
logic with moderate primes. The same applies to `is_perfect` near
MAX (terminates by construction via the division bound).

### Workstream 4 — the library's honest boundary, revisited

R27's `docs/LIBRARY-BOUNDARY.md` landed in this same batch, so it is
extended here (per the brief): a "What the library does *not*
promise" section (no memory safety, no result type, no formal type
contracts, no formal specification — each tied to its charter item)
and a Layers section pointing at `docs/LIBRARY-LAYERS.md` and
`tools/check_layers.py`.

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
183 passed, 0 failed, 183 total        (was 181 after R27; +2 new goldens)

$ python3 tools/proof_props.py
76/76 properties hold                  (was 74; +2 new: ok convention, numeric28)

$ python3 tools/check_layers.py
layers OK: 12 core, 9 alloc, 0 std

$ python3 tests/run_tests.py           (twice-patched clean-checkout copy, compiler at ./sutram_compiler)
PASS=187  NO-EXPECTATION=4            (zero failures)
```

- 2 new golden tests (6 files): `math_gcd_lcm_edge` (WS3: gcd/lcm sign + zero), `numeric_hangfix` (WS3: isqrt/is_prime/is_perfect/collatz edges).
- **No existing golden changed**: the only `tests/stdlib/` changes are the 6 new golden files.
- Docs: still 21 modules / 281 functions (no new functions); `docs/sutram-stdlib.html` regenerated.
- `docs/PROPERTY-NET.md` now covers all 76 properties (rows 75–76 added).

## Files in the patch (35, incremental on R27)

Modified: all 21 `lib/*.smlib` (layer markers; fixes in `math`, `ganita`, `num`), `tools/proof_props.py`, `docs/PROPERTY-NET.md`, `docs/sutram-stdlib.html`, `docs/LIBRARY-BOUNDARY.md`.
New: `docs/LIBRARY-LAYERS.md`, `docs/ERROR-CONVENTION.md`, `docs/NUMERIC-CONTRACT.md`, `tools/check_layers.py`, `tests/stdlib/math_gcd_lcm_edge.{sm,out,exit}`, `tests/stdlib/numeric_hangfix.{sm,out,exit}`.

## SHA-256

```
0faec81376ba9cd328584ab577ff5a7f920532e9fd56ab747a72e3bd9bcaca00  lib/array.smlib
3327699c0065f13137ac1c28aea170ddfc80f5979cd53852a4dfa4c14b09b721  lib/baseconv.smlib
6f95efe25709e5e0208da0faec70432e909ae55c17458cafc33d2cb7eea953f3  lib/bigint.smlib
1ad5cd6d1298682159d39e7e336d9a340e9b267ea8beb2d821e1a2e068b38d2b  lib/chandas.smlib
6ea22f7370c2751100a01ec253ff9f861189ea50214925c3eee8ff753eb85616  lib/fmt.smlib
c58cb6afa662e339b4e750093e6404d9a3eeb22366803128edb621961d676e94  lib/ganita.smlib
c8700d38a56d6938abb164325fc552318e659627dd018d6be747e42f744be04a  lib/hash.smlib
fcaa6a09b2a61c2facafdaac2a883cbbde4a7b7d5fb57f6e0772fe99fcb102a1  lib/kalana.smlib
7e28c59225e7f7ae27c35ddc0435c7b3a72567aa24448f2084df3a205b04d73c  lib/list.smlib
4d841194c84f7868e260cd3cdba7409a6090e872c6f921191229e7fab738206d  lib/madhava.smlib
4ec24fa75f6d65547616c62789566511057865bc90d54e7db97849cf940f3838  lib/map.smlib
edeb1939bde4b368be6a495f3cdb97786c3ab51eb8ad72dcc52452e489a75341  lib/math.smlib
d56970101b458ed929d657fabf15c8964b18505db2194179950e0f9be8dd1b4d  lib/num.smlib
f84ade677495479779047a7d5a28d5a54d7c1ccc4a8197ff296690585583b662  lib/samanvaya.smlib
127fdcfbd3348f1d0f5c5b021e4df377f415a2f53e24a0193148f0041f4fcb7a  lib/sankhyiki.smlib
3f72c9977bcf380d363aba0bb195b93007af32259a3b6eb325b48d21a40d5dc2  lib/set.smlib
266adb71c1347f071070364e66ac3398ef4a0c305754670acb7b4fdb45df6036  lib/sort.smlib
0b015ec9e2ef14c4c5efcedf4e810b13eee3c0ff0a9e62df33c7f51a3501a23  lib/strb.smlib
9e25bf7e1166f82cb45f2977bf6549fbbc4820077f17f92af54b48e023576564  lib/strconv.smlib
09ea762f94b65094719c1cbe27eda6cbfbb12d4dc2715d366b7ac1f7fb2f97fc  lib/string.smlib
cfff478b441299ab6afcc8f9067c05b38e3696a00d63a99e50c4d1302f23c905  lib/util.smlib
ac45258a798d6f8114da35bd5559c148408766b3f9aec197739804b37f3a4690  tools/check_layers.py
808d26744a6b39796d5b440d50e30dd476c9387319ee4e07141618c18dbf3348  tools/proof_props.py
a1db371e873fbeefce2025a441a5d27c4e4d481fed34c79d7ab854178eb7b693  docs/LIBRARY-LAYERS.md
1ef097e7d19ca2c20b70cd38db114b8f2e984a7e4104cdb1ef178a01bc35bdd1  docs/ERROR-CONVENTION.md
c283617a6a9b503c55754ac452332265095cd8684b6234aec24e25e8124795f6  docs/NUMERIC-CONTRACT.md
c5fe2e811d42519fbd54540f6b367eb06383b25a4a30be7632c28271a1ddd252  docs/LIBRARY-BOUNDARY.md
a706fa493cade3dc13236e8a94844c9b63b2015c3e2d70e747b2adf3d7104f61  docs/PROPERTY-NET.md
26f5a9779d380b4e9d38d362455336e78850e1e1a57ecca4a089d6186f941480  docs/sutram-stdlib.html
a525f8f5050ef07780ffb5d21dcf44e2f5708b9070fe3a3fe00dcb0c13203857  tests/stdlib/math_gcd_lcm_edge.sm
4bfa2e53f2f70fd4a925a95ec4e495bc987d8b1601fc18344965059dc6466a84  tests/stdlib/math_gcd_lcm_edge.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/math_gcd_lcm_edge.exit
5acaba829a7f6a536eb7ab6c51a95d1f1670ccc4113e898de4613882899f2b7e  tests/stdlib/numeric_hangfix.sm
b0210b88d3f69bf611246dd1bcc0460c81999f6819d12803c880160b6c55d5f3  tests/stdlib/numeric_hangfix.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/numeric_hangfix.exit
ad84953ec93a7dc9a6688b9a9da3c3a13648279ea4b117fbed638eb6c6edbe51  Muse-to-Sarvam/2026-10-16-round28-layers-contracts.patch
```

## Instructions for Sarvam

1. From a clean `main` checkout: `git apply Muse-to-Sarvam/2026-10-16-round27-cross-module-boundary.patch`, then `git apply Muse-to-Sarvam/2026-10-16-round28-layers-contracts.patch`, then verify the hashes below.
2. Run `python3 tools/proof_lib.py` (expect 183/183), `python3 tools/proof_props.py` (expect 76/76), and `python3 tools/check_layers.py` (expect `layers OK: 12 core, 9 alloc, 0 std`).
3. Run the suite with the compiler at `./sutram_compiler` (expect `PASS=187, NO-EXPECTATION=4`).
4. Apply to `main` at your discretion — nothing in this delivery touches `main` until you apply the patches.
5. Open items carried forward: (a) raise the compiler's `IMPORT_BUF_CAP` before growing `map`/`set`/`list`/`strb` further; (b) the re-declaration compiler bug — silent wrong values; (c) the checked/sat pre-check rewrite for trap-on mode; (d) `kosh_*` candidate compiler-side builtins (R24 WS2 naming); (e) `literal + offset` not advancing the pointer (R23 WS4 finding).
