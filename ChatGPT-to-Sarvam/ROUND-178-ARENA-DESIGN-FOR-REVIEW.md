# R178 — arena design for adversarial review
2026-11-03. Main base: `7be8273cbe6a1655ab5c5ebd986da67e5c2b34df` (v290). Review branch inspected: `0e71e54620d8db5a6e56327ce0969c5dad03e25e`. This is a proposed implementation contract for Muse to attack before Claude builds it, not approval to merge the existing branch.

## Decision and student model

**Choose a nonmoving arena, stable kosh descriptors, relocating data slots, and compile-time lifetime enforcement.** Ordinary aliases remain supported: a second name denotes the same collection. No garbage collector or external runtime dependency is required.

Student rule: “A kosh belongs to the block where it is created. Other names refer to that same kosh. Growth may replace its storage but preserves those names. The block reclaims all its slots when it ends; no reference may survive its owner. The budget includes old slots left by growth.”

This is a target contract, not today's complete guarantee.

## 1. Representation and invariants

Use an eight-byte kosh reference pointing to a stable, 16-aligned descriptor. Proposed descriptor layout (internal, not new source vocabulary):

| Offset | Field |
|---|---|
| 0 | data pointer |
| 8 | logical length |
| 16 | capacity |
| 24 | owner-control pointer |
| 32 | source location/diagnostic identifier |
| 40 | flags including element kind |

Descriptor size: 48 bytes. The owner control record belongs to the active block invocation; a persistent root owner has process lifetime. Its implementation fields include allocation bounds, cursor, parent owner and budget/accounting state. Control records are per invocation, including recursive calls; lexical depth is not identity.

Invariants: length ≤ capacity; initialized elements occupy [0,length); the data slot and descriptor have the same owner; every safe reference's use occurs during that owner's lifetime; every alias uses the descriptor for length/capacity/data. Descriptor addresses never change during their lifetime.

Use the descriptor ABI uniformly for block and persistent koshes to avoid accidentally interpreting data pointers as descriptors in parameters and libraries. Persistent payloads may retain their existing reservation strategy, but relocation beyond that reservation must update the descriptor. This is a reviewed ABI migration: indexing, builtins, parameters, libraries, debugging, object/module interfaces and raw interop all change together. Existing binaries using the old ABI must not be mixed.

No implicit descriptor-to-integer or raw payload-pointer conversion. Exposing an element pointer/view requires a borrow that prevents structural growth until that view ends. First implementation may reject such views altogether; it must not silently retain stale pointers.

## 2. Allocation and growth algorithm

Creation computes checked payload size, descriptor size and alignment, checks the entire required charge, then allocates and initializes the descriptor and payload. Reserve both as one transaction so failure cannot leave a half-published kosh. Empty koshes may have null data and zero capacity, with no element access allowed.

Growth evaluates the appended value once, determines a checked doubled capacity (four from zero), checks multiplication and alignment overflow, and allocates a new payload from the **original owner**. Copy exactly length elements. Commit descriptor data/capacity only after successful allocation and copy, then append and increment length. All aliases subsequently see the new payload. Old slots remain charged until owner reclamation. Allocation failure leaves the descriptor, length and inputs unchanged; already executed argument side effects are not rolled back.

Growth may be optimized in place only when all owner/boundary conditions hold; its semantics cannot depend on that optimization. No moving arena and no arena-copying realloc.

An outer block's kosh may grow while an inner block is active. **Therefore use independently controlled, nonmoving owner arenas**, not an unmodified single LIFO scratch cursor: allocating an outer owner's replacement beneath an inner checkpoint would otherwise discard it when the inner block rewinds. Each owner must retain all its own allocations until it ends.

For the initial design, each block has one fixed reservation, obtained lazily. A bounded block uses N as its maximum chargeable slot occupancy; physical reservation may be page-rounded. An unbounded block uses a documented compiler-configured finite capacity, initially the existing 1 GiB upper reservation policy if retained by the owner. This default is not infinite capacity and must be exposed in documentation. Nested block reservations add virtual-address and mapping overhead; benchmark that cost rather than importing shared-arena timings.

