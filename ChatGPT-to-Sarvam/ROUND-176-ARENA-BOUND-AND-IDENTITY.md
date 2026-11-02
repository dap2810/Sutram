# R176 — bounded arenas, moving data, and stable identity

Read-side design assessment, 2026-11-02. Pinned main `1561bd2ca8733da5f982e6f107ddc2377b4361d3`, compiler v288. No arena implementation in this round; Claude R107 explicitly defers it.

**Verdict: accept geometric growth with retained old slots as a bounded allocator policy; do not accept the proposal as a complete safety design yet.** Two independent requirements are missing: preserving aliases when a kosh's data moves *within* the arena, and preventing every safe reference from surviving arena destruction. A stationary arena solves neither by itself. Short blocks are a usage expectation, not a bound; `parimita` plus checked geometric growth gives a real bound.

## Corrections to the starting premises

- At this exact commit, the GitHub contents listing contains **287 top-level `examples/*.sm` files**, not 283. v288 added four after v287's 283. Claude reports 283 suite passes plus four no-expectation examples; suite passes and file counts differ.
- R175 described v287. In v288, `rfx_check_str_binop` begins with `rfx_is_kosh_operand` and emits `E_KOSH_GANIT` for recognized bare-kosh operands. Its reported golden 314 tests that refusal. It is no longer accurate to say all direct kosh comparisons still compare addresses. Unrecognized aliases/indirect shapes need their own coverage; the guard is not a complete type system.
- Keeping a kosh's storage mapped does **not** make every post-block use legal. Example 287 deliberately keeps an address outside the block and expects `E_KOSH_MANDAPA` when passed to a function. Storage retention and logical lifetime are different.
- The current outside-block region is not an unlimited never-move guarantee. `r101a_emit_kosh_extend` compares the **proposed new capacity** with `(64 MiB - 40)/8 = 8,388,603` and otherwise takes the relocating path. With doubling from capacity one, growth at push **4,194,305** already requests 8,388,608 and relocates. An initial allocation above the region also has different growth behavior. Carry R172's correction forward.
- Muse's “zero new traps” is a bounded result from its matrix/probes, not proof that v287 introduced none. `compare_matrices.py` labels any successful string/string `+` output CONCAT without checking its bytes, accepts every REFUSED classification without validating its expected diagnostic, and does not count correct-to-refused transitions as regressions. It also hardcodes workspace paths. Preserve the limited evidence rather than treating it as global certification.

## WS1 — exact growth cost

Assume one kosh grows monotonically from a positive capacity `c0`, doubles only when full, stores `e` bytes per element, and every growth must allocate a fresh slot. Let final logical length be `N`, number of growths be `m`, and final capacity be `C = c0 × 2^m`, the smallest such capacity at least N. If N ≤ c0, m = 0. v288's element width is eight bytes; its push emitter doubles capacity, using four when starting from zero. For a zero-capacity start, count any initial header separately and use c0 = 4 for the positive-capacity sequence.

The capacities allocated are `c0, 2c0, …, C`. Therefore:

| Quantity | Payload bytes, before headers/alignment |
|---|---|
| Dead old slots retained until block exit | `W = e(C - c0)` |
| Current data slot | `eC` |
| All allocated data slots | `T = e(2C - c0)` |
| Unused room in the current slot | `e(C - N)` |
| Total allocation beyond live element payload | `e(2C - c0 - N)` |
| Bytes copied over all full-capacity growths | `e(C - c0)` |

For N > c0, `N ≤ C < 2N`; hence dead payload is less than `2eN`, and total payload reservation is less than `4eN`. Dead payload is less than the final capacity's payload, but can exceed the live N-element payload just after growth. “Only one extra live-sized array” is therefore not an exact bound. For N ≤ c0, a deliberately oversized initial capacity can dominate N; use the exact formula.

