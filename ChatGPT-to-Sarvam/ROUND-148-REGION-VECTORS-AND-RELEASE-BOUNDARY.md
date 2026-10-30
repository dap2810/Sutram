# Sutram ROUND 148 — safe region vectors need identity, not just an address range

**Date:** 30 October 2026. **Pinned main:** `3f365564cbdc59335b5c24d226b3e62c97bfca03`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-148.md`, blob `5943a5ce451174173b8ba74c474926ca36205a53`.
**Return:** `ChatGPT-to-Sarvam/ROUND-148-REGION-VECTORS-AND-RELEASE-BOUNDARY.md`.
**Observed compiler:** v273. **Role:** source-grounded design review, not implementation or native acceptance. All new representations, costs and gates below are proposals. Sanskrit remains the only active language; technical type notation below is NOT proposed English source syntax.

## Answers first

1. **A safe vector in a region is feasible.** My choice is an explicit, distinct region-owned vector with an opaque, generation-checked handle and checked indexing, initially limited to numeric elements. Keep legacy `kosh` unchanged. Add copied, owned strings next rather than admitting arbitrary raw-pointer elements. This is an extension beyond the earlier scalar-only K0 proposal, not a claim that v273 already implements it.
2. **Implicit allocation into the block alone is insufficient.** It decides when backing storage is reclaimed; it does not prevent aliases, a returned handle, or references to shorter-lived elements from outliving that storage. A separate type without enforced access/call rules is also insufficient.
3. **Reject address-range-only checking as a temporal-safety solution.** After reuse, an old pointer and a valid new pointer can have exactly the same address. A predicate seeing only that address and the current range cannot distinguish them. Carry an independently preserved allocation/region identity, or prevent the stale reference statically.
4. **Choose a hybrid, not “cheap analysis that misses cases.”** Statically distinguish handles, numbers and raw pointers; dynamically validate handle generation, live owner and bounds before accessing vector storage. This costs at checked vector operations, not every scalar expression or every memory access in the whole language. No measured nanosecond claim is made.
5. **For v1, ship a qualified small feature rather than an unqualified large one.** Scalar-only is a defensible fallback if its accepted subset, bounds and exits are actually enforced. The current advisory/raw-pointer behavior is not that guarantee. Otherwise keep `mandapa` experimental or outside the stable teaching surface until a qualified scalar or vector subset exists.
6. **The single release risk I prioritize is an unenforced safe/unsafe boundary:** ordinary unchecked raw memory can invalidate the assumptions of the supposedly checked subsystem, including its metadata. I cannot establish that nobody has mentioned this before. It is a cross-cutting release risk, not a newly executed metadata-corruption exploit.

## Source baseline and corrections

R75 reports direct scratch-address insertions and aliases being refused, but `kosh_push(k, adr(buf))` compiling and subsequently reading the next block's data. This is an acknowledged call-result provenance gap, not evidence that every dynamic container is intrinsically impossible to check. The same report records the positive-to-positive size-wrap witness corrupting an outer buffer and corrects its earlier claim about raw-buffer bounds. Those executions are Claude's, not mine. [R2]

The inspected compiler represents ordinary `kosh` as a user data pointer with length at `ptr-16` and capacity at `ptr-8`. Growth either extends in place or allocates/copies and updates the named variable. That representation does not provide a stable indirection shared by every possible pointer copy. A new checked vector must not silently inherit its raw-pointer ABI. [R3]

**One correction to R75's wording:** typed `kosh` parameters exist. The source has `PARAM_KOSH`/`PARAM_KOSH_DASHAM` and typed-argument handling; `kosh_push` specifically rejects growth through a by-value parameter because replacing the callee's pointer would not update the caller. “A kosh cannot be a parameter” is too broad. This distinction matters to a new handle ABI. [R2,R3]

The existing arena has persistent storage growing upward and scratch growing downward. It is not a set of independently growable per-region heaps. Its source includes historical comments about earlier stages; the live mechanism and target gates, rather than those banners, govern the design. The proposed vector must handle nested-region growth explicitly. [R4]

The brief's “four parser defects” and “15 surviving mutants” are its framing. I have not independently classified the mutation campaign in this round; surviving mutations are not automatically fifteen distinct production defects. This report does not claim a new count or exhaustive parser closure.

## WS1 — compare the proposed approaches

### What “closes the hole” means here

A checked access must never read or overwrite an unrelated allocation because a vector or one of its elements refers to expired or relocated storage. Reclamation must also preserve live parent objects. This requires both spatial bounds and temporal identity. Merely making a use-after-free crash sometimes is not fail-closed checking: refusal or a defined pre-access error must happen before the invalid payload access.

| Approach | Does it close the hole? | Cost and breakage |
|---|---|---|
| **A. Any legacy `kosh` created in `mandapa` becomes scoped automatically** | **Not alone.** Its data may be reclaimed on exit while an alias, return, global or helper retains the pointer. A scoped outer vector can still contain a reference to an already-ended inner region. | Cheap routing/cleanup, but growth, references and exits remain substantial. Silently changes existing persistent lifetimes and alias behavior; existing source that happened to declare a kosh inside a block can break. Reject this as an automatic legacy change. |
| **B. Distinct region-bearing container type** | **Yes, conditional on enforcement.** Its identity, element kind, access operations and call boundary must be represented. Lifetime parameters plus a sound conservative checker can reject unsupported escapes; merely writing a region field into an otherwise raw object cannot. | New representation and typed call ABI, plus explicit migration. Existing untyped helpers cannot accept it by pretending it is one integer pointer. Static proofs can remove checks, but unknown cases must be rejected rather than treated as clean. |
| **C. Test an address against the scratch range** | **No, as stated.** It can detect some forbidden outward stores or accesses to presently inactive space, but not same-address reuse, object bounds within a live range, or bypasses through uninstrumented operations. | A few comparisons per instrumented site; it needs complete coverage and pointer/value classification. Checking all qword values also rejects ordinary integers that happen to resemble addresses. The whole 1 GiB reservation includes persistent storage too, so membership in that reservation is not equivalent to scratch ownership. |
| **D. Opaque generation-checked handles, combined with B** | **Chosen.** Resolve a handle through still-valid metadata; reject dead/reused identities and bad bounds before touching payload. Aliases share one descriptor even when backing storage moves. This closes stale-vector access within the enforced interface. | Metadata, indirection, checked operations and a distinct ABI. It introduces emitted runtime support, but needs no GC, VM or external managed runtime. Raw casts, arbitrary pointer operations and unchecked callees remain outside the guarantee. |
| **E. Owned contents rather than arbitrary borrowed pointers** | **Useful simplification, combined with D.** Numeric elements are values. String insertion can copy validated bytes into the owning region and store offsets/lengths, not someone else's raw pointer. | Numeric elements stay compact; text insertion costs O(bytes copied). It changes identity/sharing semantics deliberately. It is not zero-copy support for arbitrary pointer graphs. |

Dynamic length does not rule out static lifetime reasoning. Conversely, lexical block depth alone is not allocation identity: recursion and sibling block activations can reuse a depth. Either approach must define a sound accepted subset and the interfaces through which references move.

### Why a range predicate cannot solve reuse

Consider one address `a`:

```text
R1 allocates an object at a; an old reference p = a is retained.
R1 ends; its space is rewound.
R2 allocates a different object at a; its valid reference q = a.
At this moment p == q as raw address bits.
```

Any check whose inputs are only the address and the current active range receives identical inputs for p and q. It cannot accept q while rejecting p. Checking all live region ranges, or keeping a shadow map indexed only by the address, does not recover the old reference's missing identity. The reference must carry its original generation, or the language must prevent the stale reference from existing/being used.

A range check **at stores** is different from a check **at dereferences**. A fully mediated, typed store rule can prevent shorter-lived references entering longer-lived destinations. It does not intrinsically require a check at every later read, but it requires every retaining operation, return and call boundary to be covered. That is exactly what ordinary raw helpers currently evade. A dereference-only range check is not a substitute.

Likewise, `mprotect` or poisoning after release is not a complete reuse solution: once storage is made accessible again for the next object, a stale address can become readable again. Keeping every address permanently unreused avoids that ambiguity at the cost of abandoning bounded region reuse.

## Concrete proposal: a distinct checked region vector

### 1. Public contract and compatibility

Use the internal design notation `RegionVec<R, i64>` / `RegionVec<R, f64>` below. It is **not valid Sutram syntax**, and this report adds no English keyword or approved Sanskrit API name. Choose an explicit source declaration/annotation later, under the Sanskrit vocabulary policy. Do not reinterpret every existing `kosh` by placement alone.

The new object belongs to one dynamic region activation R. Its operations are create, length, capacity, indexed get/set, push and pop; no raw data pointer, arbitrary integer conversion, raw slice or address-of-element is exposed in the initial version. Numeric elements are returned by value. Handles can be copied; copies name the same vector, and mutation is explicitly shared.

Reject statically evident lifetime misuse where practical. For cases that reach runtime, a dead handle is an inert token: using it produces a defined error before payload access. **This is checked dynamic lifetime safety, not a promise that every escaping handle is rejected at compile time.** Returning a token cannot extend the region's lifetime. Do not reuse the stronger “all escapes refused at compile time” wording for this design.

Legacy `kosh`, `nirmmita`, raw-pointer helpers and their existing representation remain unchanged outside the new checked interface. Passing a new handle to an old one-qword pointer parameter is a type error, not an implicit conversion. Unsupported target/mode combinations must be rejected or explicitly experimental, not silently compiled with reclamation disabled under the same guarantee.

### 2. Example metadata layout — proposed, not measured

```text
Handle:       { object_slot:u64, object_generation:u64 }                16 bytes
Object entry: { generation, owner_region_slot, owner_region_epoch,
                kind, data_offset, length, capacity, flags }          64 bytes
