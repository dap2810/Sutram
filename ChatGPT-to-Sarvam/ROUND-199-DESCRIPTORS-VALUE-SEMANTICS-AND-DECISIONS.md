# R199 — descriptors, copying and closed memory decisions

Review base: main `a4cc6540d524e792961329fd0049b4c6202527e4` (v299 brief). Historical R170 and R187 reread; current source still declares R101A_REGION=0x04000000 and R101A_MAXCAP=(region-40)/8. This is a design handoff, not an implementation or benchmark.

## WS1: what I proposed, and what I did not state

**Yes: R170 explicitly proposed that growth replace backing storage behind a stable descriptor, with aliases following the descriptor, and return old backing storage to a bounded allocator.** See ROUND-170-MEMORY-DESIGN.md, “Allocation, growth, release and reset.” That design does not require a fixed 64 MiB virtual range per collection.

**No: I did not explicitly spell out “remove the 64 MiB per-kosh reservation” in that proposal.** I should have made that consequence clear. R170's proposal was based on v283, before the later R101A in-place reservation workaround described in R193's example. It was not a decision to keep the later reservation alongside descriptors. My subsequent reports documented the implemented reservation and its cost; they were not a recommendation to retain it in a descriptor redesign. R187 is primarily the withdrawal/library-contract report; I cannot substantiate the brief's attribution of a full descriptor design to that round. R170 is the actual detailed design.

The independent reviewer makes the practical consequence clearer: **replace the fixed per-object reservation, do not merely add a descriptor on top of it.** “Reservation goes to zero” means the fixed 64 MiB reservation disappears; descriptors and backing buffers still consume virtual addresses and physical/committed storage. Finite memory and allocation failure remain.

### Recommended choice: stable collection identity

Use a stable descriptor for each logical kosh; all checked collection aliases refer to that descriptor. Descriptor fields contain current data address, length and capacity. During growth:

1. Validate descriptor lifetime, capacity arithmetic and budget for both buffers to coexist.
2. Obtain new storage and copy live elements; initialize any newly exposed cells according to the contract.
3. Publish new address/capacity only after success. On allocation failure, preserve old contents, length, capacity and aliases.
4. Reclaim old backing storage only when no permitted borrow/FFI access can still use it.

A raw element pointer saved before growth does **not** follow the descriptor. Slices must retain descriptor identity plus offset/extent, or growth must be forbidden while raw borrows are active. Returning a descriptor pointer to freed descriptor storage is still use-after-free. Preserve the existing owner/lifetime rules, and keep metadata valid long enough to reject stale identities. A three-field descriptor alone solves collection relocation, not complete memory safety.

For the single-threaded checked subset, forbid retaining raw buffer addresses across operations that may grow/reset/release. FFI must pin the buffer or copy it. Unknown calls cannot be assumed not to grow. All index, append, length, capacity, function-argument and return paths must use the new representation consistently; do not quietly reinterpret legacy raw pointers as descriptors.

### Total cost, replacing the reservation

| Item | Minimal identity-only design | Additional requirements for a safe checked design |
|---|---|---|
| Descriptor | Three 64-bit fields = 24 bytes before alignment | Owner/liveness/generation/type information must live somewhere; 24 bytes is not a complete lifetime design. |
| Aliases | One descriptor address can be 8 bytes | Checked handles may be larger; R170 proposed 32-byte handles and 96-byte descriptors for broader guarantees. Do not conflate the two designs. |
| Data | 8 × capacity bytes for current numeric cells | Allocator headers, alignment, page rounding, free-list/slab overhead and lifetime metadata. |
| Growth | O(length) copy; transient old+new buffers | Failure rollback, budget charges, borrow/pinning policy and safe reclamation. |
| Access | Extra dependent load to obtain backing address | Bounds/lifetime checks and cache behavior; 1–3 cycles is an unmeasured hypothesis, not a portable price. Loads may be hoisted only where mutation/lifetime facts permit. |
| Reservation | Remove fixed 64 MiB per kosh | Replace with actual buffer allocations or bounded slabs. Never promise unlimited collections. |

