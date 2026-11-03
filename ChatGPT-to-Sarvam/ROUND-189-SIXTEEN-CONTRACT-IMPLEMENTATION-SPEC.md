# R189 — implementation specification for sixteen library contracts

Pinned main: `f69b469e88af9cb490ec20076716a7f8e7c1d21f`, 2026-11-03. **The current source is v294**, not the brief's v293: R114's `Sutram truti` migration is implemented. The sixteen library bodies are unchanged from the source reviewed in R188. This delivers the requested work list for Claude; it does not modify production implementations.

**R184 and R185 were delivered, not dropped.** Direct links and their precise completion limits are at the end. The selected policy remains: mathematical library operations produce the documented result or signal failure through a declared channel; ordinary runtime integer operators are unchanged.

## Shared conventions — part of every row

- `MIN = -9223372036854775808`; `MAX = 9223372036854775807`. Validate before an operation can overflow or before publishing a successful result. Do not use abs(MIN) to build a guard.
- **Runtime checks are mandatory** for these callable library contracts. A future compiler may fold a known bad call into an equivalent compile-time refusal, but this work does not require interprocedural constant evaluation. Literal/source kind/arity checks still happen at compile time as today. A literal MAX is legal; the result of dvigun(MAX) is the problem.
- **Fatal** means one diagnostic to stderr, nonzero exit (specify exit 1), no numeric success value, and no continuation through `yadi dosh`. Preserve each scalar success signature. Implement shared compiler-emitted failure support before wiring library guards; do not add OS-printing calls to core-layer code. Do not pretend the named library-failure primitive already exists. No external runtime dependency is required.
- **Status** means keep the existing explicit status convention and no automatic printing. A caller may handle failure silently. Listed messages for those rows are exact catalog text for an opt-in reporting adapter, not extra mandatory output. An adapter is a new facility to implement if exposed; it is not an existing API claimed by this report.
- Keep declared argument representations and caller storage obligations. These checks do not prove arbitrary pointers are valid. No automatic conversion from a packed string to a cell array; no automatic allocation of an ok cell. Document non-overlap where required, and do not dismiss an existing valid caller by inventing a precondition silently.
- Check domain first, then representability. Leave argument evaluation order unchanged and evaluate each argument once. Preserve earlier side effects; refusal is not a transaction over the whole program.

## WS1 — complete implementation matrix

The JSON companion is the machine-readable source of the sixteen rows, diagnostic literals and acceptance witnesses: [ROUND-189-IMPLEMENTATION-MATRIX.json](ROUND-189-IMPLEMENTATION-MATRIX.json).

