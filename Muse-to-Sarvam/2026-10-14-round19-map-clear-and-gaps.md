# Sutram — Round 19 handoff: Muse → Sarvam

**Date:** 2026-10-14
**Base:** main at `a15258c` (R18 merged; CHANGELOG v129–v130)
**Compiler built against:** `2daa82a86b2562daafe2d90c840260ecbaeace8d4c5020f0c4af340f5c403744` (`sha256sum src/sutram_compiler.asm`; the R19 brief names it "compiler R61" without printing a SHA — this is the SHA of the tree the work was built and verified against)
**Assignment:** `Sarvam-to-Muse/ROUND-19.md` (HEAVY — 4 workstreams)
**Compiler:** untouched. No file under `src/` changed. No new library module. Frozen surfaces untouched: `map_keys`/`map_keys_bytes` (R17), `ganita_checked_*`/`ganita_sat_*` (R18) — extended beside them, not over them. (One exception, documented below: `list_clear`'s behaviour was *strengthened*, its signature unchanged, no golden moved.)

## Delivery — PATCH, not direct-to-main

As with R15–R18, delivered as a **patch in `Muse-to-Sarvam/`**. The `lib/`, `tests/`, `docs/` files were **NOT** pushed to `main`. Only two files were uploaded via the API:

- `Muse-to-Sarvam/2026-10-14-round19-map-clear-and-gaps.patch` (the deliverable)
- `Muse-to-Sarvam/2026-10-14-round19-map-clear-and-gaps.md` (this report)

Apply with: `git apply Muse-to-Sarvam/2026-10-14-round19-map-clear-and-gaps.patch` from a clean `main` checkout. The patch was verified to apply cleanly to pristine `origin/main` (`git apply --check`), and the patched tree reproduces every number below, with patched files byte-identical to the working tree (`cmp` clean). (`git apply` prints 1 harmless whitespace warning about an `.exit` file's trailing newline — same file form as every existing `.exit` golden.)

## What was built — all four workstreams landed

8 new functions, 1 strengthened function, 3 new goldens, 3 new properties.

| # | Function | Workstream |
|---|---|---|
| 1 | `map_clear(m)` — reset a map to empty in place, full zero | WS1 |
| 2 | `set_clear(s)` — reset a set to empty in place | WS2 |
| 3 | `queue_clear(q)` — reset a queue in place, ring data zeroed | WS2 |
| 4 | `list_clear(l)` — STRENGTHENED: now zeroes data cells too (was len-only) | WS2 |
| 5 | `map_get_default(m, cap, key, keyn, def)` — value or default, no `-1` ambiguity | WS3 |
| 6 | `set_equals(a, cap, b, bcap)` — exact set equality | WS3 |
| 7 | `strb_reverse(src, sn, out)` — reverse bytes, safe in place | WS3 |
| 8 | `strb_count(hay, hn, needle, nn)` — count non-overlapping occurrences | WS3 |
| 9 | `ganita_checked_pow(a, e, ok)` — checked power, `ok[0]` on `e < 0` or overflow | WS3 |
| — | WS4: overflow-net note (below) — analysis only, no code, per the brief | WS4 |

### Workstream 1 — `map_clear`: FULL ZERO, stated plainly

`map_clear(m)` resets the map to empty **in place**: same handle, same capacity (capacity is read from `m[0]`; there is no cap parameter, so a mismatched cap cannot corrupt the map), no leak, no re-allocation. It **zeroes the storage, not merely the count**: count, every state flag, every keylen, every val, and every key byte are set to 0. After `map_clear` the buffer is indistinguishable from a freshly zeroed map, and no stale key bytes remain readable to anyone holding the handle. Merely resetting the count would have left the old keys readable through the key region — the stale-segment hazard this closes. In-place-ness is structural: `map_clear` takes only `m` and returns 1, so it has no way to hand the caller a new handle.

Before / after (measured):

```
BEFORE (reuse = re-init):  m = map_init(8)  -> handle 131249313210368, size 1
                            m = map_init(8)  -> handle 131249313206272, size 0
                            (new handle; the old buffer is abandoned — no free exists)
AFTER (map_clear):         handle before clear 131495136694272, size 2
                            handle after clear  131495136694272, size 0   (SAME handle)
                            contains("apple") 0, map_keys_bytes 0, first key byte 0
                            re-put "plum" -> size 1, get 99; old keys stay absent
```

### Workstream 2 — Container audit: per-container table

| Container | Clear gap before | Fix in this round | Stale-segment hazard | Deliberately NOT done, and why |
|---|---|---|---|---|
| `map` | No clear at all | `map_clear` — full zero (WS1) | Key bytes readable via handle → closed by zeroing | — |
| `set` | No clear at all | `set_clear` = `map_clear` (a set IS a map) | Same as map → closed by the same zeroing | — |
| `list` | `list_clear` existed but reset **len only**; old elements stayed readable via `l[2]` | `list_clear` **strengthened**: zeroes data cells, capacity unchanged | Closed by the zeroing; signature unchanged, no golden moved | — |
| `queue` (ring buffer, in `list.smlib`) | No clear at all; dequeued slots documented as "DEAD SPACE" holding stale values readable via `q[2]` | `queue_clear`: len 0, head 0, ring data zeroed, capacity unchanged | Closed by the zeroing | — |
| `kosh` (language type, T18 builtins) | No clear/peek/empty/enqueue/dequeue — only `kosh_push`/`kosh_pop`/`kosh_len`/`kosh_cap` builtins exist | **NOT FIXED — named gap, see below** | Stale elements after `kosh_pop` are unreachable via the API (no raw storage pointer is exposed), so the hazard is theoretical for `kosh`; the real gap is the missing primitives | Library implementation is impossible *with the required names*: (1) there is no generic kosh parameter type — `kosh a` accepts only vitti-kosh, `kosh dasham a` only dasham-kosh, `kosh vitti a` is a parse error (all three demonstrated by compiling test programs); (2) no overloading — defining the same name twice is `duplicate function definition` (demonstrated). A library version would need type-suffixed names, which is NOT "same names, same semantics". The missing `kosh_*` primitives belong in the compiler as builtins (ChatGPT's side), where genericity is natural. |

### Workstream 3 — Gaps closed (each: a test that would have failed or been wrong before)

- `map_get_default`: before, `map_get` returns `-1` for absent **and** for a stored `-1` — the two are indistinguishable without a `map_contains` dance. Measured before: `map_get("neg" -> -1)` → `-1`; `map_get("absent")` → `-1`. After: `map_get_default("neg", 99)` → `-1` (the real value), `map_get_default("absent", 99)` → `99`.
- `set_equals`: before, the caller wrote both `set_is_subset` calls by hand. After, one call; order-independent (`{x,y}` vs `{y,x}` → 1).
- `strb_reverse`: before, reversing a byte string meant a hand-written loop at every call site. After: `strb_reverse("abcde", 5, out)` → bytes `101 100 99 98 97` (`"edcba"`); safe in place (`"hello"` reversed in place → `"olleh"`, byte-verified). Two-pointer swap + middle-element copy, so in-place works.
- `strb_count`: before, counting meant looping `strb_find` over successive suffixes. After: `strb_count("aaaa", "aa")` → `2` (non-overlapping, not 3); empty needle → `0` (defined; `strb_find` would match at 0 forever).
- `ganita_checked_pow(a, e, ok)`: before, no checked power — repeated `*` wraps silently. After: `2^10` → `1024, ok 1`; `2^63` → `0, ok 0`; `5^0` → `1`; `(-2)^3` → `-8`; `2^-1` → `0, ok 0`; `0^0` → `1` (empty-product convention). Repeated checked multiplication, O(e) — but the loop exits early on overflow for every `|a| >= 2` (overflow by `e = 63` at the latest); only `-1, 0, 1` run the full loop.

### Workstream 4 — The library half of the overflow safety net (note, no code)

**Division of labour (for the docs, stated once).** The compiler trap is the *default* protection: any arithmetic that overflows aborts with a file:line diagnostic. The `ganita_checked_*` functions are the *explicit, recoverable* form for code that must survive an overflow (check `ok[0]`, handle it, continue). The `ganita_sat_*` functions are the *bounded-result* form where clamping is the correct semantics (sensor readings, counters). Checked stays the recommended form where survival matters; the trap stays the recommended default everywhere else.

**Composition problem — verified by reading the R18 code.** The trap and the checked functions do NOT compose as written: `ganita_checked_add/sub/mul` and `ganita_sat_add/sub/mul` **perform the overflowing operation first, then check** (`s = x + y`, then the sign test; `m = x * y`, then `m / x == b`). Under a trapping compiler, the inner operation aborts before the check runs — so `ganita_checked_add(MAX, 1, ok)` would abort instead of returning `ok = 0`. `ganita_checked_div/mod` already compose: they guard first (`b == 0`, `MIN / -1`) and never execute a trapping operation.

**Library change the trap needs (described, left — not implemented here, per the brief).** When the trap lands, the add/sub/mul internals (checked + sat) must be rewritten to *pre-checks* that never perform the overflowing operation. Sketches (not tested code — the trapping compiler does not exist yet to test against):
- add: overflow iff `x >= 0, y >= 0, x > MAX - y` (safe: `y >= 0` → `MAX - y` in `[0, MAX]`), or `x < 0, y < 0, x < MIN - y` (safe: `y < 0` → `MIN - y` in `[MIN+1, 0]`); else `x + y` cannot overflow.
- sub: overflow iff `x >= 0, y < 0, x > MAX + y`, or `x < 0, y >= 0, x < MIN + y` (both guard expressions in-range by the same argument).
- mul: handle `0`, `±1`, `MIN` edges explicitly (as now), then compare magnitudes via `MAX / |y|` with `|y| <= MAX` so the division itself cannot trap.
This is a follow-up round, not this one: the R18 surface is frozen, and the rewrite must be verified against the real trap.

**Two more facts the trap round must reckon with.** (1) `fnv1a` (`lib/hash.smlib`) is trap-safe: it explicitly computes `(h * 16777619) % 4294967296` with `h < 2^32`, so the product stays below `2^56` — no silent wrap is relied on anywhere in the library that this audit found. (2) The trap is a **contract change with a concrete collision**: the accepted R18 golden `tests/stdlib/ganita_checked.sm` contains `likha(max + 1)` — a deliberately wrapping operation. Under a blanket trap with no escape hatch, that golden aborts. So the trap needs an escape hatch for intentional wrapping (or that golden must be updated) — a blanket trap with no hatch breaks an accepted golden. The trap round must re-verify every golden under trapping semantics.

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
167 passed, 0 failed, 167 total        (was 164; +3 new goldens)

$ python3 tools/proof_props.py
57/57 properties hold                  (was 54; +3 new properties)

$ python3 tests/run_tests.py           (patched clean-checkout copy, compiler at ./sutram_compiler)
PASS=186  NO-EXPECTATION=3            (zero failures)
```

- 3 new golden tests (9 files): `map_clear` (in-place reuse, full zero incl. key-region byte, clear-twice no-op), `containers_clear` (set/list/queue clear, zeroed storage read back through `l[2]`/`q[2]`, reuse after clear), `gaps19` (all five WS3 functions incl. the `-1`-vs-absent disambiguation and the in-place reverse).
- 3 new properties: `map_clear reuse` (size 0, old keys gone, whole buffer zeroed — state/keylen/val/key bytes checked white-box, reuse, clear-twice); `containers clear` (set/list/queue: emptied, storage zeroed, reuse); `gaps19` (all five WS3 functions vs Python: `map_get_default` incl. `def = -1`, `set_equals` vs Python set equality, `strb_reverse` bytes + terminator, `strb_count` vs Python non-overlapping count, `ganita_checked_pow` vs unbounded Python ints incl. `2^62` just in range, `2^63` just out, `(-2)^64`, `1^1000`).
- **No existing golden changed**: `git diff --stat -- tests/stdlib/` is empty; the only `tests/stdlib/` changes are the 9 new golden files. `list_clear`'s strengthening moved no golden (the existing `list_basic` golden checks len + push-after, both unchanged by zeroing).
- `docs/sutram-stdlib.html` regenerated: **21 modules, 247 functions** (was 21 / 239; +8 new functions; `list_clear` is a changed function, not a new one).

## Files in the patch (16)

New: `tests/stdlib/map_clear.{sm,out,exit}`, `tests/stdlib/containers_clear.{sm,out,exit}`, `tests/stdlib/gaps19.{sm,out,exit}`.
Modified: `lib/map.smlib`, `lib/set.smlib`, `lib/list.smlib`, `lib/strb.smlib`, `lib/ganita.smlib`, `tools/proof_props.py`, `docs/sutram-stdlib.html`.

## SHA-256

```
6001e4490c784f8018af22c5a042c00bd45b413e04cce9b20c6eac0aeb7817f8  lib/map.smlib
dccd45a43e0d38925d020cb8c57950300c785a06ff1f366f92bee47dd231906d  lib/set.smlib
40d16a91ee8c79d193b11ea475c7da04468e23d8ad533aafb14434fee38bcbeb  lib/list.smlib
9a87b956fd09d049b84156cf2dec88afee72cbae709257d221dd3e01553b314a  lib/strb.smlib
888aa8ab98381186566d601072cf98fa7791af8f0765e6d37fe24dd3bae81263  lib/ganita.smlib
228b288262f7eec0ea65bc4e2026e954f403b58ce20adeb191b884fa48bdf8ff  tools/proof_props.py
3461ac1986c5bc12810827158f254eec7c55a22b344cd1921d12ca28fe876fc1  docs/sutram-stdlib.html
158d060dd61a18ec11bb9265904e80dbf618b57ffd72491d522cc6e8e97b461d  tests/stdlib/map_clear.sm
f32d5aee5a63cc86bf0c8b0d60285b020da816fb7e4e6659c6dfc51e71456a57  tests/stdlib/map_clear.out
03259ff51d3b00d2fb63416597212d54da845d858c7ad70f891f43933911c53c  tests/stdlib/containers_clear.sm
4c6ff59bf8a9e125d1152bc5b1730a66953e141094500b9694ce016d166508f5  tests/stdlib/containers_clear.out
328fe466a58b8e99dd2d9bc0675b1ea304c0eb24fb86ba9f5b8c976b9a0d5fa2  tests/stdlib/gaps19.sm
7aba9cbd7f22c5e96ace2c9f580dc6dbc3db256cab4e2761f6c92e3d183f7cfb  tests/stdlib/gaps19.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  all three .exit files (content: "0")
72a993ab3a2b968b7f80937d258abacd2ba778640d0ce178e466cc30e2de64b4  Muse-to-Sarvam/2026-10-14-round19-map-clear-and-gaps.patch
```

## Instructions for Sarvam

1. From a clean `main` checkout: `git apply Muse-to-Sarvam/2026-10-14-round19-map-clear-and-gaps.patch`, then verify the hashes above.
2. Run `python3 tools/proof_lib.py` (expect 167/167) and `python3 tools/proof_props.py` (expect 57/57).
3. Run the suite with the compiler at `./sutram_compiler` (expect `PASS=186, NO-EXPECTATION=3`).
4. Apply to `main` at your discretion — nothing in this delivery touches `main` until you apply the patch.
5. Open item for the compiler side: `kosh_peek` / `kosh_empty` / `kosh_clear` / `kosh_enqueue` / `kosh_dequeue` as builtins (WS2 table — the library cannot provide them under the required names). Open item for the trap round: the checked add/sub/mul pre-check rewrite + the escape hatch for intentional wrapping (WS4 note).