For capacity C and a new capacity Cnew, the identity-only live storage model is approximately `24 + 8*C + allocator/alignment overhead`; growth peak includes `8*C + 8*Cnew`, plus descriptor and allocator overhead. With doubling, that is up to roughly three old-capacity payloads during growth, not one. For one million live cells, the current payload alone is 8,000,000 bytes; a second two-million-cell buffer adds 16,000,000 bytes temporarily. Those figures exclude metadata and page rounding and do not imply an 8 MB resident-set prediction.

If all backing buffers still come from a pure bump allocator with no free/reuse, old buffers remain retained until region reset. Geometric growth gives bounded historical capacity relative to final capacity for a simple growth-only sequence, but repeated replacement/shrink/regrowth can still accumulate. Use a bounded free-block allocator or releasable mappings for private growable storage. This does not require reclaiming arbitrary user objects inside a live block; old backing buffers are known dead only because the descriptor/borrow contract prevents surviving data-pointer aliases.

**Planning price:** approximately 2–5 engineer-days to finalize representation/ABI/borrowing contracts; 5–10 days for emitter, builtin, allocator and call-boundary migration; 3–7 days for independent two-platform tests and compatibility review. Rough total 2–5 engineer-weeks for a focused implementation, not a promise. The broader R170 checked-handle system is larger. Do not add all old region/header overhead to the new formula blindly, or erase it before equivalent lifetime enforcement exists. Measure hot loops, cold access, allocation churn, peak commitment, many small collections and growth failures on the actual targets.

Acceptance: aliases before/after every growth agree; the old 8,388,603-element cliff disappears as an alias boundary; raw borrows have an enforced policy; allocation failure leaves original state intact; stale descriptors refuse before touching reclaimed metadata; mixed object/library/FFI callers follow one ABI; memory tracking matches the selected logical accounting contract. No benchmark has been run here.

## WS2: deep copy is a valid choice, but not the right implicit change now

**Recommendation: preserve shared kosh identity through descriptors; provide an explicit clone operation for an independent copy. Do not silently make `vitti a = k` deep-copy in this migration.** Existing examples explicitly rely on shared identity. Changing assignment would be a semantic break, not just a safer representation. More importantly, implicit O(n) work and possible allocation failure on a simple assignment make the performance/cost model less visible to students.

For a flat numeric collection with n live cells, copying costs O(n) time and approximately 8*n additional data bytes, plus the new descriptor/allocator overhead (or capacity-based bytes if unused capacity is copied too). A million cells require about 8 MB of new payload; ten million require about 80 MB. Reading and writing those cells also uses memory bandwidth; no cycle estimate follows without measurement. Assignment failure must preserve the destination or use a specified failure result. Self-assignment and overlapping source/destination need defined behavior.

Deep copying closes collection-object aliasing only if applied consistently to assignment, arguments, returns, fields, captures and containers. A word containing an address copied into a new numeric buffer still points at the same target. Nested objects need recursive ownership semantics; cyclic graphs need an identity map to terminate and preserve intentional internal sharing. Borrowed external buffers, FFI handles and files cannot generally be cloned by copying bits. Copy-on-write would retain aliases internally and require uniqueness/refcount/borrow machinery; it is not the simple proposal described here.

Thus “aliasing simply does not exist” and “escape analysis becomes trivial” are false for this language's raw-address surface. Copying a block-local descriptor address or an element containing a pointer does not lengthen the referent's life. A closed, purely value-typed language could make a different tradeoff, but that would require much more than changing one assignment emitter.

An explicit clone gives a clear teaching distinction: assignment is another name for the same collection; clone creates another collection whose numeric contents can be changed independently. If the owner instead chooses value semantics, approve a versioned language change and audit every boundary above before implementation.

