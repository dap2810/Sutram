# Sutram ROUND 145 — escape coverage, an enforceable K0 boundary, and the false-positive bar

**Date:** 30 October 2026. **Pinned main:** `e03f6dce87782910c1de389501e6c1c12f7c5f66`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-145.md`, blob `2328cb6d7c4920ed9fc01a8c6df9c64f46ad8b42`.
**Return:** `ChatGPT-to-Sarvam/ROUND-145-ESCAPE-COVERAGE-AND-K0-CONTRACT.md`.
**Observed implementation:** v268/R72. **Role:** read-side review and acceptance specification, not the Step 4 implementation. All R72 native measurements remain partner-reported. This review does not certify later concurrent commits.

## Answers first

1. **The current implementation is not yet the lower-depth escape checker described as Step 4.** It remembers names whose initializer or assignment is a direct `nirmmita(...)`, then rejects selected plain `nivartanam` expressions while a `mandapa` is open. It does not route allocation to scratch or rewind memory. Consequently, an accepted escape is currently a missing future-lifetime check, not by itself a demonstrated v268 use-after-rewind. Do not enable reuse on the strength of this recognizer. [R2,R3]
2. **New source-confirmed gaps:** the `nivartanam siddhi(...)` / `nivartanam dosh(...)` parser path does not invoke `r72_check_return`; the tracked-name list silently stops recording after 256 entries; and assigning a scalar to a previously tracked name does not clear that name. The first two can undermine future escape prevention; the last predicts an erroneous rejection of a safe scalar return. None was executed natively in this round. [R3-R5]
3. **K0 v1 must REFUSE unsupported constructs in the containing checked function, not quietly skip their analysis.** In particular, `kosh` and pointer-containing aggregates are outside initial K0. A list of strings therefore cannot be placed in an initial K0 checked block/function. Ordinary legacy code can retain its strings/vectors outside that boundary and pass numeric values to a separately checked helper. This is a restricted feature, not general collection memory safety. Actual v268 enforcement falls short of that intended contract. [R2,R6,R7]
4. **Proposed false-positive acceptance bar: zero erroneous rejections on a predeclared must-accept K0 corpus, with zero accepted must-refuse escape cases.** Start with 200 supported-safe, 100 unsafe/must-refuse and 40 safe-but-unsupported cases, separately labelled. This is a proposed 340-case qualification manifest, not executed results or a population-wide error-rate guarantee. Unsupported-safe rejection must be reported as a usability restriction, not hidden to manufacture a low false-positive number.
5. **An uncontrolled crash is NOT “fails safely.”** A compile rejection before a usable output is produced is fail-closed; a deliberately verified pre-access runtime check can also be fail-closed. A stale address may silently alias another object, crash, or appear to work. Its eventual behavior is not determined merely by the escape channel. There is no acceptable known escape bypass in the advertised checked subset in exchange for fewer warnings.

## State of the evidence: present code versus the intended feature

R145 says Step 3 is verified and Step 4 is starting. R72's return and the source agree on the narrower fact: parsing/scoping and a limited return prohibition exist; no scratch mark, routing or rewind exists yet. Its byte-equivalent pairs are evidence for that inert stage, not an executed reclamation guarantee. The reference page explicitly labels v268 inert, although its opening sentence describes buffers as gone on block exit. Put implementation status before that future-tense promise. [R1,R2,R3,R7]

I inspected the new helper and its declaration, assignment and return call sites. I did not inspect a completed Step 4 implementation; predicting a complete list of defects in that future implementation would be unsupported. The following provides an exact description of the inspected recognizer and a finite escape-channel checklist for the proposed subset. It is not an exhaustive proof about every raw-pointer Sutram program.

### The inspected return predicate

Ignoring diagnostic plumbing, its logic is:

```text
on entering mandapa:
    save tracked-name count; increment mandapa depth
on declaration or simple variable assignment:
    if depth > 0 AND RHS is directly AST_CALL(BN_NIRMRITA)
       AND count < 256:
        append the name's spelling to the table