| # | Module.function | Mandatory refusal / behavior | Work | Phase and failure channel | Code |
|---:|---|---|---|---|---|
| 1 | ganit.dvigun | n < -4611686018427387904 or n > 4611686018427387903 | two bounds checks | Runtime: fatal | E_ATIPRAVAH |
| 2 | ganit.trigun | n < -3074457345618258602 or n > 3074457345618258602 | two bounds checks | Runtime: fatal | E_ATIPRAVAH |
| 3 | ganit.vardh | n == 9223372036854775807 | one guard | Runtime: fatal | E_ATIPRAVAH |
| 4 | ganit.nirapeksh_mulya | n == -9223372036854775808 | one guard before negation | Runtime: fatal | E_PHALA_SEEMA |
| 5 | ganit.mahattam_samapavartak | mathematical gcd magnitude == 9223372036854775808 | MIN-aware gcd rewrite | Runtime: fatal | E_PHALA_SEEMA |
| 6 | ank.viparyay_ank | sign-preserving reversed decimal integer outside [MIN,MAX] | checked digit-accumulation rewrite | Runtime: fatal | E_PHALA_SEEMA |
| 7 | ganita.ganita_nirapeksh | n == -9223372036854775808 | one guard before negation | Runtime: fatal | E_PHALA_SEEMA |
| 8 | ganita.brahmagupta_kshetr | invalid geometric domain; or floor(exact area) > MAX | exact formula/domain rewrite | Runtime: fatal | E_ATIPRAVAH |
| 9 | aadhar.brihat_ank_se | invalid descriptor/digit/base; or nonzero carry past n decimal digits | carry detection and failure-state rewrite | Runtime: return 0, no automatic output; clear valid destination on conversion failure | E_PHALA_SEEMA |
| 10 | brihat.brihat_ank_tak_laghu | non-decimal digit/negative length; or nonnegative value exceeds MAX | guard each multiply/add | Runtime: fatal | E_PHALA_SEEMA |
| 11 | patra.patra_asti | OS cannot determine existence of the followed path target (permission, loop, I/O or other non-absence error) | OS metadata-query rewrite | Runtime: fatal; 0 only for ENOENT/ENOTDIR equivalents, 1 on query success | E_PATRA_PARIKSHA |
| 12 | sadhan.yog_seema | none for valid i64 endpoints: exact sum when it fits, final-result saturation otherwise | wide/exact range-sum rewrite | Runtime: no error; retain saturating result | none |
| 13 | samanvaya.adish_gunan | logical input lengths differ | one length comparison, deliberate contract migration | Runtime: fatal | E_AKARA_ASAMYA |
| 14 | sankhyiki.bindu_gunan | logical input lengths differ | one length comparison, deliberate contract migration | Runtime: fatal | E_AKARA_ASAMYA |
| 15 | suchi.suchi_shreni | mil_shreni returns -1 (scratch allocation/size refusal) | capture status and branch; define helper success return | Runtime: return 0, no automatic output; preserve list on current pre-sort allocation failure | E_SMRITI_ABHAVA |
| 16 | vakyank.varna_tak_dashm | malformed grammar or mathematical magnitude exceeds finite binary64; leading zeros alone NEVER fail | significant-digit/exponent parser rewrite | Runtime: return 0.0 and ok[0]=0, no automatic output; valid underflow keeps ok=1 | E_PHALA_SEEMA |
## Details needed to implement the rows correctly

**1–3, doubling/tripling/increment:** use both signed bounds shown in the table. The brief's `n > MAX/2` alone misses negative overflow. These are small guards, not literally one comparison in every case. Successful results and arities stay unchanged.

**4, 5, 7, magnitude/gcd:** abs(MIN) has mathematical magnitude 2^63, which signed i64 cannot represent. It is an overflow/representability failure in the mathematical sense; the separate E_PHALA_SEEMA wording explains it without suggesting a multiplication occurred. For gcd, rejection occurs exactly for `(MIN,0)`, `(0,MIN)` and `(MIN,MIN)` among signed-i64 inputs. Other MIN cases must work. One implementable approach is Euclid on non-positive operands: normalize positive inputs by negation (safe), keep MIN negative, and special-case divisor -1 before remainder; at termination reject result MIN, otherwise negate the non-positive gcd. `(0,0)` remains 0. Do not negate MIN first or divide MIN by -1 merely to discover the answer.

**6, reversal:** accumulate in a non-positive temporary, checking each base-10 step against the chosen final sign's negative limit. Positive output limit is -MAX; negative output limit is MIN. Before the step, reject if accumulator is below the truncating limit/10, or equal with next digit larger than the allowed last digit (7 for positive, 8 for negative). Then `acc = acc*10-digit` stays representable. Extract digit magnitudes from non-positive input remainders without forming abs(MIN). Leading zeros in the reversed result disappear as today. Do not reject MIN categorically: its reverse fits.

**8, area:** accept either four strictly positive sides of a cyclic quadrilateral with longest side <= sum of others, or `d=0` and three strictly positive triangle sides with the corresponding inequality. Equality is degenerate and returns 0; negative sides, zero in other positions, or longest side exceeding the others are E_MULYA_AYOGYA. The sides determine the cyclic-quadrilateral area, not the area of an arbitrary quadrilateral. Compute integer floor only at the end. With `T=a+b+c+d`, form `P=(T-2a)(T-2b)(T-2c)(T-2d)` exactly and return `isqrt(P)//4`. Widened/multiword or bigint arithmetic is required for the full valid input domain; a fixed five-qword unsigned temporary is ample for these i64-side products, but the multiplication and square-root implementation must be verified. Refuse E_ATIPRAVAH only when the final integer area exceeds MAX, not just when a narrow intermediate would overflow. This is a rewrite, not a one-line guard or a binary64 approximation near integer-floor boundaries.