## 3. Bounds, accounting and exits

Charge descriptor bytes, payload capacity and alignment padding, including every abandoned growth slot. Check remaining owner capacity and every enclosing bounded owner's aggregate charge before allocation. A child allocation adds to its own and its bounded ancestors' charges; child reclamation removes its charge. Growing an outer owner charges that owner and its ancestors, not a younger child's arena. Persistent allocations do not become block-owned merely because they occur inside a call.

There are two independent limits: the logical parimita budget and actual allocator reservation/OS availability. Reaching either refuses before mutation; no silent persistent fallback and no growth beyond N. Distinguish budget, arithmetic overflow and allocation failure diagnostics. No new public names are proposed for these diagnostics here.

All exits reclaim the block's allocations and restore accounting: fallthrough, return, break, continue and supported unwinding. A whole-process terminating error need not run user cleanup, but must not continue with invalid state. Reclaim may release the reservation to the OS or return it to an explicitly bounded arena cache; if cached, report retained capacity separately. Do not call a cached mapping “returned to the OS.”

Reuse must initialize every descriptor field. Payload zeroing is unnecessary only while all reads are constrained to initialized length and APIs never expose uninitialized spare capacity. Raw byte allocations retain their separately specified initialization contract.

Preserve parimana's current process-accounting scope rather than silently changing it to block usage. Add occupied owner slots once; do not also count them as region allocations. Reclamation removes those charges. State excluded categories until every allocator fallback is counted; this is not RSS or virtual reservation size.

## 4. Lifetime gate before reclamation

R108's no-retain parameter analysis is a useful starting point, not certification. Require owner provenance through aliases, branch/loop joins, stored fields/elements and returns. Reject storing a reference into a destination that may outlive its owner. Unknown/foreign/indirect callees reject arena references unless they have a verified no-retain contract. Recursive summaries must converge; if an analysis resource limit is reached, refuse conservatively.

A safe call may read/mutate initialized elements during the call without keeping the descriptor. Growth through aliases is semantically valid under the descriptor design, but enabling growth through parameters requires an explicit owner-aware ABI update; until implemented, retain that refusal. Raw code/FFI capable of hiding references remains outside the safe guarantee and cannot be used to claim complete static enforcement.

Do not remove existing runtime checks and reclaim memory merely because existing examples pass. Validate sibling activation reuse, recursion, transitive retaining calls and every alias-producing expression. No runtime epoch is required for the proven safe subset; unproven programs refuse.

## 5. Cost model — estimates, not measurements

All counts below are planning estimates for x86-64 user instructions, excluding operand evaluation, cache misses, syscalls and diagnostics unless stated. They are not benchmark results.

| Operation | Estimated work |
|---|---|
| Fixed-arena bump of a known aligned size | Roughly 8–14 instructions for cursor/bound checks and update; overflow/alignment validation adds roughly 4–8 |
| Budget ancestors | Roughly 4–8 instructions per bounded ancestor for check/update, plus traversal; depth is a real cost |
| Initialize proposed descriptor | Six field stores, plus address/setup work |
| Read element through descriptor | One extra dependent data-pointer load versus equivalent direct-buffer indexing; existing index bounds checks remain |
| Length/capacity query | One field load; no payload scan |
| Growth without relocation | Constant checks/updates if the optional in-place path applies |
| Relocating growth | Roughly 20–40 setup/check/commit instructions plus allocation accounting and O(length) copying; a simple loop approximately 4–7 instructions per eight-byte element |
| Block first allocation/exit | Reservation/release system calls plus control-record setup/cleanup; not a pure bump fast path |