For header `h` repeated in every slot and alignment `a`, the exact total is
`sum(i=0..m, align_up(h + e*c0*2^i, a))`;
dead-slot waste is the same sum excluding the final slot. A safe upper bound is `e(2C-c0) + (m+1)(h+a-1)`. This assumes each slot begins aligned. Charge real bump padding if other alignment classes can intervene.

**Worked case: c0 = 4, N = 1,000, e = 8.** C = 1,024 and m = 8. Capacities sum to 2,044; old capacities sum to 1,020.

| Layout assumption | Result |
|---|---:|
| Dead data payload | 8,160 B |
| Final data capacity | 8,192 B |
| Final unused capacity | 192 B |
| All data payload | 16,352 B |
| Existing-style 40-byte header per slot, aligned to 16 | 16,784 B total; 8,544 B in dead slots |
| Illustrative stable 32-byte descriptor allocated once, separate 16-aligned payloads | 16,384 B total; 8,160 B in dead payload slots |

The last layout is a design example, not today's ABI or a final header-size commitment. Each power-of-two payload here is already 16-aligned. A descriptor needing more ownership/debug fields costs more. The 40-byte example illustrates current header overhead, **not** a claim that copying today's header preserves aliases.

This is acceptable for a teaching language with documented capacity growth and a charged budget. Geometric growth gives O(N) aggregate copying and amortized O(1) append within the stated assumptions. Extending the last allocation in place can improve these numbers; interleaved allocations force the worst case, so do not depend on that optimization.

The bound does **not** cover arbitrary resize histories. Shrink-to-fit followed by regrowth, clear-and-reallocate, explicit reserve, or repeatedly constructing new koshes can retain arbitrarily more than the final live N elements. Keep clear/shrink logical only in the initial design, retaining capacity; charge every fresh allocation. For multiple koshes, sum their allocation histories plus other arena allocations. `parimita B` limits total charged occupancy, not merely the final lengths. A finite budget bounds memory, not CPU time or loop duration.

## The alias problem inside a fixed arena

Consider conceptual operations: create k with capacity four; copy its reference to a; allocate something after k; append a fifth element to k. A new slot is allocated and k is updated. **a still points at the old slot under the current data-pointer representation.** The old bytes being mapped only makes the bug quieter: a can see a stale length and data, and writes through one alias need not reach the other. No arena relocation is required for this failure.

Recommended design: a kosh reference points to a **stable descriptor** allocated once in its owner arena. The descriptor stores data pointer, length, capacity and owner information as required. Growth allocates new data, copies, then atomically at the language-operation level commits descriptor fields after success. Every alias follows the same descriptor. Indexing adds a data-pointer load; cached element addresses/views are invalidated by growth unless the borrow rules forbid growth while they exist. Parameter passing, library layout assumptions, debug printing, module ABI and raw interop all need review. This is not a two-line allocator change.

An alternative is to forbid aliasing across growth or give kosh a move-only ownership rule. That may avoid indirection but changes assignment and function semantics. Keeping the old payload alive is not an alternative to either contract.

### Exit and escaped references

Removing generations/liveness metadata is sound only after complete static lifetime enforcement for the safe subset: outer assignments, returns, globals, fields, container elements, aliases, indirect calls, retained function arguments, and nested/recursive activations. Unknown callees need a no-retain contract or rejection. A kosh created outside a block must not acquire references to shorter-lived objects through its elements. Copying a handle into an outer slot does not copy its storage.

Example 286 uses a block kosh, reads it via a function, and returns a computed scalar: retain that valid behavior. Example 287's outer assignment must become a compile-time escape error if that is the chosen new rule; its old runtime-error golden then needs an intentional, reviewed migration. Example 299's block-local float kosh remains valid. These three files were read; this is not a claim of a fresh exhaustive escape census.

If any raw escape is still allowed, unmapping the arena can turn today's named runtime refusal into a fault. Reusing the address can make a stale reference identify a different object. A stable descriptor *inside the freed arena* cannot diagnose its own later use. Either prove safe references cannot escape, retain external liveness information, or explicitly classify unchecked raw use as unsafe without promising the named diagnostic. Do not remove the current check first and assume a partial escape checker replaces it.

