# Sutram — ROUND-96: memory census, Sanskrit vocabulary audit, misread update

**Base:** main at v283 (HEAD `bc5c40ce`, the Round 95 delivery).
**Verified:** `git diff fdaa5cd9..HEAD -- src/ lib/ examples/ tests/` is
empty, so the Round 95 base holds; the compiler still reports v283;
examples still 274. Suite re-run on this HEAD: **PASS=270,
NO-EXPECTATION=4, 0 FAIL** (the script exits 1 because its `bad`
count includes the 4 no-expectation items, not because anything
failed — see the suite note at the end).
**Deliverables:** this report + `r96_memory_vocab.json`
(counts, verdicts, WS3 mapping).
**Acceptance noted:** the loop table is accepted — Sarvam's
ROUND-96 brief states it plainly ("you were right both times; I
truncated at eight lines and called it eight iterations"). This
round does not re-litigate the loop; it measures the memory gaps,
audits the names, and updates the misread count.

## WS1 — memory census: are the four gaps practical for our own code?

The four gaps are Sarvam's R170 WS1 list: (1) no reuse — a block
gives memory back only at exit, so a program allocating in a loop
grows without bound, untested, biggest unknown; (2) `kosh` growth
abandons the old buffer, a real leak, measured, unfixed;
(3) aliasing — `vitti a = k` then relocating growth leaves `a`
on the old buffer, which is why recycling was dropped; (4) the
escape check is lexical, lifetime is dynamic — a `kosh` of scratch
pointers is invisible. Method: script the whole tree, then read
every candidate by hand, then run decisive cases. No test was
weakened; no unbounded stream was piped through `head -N`.

**Counting units, stated explicitly.** Examples: 1 program = 1 file
→ 274. Library: 1 program = 1 function → 306 (24 modules).
Combined denominator: **580**. A `kosh_push` in a loop is growth
(Q2), never allocation (Q1). A `kosh` parameter in a signature
is not a declaration. A refusal is not allocation.

| Question | Examples | Lib | Total |
|---|---|---|---|
| Q1a: `nirmmita` textually inside a loop body | 1 | 0 | **1** |
| Q1b: `kosh` declaration inside a loop body | 0 | 0 | **0** |
| Q1c: call from inside a loop to a function that itself allocates (one level) | 3 | 0 | **3** |
| Q1, distinct programs | 4 | 0 | **4** |
| Q2 definite: a `kosh` grown >1000 times on the program's own inputs | 0 | 0 | **0** |
| Q2 potential: push count input-dependent, could exceed 1000 on large inputs | 1 | 0 | **1** |
| Q3: allocates AND contains no `mandapa` anywhere in the program/function | 57 | 26 | **83** |

### Q1 — loop allocation: 4 programs, all bounded, zero unbounded

- **Q1a = 1: `258_r70_loop_indent.sm`** — the tree's only
  loop allocator. Three allocating `yavat` loops, all fixed
  bounds, all persistent arena, no `mandapa` in the file:
  `i < 3` → 3 allocations, `j < 3` → 3, `n < 1000` →
  1000. Total on own inputs: **1006, all bounded**. It is a
  deliberate test about indented loop bodies (its header says
  so; its third loop's comment reads "1000 allocations in a
  loop, each written, the counter intact"). A fourth loop in
  the file (`k < 4`) does not allocate and is not counted.
- **Q1b = 0.** The library has no `kosh` declarations at
  all (all lib `kosh` use is via parameters, as R82 found).
  In examples, every `kosh` declaration in a loop-bearing
  file sits outside the loop bodies (span analysis plus
  hand-reads of all ambiguous regions: 208, 209, 215, 216,
  237, 269, 299, 286).
- **Q1c = 3.** `217_r12_report.sm` — `yavat (i < n)`,
  n = 8 scores, calls lib `ank_tak_varna` (one `nirmmita`
  per call, persistent) → 8 calls. `237_many_variables.sm`
  — `yavat (n < 2)` calls local `gahra` (two `nirmmita` +
  one `kosh k[1]` per call, persistent) → 2 calls.
  `268_r73_return_value.sm` — `yavat (k < 1000000)`
  calls local `varga_yoga` (`nirmmita(n*8)`, n = 4,
  **inside its own `mandapa` block**, scratch freed per
  call) → 1,000,000 calls that do **not** grow memory
  without bound. It counts for Q1c (textual loop-call
  allocation) but is not a growth risk. Lib loops call
  no allocating function. One false positive was caught
  and rejected by hand-reading: `126_numeric_pipeline`
  loops 100,000 times calling `maap`, but `maap`
  allocates nothing.
- **Gap (1) verdict: real for user code, zero demonstration
  in the tree.** No tree program allocates in an unbounded
  loop. The largest bounded case (258, 1006) is a deliberate
  test. The "biggest unknown" — RSS growth in a loop — was
  not measured here, and there is no unbounded
  loop-allocation site in the tree to measure it on.

### Q2 — kosh growth >1000: 0 definite, 1 potential

**Definite = 0.** Per-`kosh` counts for all 10
push-in-loop examples, hand-read: maximum is **100**
(`286_r82_kosh_in_mandapa.sm`, `varg_yog(100)`), then
22 (299), 21 (203), 11 (208), 9 (205), 6/9/4 (209),
6/2 (126), 3 (248), 4 total (237), 1 (257). All 32
push-without-loop examples push at most 26 statements
per file, each executing once. `kosh_enqueue` is used
**nowhere** in the tree; push is the only growth op.
Lib: the three modules matching a `kosh_push` grep
(`kalana`, `samanvaya`, `sankhyiki`) mention push
only in `#` comment lines — zero pushes in lib code.
**Potential = 1: `286_r82_kosh_in_mandapa.sm`.**
`varg_yog(n)` pushes exactly `n` times into its
`mandapa`-local `kosh k` (`yavat (i <= n)`); own
inputs use n = 10 and 100, but any n > 1000 would
exceed 1000 pushes. Every other push loop has a
fixed bound.
**Gap (2) verdict: the leak's tree footprint is
small.** Largest growth on own inputs is 100 pushes;
pushes are an upper bound on abandoned buffers
(actual reallocations depend on the growth policy,
not measured here). **Open question, not claimed
either way:** whether `mandapa` exit reclaims
buffers abandoned during growth inside the block.
That needs the RSS harness (Claude's ROUND-101
WS1), not this census.

### Q3 — allocates without any mandapa: 83 of 580

Examples **57 of 274** (allocating examples: 71; of
those, 57 have no `mandapa`). Lib **26 of 306** —
exactly the 26 `nirmmita` functions (lib has zero
`mandapa` and zero `kosh` declarations). The 57
examples: 06_rachana, 08_demo, 100_t18_kosh_bounds,
101_t18_kosh_empty, 109_t18_kosh_dasham,
111_t18_kosh_dasham_function_return,
112_t18_kosh_integer_conversion, 118_t18_kosh_param,
119_t18_kosh_param_forward, 120_t18_kosh_param_mismatch,
121_t18_kosh_param_push_reject,
123_t18_kosh_param_statement_call, 126_numeric_pipeline,
134_perf_float_complex_fallback, 135_r30_float_index_scalar,
136_r30_float_complex_left, 137_r30_float_literal_rhs,
138_r30_float_comparison_index, 139_r30_float_mixed_fallback,
140_r30_index_side_effect, 144_xmm_cache_fallback,
148_stage2_array_mutation_call, 203_meru_with_kosh,
205_madhava_pi_kosh, 206_sankhyiki, 207_sankhyiki_vector,
208_kalana, 209_samanvaya, 215_r12_wordfreq, 216_r12_expr,
217_r12_report, 224_unknown_field, 226_long_field_names,
234_ambiguous_field, 235_duplicate_field,
237_many_variables, 244_r18_rachana_in_function,
247_r23_methods, 248_r23_slices, 252_r38_alias_kosh_oob,
255_r42_alias_kosh_push, 256_r44_vartani_sanskrit_names,
257_r48_kosh_empty, 258_r70_loop_indent,
273_r77_bytes_not_cells, 274_r77_bytes_loop_stops,
275_r77_cells_times_eight, 280_r80_runtime_wraps,
283_r81_parikshita_refuses_library,
285_r81_parikshita_address_param, 288_r86_kosh_alias_moves,
96_t18_kosh, 98_t18_kosh_empty, 99_t18_kosh, array_demo,
full_demo, mem_safe. (Full filenames in the JSON.)
**Interpretation, as the brief directs:** this large
number measures **low block adoption, not risk**.
`mandapa` arrived in v268; the library never adopted
it (0/306), and examples adopt it in only **14/274**
files — all 14 of which are themselves
memory/escape/`parikshita` tests (263–272, 282, 286,
287, 299), i.e. programs written to test `mandapa`,
not ordinary programs using it. No ordinary example
and no lib function uses a `mandapa` block. A program
that allocates once at the top and never in a loop
is not a growth risk merely for lacking a block;
the risk-bearing subsets are Q1 and Q2, and they
are small and bounded.

### Gaps (3) and (4) — observations, not counts

- **Gap (3) aliasing:** no tree program combines
  aliasing with loop allocation. The alias programs
  (252, 255, 287, 288) push only straight-line (≤2
  pushes each); none allocates in a loop, none is a
  Q1 program. The recycling hazard (alias on an old
  buffer after relocating growth) therefore has no
  loop-allocation intersection in the tree.
- **Gap (4) `kosh` of scratch pointers:** not counted
  — outside Q1–Q3's scope, no systematic gap-4 scan
  was run. What the hand-reads did show: the 14
  `mandapa` programs follow allowed patterns (269
  copies *data* out of scratch into a persistent
  buffer and returns that; 286 reads through `padh`
  *inside* the block; 268 computes inside and
  returns a value). No hand-read found a `kosh`
  holding scratch pointers; that is an observation
  from the Q1–Q3 reads, not a gap-4 census, and is
  not claimed as one.

### Sarvam's verified behaviours, confirmed on v283

Both re-probed here (independently, `mukhya() {}`
form): `chakra i = 0 tak 3.0` → compile refused
`E_CHAKRA_DASHAM` (line 2:22), no binary;
`dasham avg = 15 / 4; likha(avg)` → printed
`3.000000`, exit 0 (integer division before the
store, same as C). Sarvam's speed numbers (1M
allocations: 164 ms no block, 40 ms in a block)
are Sarvam's, not re-measured here; his RSS
finding stands (no RSS number is claimed here —
`/proc` polling returns zero, `ulimit -v` fails
both versions; the harness is Claude's ROUND-101
WS1, not this round).

### WS1 answer to the brief's question

If "near zero" is read as "no unbounded loop
allocation and no `kosh` grown >1000 on its own
inputs", then **yes for Q1 and Q2** (4 bounded
loop-allocators, 0 definite >1000 growths) — the
memory gaps are theoretical for our own code, in
exactly the way the 3-1-0 alias census was. Q3
(83) is not near zero and should not be forced
there: it counts programs that never adopted a
block, most of which allocate once and never in a
loop. The priority consequence: the gaps matter
for user programs (a student *can* write an
unbounded allocating loop, and the growth leak
is real), but no tree program needs the fix
today — which is why the design work (R170) can
proceed on correctness and naming first, and the
RSS harness (ROUND-101) second, without a tree
program waiting on either.

