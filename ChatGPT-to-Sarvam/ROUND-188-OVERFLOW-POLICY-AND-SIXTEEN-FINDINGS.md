# R188 — checked mathematical library contracts; preserve explicit machine arithmetic

Base: `2065ebeb71edebecfee47db14861d4d5e455bf4a`, compiler v292, 2026-11-03. Read-side policy/design review. Compiler and library source remain unchanged from the inspected R184 base; intervening GitHub comparisons contain handoffs and evidence only.

**Choose option 2 for v1.0: enforce mathematical library contracts, without globally changing plain integer operators. This is a code round, not only documentation.** Small geometry inputs, a too-small digit destination and a padded decimal string already expose errors without large numeric values. A single policy governs their failure reporting, but an overflow switch cannot repair their different algorithms.

## 1. One policy, with explicit operation domains

> A public mathematical operation must produce the result promised by its documented numeric contract, or report failure through its declared channel. It must not publish a wrapped or truncated result as successful exact computation. Modular and saturating operations are separate, explicit contracts.

- Preserve current runtime machine-operator semantics for this release, including intentional modular code such as `ganit_yadricch`. State the exact operations and edge cases; do not say “everything wraps,” because constant overflow and several runtime failures already refuse.
- Ordinary scalar mathematical convenience functions such as dvigun/trigun/vardh/absolute-value/gcd/digit reversal should reject unrepresentable mathematical results. Preserve their scalar success signatures; use a named fatal diagnostic on failure rather than inventing a valid-looking sentinel.
- Existing checked `ganita_janchit_*` functions retain their status channel, and explicitly saturating `ganita_paripurna_*` contracts retain saturation. A documented failure result is not an exact answer; 0 alone is not self-identifying as failure.
- Functions that already have an explicit success/failure channel must use it honestly: a full destination or failed sort cannot report success. Specify output state on failure; partial output must not be consumed as a successful result.
- “Mathematical result” means the stated contract: integer floor/truncation where documented, approximate binary64 where documented. It does not promise arbitrary-precision results from fixed-size storage.

This chooses library checking, not a switch that changes every arithmetic instruction. It also does not mechanically add E_ATIPRAVAH to all sixteen functions. Shape, parsing, resource and predicate failures need their own contracts and channels.

**Compatibility is real:** wrapping cases are already pinned in numeric tests and documented. Reclassifying the ordinary helpers is an intentional pre-v1.0 contract change. Record the changed cases and targeted expectations; preserve intentional modular algorithms. Do not rewrite all goldens, hide the change behind “bug fix,” or claim byte-identical output. Callers needing modular arithmetic can use the explicitly documented operator contract; checked/recoverable callers can use the checked family.

### Why not the other two options?

| Option | Benefit | Limitation / decision |
|---|---|---|
| Document all wrapping | No extra runtime instructions for existing operations; lowest implementation cost. | Does not correct wrong formulas, false success, discarded digits or premature saturation. Inconsistent with the ordinary library's mathematical promise. Reject as the solution. |
| Check at library boundaries/algorithms | Localized checks and diagnosable failures; no extra checks in unrelated user arithmetic; preserves intentional modular code. | Requires explicit contracts and algorithm changes; raw user expressions can still overflow. **Choose.** |
| Check all arithmetic by default | Broad detection of integer-overflow mistakes. | Language-wide compatibility change, optimizer/emitter coverage, explicit wrap escape hatches and checked-library composition work. Still misses the non-overflow defects. Defer. |

“Matches C” is not an accurate justification for signed wrap. ISO C's ordinary signed overflow is undefined behavior; unsigned arithmetic has modulo semantics. See [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), 6.5 paragraph 5 and 6.2.5 paragraph 9. Sutram may deliberately define signed two's-complement wrapping, but that is its own language choice. The existing docs should not teach that ordinary signed C guarantees it.

## 2. Cost and implementation constraints

These are structural costs, **not measured cycles, binary sizes or slowdown percentages**.

| Operation | Library guard before computing | Incremental successful-path work |
|---|---|---|
| dvigun(n) | require -4611686018427387904 <= n <= 4611686018427387903 | up to two comparisons/branches, then existing multiplication |
| trigun(n) | require -3074457345618258602 <= n <= 3074457345618258602 | up to two comparisons/branches |
| vardh(n) | reject n == MAX | one comparison/branch |
| abs(n) | reject n == MIN before negation | one comparison/branch plus existing sign handling |
| gcd | handle signed magnitudes without negating MIN blindly; reject only a final magnitude 2^63 | edge handling around an O(log magnitude) algorithm; do not reject all MIN inputs |
| digit accumulation/reversal | before r*base+d, check r against quotient/remainder of the result limit | constant checks per digit; same O(digits) complexity |