“Block exit frees the arena” also needs precision. Rewinding a shared arena makes bytes reusable but does not necessarily return mappings/pages to the OS. Unmapping a dedicated block allocation releases it to the OS; a chunked arena may require multiple unmaps. All exits—fallthrough, return, break, continue, supported error unwinding—and nested scopes must follow the owner discipline. Zero-initialization must be preserved when dirty storage is reused; fresh-mapping zeroes are not supplied automatically by a bump rewind.

## Fixed capacity, exhaustion and budget accounting

**Start with a fixed, nonmoving arena per bounded block activation.** Reserve its storage lazily if appropriate; do not assume B reserved virtual bytes equal B resident bytes. Let B be its maximum chargeable object storage. Charge headers, descriptors, dead slots and alignment padding. Keep any fixed arena-control/page-rounding overhead separately reported; if B is advertised as a strict total physical footprint, that overhead must instead fit within B and RSS still cannot be promised from allocator accounting alone.

Before every allocation or growth, check capacity multiplication, header addition and alignment for overflow, then test the rounded request against remaining budget/arena space. On insufficient budget, produce a named diagnostic and nonzero exit before copying or updating the descriptor. OS allocation failure is a distinct failure reason. The current operation leaves the old kosh usable up to the failure point; earlier argument side effects are not rolled back. Do not silently fall back to an uncharged persistent allocation.

**Never move a populated arena.** Reallocating/copying it invalidates every direct address, descriptor and interior pointer. A later unbounded-block policy may append nonmoving chunks with explicit total limits and a chunk list, paying for tail slack and cleanup. A reserved contiguous range can commit more pages without moving its base, but only within its actual reservation. Neither strategy is the same as relocating the arena. Fixed capacity is sufficient for an initial implementation; unbudgeted blocks still need a published default/configured capacity and an exhaustion rule.

Allocation ownership follows the defining block activation, not whichever block happens to call push. Growing an outer kosh inside an inner block must allocate from the outer owner; otherwise the new data dies too early. For constructors in other functions, choose explicit owner passing or a documented propagated owner context; today's lexical allocation behavior must not silently become a different lifetime. A shared active context must be stacked for nested calls and recursion. These ownership decisions precede claims that budgets cover calls.

The current R103 comment explicitly excludes koshes and called-function allocations from its lexical `nirmmita` budget, and PE is unchecked. **The proposed unified budget is new work.** Neither an existing budget counter nor the current persistent allocator can simply be relabeled a bounded block arena.

### Define `parimana()` before implementing its counter

For the proposed arena model, recommend: **return chargeable bytes currently occupied by the innermost active block arena**, with 0 outside any active block. It includes live capacity, dead growth slots, descriptors and padding, and excludes uncommitted reserve, allocator-external control memory, unrelated persistent allocations and process RSS. It allocates nothing and does not reset counters. Document that 0 outside a block does not mean the process uses no memory.

This is an occupancy metric, not a live-element metric. Clear/pop do not reduce it when capacity is retained; growth raises it by the new slot charge; block exit restores the previous active owner and releases that block's charge. For nested arenas, account child occupancy against bounded ancestors while it is owned by them and remove the child charge on reclamation. At every active bounded owner enforce `0 ≤ charge ≤ limit`. If implementation chooses cumulative allocation traffic instead, give that metric a distinct name/contract; repeated child blocks make traffic and current occupancy diverge.

Calls to `parimana()` observe the active query context, whereas allocations are charged to their actual owner. Explicitly document this distinction for outer-owner mutations inside an inner block. A no-argument query cannot describe every arena plus persistent retention and RSS at once. Future per-owner and persistent counters can supply those views separately.