With c0=4 and 1,000 eight-byte elements, capacities reach 1,024: payload slots total 16,352 bytes, old payload slots 8,160 bytes. Add the 48-byte descriptor once: **16,400 charged bytes**, assuming each payload already 16-aligned and excluding owner-control/page overhead. General payload sum is 8(2C-c0); dead payload is 8(C-c0). Owner reservation/control costs are separate from this arithmetic.

A separate arena per invocation may increase syscall cost versus the branch's shared scratch arena. That is an explicit correctness-first tradeoff. A bounded pool can amortize it later without moving live arenas, but its retained memory needs its own limit and metrics. The branch's reported 0.02-second/0-KB surrogate is not a measurement of this descriptor/owner design.

## 6. Concrete review-branch findings

Read the branch compiler patch and evidence README. It implements relocation plus a no-second-name restriction, not this descriptor contract. Do not merge it as an implementation of this document.

- **Silent policy fallback:** r108_kosh_alloc checks its 256-entry block-kosh table and jumps to r101a_emit_kosh_alloc when full. That can change block ownership/budget/reclamation behavior at an implementation limit. Reject compilation on metadata exhaustion instead.
- **Unproven convergence:** r108_compute_esc permits only 32 rounds and exits even if the final round changed summaries. A sufficiently long adverse-order call chain needs more propagation. Iterate to convergence with a proven bound/worklist, or conservatively refuse on exhaustion. Starting no-retain and propagating retaining uses requires convergence before using a safe result.
- **Traversal truncation:** its .push silently drops work at 65,536 entries. Analysis exhaustion must not imply no-retain; emit a capacity diagnostic or mark affected summaries retaining.
- **Alias recognition scope:** r108_check_alias recognizes a bare AST_VAR. Its presence proves direct declaration/assignment checks, not a theorem that every expression producing the same reference is forbidden. Muse should attack conditional expressions, wrappers and storage paths. These are test obligations, not claimed executed bypasses.

These findings are source-derived on the review commit. Main shares some analysis work but this round does not claim a complete independent audit of every main path.

## 7. Limits and owner constraints

This design does not:
1. Reclaim individual objects before owner exit, compact arenas, or avoid retained growth slots.
2. Make repeated concatenation or unrelated persistent allocation bounded by a kosh arena automatically.
3. Permit safe escaping block references, arbitrary raw aliases, or unchecked FFI retention.
4. Provide concurrency, lock-free publication or cross-thread ownership.
5. Eliminate dependent loads, mapping costs, recursion depth limits or OS allocation failure.
6. Certify Windows/native installer behavior, or guarantee total process RSS from parimana.
7. Implement generalized container content equality or change current operator refusals.

No GC, libc or other-language runtime dependency is introduced. Helpers are emitted/linked as project-owned native code; “no runtime dependency” does not mean no instructions execute for allocation. The pure-NASM compiler constraint is preserved. The student model stays one owner, one collection identity, one budget including waste.

## WS3 — vocabulary and review order

No new source-language concept needs a new keyword. Keep the owner's settled kshetra, kosh, mandapa, parimita and parimana vocabulary and Latin-primary/optional-Devanagari spelling. Descriptor and owner-control record are implementation explanations, not proposed English keywords. Do not shorten existing Sanskrit words or coin a new compound. If a future borrow/owner syntax needs a word, request a separately justified full Sanskrit term before exposing that syntax; this design deliberately avoids needing it in stage one. Native-speaker review remains NOT RUN.

Muse should attack the invariants and the listed branch findings first, especially outer-owner growth during an inner block, alias mutation after relocation, long recursive/call chains, capacity exhaustion, double counting, and all exits. Claude builds only the accepted contract after that review; no merge is authorized by this report.

Evidence boundary: R178 brief, Claude R108 report and review-commit source patch/evidence read. All performance counts here are estimates or arithmetic. Native build, probes, suite, guard and benchmarks: **NOT RUN — no toolchain**. Native Windows and CI: **NOT RUN**. Documentation only.