For gcd, `gcd(MIN,2)=2` is representable and should succeed. For reversal, MIN itself reverses to a representable negative result in the current special case; do not reject it solely because abs(MIN) overflows. Check the promised result, not an unnecessarily overflowing intermediate.

Shared cold diagnostic support adds code/data and failure-path printing/termination. Library guards themselves can be written before the arithmetic. A named fatal path requires an **approved compiler-emitted failure facility or internal lowering**, since core libraries must not become std-layer I/O routines just to print errors. Do not smuggle `likha`/exit syscalls into every core helper or pretend a generic named panic primitive already exists. This support need not instrument every user operator and requires no external runtime dependency. Recoverable APIs remain status/result based; converting every scalar helper to native phal would break its call contract.

If option 3 is considered later, ordinary flag-setting x86-64 signed add/sub/mul can often be followed by a conditional overflow branch to shared cold code. Negation and division need their own cases; LEA/shift/peephole forms may not provide the right overflow flags and must preserve checked semantics. A branch encoding alone can be 2 or 6 bytes, but that is not the total code-size cost. Checks add branch/dependency/code-density costs and may inhibit optimization; actual impact depends on the workload and emitter. Checked arithmetic is compatible with systems programming, but kernels/freestanding programs need a defined failure hook and intentional wrapping operations, not mandatory diagnostic I/O.

The project already has opt-in `SUTRAM_R65_TRAP_INT`, default off, and E_INTEGER_TRAP machinery. **Do not simply enable it.** Current `ganita_janchit_yuj` computes `s=x+y` before examining signs; multiplication computes the product before its division check. Trapping first prevents their promised status return. The source confirms the composition warning in OVERFLOW-SAFETY.md. Audit/rewrite those paths and every emitter/optimization before a global default change.

### What the selected policy does not solve

It does not make raw pointers safe, prevent user-level operator wrap, fix output aliasing, guarantee numerical stability, make arrays arbitrary precision, distinguish filesystem errors automatically, enforce all contracts, or make fatal diagnostics catchable by `yadi dosh`. It also cannot fix a formula whose intermediate arithmetic is perfectly in range but mathematically wrong. R185's native result mechanism and float-payload limits still apply.

## 3. E_ATIPRAVAH and the exact proposed message

The existing code is appropriate for integer overflow, but **its present emission is not the requested library diagnostic**. At `src/sutram_compiler.asm:390–394`, the text describes a literal or constant calculation outside the signed 64-bit range, and the hint gives both limits. It does not name dvigun or its runtime argument. R65 runtime traps use E_INTEGER_TRAP separately. Reusing E_ATIPRAVAH for library range refusal requires a new runtime path and documented phase extension; an existing string label does not implement that path.

Exact proposed diagnostic body for `dvigun(MAX)`, retaining the currently implemented prefix:

```text
Sutram Error [E_ATIPRAVAH]: dvigun: 2 * n iti phalam purnanka-seemam atikramati; n = 9223372036854775807.
Sanket: purnankah -9223372036854775808 tah 9223372036854775807 paryantam; dvigun-kriyayah n -4611686018427387904 tah 4611686018427387903 paryantam bhavet.
```

This is an **exact Romanized Sanskrit wording proposal**, not output observed from the current compiler and not certified by a native speaker. It names the operation, operand, result type range and allowed input range. The mathematical result would be 18446744073709551614; the failure printer need not overflow its own integer formatter to display that value. Do not print wrapped -2 as “the result.”

When the R183 prefix decision is accepted, replace only `Sutram Error` with the agreed `Sutram truti` prefix consistently; this round does not silently implement that separate migration. Attach the actual source file:line:column using available origin metadata. A library failure site must not be mislabeled as the user's call site: without new caller metadata, show the library location honestly; add call-site attribution only when implemented. No invented filename/line is included above.

Do not use this diagnostic for a missing file, length mismatch or allocation failure. Do not parse its prose to recover: explicit status APIs are the recovery interface.

## 4. All sixteen: reachability and design classification

