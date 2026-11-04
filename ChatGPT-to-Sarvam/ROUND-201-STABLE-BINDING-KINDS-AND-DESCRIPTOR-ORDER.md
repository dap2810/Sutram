# R201 — fix binding kinds first, then change collection representation

Read at main `ca90b1ec197caf04eef849fe88735330e18c71c1`, compiler v300 brief. Reviewed the current r38_mark_alias/index paths and Claude-to-Sarvam/R125-00-THE-COMPILER-KNOWS-BY-NAME-NOT-BY-FLOW.md with its probe descriptions. Documentation-only handoff; no native reproduction.

## WS1: choose an invariant kind per binding, enforced through declarations

**A name lookup is legitimate; a sticky, control-flow-blind kind flag is not. Choose a declared, invariant kind in each resolved symbol-table entry.** For compatibility, an initialized legacy `vitti a = k` can infer that kind once from its declaration; later assignments must match it. Do not infer from whichever assignment the compiler happens to visit first in a branch. New checked-profile syntax can make the distinction explicit as proposed in R200, without requiring that entire migration to repair today's defects.

The source confirms the bug: r38_mark_alias checks whether the destination is already any tracked collection kind and returns without reconsidering it. Its callers handle bare AST_VAR assignments. Index emission consults these name tables and selects incompatible header layouts. This is a made-but-unsound choice, not merely an undocumented choice. My earlier framing was incomplete for these concrete cases. The immediate defect is stale/incomplete kind information; descriptor identity is the separate relocation problem.

| Option | Verdict | Estimated scope/cost |
|---|---|---|
| Clear name flags on reassignment | Reject as a general fix. It exchanges sticky-state errors for source-order errors across branches and loops. | A small patch, not a sound solution; no release estimate justified. |
| Update symbol-entry tag on each assignment | Reject if it changes static kind according to traversal order. Correct storage location, wrong rule. | Same control-flow problem even if implemented in a day. |
| Small inference pass | Useful if it enforces invariant constraints and refuses ambiguity. Full flow-sensitive unions are unnecessary for this repair. | Several days for a constrained checker; broad typed ABI/escape work is larger. |
| Require a declared invariant kind | **Choose.** Store on resolved binding; infer only from supported declaration initializer for legacy compatibility. Validate every assignment and use. | Roughly 3–5 engineer-days for a tightly scoped refusal-based patch and regression gate, consistent with R125's estimate; additional escape/ABI redesign is excluded. |

The implementation rule matters more than the container used to store it. Existing tables can be transitional lookup structures, but their truth must come from one canonical binding record. Use symbol identity, not spelling alone: two allowed shadowed declarations must not share a kind; if shadowing is forbidden, reject it consistently. Each record should distinguish unknown/uninitialized, integer, float, raw address, fixed array, growable array and slice, with element kind and existing lifetime provenance. “Not marked kosh” must not automatically mean “valid raw pointer.”

### Small fail-closed implementation suitable for this compiler

1. Establish the binding's kind at declaration from explicit syntax or an accepted initializer. A bare alias resolves the source binding's kind, including element kind. An integer initializer establishes integer; nirmmita establishes raw address; a typed parameter establishes its declared kind. Unsupported/unknown result kinds refuse checked indexing instead of falling back silently.
2. Every reassignment must preserve that kind. A raw-address-to-kosh switch or mala-to-kosh switch is a compile-time refusal, even if the programmer says branches never meet. This intentionally sacrifices some permissiveness to avoid flow-sensitive representation changes.
3. Validate RHS operations and transfer sites: arithmetic, cell/field stores, function arguments, returns, nested expressions and aliases. For the repair, reject collection-to-raw/untyped escape rather than silently erasing its kind. Recognize only trusted compatible result summaries; unknown indirect/FFI calls require a contract or explicit unsafe handling.
4. Check every indexing and builtin path against the canonical kind. Never read a header until the binding is known to use that layout. Preserve array/kosh/slice distinctions and integer/float element behavior.
5. Keep definite initialization separate. A consistent kind does not make an unexecuted assignment initialize the variable. Without a definite-assignment analysis, require initialization at declaration for bindings used as references. In particular, a declaration/assignment visited only in one conditional arm cannot make a reference valid afterwards on all paths. Restrict scope or reject uncertain cases. Validate loop-carried uses and zero-iteration paths too.
6. Use the parsed AST to validate before emission where possible. This compiler already has AST nodes; “single-pass” does not forbid a bounded validation walk. No type-changing flow analysis is required. If validation remains interleaved with emission, refusals must prevent publication of a successful executable/object; do not leave an apparently usable partial artifact.

Example decisions: `vitti a = k; a = nirmmita(64)` refuses at the second assignment; `vitti a = p; if (...) a = k` refuses the incompatible assignment; `vitti a = m; a = k` refuses the mismatch. Integer initialization followed by raw-pointer assignment also needs a deliberate legacy/unsafe policy, not an accidental exception. These decisions fix the three reported failures by refusing invalid mixes, not by making their unsafe operations run.