**9, digit parser:** descriptors require count>=0, n>0, base in 2..16, valid source/destination storage and non-overlap. Reject invalid descriptors before destination writes. For valid descriptors, initialize the n-digit destination to zero; count=0 is successful zero. Validate each digit in `[0,base)`; after each multiply/add across all n decimal digits, a nonzero carry means insufficient representation capacity. On invalid digit or overflow, clear all n destination digits and return 0; on success return 1. This deliberately defines failed output as zero, not “unchanged.” Preserve the failure channel, including invalid-base failure. No scratch allocation is needed for this failure-state choice. Capacity failure is E_PHALA_SEEMA in the optional reporter; malformed descriptors/digits use E_MULYA_AYOGYA. Validate memory sizes without overflow; caller memory validity cannot be inferred from an integer address.

**10, bigint-to-scalar:** n>=0; digits stored least-significant first as the module already uses. Scan from the most-significant digit; require each digit in 0..9. For nonnegative accumulator r and digit d, refuse if `r > MAX/10` or `r == MAX/10 && d > MAX%10`, then compute `r*10+d`. n=0 returns 0; extra leading zero digits are allowed. Invalid digit/negative n uses E_MULYA_AYOGYA; capacity overflow uses E_PHALA_SEEMA. No wrapped or sentinel result is published.

**11, existence:** choose **followed-target existence**, not “can open read-only” and not “is a regular file.” Use an OS metadata query with target-specific error translation. Return 1 for query success, including directories and symlinks resolving to an existing target; return 0 only for an absent target or a non-directory path component (ENOENT/ENOTDIR equivalents). Permission denial, symlink loops, I/O faults, unsupported backend and other indeterminate results are fatal E_PATRA_PARIKSHA. A dangling symlink yields 0 under this explicit followed-target contract; a future path-entry/lstat predicate is a different API. Avoid opening device/FIFO contents as an existence test. This requires OS backend work; dvaram alone cannot implement the distinction. Query success is only an observation at that instant, never a guarantee a subsequent open will succeed. For callers needing recovery, add a separate status-bearing query API rather than quietly introduce -1 into this boolean API.

**12, range sum:** no new refusal for valid signed-i64 endpoints. If end<start, return 0. Otherwise compute the exact mathematical sum with widened arithmetic and clamp only that final result into `[MIN,MAX]`. Halve an even factor before multiplication where helpful, but do not saturate `start+end` before division. Preserve negative sums, full-range `(MIN,MAX) -> MIN`, and every fitting singleton. This already has an explicit saturating contract, so forcing E_ATIPRAVAH here would contradict the accepted policy's allowance for declared saturation. Memory/internal implementation failure must not be mislabeled numeric overflow; prefer bounded multiword arithmetic for this function.

**13–14, float dots:** preserve typed `kosh dasham` parameters and dasham results. Check both logical lengths once; reject unequal lengths before element loads, then use the existing binary64 scalar loop. Equal empty inputs return +0.0. Self-aliasing of these read-only inputs is valid. No new overflow refusal is promised for binary64 arithmetic here; its documented non-finite/rounding behavior remains. This is an intentional change from prefix semantics: revise the mismatch teaching example and tests explicitly, preserving separate success cases. It does not replace the new three-argument integer builtin.

**15, sort:** capture mil_shreni's result. Make its successful exit explicitly return 0 (including n<2) and failure return -1, instead of depending on a fall-through return. suchi_shreni returns 0 on -1, else 1; valid list header/length/storage remain preconditions. Current scratch-size/allocation failures precede mutation, so failure preserves list contents. If a future algorithm can fail after mutation, it must restore the list or revise this guarantee before adoption. Do not print from this library routine; test allocation failure through controlled injection in the owner's test environment, not machine-wide memory exhaustion.

