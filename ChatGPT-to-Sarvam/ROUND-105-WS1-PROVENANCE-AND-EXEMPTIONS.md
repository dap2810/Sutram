# Sutram R105 WS1 — A source-level provenance gap, and all 19 exempt allocation sites

**Read-only audit, 2026-10-22.** Pinned main `09991ba4d28e4e985fc2fd5011b678aed2980360` (v310, compiler v244). Sources examined: `tools/check_alloc_bounds.py` Git blob `55ce880c45eb36542c32c761689fc2aa0b9f6ad1`, `ChatGPT-to-Sarvam/ROUND-103-CHECK-ALLOC-SIZES.py` blob `cace924fc6af3e2b7b6e56643aa8187f8ca4fea3`, current `lib/` sources. **No tools, tests, production source, or workflows edited; test execution NOT RUN - no toolchain.**

## 1. What the actual official gate proves — and does not

R37 `tools/check_alloc_bounds.py` is integrated with `tools/gates.sh`. Sarvam's fresh-clone measurement is **25 computed allocation sites: 6 bounded, 19 exempt, 0 failed** (partner evidence, not a fresh ChatGPT run). The checker tokenizes one line at a time, recognizes direct `*` or a single `mult_vars` assignment leading to `nirmmita`, looks for `yadi (name > decimal_constant) { prati`, and allows any such bound earlier in the *function*, without comparing the constant to the required mathematical limit or proving the branch is unconditional.

**Therefore R37 can catch a simple missing check in `sz=c*8; nirmmita(sz)` IF that assignment is detected and the function is not exempt; it cannot prove validity-before-multiplication.** A bound inserted *after* `sz=c*8` but *before* `nirmmita(sz)` still gets credit. So do useless `c > INT64_MAX` prechecks or checks reachable only under a conditional branch. And a reassignment `sz = other` does not necessarily kill stale `mult_vars[sz]` origin metadata.

R103's simpler filename-level spellings checker accepts `nirmmita(sz)` whether `sz` was valid, a raw untrusted count, or fabricated by an unsafe multiply. R104 already established its **35/35 current spellings recognized** but weak semantics. **Do not install R103 as a duplicate mandatory gate.**

## 2. READ the exemptions: 12 function keys authorise 19 existing sites

The exact `EXEMPT` values in `tools/check_alloc_bounds.py` are quoted below, preserving what they promise. A conditional argument may justify a *documented unsafe/raw API* but is NOT proof that its input came from a valid constructed object.

| Exact exempt key | Number of site instances | Exact reason in gate | Source-level validity judgement |
|---|---:|---|---|
| `nighantu / nighantu_vardh` | 1 | `oldcap = m[0] <= the nighantu_srij bound, so oldcap * 33 + 1 <= 5.44e18` | **CONDITIONAL, reasonable for an intact map created by nighantu_srij**, but `m` is a raw pointer; provenance is not checked. R36 now checks the new map and scratch allocation results. |
| `nighantu / nighantu_mil` | 1 | `scap is the source map capacity, <= the nighantu_srij bound` | **WEAK**: `scap` is an **independent caller argument**; source does not check `scap == src[0]`. A perfectly valid source-map handle with an incorrect `scap` can invalidate the bound. |
| `sangrah / rakh_samroop_diff` | 2 | `a set is a map: cap <= the nighantu_srij bound` | **WEAK**: `cap` and `bcap` are caller arguments, not extracted from `a[0]`/`b[0]`; zero checks of their agreement here. |
| `sangrah / rakh_sangam` | 2 | same `a set is a map: cap <= the nighantu_srij bound` | **WEAK**, same independent supplied capacities for both source sets. |
| `sangrah / rakh_sampat` | 1 | same | **WEAK**, caller-supplied `cap` is not verified against the actual handle. |
| `sangrah / rakh_bhed` | 1 | same | **WEAK**, caller-supplied `cap` is not verified. |
| `sangrah / rakh_asti_upasamuh` | 1 | same | **WEAK**, caller-supplied `cap` is not verified. |
| `sangrah / rakh_tak_mala` | 4 | same | **WEAK**, caller-supplied `cap` is not verified; the qword-cell output extent is independent of the map allocation. |
| `aadhar / brihat_ank_tak` | 2 | `the caller's own digit count: a wrap needs more than 2^58 digits` | **CONDITIONAL/WEAK**: a genuine caller-allocated n-digit array is a plausible contract, but `n` is an untyped supplied integer, no input extent is checked, and *“needs more than 2^58 digits” is not a source-enforced bound*. The second scratch request scales by **32**. |
| `brihat / brihat_shesh` | 1 | `the caller's own digit count` | **CONDITIONAL/WEAK**: no machine-readable provenance or actual input-array extent, so not proof for arbitrary `n`. |
| `brihat / brihat_ghatmod` | 2 | `the caller's own digit count` | **CONDITIONAL/WEAK**, needs 2n result/temporary extent and valid input arrays; cannot infer from `n` alone. |
| `shreni / mil_shreni` | 1 | `the caller's own array length` | **CONDITIONAL/WEAK**: a valid array and correctly supplied `n` justify the formula, but no actual raw-array extent is read/checked before `nirmmita(n*8)`. |
| **Total** | **19** | **12 distinct key/reason pairs** | **No exemption certifies arbitrary caller input or pointer safety**. |

