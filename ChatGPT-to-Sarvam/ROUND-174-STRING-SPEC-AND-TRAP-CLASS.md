# R174 — text semantics, ownership, and systematic trap discovery

Read-side specification and audit, 2026-11-02. Pinned main: `208209a2875a3d2f5733500c8a5310673e851fef`, compiler v286; compiler blob `8445940ec60661951f3b8c6e47718a5ff8e3e1a9`.

**Decision:** text equality compares bytes without coercion; text addition produces a fresh immutable value. NUL termination is sufficient for the first implementation. Default concatenation results should have process lifetime, with their retention cost stated explicitly. Block-owned concatenation should be an explicit later operation, gated on complete escape checks. This is a proposed contract, not a claim that v286 implements it.

## Current implementation boundary

Claude R104 reports 273 suite passes, 551 changed ELF binaries with the same output/exit under its runner, 132 identical refusals, and gates 59 PASS / 1 FAIL / 1 NOT-RUN. Those are attributed results, not reproduced here. The runner's no-input `report_plain` segfault on both sides remains a limitation of that comparison. The installer mismatch and native Windows execution are still open.

I read the v286 compiler and Claude's additional patch. The hidden stack global now participates in ordinary module relocation, resolving the reported direct/object/separate mismatch. **It does not fix R173's string classification defects:** `.gs_assign` still calls `rfx_note_value` before examining the RHS; an AST_BINOP clears the destination flag; the two integer fast paths still reject string ADD operands differently from the generic path; `rfx_is_int` still treats unknown non-float expressions as integers. The stack threshold is still the fixed 8,339,456-byte delta. Do not treat application of FIXALL as closure of those findings. Object-mode exclusion from the original patch is now superseded; PE still excludes the guard.

The prototype `samaan` demonstrates the comparison algorithm on its three samples. Its 200-iteration limit is unsuitable for general equality: identical longer strings can return false. Removing the cap is correct only for valid, live, terminated operands. Neither the prototype nor the existence of `akshar` establishes type or lifetime safety for arbitrary addresses.

## WS1 — proposed normative text contract

### Values and types

For this first stage, Text is an immutable sequence of nonzero bytes followed by one terminating zero. Source text normally contains UTF-8, but equality is exact byte equality; no implicit normalization, case folding or locale comparison occurs. Length is in bytes. Raw data with embedded NUL is a byte buffer/view, not this Text type. Literal validation must reject an embedded NUL in a Text value rather than silently dropping its suffix. UTF-8 validity checking is a separate boundary contract; byte equality does not validate encoding.

Text, integer, dasham, raw address, byte view, container and unknown must be distinct compiler classifications even when their machine representation is eight bytes. A nonzero word is not evidence of Text. Literals and owned concatenation results are Text; raw allocations and pointer arithmetic are not automatically Text. Converting a raw buffer requires a bounded conversion that checks for termination within the declared readable capacity and copies into owned immutable text. That conversion cannot validate a forged pointer's readability; only a valid buffer capability can supply it. Existing raw builtins remain explicit low-level operations with caller obligations.

For the first safe implementation, infer a binding's type from its initializer and require later assignments to preserve it. Incompatible assignments receive a compile-time diagnostic. This deliberately changes v286's permissive mixed reassignment and needs migration evidence. It is simpler than pretending that last code-generated assignment is flow analysis. Unresolved overloaded operations must refuse; unknown must never mean integer. Functions need parameter/result contracts, including indirect calls and separate-module interfaces; within a whole program, inference may solve them, but polymorphic use must be specialized deliberately or rejected. Fields and collection elements need declared/inferred element types too. A partially implemented version must name unsupported shapes explicitly.

### Operator table

| Operands | `==` / `!=` | `+` |
|---|---|---|
| Text, Text | Exact content equality / its complement, normalized 1 or 0 | Fresh concatenated Text |
| Text, integer; integer, Text | Compile-time type error; no formatting for comparison | Decimal formatting followed by fresh concatenation |
| Text, dasham or container | Compile-time type error | Refuse until an explicit formatting contract exists; use an explicit conversion |
| Text, raw pointer/view | Compile-time type error | Require an explicit bounded conversion or slice API |
| Unknown operand | Resolve type first or refuse | Resolve type first or refuse |
| Numeric operands | Existing specified numeric semantics | Existing specified numeric semantics |

The integer addition rule preserves the intent of existing constant forms such as `"Year: " + 2026`, and extends that same rule to variable integers. Formatting is signed base ten, no grouping or leading plus, zero is `0`, and minimum signed integer must format without overflowing an intermediate negation. It does **not** make `"42" == 42` legal. Existing text-variable-plus-integer pointer offsets must migrate to explicit raw/view operations. This is a compatibility change, not something to conceal in constant folding.

