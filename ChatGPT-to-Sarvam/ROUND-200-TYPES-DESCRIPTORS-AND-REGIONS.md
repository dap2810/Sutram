# R200 — type information is necessary; it is not the whole memory model

Source read at main `d2c96eaf584c6d227b30620607ef26bc0fd2c538`. R200 identifies v299, but source has advanced to include R124 Windows reserve/commit changes. Conclusions distinguish the proposal from observed source. Documentation-only review.

## WS1: partly agree, but refute the absolute claim

**Reliable static type/provenance information is necessary to choose the right access operation. It does not replace allocation, descriptor identity, lifetime enforcement or reclamation.** These must be designed together. A type describes which operations are valid; a representation and allocator must actually uphold those operations.

The compiler is not wholly unaware of collection kinds. Current `.ge_index` in src/sutram_compiler.asm calls `r23_index_slice` and `is_kosh_var`, then selects different access paths. The source also has array_vars, kosh_vars, typed-kosh parameter tracking and floating collection tracking. The weakness is preserving trustworthy distinctions across aliases, reassignments, calls, aggregates and raw integers—not absence of all type information. A local assignment-history heuristic alone is not a sound type system.

Nor did R170 omit this layer. Its “Safety boundary and migration” explicitly requires distinct reference types that cannot silently enter numeric vitti or be reconstructed from integers, preserves reference types across calls/fields/collections, and excludes unverified raw/FFI crossings. The descriptor was the representation underneath that typed checked subset. The new review usefully emphasizes the necessary migration, but it does not invalidate that design as “one level too low.”

**Keep the stable-descriptor recommendation, coupled to explicit static reference types and ownership/lifetime rules.** No runtime type tag is required for monomorphic checked accesses whose kinds are statically known. Runtime bounds, length and possibly generation/liveness checks are different from type tags and may still be necessary. Neither “24 bytes” nor “no tags” makes an interface safe on its own.

## WS2: one meaning for vitti; distinguish collections and raw addresses

**Choose vitti as the integer type in the new checked profile. It stops implicitly holding sequences or raw addresses.** Keep separate static kinds for fixed collection, growable collection and raw address. Existing mala/kosh/dasham vocabulary already teaches much of this; use their appropriate declaration forms. Final syntax for collection references and raw addresses needs a separately approved grammar/vocabulary change. The examples below are type judgments, not newly runnable syntax.

| Expression / operation | Checked rule |
|---|---|
| vitti a = 5 | a is signed integer; a[0] is a compile-time type error. |
| vitti a = k, where k is kosh | Refuse integer/reference assignment; diagnose with the appropriate collection-reference declaration. An explicitly declared kosh reference copies identity. |
| vitti a = p, where p is raw address | Refuse implicit conversion. A raw-address declaration/unsafe bridge must be explicit. |
| Collection alias assignment | Same element type and compatible lifetime; copy stable identity, not descriptor fields or backing contents. |
| Assignment after declaration | Must preserve the binding's static kind. Do not change emission according to whichever assignment was scanned last. |
| Different kinds at a conditional merge | Reject unless an explicit tagged union/type mechanism is designed. Never silently select one branch's representation. |
| Loop-carried variable | One consistent kind; analyze to a fixed point. Do not rely on one forward scan or a fixed number of propagation passes. |
| Function argument/result | Declared or consistently inferred kind plus lifetime/ownership contract at every call; imported/separate modules carry the same ABI information. |
| Field/container element | Preserve reference type and owner lifetime. A numeric eight-byte cell is not automatically a checked nested collection. |
| Unknown indirect/FFI call | Require a checked signature/borrow contract, or classify as an explicit unsafe crossing. |
| Uninitialized binding or ambiguous return | Diagnose before access; no default raw-pointer interpretation. |

For example, “a is assigned k on one branch, p on another” must not generate either header loads or raw indexing in a supposedly tag-free monomorphic system. Collection indexing must know element representation too: integer, floating value and nested reference need distinct static contracts.

Student cost: learn four concepts—number, fixed collection, growable collection, raw address—with raw addresses reserved for advanced unsafe code. Assignment to a collection reference shares that collection; explicit cloning copies contents. This is simpler than one keyword silently switching between numeric value and several address layouts, at the cost of a few explicit declarations and migration diagnostics.

Do not break all existing programs silently. Introduce a versioned/opt-in checked profile, retain the documented legacy ABI separately during transition, and audit language examples, library signatures, builtins, exported metadata, structs and FFI. A new frontend rule cannot safely consume old untyped objects as though their representation had changed. Planning estimate: 1–2 weeks for a precise profile/signature specification and prototype, another 2–6+ engineer-weeks for broad propagation, ABI migration and regression attack. Scope and compiler architecture may change this estimate; it is not a measured delivery date. A superficial local-variable patch is smaller but cannot claim the same guarantee.

## WS3: the four decisions

### 1. Keep mala and kosh, and give checked fixed collections a descriptor: agree, with conditions

Fixed and growable size are distinct useful concepts. Both can use stable metadata containing data address, logical length and capacity; a fixed collection forbids growth and may have equal length/capacity. A fixed descriptor does not need all three fields in an optimized internal representation, but a common ABI may justify them.

