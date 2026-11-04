# R202 — kosh descriptor contract and scope rules

Base read: `6fba56b767cf08e7e4043099299b7b6c07e46b6a`, v301. Evidence: R202; Claude R126-00/R126-01; Muse ROUND-128-V301-TRACKING-VERIFIED.md. Tests below are acceptance requirements, not newly executed results. No production changes.

## WS1: retain invariant binding kinds, including module scope

**Keep the kind fixed at declaration/initial binding. Later assignments must match.** Students can replace one collection reference with another compatible collection reference, but cannot change that binding into an integer, raw address, fixed array or incompatible element kind. A new name is the straightforward way to express a different kind. This gives predictable indexing and avoids hidden runtime tags or source-order-dependent emission. State the stricter rejection of previously accepted global/ternary uses in release notes.

**The rule applies to all bindings, including module scope, parameters, fields and results—not only function locals.** My R201 implementation discussion focused on the per-function tables and should have explicitly named globals as a mandatory transfer boundary. That omission was mine. A function-local marker cannot establish a module binding's kind across different functions or compilation units.

For v301, retain the conservative **refusal of kosh-to-module-vitti assignment**, including call-result and indirect transfer attempts. Do not describe it as supporting checked global kosh aliases: Muse R128 confirms even valid in-bounds uses are refused. If global collection bindings are added later, they need module-wide type metadata and a lifetime owner that outlives every use; initialization order, reassignment and separate-module signatures must be specified.

Muse's report confirms all 20 prior probes and eight additional global-door attempts refused or bounds-checked. It also records stricter ternary/global behavior and the empty-name diagnostic for a global assigned a call result. These are reported results, not my native runs. They close the tested failures, not all conceivable provenance paths. Claude's report still names FFI ptr and foreign/separate-object return exceptions, and retains legacy mala/raw paths. The descriptor must explicitly handle or refuse those boundaries.

## WS2: proposed descriptor contract, ready for implementation review

This is the **single-threaded numeric-kosh contract**. It does not introduce nested collection storage, checked raw pointers or global kosh support by implication. Existing v301 transfer refusals stay in force until independently designed.

### Representation: 24-byte payload header

A kosh reference is an address D of one stable, aligned descriptor. Every alias of this logical collection holds the same D. The descriptor contains three 64-bit words:

| Offset | Field | Invariant |
|---|---|---|
| +0 | data address | Current backing allocation; not an address exposed as a stable element pointer. |
| +8 | logical length | Initialized/readable element count, with 0 <= length <= capacity. |
| +16 | capacity | Allocated element slots, with checked byte-size arithmetic; element width is eight bytes for current numeric koshes. |

Element type remains compile-time information. Capacity growth must not silently change integer-versus-dasham interpretation. A copy of D is an alias; copying these three words into a new descriptor is **not** alias assignment. It creates independent metadata and would recreate stale-buffer failures.

The three fields are the data-access header, **not the total safety metadata**. Existing owner/liveness/generation information must be retained in a stable side record or a larger private allocation around the header. Specify that representation before coding. Do not drop lifetime checks to meet a “24 bytes total” slogan. A stale-reference check must not dereference a freed descriptor or side record.

Recommended narrow ownership implementation: the owning region records the descriptor and its backing allocations; aliases are non-owning references. Root-owned objects belong to the program's root lifetime. The variable is neither the allocator nor the lifetime owner. Rebinding a variable changes that variable's reference, not the ownership of the old collection or any other aliases. Descriptor identity remains stable until the owner closes.

If static enforcement proves no alias can survive closure in the accepted subset, reclamation may rely on that proof. Where runtime stale-reference detection is promised, metadata must remain safely addressable and identity reuse must be distinguishable (generation-bearing reference or equivalent); an eight-byte reused descriptor address alone cannot distinguish an old identity from a new one. Reject unsupported escape paths rather than claiming those guarantees from three fields.

### Reads, writes and aliases

For a checked `a[i]`, resolve a's descriptor under its lifetime contract, validate `0 <= i < length`, load the current data address and then access the element. Writes use the same logical bound unless a specific growth operation is being performed. Capacity is not a readable-length substitute. Evaluate the base/index once in the language's defined order; if index evaluation or another call can grow the same collection, reload descriptor data/length afterwards before access. Never cache a raw data address across an operation that may relocate it.

A normal alias sees the same length, capacity and contents immediately after each completed operation. Growth through either alias affects the same object. Clearing changes logical length; it does not replace identity. Rebinding one alias to another collection does not redirect all aliases to the original object.

### Growth: success and failure

1. Check descriptor/owner validity, new capacity arithmetic, implementation capacity limit and the relevant accounting policy before memory writes. Preserve existing observable capacity rules unless a separately approved change says otherwise.
2. If current capacity suffices, write/initialize the new element and publish length last.
3. Otherwise obtain a new buffer with sufficient capacity. Budget the transient old-plus-new storage where the budget covers this allocation class. Do not redefine mandapa parimita's scope silently as a whole-program or whole-collection budget.
4. Copy initialized elements, initialize any required newly exposed cells and prepare the append. If allocation/commit/copy preparation fails, preserve the old descriptor fields, logical contents and every alias. Diagnostic/failure-result behavior must be explicit; a fatal refusal is acceptable for the first implementation, corruption is not.
5. Publish the new data address, capacity and length only after preparation succeeds. In a single-threaded non-reentrant operation these stores need not be a hardware transaction; do not allow callbacks to observe partial state.
6. Retire the old backing allocation under the selected allocator policy. Do not reclaim it while an authorized raw borrow can still use it.