Text subtraction, multiplication, division, modulo and bitwise/shift operators refuse. For this initial contract, text ordering also refuses; callers may use a documented explicit byte-ordering function. Conditions on Text should refuse and suggest an explicit empty/nonempty check. That avoids both an accidental address test and an unannounced adoption of another language's truthiness. These choices are new policy; the old outcomes alone do not establish bugs without that policy.

### Equality semantics and lowering

Evaluate the left operand once, then the right operand once, and preserve both values across nested calls. For valid Text, compare corresponding bytes until a difference or a shared terminator. Equal empty strings are equal; a proper prefix is unequal; there is no fixed character cap. No allocation is needed. `!=` is exactly the complement of `==`.

Keep `vartani_tul`'s existing 0-equal/1-unequal convention. Its loop can implement the operator with result inversion for `==`. Integer equality must select its numeric emitter at compile time; it needs no runtime string-tag branch or byte loop. Verify its generated code and performance instead of promising a measured zero slowdown from the design alone. A shared text helper versus inline loops is a code-size/call-overhead choice; neither changes semantics.

Immutable Text prevents a right-operand call from mutating a left operand's bytes behind the comparison. Mutating raw aliases to owned Text violates the safe API contract and must not be exposed as an ordinary typed operation. Merely tagging today's writable pointers as immutable is insufficient; copy/adopt boundaries and write checks are required.

### Concatenation and errors

Evaluate operands left-to-right exactly once. Determine both lengths; validate checked `L + R + 1` and any allocator alignment/metadata calculation before allocation. For integer formatting include its decimal byte length in the same calculation. Allocate nonoverlapping storage, copy both byte sequences, append NUL, then publish the new value. `s = s + s` reads the old value throughout; it does not mutate either input and updates the binding only after success.

Runtime allocation failure, size overflow, or exhausted allocation budget emits a distinct, stable diagnostic and terminates with nonzero status in the initial implementation. Do not promise catchable errors before such a facility exists. Compilation errors must not leave an output that can be mistaken for a successful executable. On runtime failure the destination has not been assigned and inputs have not been modified; operand side effects already performed are not rolled back.

The result is a fresh logical value, including when one side is empty. An implementation may fold literal-only operations into immutable static storage because pointer identity is not an observable Text operation. Folding must preserve content, evaluation order and effects, and enforce the same type/format rules. Dynamic concatenation remains an allocation operation with documented budget charging; do not optimize away its observable budget failures casually.

### Where results live: choose the conservative first stage

**Default `+` uses persistent storage owned by the process, not expression temporaries or the nearest `mandapa`.** Its result may be returned, passed to a callee, assigned to an outer binding, or stored in a typed container without dangling at block exit. Copying the operand bytes also means a result can outlive borrowed inputs, provided those inputs were live during the copy. Literals are static. Function return is not an implicit deallocation point for either category.

This choice has a real price: reassignment drops the old reference but does not reclaim its allocation; persistent storage is retained until process exit. Repeated growing concatenation can accumulate quadratic total copied bytes and retained payload. Do not describe it as automatic memory management or bounded memory usage. A checked builder with reusable capacity is the suitable later loop API.

Each dynamic result needs at least `L + R + 1` payload bytes, plus the allocator's overhead/alignment; per-result OS mapping would add mapping/page overhead. Prefer an allocator-backed persistent arena when available, but allocator choice does not change ownership. No C runtime, GC or wider value is intrinsically required. Hidden emitted allocation helpers still execute at runtime; “no external runtime dependency” is the precise claim.

**Budget rule for the proposed feature:** if executed under an active bounded block, charge the full requested aligned allocation including allocator metadata to that block and every bounded ancestor, even through called functions. The charge is cumulative for that block activation and is not refunded by dropping a reference. This limits that activation's allocation, not the total retained process memory across repeated activations. It requires propagated budget context; v286's lexical `nirmmita` checks do not already implement it. Until this is implemented, refuse allocation-producing text operations under a budget rather than silently bypassing `parimita`. A cumulative process allocation ceiling is a separate policy and should be configurable, not an invented universal constant.

**Explicit block-owned text is a later opt-in API, not an undocumented change in `+`.** Such a result dies when its owner block ends. Returning it, storing it in a longer-lived container/global, retaining it in a callback, or assigning it into an outer binding must refuse unless copied into a longer-lived owner while still valid. Borrow-only calls may use it transiently. Unknown callees must refuse that borrow until a no-retain contract exists. The current check's known call-through gap prevents claiming these guarantees today. Region transfer/promotion requires an explicit ownership design; returning a pointer does not transfer its storage. No new Sanskrit keyword/API spelling is prescribed here.