Muse's R112 reports fifteen native probes plus one source-only allocation-failure finding. Those are **Muse's results**, not reruns here. I reviewed the relevant source and ran separate Python exact-integer models for arithmetic cross-checks. Reachability below is a reasoned educational assessment, not measured student incidence.

| # | Function | Input/condition a student could encounter | Design classification and action |
|---:|---|---|---|
| 1 | ganit.dvigun | MAX is an explicit edge, but repeated doubling from 1 crosses the boundary after 63 calls. | Existing modular result differs from mathematical contract; enforce exact-or-refuse helper policy. Not usually accidental in a tiny single calculation. |
| 2 | ganit.trigun | Large input or about 40 repeated triplings from 1. | Same policy migration. Model confirms the cited input's true result is **MAX+2**, not MAX+1; wrapped output cited by Muse is correct. |
| 3 | ganit.vardh | MAX from input/earlier computation; counting from 0 to MAX is not a plausible short exercise. | Edge-focused policy migration; reject MAX. |
| 4 | ganit.nirapeksh_mulya | MIN parsed or produced by prior wrap. | Boundary representability failure; reject MIN under the new exact contract. Existing comment already admits wrap. |
| 5 | ganit.mahattam_samapavartak | MIN with 0 or other input whose gcd magnitude is 2^63. | Contract conflict (“always non-negative” versus admitted exception); reject only unrepresentable gcd, not every MIN operand. |
| 6 | ank.viparyay_ank | A 19-digit input, possibly imported text, reverses beyond the limit. | Large-input overflow; explicit checks. Current numeric29 tests deliberately pin wrapping, so change them intentionally. |
| 7 | ganita.ganita_nirapeksh | MIN. | Same representability/policy migration as #4; reuse existing checked absolute-value semantics. |
| 8 | ganita.brahmagupta_kshetr | Tiny valid sides (1,1,2,3), or triangle (2,3,4,0). | **Ordinary-input algorithm defect.** Current 0 instead of floor(area)=2; no overflow required. Fix semiperimeter precision. |
| 9 | aadhar.brihat_ank_se | Three decimal digits 100 into a two-digit destination, or 99999 into two digits. | **Ordinary capacity mistake plus false success.** Carry is discarded; detect nonzero overflow carry and return documented failure with explicit output-state policy. Not machine-i64 overflow. |
| 10 | brihat.brihat_ank_tak_laghu | Convert a 19-digit bigint back to scalar. | Conversion-domain edge, natural in a bigint lesson. Existing “only if it fits” precondition makes this an unenforced-domain gap, not proof of wrong results on all valid inputs. Add checked refusal/variant under the selected policy. |
| 11 | patra.patra_asti | Wrong working directory, permissions, a directory selected where a regular file was intended, or symlink behavior. | **Predicate/design mismatch**, not arithmetic. Existing body/comment promises read-openability, not a reliable existence/error discriminator. Specify path-entry vs followed-target vs regular/readable file semantics and return error separately. A directory is itself an existing path; true on a directory is not inherently an existence bug. |
| 12 | sadhan.yog_seema | Single-element range at 2^62. | **Algorithm defect at a large boundary:** returns MAX although the exact sum fits. Premature saturation of an intermediate; global traps do not make it correct. |
| 13 | samanvaya.adish_gunan | One vector has an omitted push: [1,2,3] and [4,5]. | **Common shape mistake, but current prefix behavior is documented.** Strict equal-length behavior is a reviewed contract migration, not proof that the existing loop fails its stated prefix contract. |
| 14 | sankhyiki.bindu_gunan | Same ordinary unequal-length case. | Same contract migration. The teaching example explicitly exercises prefix behavior; update intentionally or offer a distinct checked entry. |
| 15 | suchi.suchi_shreni | Scratch allocation denied while sorting; no huge scalar input required. | **False success on a resource failure.** Propagate mil_shreni failure before claiming sortedness. Potentially rare, high consequence; source-only in Muse's report. |
| 16 | vakyank.varna_tak_dashm | Padded input “00000000000000000001”: twenty characters, mathematical value 1. | **Ordinary-format parser defect:** leading zeros exhaust the “significant digit” budget, producing 0 with ok=1. Fix digit accounting and exponent handling, not overflow policy. |

The `sankhya_bindu` builtin is **additional to these sixteen library definitions**, not one of them. Its withdrawal remains R187's containment priority; do not turn 16/306 into 17/306 by mixing scopes.

