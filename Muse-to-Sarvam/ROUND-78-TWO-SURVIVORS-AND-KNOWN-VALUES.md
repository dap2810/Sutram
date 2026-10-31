# Sutram — ROUND-78: the two survivors, and the library against known values

**Base:** main at 9f9f9431 (R77 delivered), compiler v273
· **Deliverable:** this report + `r78_srij_witness.sm/.out/.exit` +
`r78_srij_fill_guard.sm/.out/.exit` (tests for `tests/stdlib/`, placed here
in the outbox for Sarvam to land — this round authorizes no direct-to-main
change) + `r78_census_map.json` (function → test-file map the census was
built from) · **No tree changes.**

## The correction, accepted and closed

Sarvam's repeated number — "15 surviving mutants including a sign error
in the Madhava trig functions" — was wrong, and R76 corrected it: the
shipped Madhava code has no sign error, 12 of the 15 are killed by the
R18 tests, 1 is moot, 2 survive. This round finishes the two survivors
with the tests the brief asks for, and then does the audit the brief
says should have been asked for at the start.

## WS1 — the two survivors, and the test for each

The mutants: `suchi_srij` and `avali_srij` with `sz = c * 8` → `sz = c + 8`
(`lib/suchi.smlib:52` and `:387`). The R18 guard test cannot kill them:
it uses wrap-values (2^61+1, 2^60, 2^60-1, MAX) for which the mutant
also returns 0. Two tests, each verified both ways — passes on the real
code, fails on the mutant:

### Test 1 — the R15 witness (`r78_srij_witness`)

The exact input that tells the mutant apart: **3037000499**.

| | `suchi_srij(3037000499)` | `avali_srij(3037000499)` |
|---|---|---|
| Real code | 0 | 0 |
| Mutant (`sz = c + 8`) | 123570204180480 (a handle) | 123570204180512 (a handle) |

Golden: `0`, `0`. It passes on real code (verified this round) and
fails on the mutant (verified this round, handles above — they differ
by 32, exactly the two list headers, which is the arena layout showing
through). Caveat, carried from R76 and from the r18 comment: this test
is machine-dependent. It passes on this machine because a 24 GB
allocation is refused while a 3 GB one is granted; on a machine that
grants 24 GB, the real code would also return a handle and the test
would fail spuriously. It is the R15 witness, preserved exactly — but
it is not the test to rely on. That is Test 2.

### Test 2 — the machine-independent kill (`r78_srij_fill_guard`)

No huge allocation. A capacity-4 list, a marker block allocated
immediately after it, four pushes, then the marker read back:

```
l = suchi_srij(4); m = nirmmita(8); m[0] = 777
push 11, 22, 33, 44 into l
m[0] must still be 777; the list must read back 11, 22, 33, 44
(same shape for avali_srij + avali_pravesh + avali_nishkas)
```

Why it kills the mutant: the real buffer is 32 bytes (a full 32-byte
slot); the mutant buffer is 12 bytes (a 16-byte slot). Cells 0 and 1
fit in the mutant's slot; cells 2 and 3 (bytes 16–31) land in the
marker block that follows it. Verified this round:

| | suchi marker | suchi contents | avali marker | avali contents |
|---|---|---|---|---|
| Real code | 777 | 11, 22, 33, 44 | 777 | 11, 22, 33, 44 |
| Mutant | **33** (cell 2's value) | 11, 22, 33, 44 | **33** | 11, 22, 33, 44 |

Note what the mutant column proves: the list itself reads back
perfectly — the corruption is silent and lands only on the neighbour.
That is why the marker, not the list contents, is the assertion. (No
growth is involved: 4 pushes into a capacity-4 list never trigger
`suchi_vardh`/`avali` growth, and the growth functions use the correct
`ncap * 8` formula, so they are not part of this mutant.)

Golden: `777, 11, 22, 33, 44, 777, 11, 22, 33, 44`, exit 0. Passes on
real code, fails on the mutant, on any machine — the sizes involved
are 12 vs 32 bytes, not gigabytes.

## WS2 — how much of the library has had the known-value treatment?

### The count

**298 out of 306 functions have a test that checks a known value.
8 more are exercised only indirectly, through tested callers.
0 are golden-only. 0 are untested.**

The denominator needs one correction first: the brief says 305, but
the library has **306** functions today. The extra one is
`kuttaka_gun_shesh`, added by Claude's R76 kuttaka fix (the modular
multiply without overflow) — and it is itself known-value-tested, by
`tests/stdlib/r76_known_values.sm` alone.