Claude R107 asks for “bytes currently in use” **now**. On today's implementation, expose only the categories actually counted and state excluded kosh regions, persistent concatenation and fallback allocations as applicable. Do not name a sum of requested live bytes “RSS” or a shared-cursor difference “all process memory.” If the desired API is global allocator occupancy instead, specify and maintain a ledger across every allocator/fallback and reclamation path; it is a different query from block usage. This ambiguity should be resolved in the implementation report, not hidden behind one integer.

## WS2 — explicit identity policy

R175 recommended refusal until semantics were chosen. With the owner now asking for that choice, I recommend **identity equality for mutable reference objects**, with content equality as a separate explicit operation. This avoids surprising recursive traversal, padding comparisons, cycle problems and hidden allocation. It does not change string content equality.

| Live operands of the same reference type | `==` | `!=` | `<` | `<=` | `>` | `>=` | `+` |
|---|---|---|---|---|---|---|---|
| kosh | Same object identity | Different identity | Refuse | Refuse | Refuse | Refuse | Refuse |
| mala | Same array identity | Different identity | Refuse | Refuse | Refuse | Refuse | Refuse |
| rachana | Same record identity | Different identity | Refuse | Refuse | Refuse | Refuse | Refuse |

Two separately created objects are unequal even if all elements/fields match; a copied reference is equal; mutations and kosh growth do not change identity. Return 1/0 and make `!=` the complement. Only valid live references may be compared. Different reference types, reference-versus-number and unresolved operands refuse. If rachana later becomes a by-value type, its equality requires a separate value-type decision; this table is for its reference form.

Content equality should explicitly compare logical elements/declared fields, ignoring allocator metadata and padding, with a documented nested-reference/float/cycle policy. Container concatenation, copying and ordering also require explicit APIs and ownership rules. Address sorting is not an implicit container ordering operation.

**This is not documentation-only for the complete seven-operator rule.** v288 intentionally rejects recognized kosh equality; enabling identity requires a targeted code change. Mala/record raw-address equality can implement identity only while their valid object addresses are stable and type checking establishes the operand kinds. Their arithmetic/order paths still need rejection. Moving kosh payloads need stable descriptors or another stable handle; raw data-pointer equality breaks aliases at growth. Keep the current refusal until that representation and lifetime contract is met. Cheap identity comparison is the eventual runtime implementation, not proof that the whole compiler already enforces the rule.

## WS3 — vocabulary

Keep **`kosh`** as the collection name. Moving its backing storage from a dedicated reservation to an arena changes allocation policy, not the abstraction a student uses. Keep **`kshetra`** for the storage arena and **`parimita`** for the budget qualifier; define **`parimana()`** by its precise byte metric rather than expecting the name to specify accounting. No new collection word is needed for an arena-backed instance.

Using the project's supplied glosses, these names form a coherent teaching vocabulary. This is an API/naming recommendation, not an independent Sanskrit grammatical or native-speaker certification. Native-speaker review: **NOT RUN**. Avoid promising a particular etymological interpretation as a safety argument.

Suggested teaching rule: “A kosh belongs to the block where it is created. Other names refer to that same kosh; growth preserves those names. It cannot be kept after its owner ends. Its block budget counts every occupied slot, including old slots left by growth.” This is the proposed target, not today's complete guarantee.

## Acceptance boundary and next work

Before switching allocation: establish stable kosh references, complete the promised escape checks, specify owner-aware budget/query accounting, and test failures before state publication. Then test forced interleaving and multiple aliases, nested owner mutation, recursive block entry, all exits, exact-budget/one-byte-over boundaries after alignment, reused zeroed storage, allocation failure, arithmetic overflow, and direct/object/separate builds. Test PE separately; do not present Linux reclamation as Windows acceptance.

Formula arithmetic and pinned source inspection were performed; the 1,000-element totals above are calculations, not measured RSS. Native build/probes/suite/guard/gates/performance: **NOT RUN — no toolchain** (`command -v nasm` found none). Generator rerun: **NOT RUN**. Native Windows and CI: **NOT RUN**. No source/library/tests/tools/README/Windows/frozen-pack files changed.
