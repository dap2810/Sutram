# Sutram ROUND 136 — close the terminology, return-order and checker decisions

**Date:** 29 October 2026. **Pinned source:** `4c556029de3be26b49e09c785f0c30819b1d4e8c`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-136.md`, blob `5d5880cc31f143e662a1b0bd279b2dc5a811df21`.
**Return:** `ChatGPT-to-Sarvam/ROUND-136-FINAL-DECISIONS.md`.
**Scope:** one read-side round. Recommendations and specifications, not implementation or measured acceptance. Only this handoff is to be added; existing source and expected outputs stay unchanged.

## Decisions

1. **Use `avayava` (अवयव, member/component) for a struct member in future diagnostics; keep `kshetra` for the memory-region construct.** The dictionary and the two requested source files were checked separately. A fourth field-related diagnostic fragment, `kshetram nasti`, must not be overlooked.
2. **Allow scalar `nivartanam` inside a region. Evaluate the complete expression first, preserve its scalar result/status, restore the exited scratch region, then emit the epilogue/return.** Allocation during expression evaluation does not invalidate this ordering. A returned reference is a different, rejected case. Under the minimal checker, `helper(buf)` with a reference argument is also rejected by the call rule, not by a blanket return ban.
3. **Adopt the conservative K0 rule set below as the recommended initial checked profile. Unknown means compile-time rejection at the unsupported use.** A documented contract describes this restriction; it is not a replacement for enforcement. No claim is made that Gemini or another party has already approved this exact convergence.
4. **ZERO additional target bytes for no-block programs is a required Step-3/4 invariant, not an executed result.** Compare against an otherwise identical Steps-0–2 compiler baseline, and keep the separate diagnostic wording change out of that comparison. The full allocator change cannot be promised byte-identical to v261.

## Item 1 — terminology checked against both dictionary and source

### 1.1 What was actually inspected

Both complete files were retrieved at the pinned commit:

- `src/sutram_compiler.asm`: blob `e64bcce50e1e05a2a0a9fca9f337b8c0b7b93345`.
- `lang/sanskrit.lang`: blob `27eda2b6a9be2cca76e375cfec9d73b865c7b4e8`.

Literal searches were performed on the retrieved file contents, not merely GitHub's code-search index. The Latin spellings `avayava`, `anga`, and `sthana` each returned no literal match in either file. The canonical Devanagari strings अवयव, अङ्ग, and स्थान likewise returned no literal match in either file. The public keyword/builtin definitions at compiler lines 690–791 and the complete Sanskrit alias pack were also inspected. These are source/pack checks, not a compiler execution or a repository-wide claim about every included file, historical handoff, transliteration variant or generated binary. Hexadecimal keyword strings are not confused with evidence obtained by searching rendered Devanagari text. [R2, R3]

**Positive controls and a necessary qualification:** the compiler does contain `kshetra` in field diagnostics; it also contains the inflected `sthane` at lines 318 and 349. Therefore `sthana` must not be advertised as an entirely unused word family merely because the literal stem is absent. [R2]

### 1.2 Candidate decisions

| Candidate | Real word and ordinary sense | Technical fit | Existing use in the two checked files | Decision |
|---|---|---|---|---|
| **`avayava` — अवयव** | Yes: member, part or portion; a component of a whole. MW 1872, page 92, directly inspected as a page image. | Good for a **member of a structure**. The programming use is a declared technical extension, not a claim that an old dictionary defines a modern struct layout. | No literal Latin/native occurrence found; not an existing keyword or builtin in the inspected definitions/pack. | **Choose.** In explanatory text, use `rachana-avayava` to make the structural context explicit. No new reserved word is needed. |
| **`anga` — अङ्ग** | Yes: limb, member, subdivision. MW's dictionary entry supports the member sense. | Defensible and shorter, but broader; visually close in Latin to the existing `anka`/अङ्क vocabulary. That is a readability concern, not a token collision. | No literal candidate occurrence found in either file. Existing `kw_anka` is a different spelling and word. | Valid alternative, **not preferred** over the more explicit component/member term. |
| **`sthana` — स्थान** | Yes: place, position, location. MW also records the locative `sthane`. | Describes where something is rather than identifying it as a named structure member; less precise. | Literal `sthana`/स्थान absent; **`sthane` already used twice in compiler diagnostics**, including the ambiguous-field hint. No candidate pack alias. | Do not choose for the field/member terminology. |

Dictionary sources W1–W3 establish the ordinary senses. The ranking and use as compiler terminology are this review's judgment. I do not certify full Sanskrit sentence morphology merely from a headword lookup.

**Important distinction:** `kshetra` in an existing diagnostic is a semantic-overload problem, not itself a duplicate lexer keyword. This differs from giving two constructs the same native token. Removing the overload is worthwhile, but no global identifier rename or public field-name change follows from this recommendation.

There is an additional advantage to “member”: `tests/r23/test_capabilities.py` uses the same unknown/ambiguous-field diagnostics for **method lookup** as well as data fields. A structural member is the useful umbrella term; do not accidentally narrow the error to a byte offset only. [R4]

### 1.3 Four source fragments, not only the three headlines

The following is a **future wording change list**, NOT a patch applied by ChatGPT:

| Compiler location | Current fragment | Recommended terminology action |
|---|---|---|
| Line 313, `r5_msg_field` | `agyat kshetra` | Use `agyat avayava` in the existing diagnostic register. Preserve `E_UNKNOWN_FIELD`. |
| Line 317, `r7_msg_field_amb` | `kshetra` | Use `avayava`. Preserve `E_AMBIGUOUS_FIELD`. |
| **Line 328, `r5_msg_field_hint2`** | `kasyashchid api rachanayah kshetram nasti` | Reword the hint consistently for a structure member; the masculine noun has nominative `avayavah`, not the old neuter `kshetram`. Review the whole sentence rather than mechanically replacing inflected suffixes. |
| Line 827, `msg_rachana_fields_overflow` | `rachana kshetra seema atikram` | Use `rachana avayava seema atikram` in the existing diagnostic register. |

The two existing `sthane` phrases describe a place and need not be changed merely because `avayava` is chosen for a member. No change to `rachana`, member identifiers, structure layout, error IDs or language-pack mappings is proposed here.

**Expected-output impact verified, not guessed:**

- `tests/expect/224_unknown_field.out` contains both `agyat kshetra` and the additional `kshetram nasti` hint.
- `tests/expect/234_ambiguous_field.out` contains `kshetra` and the separate `bhinne sthane` hint.
- `tests/expect/106_rachana_field_capacity.out` contains `rachana kshetra seema atikram`.
- `tests/r23/test_capabilities.py` pins unknown-method and ambiguous-method message substrings using `kshetra`.

Therefore changing the wording now while promising unchanged rejection output is contradictory. Keep these bytes frozen for the region implementation's legacy comparison. Apply a separately authorized terminology-only change later with an explicit expected-output delta and targeted tests. Never edit those expectations merely to disguise an unintended guard difference. [R4–R7]

## Item 2 — the evaluation-order question, answered directly

**YES: restoring immediately before the machine epilogue/return handles an allocating return expression, provided the complete expression is evaluated before that restore and its result is an admissible scalar.** Restoring before *evaluating* the expression is too early. Restoring after evaluation but before transfer is neither too late nor intrinsically complicated. Restoring after `ret` would be unreachable.

### 2.1 Source evidence for a real insertion point

The current `.gs_return` performs `gen_expr`, then scalar type conversion as needed, then `.gs_ret_func` calls `r25_emit_return_status`, then emits the frame teardown and `ret`. There is an actual boundary **after expression/conversion/status computation and before frame teardown** at which the cleanup can be inserted. This is not an abstract ordering unavailable in the current emitter. No-value returns and main exits are distinct paths and must also be considered. [R8]

Proposed sequence, preserving current expression/argument evaluation order:

```text
1. Evaluate the entire return expression while every needed region remains live.
2. Verify/establish the scalar result class; finish existing return conversions/status.
3. Keep the evaluated result in its ABI register(s), not in storage about to expire.
4. Restore only S for the regions this exit crosses, using a non-live temporary.
5. Emit the existing frame teardown and return (or specified main termination).
```

Reference-class verification occurs at compile time; it is not a runtime operation inserted between steps 1 and 3. Runtime evaluation happens once. Do not re-evaluate a load, conversion or helper after rewinding.

With R11 available, cleanup of one exited region is still the following **two additional instructions**, irrespective of how many allocations occurred during expression evaluation:

```asm
; CONCEPTUAL emitted code after the result/status is established.
mov r11, [rbp - mark_R]
mov [rel scratch_S], r11
; existing epilogue and ret follow
```

RAX/RDX and floating-result state are not overwritten by these MOVs. A live R11 requires another dead temporary or preservation; a push/pop pair adds two instructions. Marks must be placed in real, non-overlapping activation-local frame slots. The compiler's existing `FUNC_SPILL_BYTES` limit is not permission to place hidden marks over locals or saved registers; frame capacity must be checked. These are design counts, not measured machine code. [R2, R8]

### 2.2 What if `helper` allocates?

| Helper behavior during evaluation | Correct lifetime consequence |
|---|---|
| Reads `buf`, computes a scalar, retains no reference | Keep `buf` live for the call; once the scalar is obtained, caller-region rewind can occur safely under a verified borrow contract. |
| Makes a lexical persistent allocation | P may advance. **Do not restore P.** Restoring the caller's S mark cannot reclaim that persistent allocation when the two-cursor invariant holds. |
| Uses its own nested `kshetra` | The callee restores its own marks before returning; caller-owned scratch remains live until the caller's subsequent cleanup. |
| Returns a reference into a region being exited, or stores `buf` somewhere longer-lived | Reject by the reference/call-effect rules. Moving the cleanup later is not a repair for an escaping reference. |
| Fails through `prasar` before ordinary return evaluation finishes | Clean up on that actual failure-return edge; the ordinary post-expression cleanup is not reached. |

For the shared arena, the relevant relation before the caller rewind is `P <= S <= M`, where M is the saved caller-region mark. Restoring `S = M` preserves `P <= S`, including when a helper increased P. This depends on every allocation having checked the gap and on restoring **only** S, not the allocator's whole state. [R9]

**Do not conflate lowering correctness with K0 admission.** The exact expression `nivartanam helper(buf)` passes a Reference to a user helper. The minimal final K0 below deliberately refuses such calls because it has no borrowed-buffer contract. Thus that exact source is rejected at the call in K0. This is not evidence that return ordering is impossible and is not a reason to forbid every `nivartanam`.

A supported counterpart is `nivartanam helper(buf[0])`, after a null check and a statically bounded scalar load, where the exact helper body is verified as a scalar-only helper. That helper may allocate scratch inside its own checked region and return a number. Unknown helper bodies or helper results are rejection, never assumed scalar. K0 continues to refuse persistent-allocating helpers under its initial narrow whitelist; the table above explains their lifetime mechanics, not their admission to that whitelist.

### 2.3 Example that actually fits the proposed minimal rules

```sutram
# PROPOSED K0 acceptance example; kshetra is not implemented/tested here.
prakriya sahayaka(x) {
    kshetra {
        vitti t = nirmmita(8)
        yadi (t == 0) { nivartanam -1 }
        t[0] = x + 1
        nivartanam t[0]
    }
}
prakriya pariksha() {
    kshetra {
        vitti buf = nirmmita(8)
        yadi (buf == 0) { nivartanam -1 }
        buf[0] = 41
        nivartanam sahayaka(buf[0])
    }
}
mukhya() {
    likha(pariksha())
}
```

Expected successful value **by reasoning, not execution:** 42. The scalar argument is read while the caller region is live. The helper allocates and releases its own scratch, returns a scalar, then the caller restores its own mark. A replacement using `sahayaka(buf)` is a different type/effect case and must not be accepted by analogy.

### 2.4 Why a blanket return ban is not the converged rule

A ban is a possible restrictive language choice, but the evaluation-order objection does not require it. It also leaves `krama`, `agrim`, and propagated failures to solve. Use the shared cleanup-on-exit rule instead, rejecting the returned Reference rather than every return.

The separate `r25_gen_prasar` emitter performs `gen_expr`, tests RDX, and directly emits an epilogue/ret on failure. Add cleanup on that failure branch while preserving RAX/RDX. Its current conditional skip is short and explicitly checked against 127 bytes; region-enabled paths must widen or reject an oversized displacement, never truncate it. A handled `yadi dosh` that stays inside the same region does not rewind that still-live region. [R10]

For break/continue, restore only marks crossed by the actual target. For a nested exit from `[R1,R2]` to `[R1]`, restore M2 only. For return from both, restore inner-to-outer, or collapse to the outermost exited mark only while cleanup is solely a shared-cursor restore. Do not clean caller-owned regions. This closes the mechanism; acceptance tests must still establish the implementation.

## Item 3 — one final conservative rule set

### 3.1 Boundary and representation

**Recommended initial profile: K0, as a specification label, not a keyword.** It checks the whole function containing a region, not just text between its delimiters, and verifies all admitted helper bodies transitively. Ordinary source outside that opt-in boundary remains legacy code. The guarantee concerns region references through admitted operations; it is not a sandbox against arbitrary unsafe legacy memory corruption, foreign code, fabricated addresses or concurrent mutation.

Compiler-side classes:

```text
Scalar(kind)                         numeric/Boolean data, never an address
Reference(owner_id, object_id, N, d)  scalar-only object of N bytes, constant offset d
Literal                              static text only in explicitly admitted uses
Unknown                              proof unavailable; never defaulted to Scalar
```

`origin_depth` can record the owning region's depth; `taint_depth` can summarize region dependency. **Those two integers alone are not the checker.** Also retain value class, owner identity, object extent/offset, and null facts. Persistent references at depth zero are still References, not numbers. Same-depth sibling regions must not be confused. In K0, immutable reference bindings and rejected reference merges make a single known owner practical; Unknown has an explicit state, not the depth-zero encoding.

A scalar-only buffer may contain numbers that happen to equal addresses, but K0 never permits converting those numbers into References. References themselves cannot be stored into any buffer. That invariant is why a checked load may yield a safe scalar without a runtime taint map.

### 3.2 Rules, caught cases and admitted cases

Every rejection below is a compile error at a supported construct/use, with origin and use locations where available. An unimplemented-keyword parser error is not a passing safety test.

| Rule | What it catches/refuses | What it allows |
|---|---|---|
| **K01 — Scalars stay scalars.** Numeric literals/input/operators produce Scalar, never Reference. | Integer-to-pointer reconstruction, raw address guessing inside the checked function. | Numeric arithmetic, counters, Boolean tests and numeric results. |
| **K02 — Direct allocation has known extent and lexical owner.** In initial K0, positive compile-time byte sizes only. | Dynamic/overflowing/unknown allocation size; treating a returned pointer as an integer. | Fixed-size persistent allocations written outside a region and scratch allocations written within one, subject to checked failure handling. |
| **K03 — Reference bindings are immutable.** Aliases copy owner/object/extent/offset and must have usable scope contained in the owner. | Outer retention, rebinding a numeric slot to a pointer, reference-valued loop carry and ambiguous joins. | Fresh local aliases in the same or deeper valid scope. |
| **K04 — Only checked constant address offsets.** Preserve Reference identity after offset arithmetic. | `outer = note + 64`; out-of-object/wrapping offsets; bitwise/float/truncation laundering. | Same-lifetime interior aliases with statically proved bounds. |
| **K05 — Null guard must dominate access.** Re-executed initializers reset null facts; joins intersect definite facts. | Access after a check in only one unrelated arm; unchecked 0 dereference. | Continuing path after an exiting null arm, or a specified terminating assertion. |
| **K06 — Loads/stores operate on known scalar-only buffers with constant bounds.** | Pointer-containing cells, Unknown raw loads, dynamic indices, access outside extent, pointer stores through a local alias of outer storage. | Bounded scalar reads/writes, including copying numeric results outward. |
| **K07 — No unverified aggregate or raw-write shortcut.** Field/slice/pointer-bearing collection operations and raw copy/store intrinsics need separately specified checking; initially reject them. | Escapes through wrappers, list cells, `likh8`, byte-copy, aliases of unknown storage. | The explicit scalar-buffer access form in K06; legacy APIs remain usable outside K0. |
| **K08 — Direct calls require exact-body value-only summaries.** Scalar parameters/results, no unverified transitive effects, no mutable globals; initial whitelist excludes persistent allocation effects. | Unknown `helper()`, pointer result from a zero-argument call, retaining helper returning a scalar, reference arguments, stale/unverified summaries. | Verified scalar helpers, including helpers with their own checked scratch and scalar return. |
| **K09 — Unknown/recursive/indirect/FFI/assembly effects are rejected in K0.** | Hidden retention, callbacks, arbitrary memory mutation, provisional summaries accepted before verification. | Only specified trusted compiler intrinsics and verified acyclic direct helper calls. |
| **K10 — Intrinsics are checked by actual overload/effect.** | Approving raw three-argument `likha` merely because scalar `likha` is permitted; untracked text-pointer manipulation. | Scalar output, permitted static-literal output, assertions and direct allocation with their explicit contracts. |
| **K11 — Returns and result payloads are Scalar only.** Evaluate first and clean up the exited regions. | Direct/derived/pointer-bearing return, including `siddhi`/`dosh` carriers; persistent pointer returns are conservatively refused too. | Ordinary scalar return, scalar success/failure, safe scalar loaded from a live checked buffer. |
| **K12 — Every exiting edge restores precisely its region suffix.** Region identity, not depth alone, determines the suffix. | Missing cleanup on return/break/continue/`prasar`; rewinding a still-live parent or caller region; jumps into an uninitialized region. | Nested blocks, same-region inner loops, scalar early exits and handled failures that remain local. |
| **K13 — Capacity/analysis limits fail closed.** Unknown facts, exhausted tables or unsupported proof cases are diagnostics, never skipped checks. | Unsound acceptance after analyzer overflow or branch/loop facts lost. | Programs within explicit static limits; a 64-region implementation limit is acceptable if diagnosed, not wrapped. |

**Declared restrictions are part of the contract:** K0 does not initially support dynamic sizes/indices, borrowed reference arguments, reference-bearing aggregates, mutable references, opaque external effects or recursive summary cycles. It rejects some correct programs. There is no warning-only route around those restrictions while retaining the K0 safety label. The more permissive borrowed-buffer profile is later work, not implicitly approved by the allocating-return discussion.

**Names versus values:** names locate compiler bindings. `vitti q = p` and admitted `p + constant` preserve a value's origin even under renaming. In contrast a verified scalar load from a scalar-only object produces Scalar; the checker must not keep a misleading “everything derived from any pointer is forbidden forever” rule. The invariant about memory contents justifies that distinction.

### 3.3 Calls and transitive verification are not documentation alone

A no-retention comment is useful documentation but is not proof. Verify the exact function body and every admitted callee before caching its summary. Unknown separate-object metadata, cycles not yet solved, or a changed callee invalidate approval. A helper returning `1` could still retain its argument; the prior `suchi_khip` example remains the reason not to infer effects from a scalar-looking return. Reference arguments are refused in this minimal profile rather than accepted under a promise.

Lexical routing remains the owner's settled choice. K0's rejection of an unsupported helper is not dynamic rebinding of that helper's allocations. Persistent allocations may survive region exit; only S is restored. Neither this specification nor a region around a request proves whole-server bounded memory.

### 3.4 Bounded soundness argument

Within K0, only admitted allocations create References; aliases/constant offsets preserve identity; numeric values cannot become references; memory cannot contain References; calls exchange scalars only; returns carry scalars only; and exiting scopes remove every usable binding owned by the reclaimed region. With correct null/bounds/allocator arithmetic, cleanup and code generation, the allowed continuation cannot use a surviving checked reference to the reclaimed allocation.

This is a design argument under stated assumptions, **not a machine-checked proof or an implemented checker**. Scalar-only memory and whole-checked-function restrictions are essential. Remove them and the argument no longer applies. Unchanged unsafe legacy code outside the checked boundary can independently forge or corrupt addresses; the new block does not confer language-wide memory safety.

### 3.5 Price, with estimates separated from facts

| Operation | Compiler work estimate after lookup | Extra emitted provenance instructions |
|---|---|---:|
| Classified scalar assignment / new immutable alias | Roughly 8–25 simple instructions for class/origin copying/checking; metadata and lookup vary | 0 |
| Scalar arithmetic classification | Roughly 6–20 simple instructions | 0 |
| Constant reference offset | Roughly 15–40 for class/null/extent/overflow proof and propagation | 0 beyond ordinary address calculation |
| Verified direct call with a arguments | Summary lookup plus roughly 4–10 per argument; first-time body verification is additional | 0 beyond existing call/ABI work |
| Statically proved scalar-buffer access | Compiler owner/null/constant-bound checks; unknown means rejection | 0 additional runtime provenance/bounds instructions for this constant-only profile |
| Region entry | Two MOVs in the shown memory-cursor/frame-mark scheme | 2 |
| One-region exit | Two MOVs after result computation and before transfer; temporary spills may add 2 | 2 before spills |
| k-region exit | 2*k MOVs, or 2 with the valid shared-cursor-only collapse | 2*k or 2, before spills |

These are prospective engineering ranges and counts of shown sketches. They are **not disassembly measurements or cycle results**. Allocation gap checks and zeroing belong to the allocator path and are not zero-cost merely because provenance tracking is compile-time. Native null handling written in source also has its ordinary branch cost.

Retain Round 135's **960–1,800 added/changed NASM-line estimate for Steps 3–4**, not thirty lines and not a promise. It includes region/frame/edge metadata, cleanup hooks, abstract-value rules, constant bounds/null facts, call summaries, diagnostics and integration. It excludes Steps 0–2, tests, Windows allocator work and a later more permissive checker. No new estimate is being substituted for a measured implementation.

## 4. The zero-byte requirement: what can be confirmed now

**Design requirement confirmed: Step 3/4 must add zero target bytes to a translation unit with no region construct. Measured confirmation: NOT RUN.** No implementation exists in this round from which I could honestly report a passed 0-DIFFER guard.

Use these baselines:

```text
B = accepted Steps 0–2 compiler, same build flags, target and inputs
C = B plus Steps 3–4, field-diagnostic wording unchanged
For every no-region input:
  compare accept/refuse status, diagnostics, expected output and emitted bytes.