On Windows, process-lifetime allocation remains the same semantic contract; lack of block reclamation must not be used to justify accepting otherwise invalid escapes. Native Windows acceptance remains a separate test requirement. In allocator-free/freestanding configurations, dynamic concatenation requires an explicitly supplied allocator or refuses; comparison remains allocation-free.

### Is a length prefix worth it?

**NUL is sufficient, and I recommend retaining it for stage one.** It keeps an eight-byte reference and existing raw builtin interoperation, but requires O(L+R) length discovery before copying and cannot represent embedded NUL as Text. Equality still works without length discovery by comparing in lockstep.

An eight-byte prefix adds eight bytes per object before padding, makes length lookup O(1), and permits early rejection of unequal lengths. Equal-length equality still scans. It does not solve typing, lifetime, overflow, mutation or invalid-pointer safety. A 16-byte pointer/length view supports bounded slices without an owned header, but changes ABI/storage handling and still requires ownership information. Never read `[ptr-8]` from today's arbitrary pointers.

Adopt a prefix later if length/concatenation-heavy measurements justify the storage and migration costs. If embedded NUL becomes a requirement, move to length-bearing text deliberately and update printing/interoperability too; adding a prefix while retaining NUL-only printers is not sufficient.

## WS2 — the eight traps are not eight independent root causes

The family is **machine words reaching an operation without an established semantic type/contract**. The old five additionally include initialization and resource-exhaustion failures; one type checker cannot solve every one of them.

| Muse item | Classification relative to FIXALL | Contract and action |
|---|---|---|
| 1. SUB/MUL/DIV on strings | Same operand-domain failure as string ADD | Reject typed Text in numeric operators; cover every emitter, including immediate/register paths. |
| 2. String ordering by address | Same representation/semantic comparison confusion as string equality | Refuse operators initially; explicit byte ordering remains available. |
| 3. Empty-string condition is true | Same unchecked coercion boundary, but **policy question**, not intrinsically a wrong answer | Choose explicit Text conditions as errors; do not assert that empty must be false without a specification. |
| 4. Separate equal-content koshes compare unequal | Same identity-versus-content ambiguity, but **container equality is a distinct contract** | Identity equality can be legitimate. Keep/clarify the existing container contract pending a deliberate decision; do not recursively compare containers as part of the text fix. |
| 5. Printing a kosh prints an address | Same type-erasing output/overload problem as `likha`, different from raw-write arity | Define container formatting or refuse unsupported formatting; do not silently expose an address as its content. |
| 6. Storing string in mala then printing integer bits | Type information lost at a storage boundary, closely related to the old operations but a different enforcement site | For integer mala, reject Text store; typed Text collections would preserve element type and lifetime. |
| 7. String plus dasham literal | Same ADD domain/coercion failure; constant folding covers only some shapes | Refuse until explicit float formatting is specified. Do not inherit arithmetic on an address. |
| 8. Dasham bits stored into mala | Same storage-boundary class as item 6; already known, not a new independent root cause | Reject incompatible store or require an explicit specified numeric conversion; raw bit reinterpretation must be explicit. |

**Version correction for item 7:** Muse's observation is on v285. In v286, `.ge_binop` calls `rfx_check_str_binop` before float lowering. For direct `"x" + 2.5`, the literal is recognized as Text and `rfx_is_int` rejects the float operand, so source inspection predicts `E_VARTANI_CAT` now. This is **NOT RUN — no toolchain**. The untracked-parameter variants remain a different risk. Do not carry “not fixed” forward for every syntactic shape without rerunning it.

`E_LIKHA_TRAYA` belongs to ambiguous overload selection; `E_VARTANI_TUL/CAT` to operand-domain confusion; `E_MULYA_VINA` to initialization state; `E_GAHANATA` to resource bounds. Definite assignment, type resolution and resource checks need separate analyses and tests, with a shared rule: do not emit an operation whose preconditions are unknown.

### Systematic discovery plan

Use a **specification-driven type/operation matrix plus generated boundary-crossing programs**, not a collection of randomly chosen examples. This is a proposed test design for the implementation owner; no generator or source tests are installed by this round.