## WS3: closed answers, with accurate reasons

**Reuse: no automatic recycling of arbitrary allocations inside a live mandapa in v1.0.** A bump cursor alone cannot know that all aliases to an object are gone. This is a scope decision, not a proof that reuse without tracing GC is impossible. Nested regions, explicit ownership/free, reference counting with a cycle policy, or private descriptor-buffer reclamation can permit controlled reuse. The descriptor proposal itself needs the last of those if it is to reclaim moved buffers; an absolute “no reuse ever” would contradict WS1.

Reference paragraph:

> While a `mandapa` remains open, ordinary temporary allocations take the next available space; Sutram does not automatically discover and erase objects you no longer need. Reuse a buffer yourself, or put each loop iteration's temporary work in a smaller `mandapa` that ends before the next iteration. A budget stops further budgeted allocation before it exceeds the stated limit. Moving a collection's private buffer may reclaim that old buffer only under the collection's separate ownership rules; it does not make all ordinary objects recyclable.

**Threads: unsupported in v1.0, deferred beyond it—not “never because the cursor races.”** A cursor race is a defect in this implementation under concurrent use, not an impossibility theorem. Locks, per-thread arenas, ownership transfer and safe reclamation can make a memory model thread-safe. Atomic cursor updates alone cannot settle budgets, publication, descriptor replacement or region teardown. No v1.1 availability is promised.

Reference paragraph:

> Sutram v1.0 supports one execution thread per process. Its allocation and lifetime operations must not be called concurrently from foreign threads. Concurrent execution would require separately owned or synchronized memory and rules for sharing and closing collections, so it is deferred beyond v1.0. Separate processes can run independently; this does not make shared in-process pointers thread-safe.

These are settled release-scope decisions. They require no indefinite promise and no technically false “never.” A permanent product-policy ban is an owner's choice, not something implied by a bump allocator.

## WS4: explanation for a schoolteacher

The reviewer's notebook analogy is good and memorable. I would keep it, with a qualification about what belongs to the notebook:

> Think of a `mandapa` as a notebook for temporary working. Each temporary allocation uses more blank space; crossing out a value does not make that space available again. When the block ends, its temporary notebook space can be used for new work. In a loop, use a fresh small notebook for each round. Anything needed afterwards must be copied into storage that lasts longer. A collection has its own identity and storage rules, so you cannot assume every collection or library allocation is thrown away with this notebook.

This is more precise than “throw the whole notebook away” as a claim about OS memory or every called helper: region reuse need not return pages to the OS, and helper allocations may be persistent. It is not inherently a better metaphor; it is the same useful metaphor with the boundaries the implementation requires.

### Lazy commitment: useful direction, understated implementation cost

Reserve-only plus incremental commitment is the right Windows direction, but startup reservation is not literally free: it consumes address space and OS bookkeeping. The reported arena has two allocation ends, so one committed cursor is not sufficient unless the layout changes; track committed ranges for both ends. Round addresses and sizes correctly, validate arithmetic, handle commit failure before publishing state, zero newly exposed data as required, and integrate counters and region resets. Committing in 1 MiB chunks means the first touched chunk can charge about 1 MiB, not merely a few kilobytes; distinguish commitment from resident pages. An adaptive/page-sized first commit can reduce that initial cost. “Four or five assembly instructions” may describe a fast-path comparison, not OS calls, failure handling and the complete implementation. R198's cost estimate remains a planning range until measured.

## Verification and limits

Read the R199 brief, historical R170/R187 reports and current main's reservation constants. Arithmetic examples are representation calculations, not measured performance. Native builds, Linux/Windows tests, allocation probes and CI: **NOT RUN — read-side review, no toolchain used.** No changes to source, library, tests, tools, reference, packs or Windows handoffs; no merges. Deliverable is a documentation-only decision record for independent implementation and acceptance.
