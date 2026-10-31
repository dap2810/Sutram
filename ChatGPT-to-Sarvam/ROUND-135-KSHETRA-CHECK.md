# Sutram ROUND 135 — priced exit lowering and a small, honestly bounded value-level checker

**Date:** 29 October 2026. **Pinned source:** `6fe995332e7d68fbc21ba636886077a4c8bba39d`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-135.md`, blob `56e041a325f167c890c5aac12b5c6eb84f397bda`.
**Return:** `ChatGPT-to-Sarvam/ROUND-135-KSHETRA-CHECK.md`.
**Status:** design/specification only. No implementation, compiler execution, benchmark, or test result is claimed.

## 0. Decisions retained, and the answer

I take the newer Round-135 brief as the authority for this assignment: the block is the lifetime carrier; routing is lexical; persistent allocation grows upward, scratch downward; Steps 0–2 are the owner's accepted plan. I am not proposing a different allocator or reopening those choices. Their acceptance is not evidence that they are implemented or verified. Windows implementation remains the owner's work. [R1]

The older `docs/decisions/MEMORY-UNIQUE-HYBRID.md` still describes the rejected one-assignment-scope rule and unchanged allocation backend. I read it as design history, not as an instruction to undo Round 135. Likewise my Round-134 recommendation to keep the old allocator backend is superseded by the owner's accepted Step 1. [R1–R3]

**Step 3:** allow scalar `nivartanam` inside a region. Save each mark in the current activation's stack frame. Restore only the scratch cursor on every edge that exits the region, before the existing jump/return. A simple lowering costs two MOV instructions per entered or exited region, with additional spills only when the scratch register is not available.

**Step 4:** check VALUES, with names serving only as binding identities. The smallest sound proposal I recommend is a deliberately restricted checked subset, called **K0 in this document, not a new keyword**. It distinguishes scalar data from references, preserves the allocation owner through admitted address operations, disallows references in memory aggregates, and admits calls only after verifying an appropriate closed-body contract. Unknown is rejection, not a scalar default.

**This is a small static type/provenance/effect discipline, not one scope comparison.** It can have zero emitted provenance-tracking instructions, but implementation cost is plausibly on the order of a thousand NASM lines, not thirty. It accepts less than ordinary Sutram. That restriction is the price of a small check that does not knowingly let an escape through.

The soundness claim is precisely limited: **no region-owned reference escapes or is used after its region ends through operations admitted by K0, assuming correct allocation, bounds, cleanup and code generation.** This is an argument for the proposed rules, not a machine-checked proof or a statement about an implemented compiler. It does not make arbitrary legacy `yantra`, integer-as-address code, foreign code, concurrency, or existing collection aliases safe.

## 1. The two-cursor interface required by Steps 3 and 4

Use offsets into one explicitly bounded reservation:

- `P`: first unused persistent offset, growing upward.
- `S`: first occupied scratch offset, growing downward.
- `L`: reservation length, with invariant `0 <= P <= S <= L`.
- Region entry mark `M = S`.

On leaving that region, restore **`S = M` only**. Do not restore `P`, the persistent freelists, or a snapshot of the entire allocator. Persistent allocations made during the region must survive it. Nested scratch operations and persistent allocations must all preserve `P <= S`.

For positive request `n`, calculate aligned size only after checking rounding overflow. A scratch allocation succeeds only if `aligned_n <= S - P`, then takes `[S-aligned_n, S)` and updates `S`. A persistent allocation checks the same gap before increasing `P`. An implementation that adds pointers before checking overflow is not equivalent to this rule. A failed request leaves both cursors unchanged. Zero-byte requests return 0 in this proposed contract; do not hand out a repeated cursor alias accidentally.

**Why rewind remains valid when persistent allocation occurred:** at exit, `P <= current_S <= saved_M`; therefore `P <= saved_M` after restoration. This reasoning assumes no allocator operation violates the gap invariant and no independent allocation stream is falsely labelled as scratch.

Lexical routing remains exactly the owner's choice: a direct `nirmmita` in a region uses scratch; an allocation written outside regions, including in an ordinary library body, uses persistent storage. Calls do not dynamically rebind the allocator. Existing outer-`kosh` growth remains persistent under the brief's policy. Whether a particular collection operation is admitted by K0 is a separate safety question. [R1]

Scratch reuse must preserve the specified initialization contract. Freshly returning previously used bytes without clearing them is not equivalent to today's fresh zeroed allocations. Zeroing has an O(bytes) cost, separate from cursor restoration. No speed claim below omits it by silently changing semantics.

## 2. Step 3: where marks and restores actually go

### 2.1 Mark storage and exact simple instruction counts

Allocate one eight-byte hidden frame slot for each simultaneously active lexical region. A nested region gets a different slot. Recursive activations get different stack frames; never use one global saved mark. Disjoint sibling regions can reuse a slot after layout proves they are never simultaneously live.

Conceptual emitted code, with R11 reserved as a temporary at this point:

```asm
; Enter region R. S is the downward scratch offset.
mov r11, [rel scratch_S]
mov [rbp - mark_R], r11

