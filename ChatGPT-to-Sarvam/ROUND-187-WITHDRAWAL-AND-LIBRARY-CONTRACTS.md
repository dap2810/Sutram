# R187 — reserve withdrawn builtin names; reject their use explicitly

Base: `51eb82669dbcbcf28e1d434775299c47815ccd8a`, compiler v292. 2026-11-03. Read-side design only. The compiler, libraries, examples and tests inspected locally are unchanged from the R184 source base, as verified by the GitHub comparison.

**Choose a reserved, non-callable builtin entry for `sankhya_bindu` and every alias of its builtin identity.** Recognize the name and refuse it at compile time with a specific withdrawal diagnostic. Do not retain the broken emitter as a callable compatibility path. A later repair is a separate acceptance decision, not a reason to keep the current behavior available.

## 1. Withdrawal semantics

| Choice | Consequence | Decision |
|---|---|---|
| Delete the names | Unknown-function errors obscure the reason and may allow user declarations to capture names intended for repair. | Reject. |
| Keep reserved entries, reject use | Clear explanation, stable identity, no accidental fallback or shadowing, no broken generated operation. | **Choose now.** |
| Repair before withdrawing | Desirable eventually, but depends on validating both representation and result ABI; it delays containment. | Separate future reactivation. |

A withdrawn entry is a **tombstone**, meaning a reserved name with no usable implementation. Its status is part of the builtin registry, keyed by BN_VECDOT, not a spelling blacklist. Both canonical `sankhya_bindu` and legacy `sankhya_dot` map to that identity and status. Keep alias lookup and name reservation; stop normal call lowering.

### Observable behavior

1. On semantic use of either name, fail compilation with nonzero compiler status and a stable diagnostic code. Proposed code: `E_BUILTIN_WITHDRAWN` (absent from inspected src/ and lang/; proposal only, not yet implemented).
2. Report original file, line and column, spelling used, canonical name, and that the operation is withdrawn because its current implementation is incorrect, pending validated repair. Sanskrit is the active user-facing wording; exact phrasing still needs linguistic review.
3. Give a qualified alternative: typed `bindu_gunan` from `sankhyiki` or `adish_gunan` from `samanvaya` can compute a binary64 dot, **but currently use the shorter input length**. Tell the user to check equal logical lengths when they require the R186 strict contract. Do not imply an automatic safe text replacement.
4. The withdrawal error takes priority over the legacy-name suggestion to “use sankhya_bindu.” Do not warn users to switch to another withdrawn name and then fail separately.
5. No output executable/object is successfully published, and no argument expression runs. On a failed build, do not run a stale output from an earlier build. Prefer transactional output publication; preserve an existing user file rather than deleting it merely because compilation failed.
6. Strings and comments mentioning the name are ordinary text. A user declaration trying to bind the reserved name is refused; a value reference/function address is also refused wherever such a form would otherwise be supported. Do not make unused declarations or dead code a way around withdrawal. If a malformed program fails syntax parsing first, it need not produce the withdrawal diagnostic.
7. Apply the rule to batch compile, check-only, REPL, ELF, PE and object/separate compilation. Diagnose before optimization removes dead calls. The compiler-side backstop should also refuse any residual withdrawn builtin node before machine-code emission.
8. Existing already-built binaries retain their old behavior: a source compiler change cannot retroactively fix them. Prebuilt objects containing old machine code require rebuild/version discipline; do not claim the linker can detect every old call without suitable metadata.

Implementation placement: after spelling/pack canonicalization and builtin resolution, before ordinary call lowering. One shared status check should cover all emission routes. Keep a defensive failure at the old emitter entry until its removal can be verified. A table lookup alone is not a guarantee unless every call path consults it.

### Aliases and future reuse

Withdrawal attaches to semantics, not spelling: canonical name, old names, and any existing pack mappings to BN_VECDOT all refuse. Do not create or translate frozen-pack entries. Leaving their files unchanged is compatible with a central safety refusal, but any affected behavior change must be disclosed and tested by the implementation owner.

Reserve these names indefinitely for the **same conceptual operation**. Reactivation requires a reviewed contract, type/ABI implementation, accepted tests and release notes. Do not later reuse them for unrelated functionality. Preserve existing builtin numeric identities; do not renumber other entries merely because one is inactive.

Distinguish builtin and library withdrawal. Builtins occupy the language's reserved namespace. An ordinary library function should have a module-qualified withdrawn/export entry or a compile-time unavailable marker under the module system, not silently become a new global keyword. Where the current compiler cannot express an unavailable library export, that mechanism needs implementation; a wrapper returning 0 or -1 is not withdrawal. Never blanket-reserve arbitrary user function names.

## 2. Actual impact census

The attached [census](ROUND-187-WITHDRAWAL-CENSUS.json) scans ASCII identifier tokens after excluding Sutram comments and quoted strings. It includes a 306-definition inventory. The scan works on bytes because negative tests include deliberately invalid UTF-8. It is a bounded source-reference census, not analysis of dynamically generated code or external projects.