on a PLAIN value-return while depth > 0:
    reject if expression is directly AST_CALL(BN_NIRMRITA)
    reject if expression is AST_VAR whose spelling appears in the table
    otherwise this helper permits the expression
on leaving mandapa:
    restore tracked-name count; decrement depth
```

This description follows `r72_parse_mandapa`, `r72_is_nirm`, `r72_note_alloc` and `r72_check_return`. There is no general expression provenance propagation, assignment kill, control-flow join, heap-content analysis or binding identity in this helper. The simple-assignment hook only calls it for `AST_VAR` destinations, not `AST_INDEX` or `AST_FIELD`. [R3,R4]

Crucially, the result-form return parser constructs `AST_RETURN` and returns before the plain-return path that invokes the helper. A tagged value is still a return channel and must not be omitted from a future whole-function pass. A later compiler layer might reject a particular program for another reason; this review establishes the missing hook, not a native end-to-end acceptance result. [R5]

## WS1 — escape channels and whether they fail closed

### Meaning of the classifications

- **FAILS SAFELY / refusal:** the relevant checker rejects before execution, with an explicit diagnostic and no successful artifact. It may still be an incorrect refusal of a valid program; safety and usability are separate scores.
- **SILENTLY WRONG risk / not fail-closed:** the inspected mechanism has no applicable prevention. After scratch rewind is enabled, the route can retain a stale address and permit silent reuse. This is not a promise that every instance will be silent rather than crash.
- **UNKNOWN end-to-end:** other parser/type checks or later code may reject a concrete instance; native evidence is absent. Unknown is not PASS.

No new reuse-related fault follows solely from block exit in the inert v268 configuration. The risk column below is about activating scratch lifetimes without closing the corresponding route. The table includes all major channels to be dispositioned for this review, not a theorem that these fifteen rows enumerate every possible implementation defect.

| ID | Escape or analysis shape | What the inspected v268 helper establishes | Classification if relied on when rewind is enabled; required K0 treatment |
|---|---|---|---|
| E01 | Plain direct return of `nirmmita(n)` or a recorded allocation name while its block is open | The helper explicitly refuses; R72 reports three matching negative tests. | **FAILS SAFELY for those recognized forms**, subject to intact table/state and actual diagnostic execution. Keep direct negative controls. |
| E02 | Local alias: `q = p`, then return or store `q` | The alias assignment is not recorded unless its RHS itself is a direct allocator call. | **SILENTLY WRONG risk.** Preserve value origins through every supported alias operation; reject unknown provenance. |
| E03 | Expression wrapper/interior pointer: return `p + 0`, a supported offset, or a conditional selecting `p` | A non-`AST_VAR`, non-direct-allocation root passes this helper. | **SILENTLY WRONG risk.** Traverse expression meaning; retain origin/extent through permitted operations, reject unsupported pointer arithmetic. A scalar comparison result is not itself an escaping pointer. |
| E04 | Assign into an outer local or global, then return/use it after the block | A direct variable assignment can be noted while the block is open, but no store-depth rejection is performed; after closing, this return helper is inactive. | **SILENTLY WRONG risk.** Check the assignment when it happens, including global destinations, and retain facts across later statements. |
| E05 | Store a pointer in a raw cell, fixed array or structure member, then load it later | `AST_INDEX`/`AST_FIELD` destinations bypass the simple-variable tracking hook; return of an indexed/member expression is not a recorded-name check. | **SILENTLY WRONG risk.** Initial numeric-only K0 must reject pointer-valued stores and unsupported aggregates, not assume a load is numeric because it uses brackets. |
| E06 | `kosh` append/storage, including `kosh_enqueue` aliases or a collection declared outside the braces | No K0 whole-function prohibition is present in the inspected block helper or collection declaration path. R72 explicitly says general container analysis is future work. | **SILENTLY WRONG risk if admitted to checked scratch code.** Refuse unsupported collection declarations, parameters, aliases and operations throughout the checked function. Do not equate documented “not supported” with an implemented rejection. |
| E07 | Raw store/copy/serialization hides pointer bits: `likh8`, memory copying, byte writes | No effect summary or memory-content tracking is supplied by the name recognizer. | **SILENTLY WRONG risk.** Whitelist operations with verified numeric-only effects; reject raw opaque storage/round trips. Caller-declared length alone does not prove the contents are pointer-free. |
| E08 | Direct helper retains pointer in a global/caller-owned object, or returns it; helper may itself return only a scalar | The return recognizer does not analyze a helper's retention effects. | **SILENTLY WRONG risk.** Require verified non-retention and valid-access summaries, or reject the call in the checked subset. A documented convention alone is not enforcement. |
| E09 | Indirect calls, callbacks, FFI, inline assembly or an opaque callee | No corresponding interprocedural/foreign effect proof is established by the inspected source. | **Not fail-closed if admitted.** Initially refuse these unsupported forms in checked functions; any eventual unchecked boundary must be explicit and outside the checked guarantee. Do not claim future closures/async already exist. |
| E10 | `nivartanam siddhi(p)` / `nivartanam dosh(p)`; related propagation paths | The tagged-return parser does not call the plain-return helper. `prasar` needs its own full exit/effect audit; that was not rerun here. | **SILENTLY WRONG risk / missing hook confirmed.** Analyze every return payload and implicit return path, or explicitly refuse unsupported result/propagation forms. No arbitrary pointer-bearing result is K0-safe merely because it has a status tag. |
| E11 | Different branch outcomes, short-circuit expressions, loop-carried aliases or stale facts at a join | The table is populated while parsing, not by a demonstrated control-flow dataflow analysis. | **Not fail-closed for the general case.** Join possible origins conservatively; preserve early-exit distinctions; iterate loop facts to a stable result or reject unsupported loops. Do not clear taint because one branch assigns a scalar. |
| E12 | Inner region retained by an outer local; pointer retained across repeated entries at the same nesting depth | Restoring the name count at block exit forgets inner additions; the table does not establish region ancestry/instance lifetime. | **SILENTLY WRONG risk.** Check destination lifetime against allocation origin, not just spelling or destination declaration depth; reject escaping values before the inner lifetime ends. Equal depth does not make unrelated lifetimes interchangeable. |
| E13 | Address converted/encoded as an integer, arithmetic/bitwise operations, then reconstructed as a pointer | No complete origin-preserving treatment of those operations exists in this helper. | **SILENTLY WRONG risk.** Reject unsupported address reconstruction or conservatively retain pointer-derived classification. Legitimate pointer-to-Boolean comparisons need their own scalar rule, not blanket taint. |
| E14 | Analysis capacity exhausted | `cmp rdx,256; jae .r` skips a new record without a failure diagnostic; duplicate recorded names also consume entries. | **Fail-open, not fail-safe.** Capacity/resource failure must reject the checked compilation. Whether a chosen saturation fixture reaches this path must be measured rather than assumed. |
| E15 | Wrong binding identity, unsupported AST kind, wrong function-context state or source-body membership | Names are compared as strings; this helper does not establish complete resolved-binding/AST coverage. | **UNKNOWN/not certified.** Use stable binding identities and per-function/region state; refuse unhandled nodes. A checked tree with incorrectly parsed scope still cannot justify the intended source guarantee. |

### Four high-value concrete follow-ups from the actual source

**A. Alias bypass — source-predicted; not compiled here.**

```sutram
prakriya alias_demo()
    mandapa
        vitti p = nirmmita(8)
        vitti q = p
        nivartanam q