## WS2 — Sanskrit vocabulary audit: read this first

**ChatGPT's R170 return was NOT found in the repo.**
`ChatGPT-to-Sarvam/` on main ends at ROUND-99 files
(October); a search for "170" there returns
nothing. What is audited here is therefore the
**candidate list Sarvam gave in
`Sarvam-to-ChatGPT/ROUND-170.md` WS2** (the proposal
under review), not ChatGPT's choices. No ChatGPT
return was invented. When ChatGPT returns his
justifications, they can be checked against this
audit. The R170 bar, quoted: the existing
vocabulary is `kshetra` (field), `mandapa`
(pavilion), `kosh` (sheath), `nirmmita` (created),
`nivartanam` (return) — "good words because they
describe what the thing IS, not what it does in
C." The four tests applied to every candidate:
(1) complete Sanskrit word, not a fragment (the
project rule — `paripurna` shortened to `purn`
loses `pari` and is rejected); (2) no collision
with an existing keyword or library function;
(3) easy to type and remember for a student whose
first language is not Sanskrit; (4) literal
meaning describes the thing, not a translation of
an English word (this test matters most).

**Collision method (measured, not judged).**
Word-boundary grep per candidate over `src/`
(keywords and diagnostics are plain strings),
`lib/` (all 24 modules: `prakriya` definitions,
any occurrence, substring-in-name),
`docs/LANGUAGE-REFERENCE.md`, plus an `examples/`
bonus check. Keywords are matched exactly by the
lexer (e.g. `KW_MANDAPA`), so a substring inside
another name is overload, not collision. Result:
**10 of 11 candidates have zero hits in all
sources.** The exception is `seema` (below).
Near-misses assessed, not collisions: `khand_mukt`
(lib/khand.smlib, the `mukt` root, relevant to
`mukti`); `yog_seema`/`yog_tak` (relevant to
`yuga` similarity and to `seema`); `kalana`
(module name, relevant to `kalpa` similarity).
`Sanket` is confirmed as the existing diagnostic
hint label and is proposed for nothing. Test 1:
**all 11 pass** — none is a fragment like `purn`;
the fragment rule rejects nothing here.