| Scope at this base | Count | References to either spelling |
|---|---:|---:|
| Immediate examples/*.sm | **299**, not the brief's 291 | 0 |
| Recursive examples/**/*.sm (includes immediate files) | 315 | 0 |
| Immediate lib/*.smlib | 24 files / **306 definitions** | 0 |
| Recursive tests/**/*.sm | 625 files | 0 |

Therefore withdrawal introduces no **direct call-site break** in these example/library sources. It does not prove the whole test suite is unaffected or that external users have no callers.

**A real generated-test dependency exists:** `tests/r111/test_vocabulary.py:44` puts the pair into PAIRS with `vitti dp = sankhya_dot(B, B)`. The test generates both spellings, for .bin and .exe, expecting successful compilation and byte identity. The new spelling is formed by replacement. A .sm-only search cannot find those generated calls.

Change this pair's test contract intentionally: both spellings must refuse with the same canonical withdrawal reason, no runnable output, and no misleading old-name warning. Retain success/byte-parity checks for the other 21 alias pairs. Do not simply delete the pair, re-record all goldens, or say withdrawal breaks zero programs without qualifying the census.

The published reference should mark both spellings withdrawn, explain the reason and point to the qualified alternative. Remove them from active-capability counts/completion suggestions while retaining discoverable withdrawal help. Teach the replacement only with its actual length/type contract. No production edits are included in this report.

Muse's R111 observation that example/library callers are absent is supported. Its broader “withdrawal is free” conclusion misses the Python-generated vocabulary test. R186's source-backed corrections about current kosh data pointers and raw representation construction still stand; neither is needed to justify withdrawal, which is already supported by the wrong input/result semantics.

## 3. Minimum library contract

**Yes: every prakriya definition should have a contract, including helpers.** Public APIs need user-facing documentation; helpers need internal contracts and visibility metadata, not automatically a public reference page. The current count of 306 is a definition count, not proof that all are public exports.

Use one structured contract record per module + function, pinned to its source and contract version. Generate reference prose from that record where practical. Avoid duplicating independently maintained comments, HTML and JSON as three competing authorities. Existing module-wide defaults may reduce repetition, but expand them explicitly for validation; absence must not mean “safe.”

| Minimum field | What it must state |
|---|---|
| Identity and status | Module, symbol, signature, visibility, active/deprecated/withdrawn status, canonical aliases, contract version and source fingerprint. |
| Inputs | Parameter order, declared compiler kind **and semantic kind**, units/representation, valid scalar domain, array element type and accessible logical length/capacity. Untyped pointer parameters are not automatically integers. |
| Result | Semantic and representation type; returned value's meaning; empty/singleton cases; whether callers may rely on the return at all; status/result ABI when used. |
| Preconditions | Shape, bounds, initialization, non-null/liveness, ownership and alias/overlap restrictions. Say which are compiler-enforced, runtime-checked, or caller obligations. |
| Postconditions and effects | What is computed, exactly which locations may change, whether inputs remain unchanged, allocation, I/O and deterministic/nondeterministic effects. |
| Failure | Every documented refusal/error/sentinel; phase; status code/value; whether state is unchanged or partly modified; cleanup ownership; unsupported-input policy. |
| Numeric/representation policy | Overflow (wrap/check/saturate), rounding/truncation, float order/tolerance/non-finite policy, bytes versus cells, encoding and terminators where applicable. “Not applicable” must be explicit. |
| Evidence | Normal and boundary witnesses, invalid-input/alias witnesses where relevant, independent oracle/property, tested target/base, result and review status. Missing evidence is NOT RUN, not success. |

Allocation/lifetime and OS/target constraints are essential for memory and file APIs. Complexity and stability guarantees should be added where users need them; not every helper needs a benchmark. Contracts describe accepted behavior, not aspirational behavior or whatever a golden happens to print.

### Failure is not one undifferentiated “error” field

A contract must separate compile-time rejection, runtime fatal diagnostics, native `siddhi`/`dosh` results, ordinary return sentinels, and caller-owned status cells. This uses the actual R185 findings: native handlers exist, but they do not catch every fatal E_ path and do not support dasham payloads in the current result ABI.

For invalid input, select an explicit policy:

- **Rejected**: specify phase and stable diagnostic/status.
- **Checked failure**: specify result/status and state after failure.
- **Caller obligation, unenforced**: document that violating it is outside the guaranteed domain; it is a safety gap, not a checked refusal. Do not deliberately execute unsafe out-of-contract witnesses in ordinary tests.

“Unknown” is allowed during inventory, but cannot count as complete. An unenforced non-overlap requirement must not be retroactively invented to dismiss a reported bug: owner acceptance, documentation and callers need review. Likewise a current wrong result cannot be blessed by rewriting the desired contract to match it.

### Worked records, in prose

**Current `sankhyiki.bindu_gunan`:** two declared `kosh dasham` inputs, borrowed read-only and live throughout the call; binary64 result; reads indices `[0,min(len(a),len(b)))`; no writes/allocation/I/O; equal input alias is valid; zero for an empty prefix; separate left-to-right scalar multiply/add with ordinary binary64 limitations. Length mismatch is **accepted as prefix behavior**, not refused. No native floating phal result is involved. Evidence should include unequal lengths explicitly. This describes the present API, not R186's stricter proposed builtin.

