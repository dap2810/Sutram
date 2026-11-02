# R177 — concrete fixes for relocation and lifetime
Read-side design, 2026-11-02. Base `416637b6feeb91fae58324f0cc3d7afa4bdb4857`, compiler v289. Implementation remains Claude's R108 responsibility.

**Decision: use static outlives/borrow rules for the initial safe arena implementation, plus stable kosh descriptors if aliases remain supported. An arena epoch alone fixes neither alias coherence nor lifetime safety unless references and metadata are redesigned. Do not reclaim storage with the current call-through escape gap still accepted.**

## WS1 — two different invariants

Hole 1 is first a semantic correctness failure: two names promised to identify one mutable collection diverge when only one is redirected to a copied slot. Retained old bytes avoid immediate use-after-free, but do not make the result correct. Once stale length/capacity information controls access, or those bytes are reused, it can also become a memory-safety problem. Neither label licenses silently wrong behavior.

If growth **truly preserves the data address**, existing aliases remain coherent, provided length/capacity metadata is shared and updated. Allocating a new slot and abandoning the old one is relocation, even when the containing arena never moves. If in-place growth is unavailable, either refuse growth before modifying state, or implement indirection/ownership rules. Do not describe copying as nonmoving growth.

### Concrete alias-preserving representation

Use a stable descriptor per kosh: data pointer, length, capacity, owner reference and any required diagnostic metadata. All ordinary kosh references identify the descriptor, not its current data allocation. Growth performs:

1. Check size arithmetic, owner capacity and budget.
2. Allocate new data in the **original owner**, even when called from an inner block.
3. Copy exactly the initialized logical elements.
4. Publish data pointer/capacity in the descriptor only after success.
5. Retain the old slot until arena reclamation; all aliases now access the new slot.

A plausible four-word descriptor is 32 bytes before additional diagnostics/epoch fields; this is a layout estimate, not an implemented ABI. Element access adds a dependent data-pointer load compared with today's data-pointer reference; the optimizer may hoist it only while growth cannot occur. Growth remains O(length), allocation accounting includes old slots, and reference copies remain cheap. Update indexing, all collection builtins, parameter passing, debug paths and module interfaces together.

Interior element pointers/views do not automatically follow the descriptor. For the first safe subset, forbid structural growth while a borrowed element view is live, or prohibit exposing such views. Raw addresses remain an explicit unsafe boundary with invalidation documented.

An alternative is unique ownership: forbid copying/retaining kosh references, and permit temporary read borrows only while growth is prohibited. This avoids the descriptor indirection but changes assignment/call semantics. Refusing only `vitti a = k` is insufficient: assignment into an existing local, function returns, fields, container slots and indirect calls can create equivalent aliases. Stable descriptors preserve the project's existing “second name” behavior more naturally.

### Concrete static lifetime enforcement

Represent each safe reference's owner as a **block activation lifetime**, not just a numerical lexical depth. Depth alone cannot distinguish siblings or recursive activations. A reference may be stored only where the destination cannot outlive that owner. Propagate owner information through aliases, fields, element stores, return values, branch joins and loops. A join must conservatively retain every possible shorter lifetime.

For calls, infer or declare summaries: borrowed parameter, retained/stored parameter, return alias of parameter, newly allocated return owner. Compute summaries to a fixed point for recursion. At unresolved external/indirect calls, reject arena references until a compatible no-retain contract is available. Passing k to a read-only `padh(k,i)` is allowed; passing it to a function that saves it globally is refused. Returning an integer read from k remains allowed. Returning a borrowed reference to the caller can be valid only if the caller's use remains within the original owner.

Compiler analysis costs time and metadata proportional to the program/analysis, with iteration at joins and recursive summaries; a sound result can eliminate runtime lifetime checks for that safe subset. Do not promise a fixed compile-time percentage without measurements.

v289's new direct escape checks are useful but not this complete rule. Claude R107 explicitly retains runtime R82 checks for a function that returns or keeps a block kosh (example 316). The retained header currently makes that diagnostic possible. Reclamation must wait until that path is statically rejected or protected by a sound alternative. Existing error fixtures are part of the contract even when a census finds no successful program using the feature.

### What an epoch alternative actually requires

An arena epoch can detect **arena death/reuse**, not a kosh relocation while that arena remains alive. Leaving the arena epoch unchanged accepts the stale data alias; changing it on every kosh growth invalidates unrelated live objects and still needs a way to refresh valid references. An independent object mutation epoch can reject stale views, but rejection is not alias coherence.

For runtime lifetime validation, each reference must retain its expected epoch independently of reusable object storage. Check a stable owner-control record that outlives all possible stale references **before dereferencing arena memory**. A record inside the freed arena or an epoch fetched afresh from a reused descriptor is insufficient: both can report the replacement object's epoch (ABA).

A straightforward uncompressed reference is descriptor/address + owner-control pointer + expected epoch: 24 bytes on this 64-bit design. A descriptor may carry some fields only if it itself survives safely; otherwise an external lookup or stable handle is required. Control records need a reclamation policy, live/dead state, nested/recursive activation handling, and wraparound handling (refuse on exhaustion rather than reuse a live epoch).