### Per-word verdicts

| Word (concept) | Devanagari | Literal meaning | Verdict |
|---|---|---|---|
| `kalpa` (epoch) | कल्प | eon, cosmic age; also a ritual manual | PASS-WITH-CAVEAT (runner-up) — an age, yes, but cosmic scale, not a generation incrementing on every free/reuse; the ritual-manual second meaning distracts |
| `samskara` (epoch) | संस्कार | imprint, rite, conditioning — NOT a time period | REJECT as epoch — a new `samskara` reads as a new rite/impression, not a new era; fails test 4 decisively for this concept |
| `yuga` (epoch) | युग | age, era (Kali Yuga); also a yoke | PASS — an age/era is exactly an epoch; new `yuga` = new era, old handles stale; 4 letters, easiest, most familiar |
| `punaravritti` (reuse) | पुनरावृत्ति | repetition, coming back again | PASS-WITH-CAVEAT (reuse only) — precise for reuse (used again), but NOT for return (not yet used again, only given back); 12 letters, the longest keyword yet (vs `nivartanam`, 10) |
| `visarjana` (return) | विसर्जन | letting go, sending away, immersion, release | PASS — precise for return/release: the region is let go back to the pool; it does not mean reuse, which is correct, because the programmer's act is release and reuse is what the pool does later |
| `mukti` (reuse/return) | मुक्ति | liberation, freedom, release from bondage (moksha) | REJECT — says "freedom" generally, not "returned to the pool"; dominant sense is spiritual liberation; adds nothing over `visarjana`, and the `mukt` root is already in `khand_mukt` |
| `parimita` (bounded) | परिमित | measured, limited, bounded, finite | PASS — precise: a region with a measured limit; pairs with `ananta`; 8 letters, regular (`pari` + `mita`), unambiguous |
| `maryada` (bounded) | मर्यादा | boundary/limit (classical); propriety, dignity, decorum (modern Hindi) | REJECT — a Hindi-speaking student hears dignity/propriety first (`maryada purushottam`); a "maryada region" reads as respectable, not bounded |
| `seema` (bounded) | सीमा | boundary, limit, border; boundary of a field | PASS-WITH-CAVEAT (runner-up) — no hard collision (no bare `seema` keyword/function, no example use), BUT semantic overload: `seema` already means "limit" in ~20 diagnostics (`mala ank seema atikram` etc., 24 hits in `src/`), "end of a range" in `yog_seema(start, end)`, and diagnostically in the reference (line 476). All share the boundary/limit sense, so the overload is benign in direction — but real (limit property vs end vs bounded-region thing). Elegant beside `kshetra` (`seema` is the boundary OF a field); adopt only with a reference note distinguishing the uses |
| `ananta` (unbounded) | अनन्त | endless, infinite, without end | PASS — precise; pairs with `parimita` (strict-antonym note: `parimita`/`aparimita` and `ananta`/`santa` are the strict pairs, but `parimita`/`ananta` work in sense and each word is independently correct) |
| `mudra` (handle) | मुद्रा | seal, stamp, sign (raja-mudra = royal seal); also a dance gesture | PASS — a handle SEALED with its generation; on use the seal is checked, broken seal = stale. The metaphor carries the validation semantics, not just the carrying |
| `samskara` (handle) | संस्कार | imprint, impression, trace | PASS-WITH-CAVEAT (runner-up, handle only) — viable: a handle carrying its generation as an imprint, compared on use; but vaguer than `mudra` (an imprint could be any trace; primary associations are rites/mental impressions, pulling away from validation) |