The eight primarily scalar-wrap entries are #1–7 and #10. #12 is premature saturation; #9 is fixed-digit capacity; #8 is formula precision; #16 is significant-digit parsing; #15 is discarded status; #11 is predicate semantics; #13–14 are documented prefix semantics versus a desired stricter API. “All sixteen have one overflow cause” is not supported.

### Disagreement with “all sixteen are wrong, none are different”

A contract, not just a name, determines correctness. Prefix dot products compute the documented prefix result. Read-openability is what patra_asti's local comment currently states. Wrapping behavior is explicitly pinned for several helpers. These can be poor teaching defaults and justify a change, but are not indistinguishable from an implementation contradicting its contract. Conversely, documentation cannot repair semiperimeter truncation, discarded significant digits or false success. Use R187's contract records to distinguish **current behavior**, **desired behavior**, and **implementation defect**.

Reaching an edge “deliberately” is also not a waiver: parsed data and iteration can supply it. Rarity affects ordering and testing, not the obligation to implement the accepted contract. Memory pressure need not be caused by the student's own program.

## 5. Small witnesses that settle “code or documentation?”

- `brahmagupta_kshetr(2,3,4,0)` is a triangle exercise with single-digit sides. Truncating s=4.5 to 4 makes a factor zero. The correct area is sqrt(135)/4, whose floor is 2. Checked addition/multiplication still produces the wrong zero in the old formula.
- With T=a+b+c+d, an exact integer-floor formulation can use `floor(sqrt((T-2a)(T-2b)(T-2c)(T-2d))/4)` after domain validation. This is a **design direction**, not a drop-in i64 expression: products may require wider/bigint arithmetic or a documented checked range. Do not replace one overflow bug with a larger intermediate. For cyclic quadrilaterals validate the domain; sides alone do not determine an arbitrary noncyclic quadrilateral's area.
- A two-digit destination cannot hold 100. In `brihat_ank_se`, arithmetic remains small, but carry after the destination loop is ignored. Returning 1 is not made correct by machine checked arithmetic. Prefer capacity validation before committing output, or explicitly clear/invalidate output on failure if transactional scratch would be too expensive.
- Leading-zero float text has small magnitude. Significant-digit accounting must skip insignificant leading zeros while preserving fractional place/exponent information; deleting every zero indiscriminately is not a fix.
- `yog_seema(2^62,2^62)` should return 2^62 even though start+end does not fit signed i64. Change the algorithm/guard ordering, with independently derived final-result bounds. Refusing this valid result would be an avoidable regression of its saturating contract.

These are enough to establish a **code round now** without asserting that every one of sixteen is an undisclosed bug.

## 6. Work order and acceptance

1. Contain the broken builtin under R187. In parallel scheduling by the owner, prioritize actual small-input formula/parser/capacity defects (#8/#9/#16) and false-success propagation (#15). This report does not start another agent or overlap Muse's implementation.
2. Adopt the exact-or-refuse mathematical-library policy; implement common boundary/failure support and migrate the scalar edge cases, plus fix premature saturation #12. Review every changed old golden against an independent expected result.
3. Decide and migrate dot length and path predicate contracts (#11/#13/#14) explicitly. Preserve compatibility surfaces where required and teach their limitations during migration.
4. Reconcile stale numeric documentation: NUMERIC-CONTRACT.md and OVERFLOW-SAFETY.md still describe some pre-R80 behavior, old names and SIGFPE cases that current source has changed. Do not let a global prose sentence override current compiler evidence.
5. Test boundaries just inside/outside each valid result range, MIN/MAX, signs, empty/small shapes, alias/output state, allocation-failure injection and parsing with leading zeros. Validate status, diagnostics and state as well as printed numbers. Test optional trap builds separately for composition; do not enable them globally as an unreviewed fix.

Executed here: pinned-source comparisons/reading and exact-integer arithmetic models, delivered in [ROUND-188-ARITHMETIC-EVIDENCE.json](ROUND-188-ARITHMETIC-EVIDENCE.json). The model also corrects Muse's MAX+1 wording for trigun to MAX+2. No performance timings claimed. Muse's fifteen probe claims remain attributed to Muse; none were rerun here.

Native build, suite, guard, Windows and CI: **NOT RUN — no toolchain used for this read-side assignment.** Exact Sanskrit wording is a proposal pending native-speaker review. No production source, library, tests, tools, reference documents or frozen packs were changed.