; Exit region R, while this frame still exists.
mov r11, [rbp - mark_R]
mov [rel scratch_S], r11
```

**Count:** two instructions on entry, two on exit; no allocator syscall and no clearing on rewind. These are counts of the displayed sketch, not measured cycles. Memory-to-memory MOV is not a single replacement for each pair. If R11 is live, allocate another dead temporary or preserve it; a push/pop pair adds two instructions to that cleanup sequence. Do not assume the current register allocator has already granted this temporary.

Frame-slot allocation must participate in the actual local-frame size and alignment calculation. The existing return sequence discards the local frame, so load the mark **before** its `lea rsp,[rbp-8]` / pops / `ret`. The source also has no-value and main-return paths; handle those rather than patching only one label. [R4]

### 2.2 Exit-edge algorithm

Maintain a compiler-side stack of region identities belonging to the current function activation. Save that identity stack, or a persistent parent-linked scope node, at each branch destination. Save both break and continue destination scopes when entering a loop.

For an edge from active region stack `A` to enclosing destination stack `B`:

1. Require that `B` is the appropriate prefix of `A`. Never allow a jump into an uninitialized region.
2. Determine the exited suffix of `A` by **identity**, not only depth.
3. Emit restores for that suffix, inner first, while mark slots are available.
4. Emit the existing branch/epilogue and patch its final displacement.

A normal inner exit from `[R1,R2]` to `[R1]` restores `mark_R2` only. It must not restore `mark_R1`, even if both marks happen to hold equal offsets in one execution. A return from `[R1,R2]` to the function boundary exits both. A callee never restores marks belonging to its caller.

Because the only cleanup in this version is restoration of one shared scratch cursor, an optimizer can collapse multiple restores to the **outermost exited** mark. The first version can simply emit `2*k` instructions for `k` exited regions; the optimized version needs two. This optimization is valid only while there is no per-region destructor, clearing, page decommit, or independent arena cleanup to skip.

### 2.3 Placement and cost by edge

| Edge | Placement | Added cleanup instructions, before spills |
|---|---|---|
| Normal block end | Before successor statement | 2 |
| `krama` leaving one region | Immediately before its existing loop-exit JMP | 2 |
| `agrim` leaving one region | Immediately before its existing continuation JMP | 2 |
| Break/continue of a loop wholly within a still-live region | None for that region | 0 |
| Scalar `nivartanam` leaving k regions | After result evaluation/conversion/status formation, before frame teardown | `2*k`, or 2 with the proven collapse |
| Failure propagation leaving k regions | On the failing edge only, before its separate epilogue | Same as return |
| Handled failure staying inside a region | None for the enclosing region | 0 |
| Actual process termination | No reusable continuation exists; process teardown reclaims storage | No rewind required for this lifetime property |

The existing `.gs_break` and `.gs_continue` emit a JMP and record its patch position; insert cleanup **before that JMP** and record the displacement at its new position. In counted loops, continue targets the saved update point, not necessarily the condition. Preserve that target. The source's loop patch arrays currently record offsets; region destination context must be added alongside their logical loop metadata, not inferred from a coincidental code address. [R5]

### 2.4 Allow `nivartanam`; refuse an escaping result

My choice is **YES, allow it**. A scalar value computed from a region buffer can be returned. An address or carrier of a region reference cannot. Evaluate the return expression completely while the region is live, establish its admissible result class, preserve the value, restore the exited regions, then run the existing epilogue.

The two MOV cleanup sketch does not alter RAX, RDX or XMM registers. That makes preserving the ordinary result and `phal` value/status pair cheap. This is not a license to reuse RAX or RDX as cleanup temporaries. Any more elaborate error/zeroing/helper-call path must separately preserve the relevant ABI state.

**Existing extra exit:** `r25_gen_prasar` in `src/r25_phal.inc` directly emits a failure-return epilogue. It bypasses `.gs_return`. It carries value/error in RAX and status in RDX. Its short conditional branch is checked against a displacement of 127. Add the same cleanup hook to this path; if added cleanup does not fit, select a near conditional encoding for the region-enabled path rather than truncating a displacement. Leave the no-region short form unchanged where it remains correct. [R6]

A blanket ban on `nivartanam` would avoid one lowering case while leaving break, continue and `prasar` unresolved. Shared edge cleanup is the better small implementation.

## 3. Exhaustion: clean failure, never an implicit durable allocation

**Decision:** no fallback to today's per-allocation `mmap` when `P` and `S` leave insufficient room. Such a fallback would change lifetime and memory budgeting at the exact moment the budget was exceeded.

Preserve the raw allocator's error-result convention: invalid/overflowing size or insufficient gap returns **0**, with cursors and allocation state unchanged. The caller must handle that result. K0 requires a proven non-null path before reference arithmetic or access; it never treats 0 as usable memory. Generated collection allocation paths, when admitted later, must check failure before writing a header.

Returning 0 does not automatically print a diagnostic. This keeps handled failure from producing unexpected output. For a checked allocation site that chooses fail-stop behavior, or an explicit caller failure branch, propose this standard text:

```text
file:line: Sutram Error [E_KSHETRA_OOM]: क्षेत्रे पर्याप्तः अवकाशः नास्ति।
अनुरोधः = N; अवशिष्टम् = M।
```

Meaning: there is insufficient space in the region; N is the byte request and M the remaining gap. This is proposed diagnostic wording, not an existing message or formal Sanskritist certification. Stable error identifiers and source locations should accompany it. A checked use without an established null guard instead gets a **compile-time** `E_KSHETRA_NULL_CHECK` diagnostic, not a guessed runtime success.

The region emitter is not to allocate memory while trying to report OOM. Use existing static strings/output/error machinery, and preserve a clear distinction between recoverable 0 and a path that intentionally terminates.

Logical budget exhaustion can be synchronous. This specification does not promise recovery from every OS failure, hardware fault, stack overflow or external process kill. The owner must supply accessible backing memory for every allocation reported successful; Windows reservation/commit is not reimplemented in this round.

## 4. Step 4: the smallest useful closed subset I can defend

### 4.1 Why a taint bit on names is not enough

An expression such as `note + 64` still identifies region-owned memory. Calling its result an integer does not remove that lifetime. Conversely `note[0]` may be an ordinary numeric result that is safe to copy outward, **but only if the checker knows the cell cannot contain a reference**. Treating every load from an arbitrary qword as harmless would reintroduce pointer laundering.

The proposed checker therefore needs both an abstract value class and an origin. It is not enough to follow names, or to OR region bits while permitting arbitrary raw loads/casts.

### 4.2 K0 boundary — make the restrictions explicit

K0 checks the **whole function containing a `kshetra`**, including code before and after the block, and verifies callees admitted by its rules. Checking only the block while allowing the same function to reinterpret an exported number as an address afterward would not establish the guarantee.

Functions without a region retain the ordinary language unless they opt into verification as a callable K0 helper. No new pointer ownership syntax is required in source; the restrictions are static rules of the opt-in construct.

The first implementation is deliberately narrow:

- Mutable variables may hold numeric/Boolean scalar data. Reference-valued bindings are initialized once and are immutable within K0; aliases are new bindings, not type-changing assignments.
- Reference origins are direct allocations with statically known positive byte size, or aliases/constant offsets of them. Dynamic-size allocation and dynamic indexing are **rejected in K0 initially**, rather than silently losing extent information. This is a restriction of this minimal profile, not a claim that the two-cursor allocator itself cannot accept dynamic sizes.
- Memory reachable through an admitted reference is a **scalar-only buffer**. No pointer, slice, structure containing pointers, or unknown raw qword may be stored into it. Only statically bounded scalar accesses are admitted.
- No integer-to-reference reconstruction, pointer-to-number conversion, raw memory-copy loophole, pointer arguments/results across ordinary calls, inline assembly, unknown indirect/FFI calls, or mutable globals in the checked function.
- Calls are limited to specified compiler intrinsics and bodies verified for the value-only contract below. A declaration or comment saying `noescape` is not sufficient evidence.

These restrictions make the million-iteration 64-byte scratch test, fixed-size scalar scratch, numeric helpers and safe scalar returns expressible without a general heap graph, ownership inference, or lifetime-polymorphic ABI. They **do not** support arbitrary existing library routines inside a checked function. Such programs receive explicit unsupported-operation diagnostics and continue to be usable outside the new construct.

The common region example that prints the raw buffer address is not admitted by this first profile. Print scalar buffer contents or numeric results instead. This is a conscious conservative rejection, not something to hide in documentation.

### 4.3 Abstract values

Keep compiler-side metadata, not runtime tags:

```text
Scalar(kind)                  integer / float / Boolean data
Reference(owner, object, N, d) pointer into scalar-only object of N bytes,
                              at constant byte offset d