**Can `samskara` serve BOTH epoch and handle? No.**
It would conflate exactly what must stay apart
(the period, which increments, vs the token,
which is validated against it), and it already
fails test 4 for epoch. Verdict: `samskara`
takes the HANDLE use only, and only as runner-up
to `mudra`. If `mudra` is adopted (recommended),
`samskara` takes neither — there must not be two
handle words, and there must not be an epoch word
that is not an epoch.

### Ranking per concept and recommended set

- **Epoch: `yuga`** (runner-up `kalpa`).
- **Reuse/return: `visarjana`** for the act
  (runner-up `punaravritti` for reuse specifically;
  if the design needs two distinct words, use
  `visarjana` for release and `punaravritti` for
  reuse; if only one, it is `visarjana`).
- **Bounded: `parimita`** (runner-up `seema`).
- **Unbounded: `ananta`** (sole candidate, needs
  no runner-up).
- **Handle: `mudra`** (runner-up `samskara`,
  handle only).

**Recommended set: `yuga`, `visarjana`, `parimita`,
`ananta`, `mudra`** — with `punaravritti` held for
reuse-if-distinct, `kalpa`/`seema`/`samskara` as
runners-up, and `maryada`/`mukti` (and
`samskara`-as-epoch) rejected. No recommended word
collides with any existing keyword or function.