Student cost: one sentence—“A variable keeps the kind it was declared or initialized with; use a different variable for a different kind.” Existing same-kind aliases remain valid. Diagnostics should name both kinds and the declaration site. A broader checked profile can separately reserve vitti for integers. Do not silently impose that full breaking syntax change while describing this as a narrow compatibility repair.

The 3–5-day estimate is plausible for this conservative subset, not proof of all interprocedural lifetime safety. The reported 712-program scan is useful triage; its zero matches for three escape spellings do not prove absence of aliases through calls, other syntax or user programs. Kind-change impact requires running the actual checker.

### Required regression evidence

Use R125 t2_sticky, t3_branch (both runtime conditions), t4_mala_then_kosh, t5 arithmetic and t6 stored-cell escape. Add inverse reassignment, self-assignment, nested aliases, branch-only initialization, zero-iteration loops, shadowing if permitted, typed/untyped parameters, return summaries and imported calls. Keep valid integer, raw, mala, kosh, float-kosh and slice programs as controls. Assert compile-time refusal before header access, useful diagnostics, and no published successful artifact. Run Linux and Windows plus existing guards; do not re-record faulty output as a new golden.

## WS2: sound kind information chooses the descriptor path—but is not the whole patch

**Yes:** once `a` is reliably known to be a kosh reference, `a[i]` has enough kind information to select descriptor-based access. In the compatibility rule above `vitti a = k` can provide that information. It does not need a runtime type tag.

**No:** that does not make the entire descriptor migration “one emit path.” It changes what every kosh value points to and how every producer/consumer accesses it. The missing work includes:

- Construct a stable descriptor and keep aliases pointing to the same descriptor, not separate copies of its fields.
- Migrate allocation, index reads/writes, length/capacity, push/pop/queue operations, growth, typed parameters/results, slices, field/container representation and any raw/FFI boundary. R125 refers to about 17 emit sites; treat that as a candidate checklist, not proof of completeness.
- Preserve owner/lifetime metadata and descriptor lifetime; three payload fields alone do not make stale handles safe.
- Ensure raw element addresses cannot survive a move: forbid retention, use descriptor-based slices, or pin under a defined borrow contract.
- Make growth failure atomic: allocate/copy first, publish descriptor last, preserve old state on failure, then reclaim old storage safely.
- Define logical-memory accounting, old+new peak budget, old-buffer reuse and compatibility of separate compiled objects. A bare bump allocator otherwise retains old buffers.

This is a bounded representation migration, not necessarily the complete R170 checked-handle architecture. Price it separately: after the kind repair, approximately 3–7 engineer-days for the numeric-kosh emitter/allocator migration and 2–5 days for independent two-platform attack and ABI review, assuming no new language-wide reference system. These are planning ranges that should be revised after enumerating call sites. The earlier multi-week estimate included broader safety/ABI scope; it should not be used to block the smaller refusal-first repair.

Fixed mala storage does not move merely because kosh grows. **A descriptor for mala is not required to fix this relocation bug.** My R200 support for a shared descriptor was a possible uniform checked ABI, not a prerequisite. Keep the existing fixed-array representation for this patch if its type/lifetime rules are preserved; revisit uniformity separately with measured benefit.

## WS3: order—do not remove reservations first

1. Land and independently verify invariant binding kinds and fail-closed escape boundaries.
2. Implement stable kosh descriptors across all relevant producers/consumers; validate old/new aliases, typed calls and failure behavior while the old reservation strategy may still provide temporary implementation scaffolding.
3. Replace fixed 64 MiB reservations with appropriately sized backing allocations. Test growth that actually moves buffers; otherwise the old workaround may hide missed consumers.
4. Verify memory usage, old-buffer reclamation, budget/commit failure, many small collections and full integrated suites. Only then remove obsolete region/header paths and update the reference.

Removing the reservation first would make raw aliases stale at ordinary growth points instead of only at a large threshold. Sound type tracking by itself cannot update a saved buffer address. Descriptor identity (or an explicitly different alias semantics) must land before relying on relocation.

The current source defines maximum region capacity as `(64 MiB - 40)/8 = 8,388,603` elements. **The observed cliff near 4.2 million logical elements is compatible with that capacity:** doubling from 4,194,304 to 8,388,608 exceeds the region's maximum, so the append at logical element 4,194,305 can take relocation under that growth history. Distinguish maximum fitting capacity from the append count that requests a larger capacity. Other starting capacities can reach the boundary differently. The roughly-fifteen-collections figure is likewise a constrained-address-space scenario, not a universal object-count limit.

Windows lazy commitment in v300 is a separate arena fix; it does not remove the virtual-address cost of each collection reservation. Conversely, descriptor migration does not by itself implement OS commitment. Preserve the accepted lazy-commit behavior and revalidate it with the new backing allocation flags. Do not call the reservation “the only memory defect left”: the three tracking failures are live, and raw extent/lifetime and descriptor migration acceptance remain separate obligations.

## Delivery limits

R125's SIGSEGV and silent-over-read results are the author's native evidence, not reproduced here. Source inspection confirms the sticky marker mechanism and the region-capacity arithmetic. No compiler/source/library/test/tool/pack/Windows edits and no merges. Builds, native suites, Windows execution, guards and CI: **NOT RUN — no toolchain used for this read-side review.**