**`samanvaya.vivartana`:** float collections plus integer dimensions; transpose specified by `out[j*m+i] = old(a[i*n+j])`; initialized output logical length must cover m*n, with checked shape arithmetic. Alias policy needs explicit resolution because R186 demonstrated overwrite hazards. Mark it `needs_decision`; do not mark a schema-valid record as behaviorally accepted. Distinct-output tests do not establish in-place correctness.

**`patra.patra_likh_sarv`:** NUL-terminated path, byte pointer and nonnegative byte count; reads input bytes, creates/truncates a file, may produce partial external writes before failing; owns/closes its descriptor; return byte count versus -1. Closing-error treatment and target flag semantics need explicit resolution. Failure cannot promise to restore the original file, because truncation/writes are effects already performed.

## 4. Mechanical checking: useful, bounded claims

Build on existing checks rather than call a comment a proof:

1. **Inventory/schema gate:** exactly one record per definition, including helpers; explicit unknowns; no orphan/duplicate records; valid vocabulary, evidence paths and source fingerprints. Status transitions reviewed. This checks presence and shape only.
2. **Signature gate:** compare module/name, arity, parameter labels and declared kinds against parsed source and the generated reference. The existing `tools/check_doc_signatures.py` already provides this floor; extend its data flow rather than duplicate it. Inferred return kinds require compiler metadata or a conservative checker; a regex cannot certify them.
3. **Effects and call-graph checks:** compare declared effects with builtin identities and transitive callees, converging to a fixed point. Canonicalize aliases. Unknown indirect/FFI calls are unknown unless summarized, never silently pure. Preserve allocation provenance; the project's prior spelling-only and fixed-iteration problems apply here too. Existing `check_layers.py` is a module-level aid, not a proof of individual contracts.
4. **Behavioral witnesses:** run selected valid/boundary cases against independent mathematical/reference oracles, not only existing output goldens. Check status, exit behavior and before/after state, including guards/overlap where safe. Existing proof/property/mutation tooling can host them; tests remain finite evidence, not universal proof.
5. **Evidence freshness:** record actual compiler/source hashes, target, relevant build flags, test identity and result. Changed source marks old evidence stale. Track missing coverage by function and contract clause, not just global test count.

Do not execute arbitrary strings from contract records as shell commands or Python eval. If structured predicates are introduced, use a small validated expression language with defined overflow and bounded evaluation. For lengths, use mathematical integers or checked operations so a checker does not repeat the program's multiplication overflow. Plain explanatory prose can remain alongside structured facts; it cannot be mechanically proven merely because it is present.

Suggested independent status columns: `contract_present`, `signature_matches`, `preconditions_enforced`, `behavior_reviewed`, `witnesses_passed`, `evidence_current`. Never compress them into one unqualified “verified” checkmark. Fail an acceptance gate on unknown required fields while allowing an inventory stage to report them honestly.

### Static check actually run

Executed `python3 tools/check_doc_signatures.py --repo-root <pinned local tree>`: **24 source modules, 306 declarations; 24 documented modules, 306 signatures; 0 issues; PASS (static signature floor only)**. This does not check behavioral contracts, return ABI, alias safety, arithmetic accuracy or native execution. The source-token census was also run; its evidence is attached.

The first census attempt encountered deliberately invalid UTF-8 in negative fixtures; the final byte-based scanner handled those without dropping files. No native programs or compiler builds were run.

## 5. Acceptance sequence

1. Implement the shared withdrawn-status check for BN_VECDOT and its aliases; keep the reserved spellings and accurate help. Refuse before code emission in every compile mode.
2. Replace the affected vocabulary pair's success expectation with explicit negatives; test old/new names, source locations, nested/imported/dead calls, reserved declarations and literal mentions. Ensure no stale executable is launched after refusal. Recheck other aliases unchanged.
3. Inventory all 306 contracts with explicit gaps; prioritize memory, file, numerical and collection routines. Muse's function-body review feeds concrete discrepancies into those records; this design work does not duplicate its full body audit.
4. Accept a small contract-schema pilot before mass annotation. Use the current dot library, matrix transpose and file writer as contrasting examples. Establish a baseline so missing contracts stay visible; additions/changes must not increase unresolved gaps.
5. Reactivate the builtin only after the R186 typed equal-length design, result classification and target tests pass. Do not conflate containment with repair completion.

R184 and R185 reports and evidence are already delivered. Their remaining open work is explicitly bounded: R184 vocabulary approval and complete compiler-message reachability; R185 owner decisions, documentation reconciliation and native verification. R187 depends on their findings but does not claim those remaining approvals/tests are complete or authorize production changes to finish them.

Native compiler/build, suite, guard, CI and Windows: **NOT RUN — no toolchain used for this read-side assignment.** Production src/lib/tests/tools/reference files, Windows work and frozen non-Sanskrit packs are unchanged. Only this handoff and its evidence are delivered.