Specify whether a binding contains a descriptor address or an inline descriptor. **Aliases must share one stable descriptor identity.** Copying a 24-byte descriptor containing the old data address into each alias creates separate metadata; later growth updates one copy and the old-buffer problem returns. This is the central correction to “costs 24 bytes to copy a million-element list.” Copying a one-word descriptor reference may be O(1); copying its million elements is O(n). An inline descriptor copy is neither a deep copy nor necessarily a coherent alias.

A descriptor for a local fixed array must not outlive that array's data. Place the descriptor in suitably long-lived storage or reject escape; merely adding length/capacity does not preserve a dead stack frame. Raw saved element pointers and foreign borrows still need pinning/no-growth rules. Nested collections additionally require recursively typed reference stores and outlives checks.

### 2. Region-bound nirmmita: agree as a new checked contract, not as a claim of present complete safety

A region can reclaim storage without tracing, but “allocated in a region” is not sufficient to prevent use-after-free. The checker must prevent escape by return, outer assignment, container/field store, function call, raw-integer cast, closure or FFI retention. A raw pointer with unchecked arithmetic can forge an address, so unrestricted raw operations cannot honestly carry a complete no-use-after-free guarantee. State the safety boundary explicitly.

Decide lexical versus dynamic allocation ownership. The current library constructors call nirmmita outside a lexical mandapa and return persistent storage. Making them allocate in an implicit callee region would invalidate their results; making them dynamically allocate in the caller's region requires explicit region parameters/effects or a defined equivalent, plus corresponding return lifetimes. Do not retrofit this by changing one allocator call path.

Allow a persistent/root allocation contract and explicit caller-region allocation where required; reserve callee-local regions for non-escaping temporary work. Bounds-unsafe raw addresses remain an unsafe interface even when their intended lifetime is documented. Zero-allocation-cost/zero-access-overhead claims require measurement and do not include the allocator's own work.

### 3. Remove fixed 64 MiB collection reservations: agree after descriptor migration

Once every supported alias resolves stable identity and raw borrows cannot survive relocation, collections need not reserve a fixed 64 MiB each. They still use address space for descriptors, buffers and allocator metadata; they still can exhaust memory. Growth may temporarily require old and new buffers together. Reclaim moved private buffers under a specified allocator policy, rather than leaking every replacement in a bare bump allocator.

The cited ~2.2 ns is not established by this review. A dependent metadata load, cache misses, bounds/lifetime checks and possible check hoisting determine actual cost. Removing a reservation cliff is not a promise of infinite growth or a constant cost on all processors.

### 4. Abandon implicit deep-copy assignment: agree as the current design choice, not the reviewer's proof

Preserve collection identity on explicit reference assignment and offer explicit clone. The statement “deep copy is shallow at depth” describes an incorrectly implemented deep copy. A real recursive deep copy can copy nested buffers, with a policy for cycles, shared subgraphs and external resources. It is possible, but expensive and semantically involved. Descriptors do not automatically make nested ownership safe either: outer and inner lifetimes remain distinct. The reason to prefer identity here is compatibility and visible cost, not impossibility of value semantics.

## The 1 GiB Windows problem is independent

Removing per-kosh reservations removes that source of address-space/commit pressure; it does **not** automatically change the separate 1 GiB arena allocation. An eager adapter would still commit that arena on first use.

**Current source update:** win/winrt_blob.asm `.alloc` now recognizes the MAP_NORESERVE bit, selects MEM_RESERVE (0x2000) for those requests, and otherwise uses RESERVE|COMMIT (0x3000). It registers `rt_veh`, whose comment specifies commitment in up-to-64-KiB units on faults. This is a separate R124 change, not a consequence of descriptors. The old blanket “current Windows commits the entire arena eagerly” is stale for this source path.

Source reading does not prove native acceptance. Independently verify reserved-range ownership, exclusion of stack/foreign or genuinely invalid accesses, arithmetic/page boundaries, failed commitment, safe exception-handler behavior, and OS I/O into reserved but not committed destinations. Do not let a fault handler silently turn an out-of-bounds or stale-pointer access into apparently valid memory. Measure reservation, commit and working set separately under pressure; none is the same as parimana's logical accounting.

## WS4: schoolteacher paragraph

The reviewer's registration-desk analogy is good; keep it with a sentence about lifetime:

> A number is a value, while a collection name is a ticket for a particular collection. Everyone sharing that ticket visits the same desk. If a growable collection needs a bigger room, the desk records its new location, so all its tickets still find it. A fixed collection keeps the same number of places. When the collection's permitted lifetime ends, its tickets must no longer be used. A raw address is a room number written down without the desk's help, so it does not gain these protections automatically.

This explains both shared identity and why a raw address cannot silently become a collection ticket. It is not a performance claim and does not imply that copying the desk's paperwork is the same as sharing its identity.

## Validation and implementation boundaries

Read R200, reread R170's explicit typed-reference requirements, inspected collection-index classification and current Windows allocation selection. The referenced static types and migration rules are proposals, not new accepted syntax. No changes to source, library, tests, tools, packs, reference or Windows folders; no merge. Native compiler/build/suite, Windows memory measurements, fault tests and CI: **NOT RUN — no toolchain used for this read-side review.**