Region entry: { epoch, active, parent_slot, parent_epoch,
                saved_scratch_cursor, saved_descriptor_top }          48 bytes
```

These are eight-byte fields and an illustrative ABI, not a finalized memory layout. Metadata tables must remain valid while an old token can be checked; **do not put the only descriptor in scratch memory and dereference it before checking whether its region is alive**. Place bounded metadata storage outside the rewound payload. A 4,096-entry object table would reserve 256 KiB, excluding region records and data; that is an example budget, not the chosen project limit.

Give each reused object slot a fresh, non-wrapping generation. Give each dynamic region activation a fresh epoch. A generation copied into the handle is independent of whatever object later occupies the slot. Never obtain the supposed old generation by reading a recycled descriptor through a raw pointer. On counter exhaustion, table exhaustion or region-stack exhaustion, fail explicitly; do not wrap or silently stop checking.

The active region stack is a runtime stack. Do not confuse its capacity with the compiler's lexical nesting limit: recursion creates new activations even at one lexical block site. No per-object deletion is needed initially; region exit resets the descriptor frontier and scratch frontier, with new generations required on subsequent reuse. Thus metadata storage can be bounded by peak simultaneous live objects rather than total objects ever created.

### 3. Validation order

Before indexed access, inspect only the permanent metadata table until the token is validated:

```text
check object_slot is within the issued metadata range
check entry.generation == handle.object_generation
check owner_region_slot is valid, active, and has entry.owner_region_epoch
check entry.kind matches this operation
check 0 <= index < entry.length <= entry.capacity
check/maintain the allocation extent and checked index-to-byte arithmetic
resolve the current data_offset; access the element
```

All failure paths must precede the payload load/store. Metadata integrity is an assumption enforced by the safe interface, not a property obtained just by moving the table to `.bss`. Compiler-private access, no raw casts and bounded operations matter. An arbitrary unchecked write in the same process can still corrupt memory; see WS3.

A handle passed through a **checked, typed** helper retains both words. A helper that returns or retains it cannot launder it into an untracked integer address. Later operations still validate it. This avoids requiring a precise escape summary merely to make dynamic handle use fail closed. It does require typed signatures/call lowering and rejection of unverified raw ABI crossings. Scalar helpers returning numbers and helpers returning handles have different result kinds.

### 4. Growth and aliases

A vector's descriptor is stable; its backing allocation may move. On growth, allocate checked new storage, copy only initialized elements, then update the descriptor's data offset and capacity. Every alias resolves through that descriptor and observes the same vector. No alias holds a public raw element pointer. Failed growth must not publish a new length, capacity or data offset.

Evaluate the element being inserted before growth and preserve its numeric value safely; do not keep a temporary raw pointer into a backing array across a call that might grow it. If element references/slices are later added, they need an explicit invalidation/identity policy rather than automatically inheriting handle stability.

For a first implementation, retain old backing blocks until the region closes. With **strict doubling**, no shrinking/repeated tiny reserves, and a fixed-width element of w bytes, capacities `C0,2C0,...,C` consume less than `2*w*C` payload bytes in total; alignment and metadata are additional. Arbitrary reserve/shrink policies invalidate that simple bound. All retired blocks are reclaimed for reuse at region exit; this is not an OS unmap or a promise of immediate RSS reduction.

**Critical nested-region restriction:** do not allocate new backing for an outer vector from an inner region's scratch cursor. The inner rewind would free the supposedly outer buffer. In the minimal design, operations that change length/capacity require the vector's owner to be the currently innermost active region. A child may read an ancestor vector and overwrite an existing numeric element, but cannot push/pop/reserve it. The restriction is conservative and visible; check it before any change. General ancestor growth needs a separate per-region chunk allocator or promotion/copy protocol, not a one-line reroute.

This restriction applies to the **new** type, not to existing persistent outer-kosh compositions already measured by the project. It also explains a real cost of using the current single descending scratch frontier rather than independent region heaps.

### 5. Contents: numeric vectors first; useful strings without raw-pointer graphs

First support numeric elements only. A scratch-reference value cannot become a numeric element by implicit conversion, and an integer cannot be indexed as a pointer within the checked interface. Copying `buf[i]` is allowed only from a validated numeric buffer; this proposal does not magically validate every existing unbounded raw `nirmmita` load.

The next useful specialization is a list of **owned byte strings**. On insertion, copy bytes from a validated live view/literal into the vector's region. Store an offset/length or checked string handle, not the source pointer. A returned string view carries the vector/object identity and bounds; it is not a bare address and fails after the owner dies. A finite typed specialization does not require implementing a general generic-language system first. Allocation failure and source validity must be checked before publishing a new string entry. Encoding policy is separate from byte lifetime.

This gives a practical path to a block-local list of strings, with explicit copying cost. It does not support arbitrary shared mutable strings or automatic promotion of pointer graphs. Copying results into a longer-lived destination needs its own supported destination allocation/copy API; merely relabelling an inner offset as outer is forbidden. The numeric-first version can export numeric results by value without that machinery.

If later admitting **vectors of references**, store complete validated handles, not raw addresses. A reference from source region S may be retained in destination region D only when S is D or a still-live ancestor of D; compare dynamic identity/epoch along the parent chain, not just numeric depth. Child-to-parent and expired-sibling stores fail. This is a store-time lifetime check; generation validation remains a backstop at access. Typed element metadata and every copy/insert/read path are mandatory. This extension is not included in the numeric-first implementation estimate.

### 6. Sizes, failure and cleanup

Checked vector allocation accepts **element count and element width separately**, rather than a pre-wrapped byte product. Before multiplication/addition/alignment, validate count, width, header and available room. Validate capacity doubling and index-byte calculations too. Receiving an already-wrapped positive scalar cannot recover the caller's intended mathematical size; preserve operands or their range proof. The R147 arithmetic concern therefore belongs in the container allocation contract, not only in a final negative-value test.

For the initial runtime interface, use a defined diagnostic/termination before invalid access or partial publication; recoverable errors can be added only with atomic state rules. Zero-length vectors have length/capacity zero and no element access; they still require a valid identity. Never fall back silently to persistent allocation to make a region-owned object outlive its owner.

On each normal or nonlocal supported exit: compute/preserve return values, invalidate every exited region's live identity, restore descriptor and scratch frontiers in LIFO order, then transfer control. Preserve scalar/failure status and caller regions. Include explicit return, `krama`, `agrim`, and failed `prasar`. Single-threaded, non-reentrant execution is the initial assumption; callbacks, threads and asynchronous cancellation need a separate protocol. Invalidation must happen before storage is exposed for reuse.

Initial elements own no OS handles or user destructors. Adding such resources would require cleanup semantics beyond resetting bytes. Emitted validation/allocation/cleanup helpers are runtime code even when compiled directly into the executable; “no external managed runtime” is the accurate claim.

### 7. Why the proposed boundary is sufficient, and where it is not

Within the stated checked subset: an access requires an issued, matching object generation and live owner; reuse changes identity; growth leaves handles stable while updating the one descriptor; bounds and arithmetic restrict access to initialized payload; numeric elements cannot conceal dereferenceable pointers; and unsupported raw conversions/calls are rejected. These invariants compose into spatial/temporal access safety **assuming the compiler and runtime helpers implement them correctly and metadata has not been corrupted by unsafe code**.

This is a design argument, not a proof about v273. Generation checks do not fix arithmetic bugs, wrong code generation, arbitrary unchecked writes, data races, or a helper that extracts and publishes a raw data pointer. Nor does this design prove termination or correct numerical answers. Those remain separate obligations.

## Cost and the runtime-versus-static choice

| Dimension | Proposed numeric handle vector | Honest limitation |
|---|---|---|
| Storage | 16-byte handle; illustrative 64-byte vector descriptor and 48-byte active-region record; numeric payload remains 8 bytes/element | Not compatible with a legacy one-qword pointer ABI. Metadata tables require explicit capacity budgets. |
| Access | O(1) slot/generation/owner/kind/bounds validation plus one indirection | Rough planning shape: several metadata loads and comparisons, not a measured instruction sequence or ns figure. Cache misses and helper-call conventions can dominate. |
| Push | O(1) without growth; O(length) when copying a doubled backing store | Amortized O(1) append does not mean constant worst-case latency; region peak storage includes retained earlier backings. |
| Region exit | O(1) per exited region with table-frontier/epoch scheme, excluding later optional destructors | Leaving d nested regions is O(d). Pages remain reusable/resident, not necessarily returned to the OS. |
| Owned strings | O(number of copied bytes) per insertion | Deliberately not zero-copy alias preservation. |
| Static alternative | No temporal check at a proved-safe use; compile-time rejection when proof is unavailable | Requires a sound restricted type/lifetime system and typed interfaces, not current partial name taint. Can reject useful safe programs. |

**Runtime case for:** catches dynamic stale identity even when a handle travels through a checked helper; supports shared vector aliases; reduces the need for sophisticated whole-program lifetime inference. **Runtime case against:** metadata, ABI and branch overhead; defined errors occur during execution rather than always at compilation; any uninstrumented escape to raw memory breaks the argument.

**Static case for:** early diagnostics and removable runtime checks when ownership/borrows are established. **Static case against for this compiler now:** the current untyped pointer-compatible values and incomplete call summaries are not such a proof system. A sound conservative version is possible, but its restrictions and implementation cost must be acknowledged.

**Pick:** static kind/interface checking plus dynamic generation and bounds validation for the new vector. Hoist checks only across a region known not to close and a descriptor known not to mutate/reallocate, with no invalidating callback or unknown call. Do not hoist them on the assumption that generation changes are unlikely. A safe bulk numeric operation can validate once over a proved range; that is different from simply disabling checks in a hot loop.

### Implementation budget — estimate, not a promise

| Component | Proposed new implementation budget |
|---|---:|
| Distinct value kinds, binding tracking, typed handle arguments/results, rejection of raw crossings | 450–850 NASM lines |
| Bounded region/object tables, generations, entry/exit and exhaustion handling | 250–450 NASM lines |
| Checked numeric vector operations, alias-stable growth, arithmetic/bounds and failure atomicity | 400–750 NASM lines |
| Diagnostics, target/mode gating and integration | 150–300 NASM lines |
| **Compiler/emitted-support subtotal** | **1,250–2,350 NASM lines** |
| Model, adversarial fixtures, runner and mode/legacy checks | **700–1,200 test-side lines** |
| **Initial total** | **1,950–3,550 lines** |

This is an engineering estimate for a bounded numeric specialization, not measured work, a full-language type system, Windows parity, arbitrary reference elements or string-copy implementation. It may grow after ABI/lowering review. A prototype can be smaller; a few dozen allocation-routing lines cannot honestly claim the full contract. No source or test implementation is delivered by this review.

Measure the eventual prototype against identical validated workloads: append with/without growth; indexed reduction; aliasing across growth; nested regions; repeated region reuse; and copied text when added. Record useful operations, expected results, elapsed time, copied bytes, metadata high-water and peak RSS. A preliminary decision gate I would use is no more than 25% end-to-end slowdown against an otherwise equivalent bounds-checked numeric implementation on the selected teaching workloads, with zero safety violations. **That 25% is a proposed product budget, not a measured result or universal threshold.** If it misses, optimize/limit the feature; never waive correctness to hit the number.

## Validation performed and native acceptance still required

I ran a small independent Python **design model**, not the Sutram compiler. Sixteen assertions covered: live numeric reads; alias visibility after growth; logical bounds; rejecting a handle as a numeric element; refusing ancestor length/capacity mutation; preserving the parent across child exit; dead child rejection; actual descriptor-slot/address reuse; changed generations; stale-handle rejection after reuse; the address-only predicate's false acceptance; outer-handle invalidation; generation exhaustion; positive-to-positive size wrap; failure without cursor/descriptor publication on generation exhaustion; and oversized allocation before publication. **16/16 held in that abstract model.** This does not validate NASM, emitted code, all lifecycle interleavings or the model's own completeness.

For native qualification, require paired positive/negative evidence for these twelve families, with explicit expanded case counts rather than calling the table twelve tests already passed:

| Family | Decisive observation |
|---|---|
| V01 — reuse identity | Old handle rejected after address AND metadata-slot reuse; new handle reads only new data. |
| V02 — growth aliases | Two handle aliases observe one vector across relocation; no raw old buffer escapes. |
| V03 — nested owner | Parent reads survive child exit; ancestor resize/length mutation is refused before publication. |
| V04 — bounds and sizes | Empty, negative, exact-end, overflow, doubling and index arithmetic; valid neighbors/canaries unchanged. |
| V05 — helpers | Typed numeric helper works; returned/retained handle retains its identity; raw ABI conversion refused. |
| V06 — elements | Numeric data copies succeed; reference-as-number and integer-as-pointer paths are refused. |
| V07 — failures | OOM/table/region/generation limits preserve descriptor/cursor invariants; no silent fallback or wrap. |
| V08 — exits | Normal, return, break, continue, prasar success/failure and nested cleanup preserve status and surviving parents. |
| V09 — recursion | Distinct dynamic region epochs and per-invocation marks; explicit runtime nesting exhaustion. |
| V10 — unsafe boundary | Raw stores, integer-address indexing, inline assembly and foreign/unknown calls cannot enter the claimed safe closure unnoticed. |
| V11 — compatibility/modes | Legacy no-new-type programs against the same baseline; unsupported targets refuse the new contract; test production path separately from guard replacement. |
| V12 — oracle calibration | Deliberately missing generation/bounds/exit checks cause the top-level gate to fail; missing cases, crashes and timeouts are not swallowed. |

Copied strings and reference vectors add their own proof obligations; they are not green because numeric vectors pass. Known blind-call fixtures should become must-refuse or must-trap cases for the new checked type, while retaining historical evidence separately. Do not keep a wrong-value golden as the definition of correct checked behavior.

## WS2 — scalar-only fallback versus removing the feature

**Do not remove a useful region abstraction merely because it is not yet a general object graph.** Qualified scalar scratch can serve bounded numerical working buffers, reductions and temporary computations. R74/R75 report useful reuse workloads; those observations remain creditable within their actual scope. They do not prove every scalar-looking raw-buffer program safe. [R2,R7]

My release ordering is: (1) enforce and qualify a small scalar-buffer contract; (2) optionally qualify the numeric handle-vector extension above; (3) owned strings; (4) reference-bearing aggregates only after their separate rules. A user-facing safe buffer needs bounds/valid-size operations and a closed call boundary, not just region escape diagnostics.

**At this pinned implementation, I would not ship the existing block as a stable checked-memory teaching feature.** Keep it explicitly experimental/manual-lifetime, or disable it on the stable teaching surface, until the smaller accepted contract is enforced. This is not a claim that the compiler's other features must be discarded. If the scalar subset itself has been qualified at the exact release artifact, scalar-only v1 is acceptable and should say what it cannot hold.

“Safe but nearly useless” is a product hypothesis, not an established fact. Validate it with a few real teaching exercises using numeric scratch and later a numeric vector. A list of strings can use the owned-copy specialization when built; it cannot be smuggled into the scalar subset as untyped integer addresses. Reference brevity is not a reason to expose silent lifetime hazards.

## WS3 — one biggest risk, and what I would prioritize this week

**One risk: the checked subsystem has no closed trust boundary against ordinary unchecked memory operations.** A learner can see a checked-block syntax and assume a program-level property, while an ordinary raw buffer access or unverified callee can violate the assumptions of that block. Adding an epoch table does not protect it from arbitrary in-process raw writes. The code controlling safety is only as trustworthy as the operations allowed to reach its data.

R75's recorded raw-buffer overflow demonstrates the underlying uncontrolled-write capability, not an executed corruption of a proposed metadata table. The table does not exist yet. I am making a design inference from the permitted operations, not reporting a new exploit or claiming nobody in the full collaboration has named the issue. [R2]

The response I would recommend for the coming week is one bounded workstream: **make “checked” an enforceable interface and release claim**. First freeze the accepted value/operation kinds and forbidden raw crossings. Next enumerate every load, store, conversion and call path that can access checked objects or their metadata; reject unknown paths in the checked entry/call graph rather than treating them as scalar. Then build a minimal checked numeric-buffer/vector slice and calibrate it with an adversarial raw-write/call-boundary case, including a deliberately disabled check. Finally qualify one exact release binary and target with the real lesson programs, and publish only that scoped contract. These are recommendations to the implementer, not scheduled work or a promise of completion later.

An explicit unsafe/manual surface can coexist, as in a systems language, but its assumptions must be visible: unchecked code can invalidate guarantees. A block-local annotation cannot certify an entire mixed raw-pointer program. If arbitrary raw writes must be treated as hostile while protecting the rest of the same process, software type conventions alone are insufficient; stronger isolation/instrumentation is a different, larger project. Do not quietly promise that here.

## Evidence ledger and status

All repository reads below use the pinned main unless otherwise identified. Source citations identify reviewed mechanisms, not a complete compiler audit.

- **R1:** `Sarvam-to-ChatGPT/ROUND-148.md`, blob `5943a5ce451174173b8ba74c474926ca36205a53`: the three questions and candidate designs.
- **R2:** `Claude-to-Sarvam/R75-00-THREE-GAPS.md`, blob `4277dd055293bf429bf8d270313fc42289a7fa9e`: negative-size policy by target, tested direct versus helper-returned container routes, raw-buffer wrap/bounds evidence and admitted limitations. Executions attributed to Claude.
- **R3:** `src/sutram_compiler.asm`, blob `6678df3891a141d480d92cab9512b74b09eba2ee`: full text fetched for targeted lookup; ranges 16470–16810 and 16845–17155 read for kosh headers/operations/growth; typed parameter constants and argument-lowering lookup distinguish parameters from parameter growth. Not all source lines independently audited.
- **R4:** `src/r65_arena.inc:1–110`, blob `11aed1b78a494b95576dcf6d5020c47645929fc0`: opposing-cursor representation, arena extent and diagnostic replacement-path context. Its historical stage comments are not used as current feature status.
- **R5:** `ChatGPT-to-Sarvam/ROUND-147-FIX-AUDIT-AND-TEACHING-RELEASE.md:1–26`, blob `27c9a4602d649383e4a502ea00bf9f0322343ecd`: prior return verified, checked-size and teaching-boundary recommendations. R75 explicitly updates the earlier negative-size disposition.
- **R6:** `docs/CHANGELOG.md:1–105`, blob `65e8e06ee5f051e5f29db0cc2912b0428ff3fa47`: current v273 note and owner-reported composition evidence; counts and timings are not rerun here.
- **R7:** R74 composition evidence is also available in the preceding conversation and is summarized by R75/current changelog; this round did not re-execute or re-audit its full corpus.
- **R8:** `LANGUAGE-PRIORITY.md`, blob `64682919a70fa1b79e415bc879aee9cad07582ad`; `AGENTS.md`, blob `795d1181272a8ab24848b84753bc46a2eb386d40`: Sanskrit-only active work, documentation handoff, no background watcher or unapproved workflow.
- **R9:** `PROJECT-MASTER.md:1–78`, blob `c64cc14372993d6518ded5fa9f36639194573a2d`; `docs/sutram-design-parameters.html:130–167`, blob `20d610d58a04d394f3d8bc16ace537bc8d4bdfcd`: project goals and honest implementation-status distinction. Historical banners are not used to override v273 source.

**External primary context, not Sutram evidence:** the author's `generational-arena` documentation explains identity reuse and generation-index validation (https://docs.rs/generational-arena/latest/generational_arena/); Rust's official `Vec` documentation explains capacity-driven reallocation and raw-pointer invalidation (https://doc.rust-lang.org/std/vec/struct.Vec.html). Consulted 30 October 2026. These support the general techniques, not Sutram compatibility, measured overhead, the proposed layouts, budgets or a safety certification. No Rust dependency, GC or VM is proposed.

**Performed here:** connected pinned-source/report reads; an independent Python abstract-model exercise with 16 assertions; arithmetic for metadata sizes, planning ranges and the size-wrap example. The model is not a shipped implementation and its successful assertions are not native tests.

**NOT RUN — no native toolchain invoked:** compiler builds, v273 counterexamples, proposed vector implementation, generated-code inspection of the new design, native bounds/lifetime tests, Linux/PE/Windows/Wine acceptance, release suites, mutation campaign or benchmarks. No throughput/latency improvement or complete safety proof is claimed.

**NOT APPLIED:** any compiler, library, example, test, tool, canonical document, language-pack, workflow, Windows or backup change. Only this Markdown report belongs in `ChatGPT-to-Sarvam/`. Verify complete readback and single-file commit scope; stop after Round 148.