Literal                       static text allowed only in specified operations
Unknown                       unverified origin/effect; never assumed Scalar
```

`owner` is persistent storage or one lexical region in the current function. `object` is a binding/allocation identity, not a variable spelling. Record the region of an alias unchanged. A frame instance supplies the dynamic mark; lexical identities are not runtime generation counters.

For an implementation using one 64-bit ancestry mask, cap the checked function at 64 region identities and diagnose overflow. Do not silently wrap a bit index. This is an implementation limit, not a mathematical limit on the language.

Each destination binding records the lexical scopes in which it can be used. A reference owned by R may be bound only where its usable scope is contained in R; persistent references have no scratch bit, but are still References, not Scalars. Empty region bits must never be mistaken for permission to reinterpret an integer as a pointer.

### 4.4 Transfer and rejection table

Every row specifies what is caught and what is allowed. Unsupported cases are compilation errors, not untracked values.

| Operation | Value-level rule | Catches / refuses | Allows |
|---|---|---|---|
| Numeric literal or numeric input | Scalar; numeric operations never manufacture Reference | Attempt to dereference a number, even if it happens to equal an address | Ordinary arithmetic and numeric state |
| Direct `nirmmita(C)` | Reference to a fresh scalar-only C-byte object; lexical owner from allocation site; possibly null | Unknown/overflowing extent in K0; treating the result as a plain integer | Constant-size persistent or scratch allocation, with failure handling |
| `vitti q = p` for a Reference | Copy the complete abstract reference; check destination lifetime; q becomes immutable | Alias moved to a longer-lived binding; later class-changing/rebinding assignment | Same-region/deeper local alias |
| `p + constant` | Require non-null base and a checked constant offset within the same object; retain owner/object/extent | `outer = note + 64`; out-of-object offset; wrapped offset | A bounded interior reference in a permitted local |
| Other arithmetic/bit operations on a Reference | Reject in K0; do not erase or downgrade the reference class | XOR masking, float conversion, truncation, split/recombine address schemes | Scalar arithmetic with scalar operands |
| Reference equality/inequality with 0 | Special null test; yields Boolean; establishes a non-null fact on the appropriate path | Treating an arbitrary address comparison as scalar arithmetic permission | Ordinary allocation-failure guards |
| Scalar local assignment | Require scalar source; destination remains scalar | Assigning a reference into an integer slot as an escape disguise | Mutable counters, sums and numeric results |
| Scalar read through a Reference | Require live owner, non-null fact and static access bounds; scalar-only object invariant yields Scalar | Loading an address from an unverified raw buffer and treating it as a safe pointer | Reading numeric contents and returning/copying the number |
| Memory store | Require admitted scalar-only destination and Scalar source, with static bounds | Pointer retention in ANY memory object, even an inner one; local-alias store to outer storage | Numeric writes to proved buffers |
| General `likh8`, byte-copy, field/slice/aggregate operation without checked lowering | Reject; ordinary raw APIs are not proofs | Storage or reload that evades the scalar-only buffer invariant | A later explicitly verified intrinsic, not an accidental current exception |
| Direct function call | Verify value-only summary and scalar arguments; result is the verified scalar/result kind | `helper()` with unknown or pointer return; retaining `helper(p)` | A verified numeric helper or checked helper using only its own region |
| Return / `siddhi` / `dosh` payload | Require Scalar in K0; then emit cleanup | Direct/derived/wrapped reference returned from any exited region; persistent pointer returns are also conservatively refused in this profile | Scalar success, scalar failure, numeric return |
| Unknown indirect call, FFI, inline `yantra` | Reject anywhere in the checked function unless it is a separately specified trusted intrinsic | Hidden retention, guessed addresses, callback escape, bypassing cleanup | None in K0; legacy usage remains outside the construct |

**The memory restriction is deliberately stronger than the lifetime relation alone.** Even storing a pointer in a same-region buffer is rejected, because supporting pointer-containing heaps needs additional load/store provenance analysis. This avoids pretending a one-word tag can describe an arbitrary object graph.

Bounds are static in K0: for qword access require `0 <= d + 8*i` and `d + 8*i + 8 <= N`, with checked compile-time arithmetic. A one-past address may be a reference value but is not dereferenceable. If the proof needs a dynamic index range, reject until a separately specified bounds-check extension is implemented. This avoids both silent corruption of allocator metadata and unpriced fat-pointer metadata on every assignment.

### 4.5 Null facts, branches and loops

The reference binding never changes, so null facts can be keyed to its object/binding identity. Accept a dereference only under a dominating check, for example the continuing path after:

```sutram
# Proposed K0 usage, NOT RUN.
vitti p = nirmmita(64)
yadi (p == 0) {
    nivartanam -1
}
p[0] = 7
```

The verifier must prove that the null arm terminates the relevant path; merely finding a nearby textual `p == 0` is not enough. A successful `nishedha(p != 0)` can also establish the fact because its failure path terminates. Intersect definite facts at joins; do not keep a fact established in only one continuing arm.

Reference rebinding and pointer-valued branch merges are rejected by K0. Mutable loop-carried state is scalar only. Thus the first checker does not need a general points-to fixed point to discover a pointer assigned on a later loop iteration. Re-executing a reference initializer resets its null facts. A region-local reference cannot be retained across an iteration exit in a mutable outer slot or aggregate.

A later, more permissive checker may join possible origins or solve loop data flow. It must not be smuggled into K0 as an incomplete one-pass heuristic.

### 4.6 Calls: the answer to `outer = helper()`

Verify a **value-only call contract from the body and transitive callees**:

```text
parameters: scalar only
result: scalar, or phal with scalar success/failure payloads
retains caller addresses: impossible through this interface
mutable globals / arbitrary external memory / inline asm: absent
callee references: confined to its own verified locals and regions
allocates persistent storage: explicitly classified, never confused with scratch
```

For the smallest initial call whitelist, admit only the no-persistent-allocation form of that contract. Helpers that create persistent objects are not dynamically rebound to scratch; they are rejected by this minimal call policy. This is a rejection of unsupported interoperation, not a change to the settled lexical routing rule.

Verify all bodies before treating their summaries as trusted. Unknown source, separate-object metadata without a verified contract, indirect targets, or missing summaries produce `E_KSHETRA_CALL_UNVERIFIED`. Initially reject recursive summary cycles rather than assuming a provisional safe summary; activation-local marks already make later recursive support possible, but a sound call-graph verifier must be added before accepting it.

Consequences:

- `helper()` returning `7 + 8` can be verified and assigned to an outer scalar.
- `helper()` returning a raw allocation is not a value-only helper, even though the ABI puts its result in the same register as an integer.
- `helper()` returning from its own region with a pointer is rejected while checking that helper.
- `helper(p)` returning only `1` is NOT safe evidence: `suchi_khip` demonstrably stores its value argument into list backing storage before returning an integer. K0 rejects reference arguments, instead of trying to infer safety from that return type. [R7]
- A library name or an annotation is not proof. A summary belongs to the exact verified definition/build, not permanently to the spelling `helper`.

Trusted intrinsic cases must be explicit and checked by actual builtin overload: scalar `likha`, literal output, scalar assertions, and direct allocation are examples. Do not accidentally approve the raw three-argument write form of `likha` because a different overload prints integers.

A later K1 could admit synchronous borrowed-buffer functions with checked read/write/retention summaries and extent contracts. **K1 is not included in K0's claimed coverage or cost.**

### 4.7 Why this is about values, not names

The record for `q` is a binding to an abstract value. It contains the same owner and object as `p` after `vitti q = p`, and retains them after admitted constant address arithmetic. Renaming p or q cannot affect the result. A scalar and a Reference may occupy the same machine register, but their compiler classes differ. RAX return convention does not decide the class.

This is also why a scalar load can be useful: the scalar-only memory invariant, not the spelling of the destination variable, justifies returning the contents. Without that invariant, an unknown qword load stays Unknown and cannot be treated as harmless.

For independent terminology context, LLVM's language reference distinguishes address capture from the ability to retain memory access, and models capture through returns and calls. That is not Sutram's semantics and is not an implementation dependency; it reinforces why a scalar-looking machine value or a callee's surface name is insufficient. [W1]

## 5. The soundness argument, and its non-negotiable boundary

The proposed argument is by induction over admitted operations and cleanup edges:

1. Only direct allocation creates References. Numeric data cannot be converted to a Reference. Each reference has a live owner and a known object extent, or is the null result awaiting a check.
2. Alias creation and constant address derivation preserve owner/object. Reference bindings are immutable and cannot have a usable scope outside that owner.
3. Memory contains scalar data only. Storing References, reading unverified memory as References, raw copies and reference-bearing aggregates are disallowed, so there is no hidden reachable carrier to inspect at exit.
4. Verified calls take and return scalars; they cannot retain a caller's reference through their admitted interface. Opaque effects are not allowed in the checked function.
5. Returns carry scalars only. Branches cannot jump into a region, and all edges leaving it perform the specified rewind after value evaluation.
6. At rewind, every admitted reference owned by the exited region is confined to bindings whose usable scopes are ending. No accessible scalar can later be dereferenced as that pointer. Therefore the allowed continuation cannot access that allocation through a surviving checked reference.

This argument depends on correct null/bounds checks, safe allocator arithmetic, correct code generation and isolation of compiler-private cursor/mark storage. A malicious raw store that overwrites the cursor defeats it; that is precisely why unchecked memory operations are not admitted into K0.

**It is not a whole-program sandbox against unchanged unsafe code.** Legacy assembly can guess an address, violate bounds or retain unrelated dangling pointers independently of a region. If “never lets a dangling pointer through” means even arbitrary unmodified raw code must be unable to fabricate one, that cannot be honestly promised by a checker only on the new block. Meeting that stronger requirement would require restricting/validating the whole relevant program boundary or changing the raw-memory model. No claim here conceals that distinction.

K0's unsupported cases are rejected, not merely warned about. It does not accept a known hole and call the construct safe. Missing the programmer's intended lifetime may cause a false rejection, not acceptance of an untracked reference.

## 6. Price: compiler work versus emitted instructions

### 6.1 Static-operation price

All instruction estimates below describe a prospective compiler implementation. They are NOT counts from built code or cycle measurements. Symbol lookup, error rendering, existing expression generation and the initial verification of a callee body are separate costs.

| Source operation | Proposed compiler-side work | Extra emitted provenance instructions |
|---|---|---|
| Scalar assignment | Check source/destination class; update scalar definite-assignment state | 0 |
| New reference alias binding | Copy owner/object/constant extent/offset metadata; test destination lifetime; reject rebinding | 0 |
| Scalar arithmetic | Check admitted scalar operand classes | 0 |
| Constant reference offset | Check class, null fact, constant range/overflow; preserve owner/object | 0 beyond ordinary address arithmetic |
| Unsupported pointer arithmetic | Emit diagnostic, no target code | None; compilation fails |
| Direct verified call with a arguments | Lookup verified summary and check a scalar argument classes/result | 0 beyond existing call/ABI work |
| Unsupported/opaque call | Emit diagnostic, no target code | None; compilation fails |
| Constant bounded scalar buffer access | Verify owner, null fact, scalar-only object and constant range | 0 additional runtime provenance/bounds instructions in K0 |
| Region entry/exit | Allocate/load mark slot and lower correct edges | 2 at entry; 2 per exited region, before spills |

For illustration, one ancestry-mask rejection predicate can be compiled inside the compiler as:

```asm
; COMPILER-side conceptual check, not emitted into the user program.
mov rax, [rhs_region_mask]
mov rdx, [destination_allowed_regions]
not rdx
test rax, rdx
jnz reject_region_escape
mov [new_binding_region_mask], rax
```

That is six displayed compiler instructions for this predicate alone; class/object/extent handling is additional. A rough implementation budget is about 8–25 simple compiler instructions for a simple classified assignment, 6–20 for scalar/operator classification, 15–40 for constant reference-offset validation, and fixed summary lookup plus roughly 4–10 per argument for a verified call. These ranges are engineering estimates, not an assertion that NASM coding style, table lookup or cache behavior will deliver those numbers.

Reference metadata is a few compiler-side machine words per relevant binding/expression; no per-object runtime reference count and no runtime taint map. Cap tables explicitly and diagnose exhaustion, as the compiler already does for other capacities. Do not let analyzer capacity exhaustion turn into an unchecked compile.

Structured branches still need definite-fact joins. Value-only callees are checked once per definition/build and summaries reused; their checking cost is not recharged as a runtime call tax. A general mutable-reference data-flow solver is excluded by K0's restrictions.

### 6.2 NASM source estimate

| Implementation unit | Estimated added/changed NASM lines |
|---|---:|
| Region AST/binding identities, frame slots and scope/loop destination metadata | 150–250 |
| Shared cleanup lowering and return/break/continue/propagation hooks | 180–320 |
| Abstract value classes, alias/offset rules and immutable-reference restrictions | 150–280 |
| Scalar-only memory rules, constant bounds and definite-null facts | 180–350 |
| Direct-call verification, summary cache and unknown/recursive rejection | 180–350 |
| Diagnostics, limits and integration glue | 120–250 |
| **Steps 3–4 total, estimated** | **960–1,800** |

These are estimates for K0, not measured development size or a promise. They exclude Steps 0–2, test fixtures, Windows allocator implementation and a later K1. Existing helper reuse may reduce them; parser/source-location limitations or optimizer interactions may increase them.

Most new logic can live in one NASM include, but the actual source has a separate `r25_gen_prasar` emitter. It needs a hook too. “One new logic file” is plausible; “only one physical existing file touched” is not established by this source layout. Tests and documentation are also separate files. [R4–R6]

**Cheap answer versus broad answer:** a permissive checker for the existing raw-pointer, mutable-aggregate, indirect-call language is not cheaply made sound by adding a scope field. K0 is the affordable option because it explicitly refuses that complexity. If these restrictions are unacceptable, broaden the specification and budget; do not lower the safety claim by silently accepting unknown cases.

## 7. Concrete examples and tests that discriminate the design

All snippets and tests in this section are proposals, **NOT RUN**. `kshetra` is not claimed implemented on the pinned compiler.

### Positive test: scalar result, explicit failure handling, one region per iteration

```sutram
prakriya pariksha() {
    vitti total = 0
    vitti i = 0
    yavat (i < 1000000) {
        kshetra {
            vitti p = nirmmita(64)
            yadi (p == 0) {
                likha("क्षेत्रे पर्याप्तः अवकाशः नास्ति।\n")
                nivartanam -1
            }
            p[0] = i
            total = total + p[0]
        }
        i = i + 1
    }
    nivartanam total
}
mukhya() {
    likha(pariksha())
}
```

Expected successful scalar result by arithmetic: `499999500000`. No pointer escapes; `p[0]` is a constant bounded scalar access after a null guard. The early failure return requires cleanup. The expected scratch high-water is one aligned 64-byte allocation at a time, excluding other specified allocator metadata, not one million live allocations. This is not a measured RSS result.

### Negative arithmetic escape

```sutram
# Proposed negative test, NOT RUN.
prakriya asvikarya() {
    vitti outer = 0
    kshetra {
        vitti note = nirmmita(1024)
        yadi (note == 0) { nivartanam -1 }
        outer = note + 64
    }
    nivartanam outer
}
```

Required diagnostic: escaping region-derived Reference at the assignment, identifying allocation and retaining-use lines. The `+ 64` does not erase the origin. Prefer an escape diagnostic over an uninformative integer-type mismatch when both conditions apply.

### Call result is not automatically a number

```sutram
# Existing allocator spelling; proposed K0 call-policy test, NOT RUN.
prakriya helper() {
    nivartanam nirmmita(64)
}
```

Its allocation is lexical persistent storage under the settled policy. Nevertheless `outer = helper()` inside a K0-checked function is rejected by the minimal value-only call rule: the body returns a Reference. That rejection is conservative, not a false assertion that the returned pointer is scratch or already dangling. Replacing the body with `nivartanam 15` permits verification as a value-only helper.

### Acceptance matrix

| ID | Case | Expected K0/lowering outcome |
|---|---|---|
| T01 | Direct region Reference assigned to an outer variable | Reject with origin and retaining-use locations |
| T02 | `outer = note + 64` within valid allocation extent | Reject escape; retain Reference origin through addition |
| T03 | Same-region immutable alias plus bounded constant offset | Accept after null proof |
| T04 | Reference XOR/float conversion/truncation or integer-to-address use | Reject unsupported reference operation |
| T05 | Store Reference through local alias of outer buffer | Reject reference-in-memory store |
| T06 | Store Reference into same-region scalar buffer | Reject too: no pointer-bearing heap in K0 |
| T07 | Read scalar from checked buffer and assign/return it outward | Accept |
| T08 | Read unknown raw memory and use loaded qword as address | Reject |
| T09 | `suchi_khip` or other retaining call supplied a Reference | Reject unsupported reference interface; do not infer safety from integer return |
| T10 | `helper()` unknown or returning an allocation | Reject unverified/non-value result, even with zero arguments |
| T11 | Exact-body verified scalar helper | Accept; no runtime tracking overhead |
| T12 | Unknown indirect call, FFI, inline assembly or mutable global access | Reject in checked function |
| T13 | Mutable Reference or pointer-valued branch/loop carry | Reject; no incomplete join analysis |
| T14 | Null test in only one non-dominating arm | Reject later unproved access |
| T15 | Negative/out-of-range constant access or unknown dynamic index | Reject before emitting access |
| T16 | Nested normal region exit | Restore inner mark only; outer buffer remains valid |
| T17 | Scalar return from two nested regions | Evaluate first, restore both/outermost exited mark, preserve result |
| T18 | Reference returned directly or in `siddhi`/`dosh` | Reject |
| T19 | Break and continue leaving a region | Cleanup before correct loop destination |
| T20 | Break/continue within inner loop that stays in region | No premature surrounding-region cleanup |
| T21 | `prasar` failure and locally handled failure | Cleanup only on escaping edge; preserve value/status and branch range |
| T22 | Persistent allocation between region entry and exit | P remains advanced; only S rewinds |
| T23 | Exact gap, oversize, alignment overflow and zero size | Correct success/failure; failure changes neither cursor |
| T24 | Million-iteration positive example | Correct checksum and bounded scratch high-water; record actual metrics |
| T25 | One region surrounding the whole allocation loop | Accumulation or logical OOM, not fictitious iteration cleanup |
| T26 | Reset/reuse after nonzero data | Specified zeroing preserved |
| T27 | Unsupported separate-object call metadata or recursive summary cycle | Explicit rejection, never assumed safe |
| T28 | Identifier named `kshetra` in legacy source; no-region source path | Contextual syntax/compatibility preserved; no new Step-3/4 checker restrictions outside opt-in use |

Do not count rejection of the unimplemented keyword as a successful escape test. First compile/run a supported positive region program, then require the intended diagnostic for each negative case.

The K0 set is much narrower than the general 28-case ambitions of Round 134. Some formerly proposed operations now deliberately expect an unsupported-operation error rather than a permissive analysis. That is a specified first implementation boundary, not a claim that all of the general design is finished.

## 8. Integration and release recommendation

**Recommendation: accept this as a concrete restricted Steps-3/4 specification candidate, not as evidence of implementation readiness or a completed safety proof.** The owner's next acceptance choice is explicit: adopt K0's restrictions, or budget a larger checker. Do not ship a permissive block under a 'safe' label with only a documented danger note.

Implement in reviewable units: region identity/frame slots; shared exit cleanup; K0 checking before emission; diagnostics and negative cases; then controlled integration with Steps 0–2. No code is changed by this handoff.

Compatibility gates need to distinguish stages. Step 1 intentionally changes allocation code, so blanket binary identity against v261 cannot be promised for allocations. Preserve old accepted-source behavior and expected outputs where specified. To detect unintended Step-3/4 changes, compare no-region programs against the same Steps-0–2 baseline: the new block checker should emit no extra region machinery for them. Never edit goldens solely to hide changed behavior.

The existing `kosh` plan is an input, not something this checker certifies. K0 initially refuses pointer-bearing collection interoperation instead of attempting to prove that every legacy collection alias is safe. Outer-`kosh` growth still has persistent routing when the operation is supported; region cleanup must never rewind its allocations. Step 0's freelist correctness and alias contracts require their own tests, not this document's approval.

No whole-server bounded-memory promise follows just from a region around a request. Persistent allocations outside the lexical region, other resources and unsupported helper effects still exist. K0's value-only/no-persistent-allocation helper whitelist is deliberately narrower than arbitrary request handling.

## 9. Evidence, assumptions and execution status

### Pinned repository evidence

- **R1:** `Sarvam-to-ChatGPT/ROUND-135.md`, blob `56e041a325f167c890c5aac12b5c6eb84f397bda`: accepted Steps 0–2, lexical two-cursor routing, requested exit/cost/check specification.
- **R2:** `docs/decisions/MEMORY-UNIQUE-HYBRID.md`, blob `967b117eec9ecd59d6d7424458c4bab2c7f67c94`: older synthesis; not silently treated as matching the revised brief.
- **R3:** `ChatGPT-to-Sarvam/ROUND-134-KSHETRA-REVIEW.md`, blob `e2f67d16e37b768fa8c374833b17cbee84b4245f`: previous returned critique and conditional block recommendation; opening re-read at the pinned head, full prior report available in conversation.
- **R4:** `src/sutram_compiler.asm:14420–14710`, blob `e64bcce50e1e05a2a0a9fca9f337b8c0b7b93345`: ordinary/no-value/main returns, type conversion, epilogue, halt and existing bounds-error machinery.
- **R5:** `src/sutram_compiler.asm:14005–14165`, same blob: break/continue JMP patching and saved counted-loop update target. Additional inspection at 13570–13780 confirmed branch emission and inline-machine-byte handling.
- **R6:** `src/r25_phal.inc:143–253`, blob `a36bd286aa6beea0b854576945e6874ba8835af0`: direct `prasar` failure return, RAX/RDX result/status, short-branch limit and handler distinction.
- **R7:** `lib/suchi.smlib:46–100`, blob `a6834561bf086f163c933bf18afe9e7d310eaec3`: returned header/backing graph, persistent backing mutation and retaining append despite scalar return.

The repository's Sanskrit-only directive and documentation-only return permissions are retained. This was targeted reading, not another census of every allocation or a claim that all 305 routines have been re-verified.

### External reference, separately identified

- **W1:** LLVM Language Reference Manual, Pointer Capture and `captures` attribute, checked 29 October 2026: https://llvm.org/docs/LangRef.html#pointer-capture . Used only to distinguish capture through values/returns/calls and address versus access provenance. LLVM's rules are not silently substituted for Sutram's language contract. The K0 rules, proof outline, restrictions and cost estimates are proposals in this report, not claims sourced from LLVM.

### Execution and return status

- **Completed:** source-grounded Steps-3/4 design; priced cleanup; explicit value classes and restrictions; call boundary; soundness argument with assumptions; Sanskrit diagnostic proposal; 28 proposed acceptance cases.
- **NOT RUN:** Sutram compiler, checker implementation, native Linux/Windows execution, allocation-failure probes, benchmarks, regression/proof suite, guard or new acceptance cases. No native toolchain was invoked in this read-side round.
- **Not measured:** the NASM line budget, compiler instruction ranges, real execution cycles or acceptance rate of existing programs under K0.
- **NOT APPLIED:** compiler, library, tests, tools, canonical docs, language packs, Windows folders, workflows or backups. All design snippets remain proposals.
- **Delivery scope:** one new Markdown report under `ChatGPT-to-Sarvam/`, followed by GitHub readback and commit-diff verification; stop after Round 135.