```

The direct allocation records `p`, not `q`. This is also one of R72's explicitly acknowledged omissions. Under current persistent allocation it is not a new use-after-rewind; under later scratch reuse it must be rejected. [R2,R3]

**B. Scalar reassignment — a predicted false positive, not a harmless test omission.**

```sutram
prakriya scalar_demo()
    mandapa
        vitti p = nirmmita(8)
        p = 7
        nivartanam p
```

The return value is a scalar. The inspected recorder does nothing for `p = 7`, leaving the old name in the table, so the helper predicts refusal. Correct value tracking needs a strong update for an unaliased local binding; this does not clear the taint of a different alias that still holds the old address. Put this case in the promised must-accept subset after its policy is frozen. [R3,R4]

**C. Result-form return — source-confirmed hook bypass; full compilation remains to be tested.**

```sutram
prakriya result_demo()
    mandapa
        vitti p = nirmmita(8)
        nivartanam siddhi(p)
```

`.r25_ret_phal` creates the return directly, without calling `r72_check_return`. This needs a minimal caller using the supported result convention, and a corresponding scalar-result positive, to distinguish escape refusal from an unrelated syntax/type failure. `dosh` follows the same parser branch, but its valid payload domain must be respected in the fixture. [R5]

**D. Capacity exhaustion — do not call “silent” an acceptable checker outcome.**

The comment on the 256-entry boundary literally says the check is silent. The recorder appends records without deduplication. A useful proposed calibration is two ordinary branch bodies containing many repeated direct allocation assignments to the same existing local, followed by allocation/return of a fresh name. This can pressure the tracking table without requiring 257 distinct bindings or 257 direct statements in one block. Establish actual parser/code-buffer limits and reachability natively; this report does not assert that such a full program was accepted. The fix criterion is unconditional: an exhausted analysis must not silently permit unchecked code. [R3]

### What the future depth check must know

A comparison of two depth integers is only useful if the value's origin and the destination object's lifetime are already correct. Track at least binding identity/declaration scope, value kind, possible reference origins, destination object identity/lifetime, numeric-buffer content restrictions, extent/null facts and verified call effects. Retain branch/loop joins. A scalar local declared inside a block can be assigned outward; a pointer to an inner block cannot be laundered by assigning it to an inner alias of an outer object.

A local flow-sensitive strong update is appropriate for `p = 7`; blindly “untainting” all aliases or treating every syntactic assignment as unconditional is not. Initial K0 can avoid general heap analysis by banning pointer-valued buffer contents and unsupported container/call forms. That is the point of restricting the subset, not a claim that those general problems have been solved.

For a complete disposition, enumerate every admitted expression/statement kind, builtin effect and exit form in a manifest. Every form must be either **checked by a stated rule** or **rejected**. Default/unknown cannot mean clean scalar. This is achievable coverage for a closed subset; an unrestricted complete escape classifier is not established by this round's code or tests.

## WS2 — refuse, not silently decline to check

### The v1 contract I recommend keeping

> A function containing a checked `mandapa` is accepted only if the whole function belongs to the initial K0 subset. Unsupported `kosh` values/operations, pointer-containing aggregates and unverified effects are compile errors in that function. Acceptance is not an advisory “best effort” analysis.

“Whole function” includes its signature and relevant declarations/uses before and after the block, not only the indented body. A vector parameter disguised as a raw integer/pointer must not become admissible through an unchecked call boundary. Unknown incoming reference origin/effects require rejection or an independently verified interface contract.

An ordinary function without a checked block remains legacy code; it is not made memory-safe by calling a checked helper. It can retain its list of strings and call a separate helper with supported numeric inputs. Conversely, the helper cannot call arbitrary legacy pointer-retaining code and continue to claim checked safety. Initial cross-function boundaries should be deliberately narrow.

**What actually ships at this pin:** the v268 source's `.ps_kosh` parser constructs the ordinary collection declaration, and the inspected R72 mechanism supplies no whole-function K0 gate. R72 reports only the direct-return rule. I therefore do not claim that v268 already implements the above restriction. A complete production-path/native rejection test remains required. [R2,R3,R6]

### Can a programmer put a list of strings in the block?

**Not in initial checked K0, when “list of strings” means a growable collection or pointer-containing aggregate.** The list's elements are references whose lifetimes require more than numeric-buffer checking. Allocating the list itself inside the block does not prove that its references cannot escape through a return, caller object, helper or alias.

Keep such a list in the ordinary part of the program, or propose a later explicitly specified reference-aware subset. A packed pointer-free representation using fixed numeric storage is a different design, not an automatic exemption for arbitrary strings, variable-length encodings or dynamic indexing. Only already-approved operations and bounds are accepted. Do not promise this alternative is supported without its own contract and tests.

This limitation is intentional and substantial. Report it as a scope/usability limit; do not describe it as a false alarm about a dangerous program. The future language may support safe string lists, but that is not what the current K0 commitment establishes.

### Distinct diagnostic meanings

Keep separate explanations for:

- **An escape violation:** a reference may outlive its allowed region.
- **An unsupported K0 construct/effect:** the subset does not admit this feature; its use is not proof the program is inherently unsafe.
- **An analysis limit/internal failure:** the compiler could not complete the check; compilation fails closed.

These are proposed diagnostic categories, not new implemented message IDs or language-pack edits. Existing `E_SCRATCH_ESCAPE` should not misleadingly explain every unsupported safe vector program as a demonstrated escape. Sanskrit remains the active diagnostic language; frozen packs are unchanged.

### Activating allocation reuse is a separate gate

Do not change lexical `nirmmita` routing or start rewinding after only adding a lower-depth assignment check. Require coverage of alias/expression/store/call/return channels, all cleanup exits, analysis failure, parser scope fidelity and backend preservation first. A word accepted by the parser is not a working memory-safety boundary. The current inert-stage tests must be labelled as such and cannot establish these later guarantees.

The reference's promise that “nothing you write changes then” is too broad if v268 currently accepts alias escapes or unsupported constructs that the future checker must reject. Either keep this stage explicitly experimental or document that future checked activation can reject currently accepted inert programs. Do not promise compatibility for programs that violate the coming lifetime contract. [R7]

## WS3 — a numerical false-positive bar and a method

### Two objectives, not a trade permitting known unsoundness

The brief's statement that refusing valid programs is worse than missing unsafe ones is not an acceptable general rule for a feature sold as checked lifetime safety. Wrong refusals harm usability and are compiler defects inside the promised accepted subset. Wrong acceptance can invalidate the advertised safety guarantee. Fix both, but do not lower the rejection rate by quietly accepting an unanalysed escape.

A conservative subset will reject some programs that are safe in the full language. That is an expressiveness restriction, not a reason to label every rejection an escape or to hide these users from measurement. The specification must freeze its **must-accept** and **must-reject** boundaries before testing, not redefine them after each failure.

### Proposed release numbers

| Independently labelled set | Initial count | Required result for the claimed profile |
|---|---:|---|
| Supported, safe, MUST ACCEPT K0 programs | **200** | **200/200 accepted and correct; 0 erroneous rejections (0% observed).** A crash, timeout or wrong result also fails qualification. |
| Unsafe escape / MUST REFUSE programs | **100** | **100/100 rejected for the intended relevant rule; 0 unexpected acceptances.** A syntax error in an invalid fixture is not evidence that escape checking worked. |
| Safe in legacy semantics but expressly outside initial K0 | **40** | **40/40 refused as unsupported in the checked form**, not silently accepted as unchecked. Record these restrictions separately. |
| Same supported legacy sources without checked blocks | Existing pinned regression manifest | **Zero unexpected new rejections or semantic differences** from checker activation. Unsupported checked code is not a reason to break ordinary legacy code. |

**340 = 200 + 100 + 40 proposed primary cases. None was executed here.** These are acceptance targets for an initial manifest, not a claim that finite testing proves soundness or that the counts are a measured false-positive rate. They can reuse suitable earlier K0 fixtures rather than being 340 additional hand-written examples.

The 200 safe cases should be **ten reviewed families with twenty semantic/input variants each**: scalar computations; inward/outward scalar assignments; fixed numeric-buffer initialization and stores; numeric loads and scalar returns; local reference aliases that remain within lifetime; pointer-to-scalar reassignment before return; nested regions exporting only scalars; supported branch joins; supported bounded loops; and supported scalar exit/cleanup paths. Freeze the precise acceptance rules first, including bounds/null preconditions. Native cleanup cases run only when the relevant lowering exists; inert builds cannot be scored as passed cleanup tests.

The 100 unsafe cases should cover **ten families with ten variations each**, drawn from the escape ledger: aliases/expressions; outside locals/globals; raw/aggregate stores; collection retention; opaque retention calls; alternate return/propagation; branch/loop-carried escapes; nested region retention; address encoding/recovery; and analysis saturation/unhandled forms. Some fail because K0 forbids the construct, others because an admitted construct carries an escaping value. Record the expected reason in advance and do not count the same source in two totals.

The 40 safe-but-unsupported cases should expose **eight restrictions with five examples each**: numeric `kosh`; string lists; reference-bearing structures; unsupported dynamic sizes; unsupported dynamic indexing; safe-but-unverified helper effects; indirect/foreign operations; and low-level address operations outside the accepted subset. Labels require independent review: a program is not deemed safe merely because it happened not to crash. Maintain paired ordinary-code controls where legal.

### Measurement protocol

1. **Freeze the candidate and contract.** Record source/binary hashes, target/profile, actual enabled scratch/checker features and approved K0 acceptance rules. Current v268's limited recognizer is not a qualified K0 candidate.
2. **Label independently.** Two reviewers examine the source structure, value origins, lifetime, bounds, allowed effects and expected diagnostic category. Disputed labels remain unresolved and block claims about that row; do not silently remove them from a published denominator. Do not derive expected acceptance from the checker being tested.
3. **Separate development and holdout variants.** For each family, reserve variants before implementation tuning. Publish their actual role and counts; a hand-picked regression corpus is not an independent random sample of all future user programs.
4. **Run both acceptance and semantics.** For a positive, require successful compilation, correct result/effects and applicable cleanup behavior. For a negative, require the intended refusal and no runnable success artifact. For the inert stage, report analysis-only findings without claiming release/reuse verification.
5. **Calibrate failure handling.** The stale-name scalar-return case must be a positive when admitted by the frozen K0 policy; alias and tagged-return escapes must not pass. Force a checker-table limit and an unknown-node condition. A missing case, stale executable, crashed checker, timeout or malformed result must fail the top-level gate.
6. **Report disjoint rates.** `FP_supported = wrongly rejected must-accept cases / all must-accept cases`; `unsafe_acceptance = accepted must-refuse cases / all must-refuse cases`; and `safe_restriction_rejection = refused safe-but-unsupported cases / that separate set`. Preserve infrastructure failures separately while still failing qualification. Do not blend these into a flattering overall accuracy score.
7. **Do not overstate 0%.** Zero out of 200 establishes zero observed errors on that declared corpus. It does not establish a true universal false-positive rate, a confidence interval without a sampling model, or absence of untested escapes. Report real user rejection/friction separately as the feature is evaluated.

Thus my number is **0% observed erroneous rejection on the frozen promised subset**, not “at most X% of arbitrary safe Sutram programs will be rejected.” The latter requires a declared workload population and measurements that do not exist in this review. Initially string lists and vectors have a 100% restriction rejection rate inside K0 by design; hiding that fact would make the 0% figure misleading.

### Price: what is and is not covered

For the proposed **test/evidence harness**, budget approximately **200–350 Python/manifest lines** for reviewed templates/adapters, **180–300** for bounded execution/structured oracles, and **40–100** for inventory/mutation integration: **420–750 lines**, excluding existing reusable infrastructure. These are estimates for an authorized implementer, not measured work, a source patch or a delivery-time promise.

The checker itself is separate work. Direct tagged-return hooks, fail-closed capacity handling and scalar strong updates are small local tasks compared with complete alias/branch/loop/effect handling. I do not price the whole missing Step 4 as a few extra name comparisons. A credible implementation estimate needs its finalized accepted AST whitelist, call policy and bounds/null model; none should be silently removed to meet the test-harness budget. The prior K0 design estimates remain planning context, not proof that this implementation is complete.

## Immediate dispositions for Sarvam

- **Keep v268 described as inert plus a limited return recognizer.** No new use-after-rewind is claimed from this read-side review.
- **Close the source-confirmed tagged-return, stale-name and table-limit issues before treating the recognizer as a safety checker.** Verify concrete acceptance/refusal programs, including a safe scalar companion for each negative.
- **Freeze K0 as mandatory rejection of unsupported constructs in the containing checked function.** Do not provide an implicit unchecked fallback under the same success/safety label.
- **Enable scratch reuse only with the complete intended boundary and cleanup contract.** Acceptance of a pointer-bearing `kosh` or string list is not compatible with the initial numeric-only guarantee.
- **Publish the denominators and scope of the false-positive claim.** The specified 340-case plan is a proposal; all native outcomes remain NOT RUN in this review.

## Evidence ledger and execution status

All repository reads used the pinned main unless an explicit historical commit is named.

- **R1:** `Sarvam-to-ChatGPT/ROUND-145.md`, `2328cb6d7c4920ed9fc01a8c6df9c64f46ad8b42` — three questions, reported Step 3 status and proposed Step 4.
- **R2:** `Claude-to-Sarvam/R72-00-MANDAPA-INERT.md`, `8c3cc3fc2567379067a5e5f8a83e9246e94556f7` — reported native results, inert behavior, limited return check and admitted omissions. Historical implementation commit inspected: `ec792699c70363483611a691ab9b7faa4c012dd1`.
- **R3:** `src/sutram_compiler.asm:7410-7515`, blob `ac7194e5ac490b60b1f673d7b623af06b549c1df` — complete R72 helper logic, table limit, depth/count restoration and name-based return recognition.
- **R4:** same compiler blob, `9165-9205` and `10220-10290` — declaration/simple-variable assignment tracking, absence of a non-allocation kill in the recorder, indexed/member destinations outside that hook.
- **R5:** same compiler blob, `9980-10085` — result-form returns versus the plain-return path. The result path constructs AST_RETURN without the R72 call; no native full-program test performed.
- **R6:** same compiler blob, `9203-9280` — ordinary kosh declaration parser, with no R72/K0 whole-function rejection in that path. This targeted read is not a complete compiler audit.
- **R7:** `docs/LANGUAGE-REFERENCE.md:690-860`, `68257579cb0cb0dae8436a1b026f05ec13fa57b2` — section 19's intended scope, inert status and future compatibility wording. The fuller unrelated multilingual reference section was not used as evidence of K0 enforcement.
- **R8:** `tests/r72_mandapa/test_mandapa.py`, `d23b78648520da596b97dff2475382c7d04d9d0d` — current pair/refusal/allowed test organization. I read it but did not run it. Equality of pairs is not an independent oracle for all lifetime behaviors.
- **R9:** `Sarvam-to-ChatGPT/READ-FIRST.md`, `583fbbcbde15569d0ff32aa0e2a7a8d2d743ee34`; `LANGUAGE-PRIORITY.md`, `64682919a70fa1b79e415bc879aee9cad07582ad` — Sanskrit-only active work; frozen packs remain unchanged.
- **R10:** R144 return in the conversation and verified latest return-folder commit `c48ae29bf1973c21791255e2d88884feb847d674` — previous prospective inert-stage/whole-function scope recommendations. Those recommendations are not evidence of present implementation.

**Performed here:** connected pinned-source reads; four small local Python checks modelling the inspected recognition predicate (stale name, missing alias, non-variable expression root, saturated table); arithmetic for the proposed 340-case manifest. The model is illustrative and does not execute the actual parser or verify a whole source program. Conclusions marked source-predicted remain unrun.

**NOT RUN — read-side round; no native toolchain invoked:** v268 or later builds, candidate snippets, escape/refusal regressions, scratch routing/reuse, checker saturation reachability, cleanup, canaries, Linux/PE/Windows/Wine execution, suites/proofs, benchmarks and release qualification. No population false-positive rate was measured. No complete new whole-tree or future-Step-4 audit is claimed.

**NOT APPLIED:** compiler, library, examples, tests, tools, canonical docs, language packs, workflows, Windows or backups. Only this Markdown handoff is added under `ChatGPT-to-Sarvam/`; verify full readback and single-file commit scope, then stop after Round 145.