**16, decimal parser:** retain the existing grammar, sign, character-code-cell input and ok-cell convention. Leading zeros do not consume the significant-digit budget. All zeros still count as syntactically valid digits. Zeros after the first significant digit do consume it. Fractional leading zeros still decrement the decimal exponent; integer leading zeros do not increase it. Retain the documented at-most-18-significant-digit accumulation/truncation policy for this fix; it is not a correctly-rounded strtod implementation. Discarded integer tail digits adjust exponent, discarded fractional tail digits do not. Parse explicit exponents with bounded/saturating bookkeeping so huge exponent text cannot wrap; still validate all characters. Malformed input returns 0.0 with ok=0 (E_MULYA_AYOGYA if explicitly reported); finite-range overflow returns 0.0 with ok=0 (E_PHALA_SEEMA); valid extreme underflow returns signed/unsigned zero according to the documented sign policy with ok=1. An all-zero significand with a syntactically valid huge exponent remains zero, not overflow. The padded representation of 1 must return 1 with ok=1, not be refused.

## Exact diagnostic literals

These are proposed ASCII/Romanized Sanskrit strings with one trailing newline. Linguistic certification is **NOT RUN**; they are concrete implementable drafts, not quotes from current output. Prefix is the now-implemented `Sutram truti`. Attach actual file/line metadata outside the literal; do not fabricate call-site locations if only the library failure site is available. Failure messages must not themselves perform overflowing arithmetic.

For rows 9, 15 and 16 there is **no student-visible string by default**: their status channel is the contract. The strings below are for an explicitly requested diagnostic adapter. Requiring unconditional printing as well would change their composability and should not be hidden in a “one-line check.” Row 12 has no error string because final-result saturation is intentional.

**1. ganit.dvigun**

```text
Sutram truti [E_ATIPRAVAH]: dvigun: dvigunitam phalam purnanka-seemam atikramati; n -4611686018427387904 tah 4611686018427387903 paryantam bhavet.
```

**2. ganit.trigun**

```text
Sutram truti [E_ATIPRAVAH]: trigun: trigunitam phalam purnanka-seemam atikramati; n -3074457345618258602 tah 3074457345618258602 paryantam bhavet.
```

**3. ganit.vardh**

```text
Sutram truti [E_ATIPRAVAH]: vardh: ekena vardhitam phalam purnanka-seemam atikramati; n 9223372036854775807 tah nyunam bhavet.
```

**4. ganit.nirapeksh_mulya**

```text
Sutram truti [E_PHALA_SEEMA]: nirapeksh_mulya: nirapeksha-mulyam 9223372036854775808; purnankasya adhikatamam mulyam 9223372036854775807.
```

**5. ganit.mahattam_samapavartak**

```text
Sutram truti [E_PHALA_SEEMA]: mahattam_samapavartak: mahattama-samapavartakah 9223372036854775808; purnankasya adhikatamam mulyam 9223372036854775807.
```

**6. ank.viparyay_ank**

```text
Sutram truti [E_PHALA_SEEMA]: viparyay_ank: viparita-ankasya mulyam purnanke na dharyate; seema -9223372036854775808 tah 9223372036854775807 paryantam.
```

**7. ganita.ganita_nirapeksh**

```text
Sutram truti [E_PHALA_SEEMA]: ganita_nirapeksh: nirapeksha-mulyam 9223372036854775808; purnankasya adhikatamam mulyam 9223372036854775807.
```

**8. ganita.brahmagupta_kshetr**

```text
Sutram truti [E_ATIPRAVAH]: brahmagupta_kshetr: kshetraphalam purnanka-seemam atikramati; adhikatamam mulyam 9223372036854775807.
```

**9. aadhar.brihat_ank_se**

```text
Sutram truti [E_PHALA_SEEMA]: brihat_ank_se: ankasya mulyam dattasu n ankasthaneshu na dharyate.
```

**10. brihat.brihat_ank_tak_laghu**

```text
Sutram truti [E_PHALA_SEEMA]: brihat_ank_tak_laghu: ankasya mulyam purnanke na dharyate; adhikatamam mulyam 9223372036854775807.
```

**11. patra.patra_asti**

```text
Sutram truti [E_PATRA_PARIKSHA]: patra_asti: patrasya astitvam nishchetum na shakyate; anumati-marga-avastham parikshatam.
```

**12. sadhan.yog_seema**

No error string: this operation retains explicit final-result saturation.

**13. samanvaya.adish_gunan**

```text
Sutram truti [E_AKARA_ASAMYA]: adish_gunan: dvi-koshayoh dirghate asamane; samane dirghate apekshite.
```