**Initial retention policy:** if backing buffers use the existing bump arena, retain replaced buffers until their owner is reclaimed, and charge/report them honestly. Descriptors alone do not add free/reuse. For pure geometric growth, retained historical payload has a geometric bound relative to final capacity; that is not a universal bound for arbitrary replacement, cloning or shrink/regrow policies. A later free-block allocator can reclaim private old buffers without changing identity semantics. Root-owned retention may last for the process. Do not promise immediate OS memory release on shrink or block exit unless implemented and measured.

### FFI, slices and separate objects

FFI ptr must not accidentally receive D when it expects elements. Provide only a synchronous non-retained buffer borrow with no growth/reset/release during the call; reentrant callbacks require an explicit pin/no-mutation rule. Otherwise refuse the call. A foreign function returning an untyped pointer cannot be assumed to return a valid descriptor. Descriptor-aware cross-object calls require versioned type/ABI metadata; reject incompatible legacy objects instead of reading their raw buffers as headers.

A slice must retain stable collection identity plus offset/extent, or prohibit growth while a raw slice exists. Growth does not enlarge a saved slice's extent automatically. Nested kosh values remain refused by v301; this contract does not silently add them. Every producer/consumer—including bounds checks, all kosh builtins, constructors, parameter/result lowering and cleanup—must migrate. Correct kind selection makes choosing the path straightforward, but does not collapse the work to one emitter site.

### Closing a region with aliases

**A descriptor does not grant permission to escape. Keep the current rule: a block-owned kosh cannot be stored or returned outside its owner.** Aliases within that block may still be in variables when it closes; those references cease to be usable together. Reject an attempted outward store/return before it happens. Returning a caller-owned borrow is a different case: the owner remains alive and must be proven to outlive the use.

On close, invalidate the owner's lifetime before reusing any associated storage. Dispose of or retain descriptor/metadata safely according to the accepted static/runtime lifetime strategy, then reclaim the owner's backing allocations where supported. A forbidden surviving alias must not silently turn into a reference to a new object at the same address. If an unsafe raw/foreign path bypasses these rules, it is outside the checked guarantee; a descriptor cannot retroactively make it safe.

Future ownership transfer or promotion to a longer-lived region would be a distinct operation with budget and alias rules. It is not part of this contract and should not delay the narrow migration.

## WS3: will both reservation-related failures disappear?

**Yes, for supported descriptor aliases, if the migration is complete and the fixed reservation is actually removed:** growth no longer changes D, so the 4.2M relocation cliff disappears; allocating appropriately sized buffers removes the fixed 64 MiB-per-kosh address-space charge and therefore the specific roughly-fifteen-reservations failure under a 1 GiB address limit.

**Neither follows from merely adding the descriptor while retaining the old allocator.** If the reservation remains, its address-space cost remains. If one path keeps a buffer address rather than D, relocation can still break that alias. General address-space, commit, allocator-capacity and budget exhaustion remain and must fail predictably. The change removes two mechanisms, not all finite-memory limits.

Acceptance must force actual moves at small capacities as well as across the old boundary; compare both aliases' values, lengths and capacities; grow through each alias; exercise index expressions that themselves trigger growth; test failed growth without mutation; reject closed-region and foreign/legacy-object misuse; run many small collections under an address limit; and measure logical bytes, committed storage and reserved addresses separately on Windows and Linux. A “passes while data never moves” test does not validate the descriptor.

Do not certify “memory model with no known defect” based on these two fixes alone. Scope any verdict to the accepted checked operations, keep FFI/raw/legacy lifetime exceptions visible, and require the new implementation's independent attack results. The fixed-kind report itself excludes some boundaries; those must be closed or explicitly unsupported before descriptor deployment.

## Windows history and current boundaries

The history is useful evidence of cross-platform exposure. Two wording corrections remain necessary: a minimal Linux probe printing the right value does not prove the old transient-stack-pointer implementation was safe on Linux; and current merged vartani_sandhi preserves in-place semantics with literal-destination refusal, rather than adopting the branch's allocate-new behavior wholesale. R195–R200 already recorded that integration distinction.

The reported GUI editor-limit behavior—showing previous output after rejecting a new program—is a separate user-visible defect. Keep it open for its owner: a failed/oversized input must clearly invalidate or label prior output and must not appear to have run the new program. No Windows/IDE files were changed here. The brief's GUI category totals should be reconciled by that owner before treating them as an exhaustive 335-case partition.

## Verification limits

R126 and R128 native/Wine results are attributed to their authors; I did not rerun them. The descriptor is still a proposed contract. Compiler build, Linux suite, Windows execution, memory-pressure probes, GUI and CI: **NOT RUN — no toolchain used for this read-side review.** No production code, reference, library, tests, tools, packs or Windows handoff changes; no merge. Delivery is documentation only, pending implementation and independent acceptance.