**Mathematical note:** R35's map constructor prechecks `cap <= floor((INT64_MAX-16)/56)=164703072086692424`; therefore `33*cap+1` fits **for a correct constructor-created map**. The calculation is sound. The missing fact is `scap/cap/bcap == handle[0]` and that the handle itself is valid. Do not call correct map arithmetic an unbounded-multiply bug when its precondition really holds.

### Bigger hole in the exemption implementation

The key is only `(module,prakriya)`, not `(function,allocation-site,expected-expression,operands)`. **Any NEW computed `nirmmita` inside `rakh_sangam` or `nighantu_mil` can borrow that function's old exemption, even if it is an unrelated, dangerous multiplication.** The exemption's prose is not checked against the new variable. Exemptions should be **exact-site, canonical formula + operand provenance** commitments; adding a new one should fail until individually reviewed.

## 3. Minimal mechanizable step (not a general proof)

**YES: the named `sz=c*8` defect can be caught mechanically without a full compiler.** For a deliberately narrow subset only:

1. Tokenize actual Sutram statements/function blocks, including comments, strings and multiline calls; reject an unparseable allocation sink instead of silently skipping it. No regular-expression split-at-first-parenthesis or skip-on-multiline.
2. At each allocation sink, walk assignments of the size variable **backwards**, keep *current* reaching definition(s) and invalidate old definitions on reassignments. Recognize `sz=c*S+h` and `sz=c*S` only when `S>0,h>=0` are checked integer constants. A helper-return or unknown expression is a **REVIEW_REQUIRED** result, not approved by a familiar `sz` token.
3. Before the **assignment that multiplies** (not merely before the allocation), require a guard that **dominates the assignment** and exits on `c<0` and `c>floor((INT64_MAX-h)/S)`. Verify the **actual numeric threshold**; `c>MAX` is insufficient for S=8. For compound `count*2*8`, prove the entire composition before the first multiply. A bounded alias is acceptable only with its own tracked proof.
4. Exemptions must specify **the exact canonical expression, original operands, and what validates their provenance**; require a human-reviewed unsafe/caller-contract designation when the actual pointer extent is unavailable. Unknown new allocations or conditional code paths fail closed / require review. Count number of sites, compare to pinned inventory, and reject any changed assignment preceding a sink pending an updated proof.
5. Print two separate states: **FORMULA PROVED (within supported syntax)** or **REVIEW_REQUIRED/UNKNOWN**. Never print “all allocations memory-safe”: no sound proof of arbitrary raw-pointer provenance, aliases, allocation failure or writes follows from this syntax.

**Check-the-check mutations to require**: `sz=c*8` with no guard; an unsafe `c>MAX` guard; guard moved *after* `sz=c*8`; guard in a branch that may not execute; `sz` reassigned; safe `c<0` + `c>MAX/8` before assignment; a new computed allocation inside an exempt function; multiline `nirmmita`; a valid `32*2` constant expression. Reject unsafe mutations; accept valid ones. This is a **specification of a mechanical improvement, not a shipped checker**.

**Fundamental limit:** if `n` and a raw pointer are arbitrary user inputs, a source scanner cannot derive actual allocation extent or pointer lifetime. That needs language-level types/ownership or runtime bounds metadata plus an analysis of control flow and aliasing. Human review must state trusted caller preconditions explicitly; don't pretend an exemption is the proof.

## 4. No toolchain / evidence boundary

- **PASS (read)**: exact 12 EXEMPT entries and their grouped 19 existing call-site instances cross-referenced against current source.
- **PASS (design)**: finite, explicit mechanism for direct constant-stride assignment with fail-closed unknowns.
- **NOT RUN - no toolchain**: native Sutram test, complete regression suite, native Windows test, build or fuzz gate.
- **NOT RUN - no toolchain**: candidate new checker and its mutation tests (no code was authored under `tools/` or elsewhere).
- No source code or existing golden changed. Claude R39 independently owns its assigned provenance evaluation; this WS1 was prepared before his R39 handback was read.