**14. sankhyiki.bindu_gunan**

```text
Sutram truti [E_AKARA_ASAMYA]: bindu_gunan: dvi-koshayoh dirghate asamane; samane dirghate apekshite.
```

**15. suchi.suchi_shreni**

```text
Sutram truti [E_SMRITI_ABHAVA]: suchi_shreni: shrenikaranaya avashyaka smritih na labdha; suchi aparivartita.
```

**16. vakyank.varna_tak_dashm**

```text
Sutram truti [E_PHALA_SEEMA]: varna_tak_dashm: dashama-mulyam dharana-seemam atikramati.
```

For additional invalid-input branches, the exact literals are:

```text
Sutram truti [E_MULYA_AYOGYA]: brahmagupta_kshetr: dattam mulyam ayogyam; kriyayah niyaman parikshatam.
Sutram truti [E_MULYA_AYOGYA]: brihat_ank_se: dattam mulyam ayogyam; kriyayah niyaman parikshatam.
Sutram truti [E_MULYA_AYOGYA]: brihat_ank_tak_laghu: dattam mulyam ayogyam; kriyayah niyaman parikshatam.
Sutram truti [E_MULYA_AYOGYA]: varna_tak_dashm: dattam mulyam ayogyam; kriyayah niyaman parikshatam.
```

The first/third are fatal; the second/fourth are opt-in status explanations. The corresponding function sections define exactly which input is invalid; the reporter may add operand/context fields without changing the diagnostic code.

## WS2 — six error families, not sixteen codes

| Code | Assignment | Status |
|---|---|---|
| E_ATIPRAVAH | Arithmetic result out of i64: #1/#2/#3 and final area in #8 | Existing code; runtime library use is a new emission path, not already implemented by its compile-time string. |
| E_PHALA_SEEMA | #4/#5/#7 magnitudes; #6/#10 representation conversion; #9 digit capacity; #16 finite float range | Proposed new result-representation limit family. Context names the destination limit. |
| E_MULYA_AYOGYA | Invalid geometry, digits/base/descriptors or decimal grammar in #8/#9/#10/#16 | Proposed new invalid-domain family. |
| E_PATRA_PARIKSHA | #11 indeterminate filesystem query | Proposed new OS query family; preserve underlying reason as metadata if exposed. |
| E_AKARA_ASAMYA | #13/#14 unequal vector lengths | Proposed new shape family. |
| E_SMRITI_ABHAVA | #15 scratch storage unavailable/size cannot be allocated | Proposed new resource family, not a string-specific allocation code. |

These are **one existing plus five proposed codes**. Rows with explicit status do not need to acquire a printed diagnostic or a new public integer error-code ABI merely because a catalog class exists. Add their reporter strings only with the reporting facility. Do not reuse E_VARTANI_SMRITI (string memory) for list sorting or E_PARSE (source syntax) for data parsing.

Abs(MIN) is a representability overflow, not a separate mathematical phenomenon. Giving it E_PHALA_SEEMA is an ergonomic diagnostic distinction: the message explains the unrepresentable positive value. The table is a chosen taxonomy, not proof that E_ATIPRAVAH would be mathematically false.

The brief's “55” is not a verified current native-code inventory. A fresh bounded scan of src/*.asm and src/**/*.inc, excluding generated r11_sandesh.inc, finds **48 distinct E_ tokens** at this base (R185 found 47 before E_RACHANA_GANIT). Optional/fixture/reference-tool distinctions still matter. None of the five proposed names occurs in that source set. This is an exact-spelling code collision check, not a guarantee every token is emitted in every build. Adding five codes does not authorize claiming a new total across different scopes.

## WS3 — exact reference paragraph

> `vitti` stores a signed 64-bit integer from -9223372036854775808 to 9223372036854775807. In the default compiler build, ordinary runtime `+` and `*` keep the low 64 bits of the result and interpret them as a signed value: for example, adding 1 to the maximum produces the minimum, and multiplying the maximum by 2 produces -2. This is wrapping, not a mathematical answer, and it can happen even when you did not intend it; plain runtime operators do not report it. Written integer literals and constant expressions outside the supported range may instead be rejected during compilation, and the optional trapping compiler configuration has different behavior. Mathematical library functions must follow their individual documented contracts—exact result or declared failure, or explicit saturation where specified—so use the checked/status form when your program must detect a failure and continue. Neither a function's Sanskrit name nor a zero return value by itself proves that the computation succeeded.