One line of `.sm` code using each recommended word
(as R170 asks). **These are PROPOSED usage, not
v283 code: none of the five words is a keyword on
v283, so none of these lines compiles today.**
They show how each word would read, in
Sutram-idiomatic positions (the qualifier grammar
on `mandapa` is for the implementer to settle;
the point is the word choice, not the grammar).

```
vitti e = yuga(kshetra)        # the epoch of this region (cf. kosh_len(k))
visarjana(kshetra)             # release this region back to the pool
parimita mandapa {             # a bounded block
ananta mandapa {               # an unbounded block
vitti h = mudra(kshetra)       # a sealed handle for this region; a broken seal is stale
```

## WS3 — misread update for v283: the Round 95 numbers stand

The brief asks for the misread count updated for
v283, "now that four behaviours changed", and
quotes the brief's denominator as 267. The
denominator is stale, as Round 95 established:
**274** top-level examples, not 267 (267 is the
pre-300-302 PASS count). And because no code or
examples changed since the Round 95 census base
(diff empty, suite re-verified 270/4/0 on this
HEAD), the Round 95 answer is already the v283
update — reconciled here, not redone. **Misread
count on v283: 0 (reference-reader definition) /
30 (R84/R86 definition), denominator 274.**
The four changed behaviours, each mapped to its
effect on the count:

| Behaviour changed | v282 | v283 | Effect on misread count |
|---|---|---|---|
| Decimal `chakra` bounds | run away (hang) | refuse `E_CHAKRA_DASHAM` | **None.** No tree example uses a dasham loop bound (census zero, R92), so no example's misread status changes. The behaviour change matters for user programs, not for the count. |
| Computed float-to-int conversion | truncate silently | whole → whole, fraction → refuse `E_DASHAM_VITTI` | **None beyond R95.** R95 already applied this: 93/94 now whole (`blend(1.0,3.0)=2.0`, probed exit 0), which is why float fell 2 → 0 from R86's 31. No further change. |
| Decimal `%` / bit operators | garbage | refuse `E_DASHAM_KRIYA` | **None.** No tree example exercises the old garbage behaviour, so no example's misread status changes. |
| Dasham division by zero / NaN | inf silently / wrong compares | refuse `E_SHUNYA_BHAJAN` / IEEE compares | **None.** The examples touching it (289, 291, 294, 299) are deliberate fixtures with headers stating the behaviour and matching goldens; they are demonstrations, not traps, under both definitions. |

**The assumptions page needs one v283 edit, not a
recount.** R86 verified 26/26 on v279. On v283,
the sixth assumption — a dasham `tak` bound never
terminates — is no longer true as stated: decimal
`tak` bounds now **refuse** (`E_CHAKRA_DASHAM`),
they do not hang. The proposed edit is one line
(hang → refuse); the other 25 items are unaffected
by the four changes, for the reasons in the table
above. This round proposes the edit; it does not
apply it (the reference is the owners' document).
**Sentence: no change proposed.** The R93
inf-only sentence stands; the memory gaps add no
new user-facing surprise in any tree example
(Q1/Q2 are bounded, Q3 is adoption, not
behaviour), so there is nothing new for the
sentence to warn about.

## NOT RUN

Windows, browser, implementation (no compiler
change, no word added to the compiler, no RSS
harness built — the harness is Claude's
ROUND-101 WS1, and the implementation is R170's
design, neither assigned here). Native-speaker
review of the vocabulary audit (all Devanagari
forms and literal meanings are best-effort from
standard Sanskrit vocabulary and must be confirmed
by a native speaker before any word ships, as the
project requires for transliterations; in
particular the `maryada` modern-Hindi judgment
and the `kalpa` ritual-manual second meaning).
Guard, gates, proofs (not re-run; no src/lib/
examples/tests changes since the Round 95 base).
Suite note: re-run on this HEAD gives PASS=270,
NO-EXPECTATION=4 (215, 216, 217, 219), 0 FAIL;
the script exits 1 because its `bad` count is
FAIL + COMPILE-FAIL + NO-EXPECTATION, so the
exit code reflects the 4 no-expectation items,
not a failure.