```

The comparison is C versus B, not C versus old v261. Step 1 deliberately changes allocation emission, so blanket byte identity of the entire allocator rollout against v261 is not established by making the new checker static. [R9]

Implementation obligations for the C/B invariant:

- Recognize the new construct contextually without globally stealing a formerly valid identifier `kshetra`; check legacy identifier/parse cases, comments and strings.
- If the parsed translation unit contains no region, take the old Step-0–2 paths: no K0 restrictions, no mark slots, no extra register saves, no cleanup emission and no new per-program data/helpers/literals.
- Keep feature-dependent image sections, literal pools and frame growth lazy. Static compiler metadata is not target data; adding a compiler table need not alter the emitted program, but an unconditional embedded helper does.
- Do not perturb code/relocation/literal ordering or rewrite no-region short branches. In particular, `prasar` branch widening is conditional on the changed region-enabled path.
- Verify accepted programs and refused cases, including object/separate and supported targets; explicit unsupported-region mode diagnostics must not alter ordinary no-region acceptance.
- Keep the `avayava` diagnostic migration in a different, acknowledged change. Its pinned expected-output differences cannot coexist with a claim of unchanged old diagnostic bytes.

A documentation-only handoff has changed no target program bytes. That fact must not be presented as a successful future compiler guard.

## 5. Focused acceptance cases to close these items

All are **proposed, NOT RUN**; retain the full R135 matrix as well.

| ID | Case | Required result |
|---|---|---|
| F01 | Candidate dictionary and exact pinned source/pack checks | Recorded headword senses and scoped occurrence evidence; not a global uniqueness assertion |
| F02 | Future field-diagnostic rename | Update all four fragments and the reviewed expectations intentionally; preserve IDs/source locations/member layout |
| F03 | Scalar return with no allocating helper | Evaluate result, rewind correct marks, preserve value |
| F04 | `sahayaka(buf[0])` example above, helper allocates its own scratch | Successful value 42 and correct nested cursor restoration |
| F05 | Exact `helper(buf)` Reference argument | K0 call-contract rejection, not a misleading universal return prohibition |
| F06 | Helper returns a scratch pointer / caller returns direct allocation | Reference-result rejection |
| F07 | Return expression takes `prasar` failure path | Cleanup on the failure edge with preserved RAX/RDX and valid branch displacement |
| F08 | Locally caught failure continues in region | No premature rewind |
| F09 | Allocator/emitter harness: persistent P advances during an expression | Cleanup restores S only; P remains advanced; this harness is not proof that persistent-allocating helpers are admitted by K0 |
| F10 | Nested break/continue exits inner only versus exits both | Correct region identities/marks, no outer or caller invalidation |
| F11 | Arithmetic alias and indirect-storage escape probes | K04/K06/K07 reject; no name-based laundering |
| F12 | Unknown zero-argument helper, pointer-result helper, indirect call | Unknown/non-value call diagnostic |
| F13 | Re-executed allocation initializer and a non-dominating null test | Null facts not carried from a previous iteration or wrong branch |
| F14 | Two-cursor exhaustion / rounding overflow / zero bytes | Specified 0 result and no state mutation; no silent OS fallback |
| F15 | No-block C/B regression and guard corpus | Zero added bytes/unintended diagnostic changes under identical baseline and flags |
| F16 | Region-enabled callee versus unverified external/legacy code | Checked boundary is enforced, not extrapolated to whole-program safety |

## 6. Source ledger and execution status

### Repository evidence, all at the pinned commit

- **R1:** `Sarvam-to-ChatGPT/ROUND-136.md`, blob `5d5880cc31f143e662a1b0bd279b2dc5a811df21`: the three requested decisions and reported disagreement. Other parties' positions here are attributed to that brief, not inferred as agreement.
- **R2:** complete `src/sutram_compiler.asm`, blob `e64bcce50e1e05a2a0a9fca9f337b8c0b7b93345`: complete-text literal checks; focused reads at 307–350 and 684–830; field strings at 313,317,328,827; `sthane` at 318,349; keyword/builtin definitions and compiler frame-capacity declaration.
- **R3:** complete `lang/sanskrit.lang`, blob `27eda2b6a9be2cca76e375cfec9d73b865c7b4e8`: canonical/native alias text and candidate checks.
- **R4:** `tests/r23/test_capabilities.py`, blob `789827e2979b8abc0af01180521e9c4c1efc1f08`: method-related expected substrings and test procedure, read but not run.
- **R5:** `tests/expect/224_unknown_field.out`, blob `9135ef868cecd2da6f3076aaa14dbbc87400b4c9`.
- **R6:** `tests/expect/234_ambiguous_field.out`, blob `44157054c7970364289ba02f5aefa162526ed1fe`.
- **R7:** `tests/expect/106_rachana_field_capacity.out`, blob `50f1746965adab4e7ea087cd7e072e2c3c7d1350`.
- **R8:** compiler lines 14439–14553, same R2 blob: expression generation before return conversion/status and epilogue, including no-value/main paths.
- **R9:** `ChatGPT-to-Sarvam/ROUND-135-KSHETRA-CHECK.md`, blob `ef1e6d8e4f69291ced0b514b23e77d18fa6043d3`: returned design, K0 restrictions, two-cursor invariant and baseline distinction. Opening re-read; complete prior report is available in this conversation. Its restrictions are retained, not silently expanded.
- **R10:** `src/r25_phal.inc:181–224`, blob `a36bd286aa6beea0b854576945e6874ba8835af0`: expression evaluation, separate failure epilogue and 127-byte skip bound.

### External lexical evidence checked in this round

- **W1:** Monier-Williams Sanskrit-English Dictionary (1872), original page 92, middle column, `ava-yava`. Original page image inspected: https://www.sanskrit-lexicon.uni-koeln.de/scans/MW72Scan/MW72Scanpdf/pg_0092.pdf . Supports member/part/portion; the struct-member recommendation is this report's technical judgment.
- **W2:** Monier-Williams dictionary, University of Hyderabad digital transcription, `aṅga` entry: https://sanskrit.uohyd.ac.in/SKT/MW/2.html . Supports limb/member/subdivision; does not prescribe a compiler keyword.
- **W3:** Monier-Williams `sthāna` entry, page 1263 column 1, reproduced with source attribution at https://akshara.ru/kosha/w/sTAna . Supports place/position and the inflected `sthane`; not a distinct definition of a struct member.

### Status

**Completed:** pinned source and pack reading; literal candidate checks and keyword-definition review; primary dictionary-page inspection; expected-output/test-source inspection; evaluation-order decision; one conservative recommended checker contract; cost and byte-identity boundaries; 16 focused proposed acceptance cases.

**NOT RUN:** native Sutram compilation, parser acceptance, new region checker, Linux/Windows execution, return/escape/OOM experiments, benchmarks, regression/proof suite or byte-identity guard. No native toolchain was invoked in this read-side round. No exact cycle or implementation-line measurement is claimed.

**NOT APPLIED:** diagnostic renames, compiler/library/test/tool/canonical-doc changes, language-pack changes, Windows work, workflow changes or backups. No other-language pack development. This report is not approval of untested allocator/freelist alias behavior in Steps 0–2.

**Return procedure:** upload this one Markdown file only to `ChatGPT-to-Sarvam/`, read it back, verify the commit diff, report the commit, then stop after Round 136.