1. Maintain one table of allowed operand types, result types, conversions, effects and failure stage for each operator/builtin/store/call/condition. Include every enum operation, unary form, compound lowering and indexing operation. Unsupported and unknown combinations explicitly say “compile error.” Tie each dispatch arm to a semantic rule ID; inspect any arm without one. Run the same validation before folding and before any optimization.
2. Enumerate kinds: integer, dasham, Text, raw pointer, bounded view, mala, kosh, function value, unknown. For each binary operator generate the ordered type pairs (10 by 10 = 100 cells per operator before contexts); use compatible representative values, and independently assign the expected result/error from the contract. Containers need element-kind coverage, not just a container flag.
3. Cross the risky cells with provenance: literal, initialized local, alias, reassignment, parameter, return, global, field, index, branch join, loop-carried value, indirect call and separately compiled function. Include local/global shadowing and recursive call summaries. Make the entire positive core matrix exhaustive; use pairwise combinations for large secondary dimensions, then exhaustive targeted combinations around every discovered bypass. Publish exercised cells and missing cells, not just a pass count.
4. Apply semantics-preserving transformations: replace a literal by a same-typed local; wrap a value in a typed identity function; move it across a module boundary; add unused locals to force spills; switch supported optimization modes; add an unreachable assignment; compare inline expression versus assigned temporary. Results and legality should remain the same. Include `s=s+s`, `s=s+"cd"` and two-branch joins specifically. An old buggy compiler is not the oracle.
5. Use independent host-side byte-string and numeric models for accepted programs. Keep generated inputs bounded and valid, and generate compile-negative programs separately. Compare output bytes, runtime exit, compile exit and diagnostic identity/location. Use timeouts and record signals/timeouts as failures, never as successful refusals. Syntax/parse failures do not count as successful type rejection.
6. Add property cases: reflexive/symmetric/transitive Text equality; `!=` complement; empty concatenation identity; byte length and prefix/suffix preservation; unchanged inputs and self-concat; once-only left-to-right side effects. Associativity of concatenation applies to resulting bytes when allocations succeed, not to budget failure timing. Include multibyte text, lengths 0/1/199/200/201, allocator boundaries, very long common prefixes, and integer formatting at both signed extremes.
7. Add ownership/resource cases separately: allocation failure and overflow injection, bounded nested calls, repeated block entry, outer stores/returns, unknown callees, and smaller supported stack environments. Exercise every exit form. Raw-pointer invalid-memory probes are isolated tests with explicit unsafe expectations, not ordinary valid Text inputs.
8. Shrink every failure while preserving its expected semantic rule and actual failure. Seed the regression corpus with the minimized program and its transformation pair. Mutation-check the checker: deliberately omit a type gate, treat unknown as integer, move type update before RHS, bypass validation in a fast path, or skip a budget charge. Require the targeted tests to detect each seeded defect; undetected mutants expose test gaps.

Record compiler source/build hash, flags, target, source hash, rule ID, operand kinds, provenance, expected outcome, actual compile/runtime outcomes, and transformations. For old/new regression DIFFERs separate intentional semantic changes, migration changes and regressions. Do not overwrite old goldens wholesale. The 683 existing programs remain valuable regression coverage but cannot establish closure of a class they barely exercise.

## WS3 — proposed first README paragraph for current v286

> Text support in Sutram is still incomplete. Text literals use zero-terminated bytes; `vartani_tul(a, b)` compares their contents and returns 0 when equal and 1 when different. Do not rely on `==`, `!=`, or `+` for string variables yet: some forms are rejected, while forms the compiler does not recognize can still compare or add addresses. Constant string concatenation, including integer constants, already works, but general string concatenation is not implemented. `vartani_cat(dst, src)` appends into an existing writable buffer, does not allocate or check capacity, and must not be used with a literal destination or overlapping inputs. Content equality and fresh-result concatenation are the intended operator behavior, pending complete type and allocation rules.

This paragraph describes current behavior, not the proposed contract above. Replace it only after the new behavior is verified across the promised shapes. It is supplied here for Sarvam's integration; README itself is unchanged.

## Acceptance and handoff

Claude owns source implementation under R105. Prioritize shared semantic classification, RHS-before-destination updates, and consistent fast paths before wiring in byte loops. Implement and document persistent result allocation plus budget handling before claiming general `+`. Preserve explicit builtin conventions and migrate raw pointer offsets/three-argument raw writes deliberately. Confirm direct/object/separate parity and platform-specific behavior independently.

Read-side checks completed: current assignment, AGENTS/master/charter, v286 compiler, README, Muse R100, Claude R104 plus its corrective diff, and Claude's R105 brief. No source, library, tests, tools, README, Windows or frozen-pack files were modified by this round.

Native build: **NOT RUN — no toolchain** (`command -v nasm` found none). Operator probes: **NOT RUN — no toolchain**. Generated matrix/property/mutation tests: **NOT RUN — design only**. Suite/proofs/guard/gates: **NOT RUN — no toolchain**. Native Windows: **NOT RUN**. Performance and memory measurements: **NOT RUN**. CI: **NOT RUN**.

All current behavior predictions are source-derived. All policy, type, ownership, budget and discovery mechanisms proposed here require implementation and independent acceptance; this document does not certify them as shipped.