“Roughly three instructions” can describe only a hot load/compare/branch when the owner pointer and expected epoch are already available and owner liveness is encoded appropriately. It excludes retrieving those values, extra loads, cold diagnostics, reference-width/ABI costs, checks at stores/calls, and metadata allocation/reclamation. No universal three-instruction safety price is justified.

**Choice for R108:** static lifetime enforcement for the supported safe subset; reject unresolved escapes. Stable descriptors separately solve mutable alias coherence. These are not “both lifetime strategies”: descriptor indirection and outlives checking solve different problems. Keep today's reclamation behavior if the static gate cannot yet be made sound. Do not add epoch machinery merely to conceal missing call summaries.

## WS2 — fixed bound, no relocating arena

At `parimita N`, refuse the allocation/growth that would exceed the defined charge **before** publishing any change. Include descriptor/header bytes, padding, current capacity and abandoned growth slots. Check arithmetic overflow before alignment and compare against remaining space. Distinguish budget exhaustion from OS allocation failure.

A moving populated arena is unacceptable under existing raw/direct-reference semantics. Copying it invalidates descriptors, payload addresses and interior references. Future nonmoving chunks or extension within an existing reservation are possible, but must remain within N; they do not make “grow past the budget” legal. An outside-owner kosh grown inside an inner block must retain its outside owner.

Rewind/reuse is logical reclamation, not proof of OS page release. Preserve initialized-data semantics on reuse; skipping zeroing is valid only when every read is bounded by initialized length and all required header fields are initialized. Handle every supported block exit and recursive activation.

R107's “slot never touches the slow path” is conditional on an initialized arena and sufficient space, as its own report names reservation and exhaustion paths. Its scratch-slot surrogate benchmark is not a benchmark of a complete alias-safe arena kosh implementation.

### Current parimana is not the proposed block-only query

R107 reports a process-level partial allocator total: persistent arena occupancy + scratch occupancy + counted region header/capacity. Fallback mmap allocations are excluded; Windows returns 0. This differs from R176's proposed innermost-block query, and must not be silently redefined.

For the migration, preserve the documented scope or version it explicitly. Count each arena-backed descriptor/data allocation once through arena occupancy; remove its separate region charge to avoid double counting. Growth increases occupancy by the new slot, including retained old slots; block rewind lowers scratch occupancy. Region allocations outside blocks remain separately counted. State that this is allocator accounting, not RSS, and that uncounted fallback allocations prevent a claim of total process memory. Test counters before/during/after nested blocks, failure and repeated entry.

## WS3 — explicit reference identity contract

| Same established live reference type | == | != | < | <= | > | >= | + |
|---|---|---|---|---|---|---|---|
| kosh | Same object identity | Different identity | Refuse | Refuse | Refuse | Refuse | Refuse |
| mala | Same array identity | Different identity | Refuse | Refuse | Refuse | Refuse | Refuse |
| rachana reference | Same record identity | Different identity | Refuse | Refuse | Refuse | Refuse | Refuse |

Copied references compare equal; separate objects with identical contents compare unequal. Mutation and growth preserve identity. Results are normalized 1/0. Different reference kinds, reference-versus-number and unresolved kinds refuse. Dead references must not be compared through reclaimed memory. Explicit content operations may compare logical elements/fields under their own nested-reference and float contracts; no padding/header byte comparisons.

This repeats and makes explicit R176's choice. Identity is appropriate for mutable reference objects because it answers whether a mutation through one name affects the same object through another without hidden traversal/cycle rules. It is not a substitute for text content equality.

**Not documentation-only:** v289 inherits the recognized-kosh operator refusal, so allowing identity equality needs code changes. Mala/record word equality can implement identity only for valid stable references with established types. Their ordering/addition must be rejected. Kosh data-pointer equality cannot implement stable identity across relocation; compare the stable descriptor instead. Retain refusal until the representation/type/lifetime requirements are satisfied.

## Evidence and acceptance

Read R177, Claude R107 and R108 at the pinned base. Current compiler source fetched at blob `37dbd3c66c27403255ccbd4681a513895f5cdb12`. R107 measurements and gate results are attributed, not reproduced. Its count is 289 example files after adding 316/317, with 285 passes plus four no-expectation cases; the brief's 287/283 is the previous version.

Required acceptance probes: aliases across forced interleaved growth; mutation through both names; failure preserving old descriptor; element-view/growth conflict; function/global/field/return escape; sibling and recursive activation reuse; unknown indirect calls; owner-correct nested growth; exact budget and overflow boundaries; all exits; counter non-double-counting; direct/object/separate and native target behavior.

Native build, probes, suite, guard, performance: **NOT RUN — no toolchain**. Native Windows and CI: **NOT RUN**. No source changes or arena implementation by this round. This is a concrete specification for independent implementation and verification, not a safety certification.