Do not say “as in C” for ordinary signed overflow. Publish this paragraph alongside the migration status: until the sixteen changes are accepted, it is a target library policy, not a claim that all current routines already enforce it.

## WS4 — R184 and R185 were delivered; exact receipts

Both were written to main and verified through the GitHub API before R186. They were not silently dropped.

| Work | Direct artifact | Delivery commit |
|---|---|---|
| R184 report | [ROUND-184-WHOLE-TREE-ENGLISH-AUDIT.md](ROUND-184-WHOLE-TREE-ENGLISH-AUDIT.md) | f1f91a014d65a74e16fe194f0342e469e921714e |
| R184 complete table, 531 rows | [ROUND-184-ENGLISH-TABLE.csv](ROUND-184-ENGLISH-TABLE.csv) | abef84fd7ffcbc4dfaa88d6ba81ace2435309486 |
| R184 location evidence, 2,251 occurrences | [ROUND-184-ENGLISH-INVENTORY.json](ROUND-184-ENGLISH-INVENTORY.json) | 38af997c3d62d5600dfa891a5238b34cf69e8bd0 |
| R185 error-handling/float-store review | [ROUND-185-ERROR-HANDLING-AND-MALA-REVIEW.md](ROUND-185-ERROR-HANDLING-AND-MALA-REVIEW.md) | e7c3a952e9be4fd8555f3d4773597f7034fd2a9d |
| R185 47-code phase inventory at its pinned base | [ROUND-185-CODE-PHASES.json](ROUND-185-CODE-PHASES.json) | 0241045eb4a5d91e9cc6967dd91b10ce633f7f45 |

R184 delivery is a counted lexical inventory and proposed vocabulary, not native-speaker approval or exhaustive compiler-message reachability proof. Those remaining limitations are written in its report. R185 delivers the requested design and corrects stale premises: native siddhi/dosh/prasar/handlers already exist; fatal E_ traps are not generally catchable; the recognized mala float-store path already converts exactly. Native verification and owner implementation decisions were not claimed complete. Historical reports retain their original source pins; they should not be overwritten to pretend their counts describe v294.

## Current-baseline caution and implementation boundaries

R113 has chosen a **three-argument wrapping integer dot**, not R186's proposed two-argument binary64 operation. Treat that as the current accepted source; this round does not withdraw it or silently reverse the implementation. The library float-dot rows remain separate APIs.

However, R113's rationale that no dasham array exists is contradicted by current `kosh dasham` support and the two typed library dot signatures. The new builtin's raw cell loop and explicit n do not make it a typed binary64 dot or a length-safe operation. Its doc contract must restrict it to integer-cell inputs with sufficient accessible storage. This note does not certify the new builtin or claim its overflow/bounds issues are fixed by the sixteen library changes.

Implementation sequence: (1) shared named failure path and catalog schema; (2) simple scalar guards plus gcd/reversal; (3) domain/algorithm rewrites and status propagation; (4) explicit dot/path contract migrations; (5) targeted tests/reference updates. Prioritize ordinary-input defects and false success from R188; the sequence denotes dependencies, not permission to postpone those bugs indefinitely.

The JSON lists independent acceptance cases for every row. Test exact boundary successes as well as refusals; injected resource failure; preserved/cleared output according to each contract; both default and optional trapping builds where claimed. Never approve by reproducing the old wrapped golden alone. Do not mass-record expectations. Preserve non-Sanskrit packs under the current freeze; the R114 exception authorized only the fixed prefix, not these new messages.

Performed here: current commit/source review, library unchanged check through GitHub compare, source-code-name census, specification/JSON generation, boundary algebra checks and delivery integrity verification. **Native compiler build, suite, guard, Windows and CI: NOT RUN — no toolchain used for this read-side assignment.** No production source, lib, tests, tools, docs or pack edits. No benchmark or native linguistic approval claimed.