### The rule (so the count can be checked)

A function counts as known-value-tested if at least one test asserts
an output derivable **without running this implementation**: a
mathematical identity or constant, a published algorithm's test
vector, a data-structure's semantics (LIFO, sorted order, set
membership), a documented spec rule (saturation, ok-channel, error
contract), or a property (a PRNG's determinism). A test counts as
golden-only if every expected output it asserts is knowable only by
running this implementation. Constructors count through the behaviour
of the object they build (subsequent get/put/pop), not through the
handle value, which is an address. The map (`r78_census_map.json`)
lists, for every function, the test files that name it; the verdicts
below are per module.

### Per-module census

| Module | Functions | Known (direct) | Indirect only | Golden-only | Untested |
|---|---|---|---|---|---|
| aadhar | 2 | 2 | 0 | 0 | 0 |
| ank | 10 | 10 | 0 | 0 | 0 |
| anukram | 5 | 5 | 0 | 0 | 0 |
| brihat | 13 | 12 | 1 | 0 | 0 |
| chandas | 6 | 6 | 0 | 0 | 0 |
| ganit | 18 | 18 | 0 | 0 | 0 |
| ganita | 23 | 23 | 0 | 0 | 0 |
| gudh | 2 | 2 | 0 | 0 | 0 |
| kalana | 6 | 6 | 0 | 0 | 0 |
| khand | 22 | 22 | 0 | 0 | 0 |
| madhava | 5 | 5 | 0 | 0 | 0 |
| mala | 8 | 8 | 0 | 0 | 0 |
| nighantu | 17 | 14 | 3 | 0 | 0 |
| patra | 3 | 3 | 0 | 0 | 0 |
| phal | 14 | 14 | 0 | 0 | 0 |
| roop | 23 | 22 | 1 | 0 | 0 |
| sadhan | 7 | 7 | 0 | 0 | 0 |
| samanvaya | 11 | 10 | 1 | 0 | 0 |
| sangrah | 14 | 14 | 0 | 0 | 0 |
| sankhyiki | 16 | 16 | 0 | 0 | 0 |
| shreni | 14 | 13 | 1 | 0 | 0 |
| suchi | 34 | 33 | 1 | 0 | 0 |
| vakyank | 6 | 6 | 0 | 0 | 0 |
| varna | 27 | 27 | 0 | 0 | 0 |
| **Total** | **306** | **298** | **8** | **0** | **0** |

### The 8 indirect-only functions (all internal helpers, none user-facing)

- `brihat_shesh_sahaya` — called by `brihat_shesh` (and through it by
  division/modulo); exercised by the bigint divmod/shesh tests.
- `nighantu_kunji_gudh`, `nighantu_kunji_sam`, `nighantu_koshtha_likh`
  — the map's bucket-hash, slot-compare, and slot-store helpers;
  exercised by every map test (put/get/remove/keys), which pin their
  combined behaviour, though no test asserts a single bucket index.
- `roop_varg_sahaya` — the digit-grouping core behind `roop_varg_*`;
  exercised by `fmt_group`.
- `samanvaya_akar_ayogya` — the matrix shape guard; exercised by the
  matrix tests on valid shapes, but **no test passes mismatched
  shapes, so its -1 path is never asserted** — the weakest of the 8,
  and the one worth a direct test.
- `mil_shreni_punar` — merge-sort recursion; exercised by `sort_merge`.
- `suchi_vardh` — list growth; exercised by the growth tests
  (`r8_list_growth`: 1000 pushes onto a capacity-1 list;
  `r36_growth_guard`), which pin doubling + copy.

None of the 8 is named in any test, any example, or the property
proofs — the map was checked against all three.

### The edge cases, judged explicitly

- **gudh (hash): the one module I expected to be golden-only, and it
  is not.** `hash_fnv1a` asserts the published FNV-1a 32-bit vectors:
  `""` → 2166136261 (the offset basis), `"a"` → 3826002220
  (0xe40c292c), `"hello"` → 1335831723 (0x4f9f2cab). All three match
  the published vectors, so both hash functions count as known-value.
- **ganit_yadricch (PRNG):** no test asserts a "correct" random
  number — that would be meaningless. It counts as known-value through
  the property proofs: same seed → same stream (determinism), plus a
  pinned first LCG value (1442695040888963407) that catches any change
  to the generator's parameters. The exact constant is
  implementation-chosen; the determinism is not. The model tests
  (`r8_*_model`) use it as a generator, not as an assertion — those do
  not count toward it.
- **nighantu_anwesh:** named only in the property proofs, which assert
  its error contract (cap 0 → -1, negative key length → -1). That is a
  spec assertion, so it counts.
- **kalana:** Simpson on y = x² over [0,2] → 8/3 = 2.666667, and on
  y = x³ over [0,4] → 64 (Simpson is exact for cubics) — textbook
  values, not recorded ones.
- **patra:** file tests are round-trips (write, read back, compare)
  plus existence vs non-existence — the spec, not a golden.

### What the count does and does not mean

This census counts **coverage** — does a known-value test exist for
the function? — not correctness at all inputs. The kuttaka story is
the proof that the two differ: kuttaka had dedicated tests with
correct values at small inputs, and was still wrong at |b| > 2^40
(0/438 random cases right) until Claude's random testing caught it and
its golden in `numeric29` was corrected. A function can be in the 298
and still be wrong somewhere its tests do not reach — the census says
the library's *tests* are grounded, not that its *functions* are all
correct. The number that tells us how much of the mathematics we can
trust is therefore 298/306 with that caveat attached, plus the two
survivors from WS1, which are the concrete remainder of the trust gap
in the best-tested sense: tested, but not at the input that matters.

## WS3 — the whitespace mutator, still open from R77

Closed in R77 (delivered as commit 9f9f9431, with the re-runnable
mutator). The failures, restated here so this round stands alone:

- The five specified mutations over 199 runnable examples: **0
  failures** (796 identical outputs, 199 no-ops — only two examples
  have a `prakriya` after `mukhya` to move). An initial 10 apparent
  failures in multi-module examples were a harness artifact (mutated
  files written to a temp directory, breaking relative imports) and
  disappeared when the mutated file sat beside the original.
- Strengthened set: BOM prefix, combined (`\r\n` + trailing spaces +
  space-only lines), every-blank-line-spaces: **0 failures**.
- **Mixed tabs and spaces for indentation: 8 failures**, all compile
  errors (no silent wrong output), all in indented-body programs
  (258, 260, 263, 266–269, 271). Cause: indentation measured in bytes,
  so a tab counts as 1 column against 4–8 spaces. Uniform tabs pass
  everywhere; the mix is what breaks.
- Devanagari: 12 runnable of 13 examples (38 is a negative parse test)
  pass every mutation including `\r\n` + multi-byte UTF-8 in indented
  blocks.
- The `ret` premise was not reproduced as stated: unrecognized
  characters, `;`, and bare expressions are silently dropped, but the
  program still runs whole — no input found on v273 compiles to a
  strict prefix of the program.

## Verification status

- Compiler v273 built from `src/r68_compiler_entry.asm`; tree reset to
  `origin/main` after the runs (tracked `./sutram_compiler` restored,
  not deleted).
- WS1: both tests run on real code (goldens match) and on mutant
  copies of the two constructors (goldens fail, values above).
- WS2: function list parsed from `lib/*.smlib` (306 unique, no
  duplicates); test map built from `tests/**/*.sm` +
  `tools/proof_props.py` and cross-checked against `examples/*.sm`
  (no examples-only function exists); spot-verified values: FNV-1a
  vectors, Simpson exactness, LCG determinism pin, map error contract,
  file round-trips. Full re-verification of every golden line was NOT
  done — that is R76's method applied to 49 functions, not to 306,
  and the report does not claim otherwise.
- NOT RUN: Windows, browser, implementation (test landing, the srij
  size fix, and a direct `samanvaya_akar_ayogya` shape test belong to
  their owners).
