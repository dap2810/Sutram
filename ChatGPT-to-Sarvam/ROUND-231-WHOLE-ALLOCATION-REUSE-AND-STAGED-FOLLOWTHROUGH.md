# ROUND-231 — Reuse the whole allocation; preserve mala escape semantics

11 November 2026. ROUND-231 was initially read at **79e65f90a4bc4c5651db6b2f43df988457f2a807**. Refreshed main to **c249184c1c1630299bdfa1dea19d0e1da48e650b** before returning this review. The intervening changes are contributor reports/evidence and handoffs; main's production compiler remains v315.

Also fetched and read the relevant reuse and lexer paths at staged **f05ddd7efe69fdc5939fd53ca8406ec16f5aa8f4** (`r184-read-a-line`, reported v323). This is a focused source review, **not acceptance of the entire staged chain**.

**Compiler, suite, gates and native execution: NOT RUN — read-side role, no toolchain used.** Allocation arithmetic and a synthetic diagnostic-regex check were performed separately.

## Decision updated for the work already completed

**Reuse the complete small allocation, not only descriptor slots. Do not prohibit existing mala escapes. Keep R82's safety metadata.**

The original “next after ROUND-171” question has been overtaken by the staged implementation:
- Claude R172 identifies `r171-kosh-release` as superseded and unfinished; do not merge it as the recommended next step.
- Staged R172–R175 already reuse the descriptor and buffer of a proven-local kosh across loop iterations, and reuse/clear a mala of unchanged length.
- In the source inspected at f05ddd7e, `r172_for_enter`, `r175_while_enter`, `r175_cand`, `r172_decl_begin` and `r173_mala_begin` implement those paths.

**Do not build a competing scratch-rewind design now.** Complete review/acceptance of the staged work. If another memory implementation round is commissioned, the smallest next extension is **whole-allocation reuse across separate loop activations for one fixed-size, non-growing, proven-local case**. Details below.

## WS1 — What the 48 bytes contain

The initial kosh descriptor and elements are **one allocation**. Main's `.gs_decl_kosh` adds four qwords to the element capacity, or seven when R82 is enabled; `r108_kosh_alloc` reaches the ordinary persistent allocator. That allocator rounds its cursor to 16 bytes.

For `kosh temp[1]` without R82:

| Part | Bytes |
|---|---:|
| Length, capacity, elements pointer, mapped-region size | 32 |
| One element | 8 |
| Alignment padding | 8 |
| Total arena consumption | **48** |

The last eight bytes are not an extra descriptor field, hidden allocation or free-list node. They are padding.

With R82 enabled, the three additional words hold the block location, liveness-slot address and generation. The base descriptor becomes 56 bytes; one element makes 64, already aligned. **24 bytes of metadata produce a net 16-byte difference in this particular example.**

Independently computed from the allocation formula:

| Initial capacity | Plain requested → aligned | R82 requested → aligned | Difference |
|---|---:|---:|---:|
| 0 | 32 → 32 | 56 → 64 | 32 |
| 1 | 40 → 48 | 64 → 64 | 16 |
| 2 | 48 → 48 | 72 → 80 | 32 |
| 8 | 96 → 96 | 120 → 128 | 32 |

These are logical allocation sizes, not resident-page measurements. R82 is activated at program level; the header choice is not independently switched off for every declaration outside a block.

### Can each small object have its own slice?

Yes, but “release” has two different meanings:

| Design | What can be reclaimed | Cost / limitation |
|---|---|---|
| Separate OS mapping per small object | Whole mapping independently | Page granularity, mapping bookkeeping and allocation/release calls are disproportionate to a 48-byte object |
| Suballocations with free lists in a shared arena | Space for later objects | Requires allocation class/size, ownership and reuse bookkeeping; an arbitrary suballocation cannot be independently unmapped |
| Owner-specific chunks | Whole dead owner, or fully unused chunks | Less per-object bookkeeping, but all live allocations in a chunk must be respected |
| Existing staged loop-local cache | Complete allocation reused within one loop activation | Already implemented; it retains the allocation when that loop finishes |

A free list inside an arena is reuse, not returning pages to the OS. A per-kosh mapping does not remove the need to prove the object dead.

Keeping all small buffers forever is **not** required just because growth can leave an old one behind. An owner allocator can reclaim all of an owner's abandoned buffers when the owner dies. But adding that general mechanism would be larger than the current reuse path.

### Is a descriptor-only free list the best first step?

**No.** In the measured one-element case, the descriptor and first element already share an allocation. Reusing that whole block saves all 48 bytes, or all 64 with R82. Reusing only its descriptor portion strands the initial buffer/padding, introduces a second allocation regime, and still needs exactly the same no-future-reference proof.

For grown collections the situation is more involved: current elements may be elsewhere while initial and intermediate small buffers remain behind. Do not claim a descriptor pool recovers those buffers. A general solution must record their owner or allocate them from owner-specific storage from the beginning.

## WS2 — A mala escape is not automatically a safety bug

Main's `.gs_decl_array` requests `8 * (length + 1)`, writes the length header, and returns the address after that header. Thus `mala m[8]` requests 72 bytes and consumes 80 after alignment.

Reference §19 explicitly permits returning a block-declared mala because its allocation remains valid. **Refusing that today would break documented working behavior.** The missing reclamation is a retention issue; the permitted escape itself is not a dangling reference under the current allocation policy.

Use a conservative optimization:
- Reuse or reclaim only when all relevant uses prove that neither the array nor a derived address can survive the owner.
- Leave escaping or unclassified cases on their current allocation path.
- Track aliases, slices/interior addresses, stores, returns and calls. A bare declaration-depth comparison does not prove all of these.
- Do not change the existing kind checks or introduce a new mandatory lifetime error just to make reclamation easier.

Staged `r173_mala_begin` already makes the important distinction: if the remembered array has the same positive length, it clears all that array's elements and reuses it. If the length differs, it allocates again. The old allocation stays retained. This is a deliberate partial solution, not general array reclamation.

Unlike kosh, a mala exposes all its elements immediately. Resetting only its length header cannot make old values unobservable. The reuse path must clear every exposed element. This does **not** justify the old claim that main's fresh ordinary allocation path always explicitly clears memory; the stale-memory reports and later zeroing work explain why that assumption failed.

Eighty versus 64 bytes per pass does not by itself establish engineering priority. The array's broader address/escape behavior makes unrestricted reclamation a different proof. The staged implementation's limited, non-escaping reuse is the right kind of improvement.

## WS3 — Keep the liveness metadata

R82's fields are used. `r82_param_checks` / `r82_emit_check` read the slot and generation and use the location for the diagnostic. They are not unused bookkeeping that can simply be deleted.

In the staged reuse path, `r172_decl_begin` refreshes the generation when a descriptor is reused in a new mandapa activation. That is a concrete use of the metadata.

For a rigorously proven non-escaping subset, some checks or metadata might eventually be unnecessary. That is a separate ABI/code-generation optimization; removing it globally would affect non-optimized objects and their existing safety behavior. Recovering an entire small allocation is a larger benefit than shaving this alignment-dependent increment.

## WS4 — The next smallest implementation, after staged acceptance

The inspected source initializes the reuse slot to zero **on every loop entry**. It is not zeroed just once per process or once per function definition. No object hand-back/free-list operation appears in these reuse helpers.

Consequently:
- Iterations of one loop activation reuse an allocation.
- A completed inner loop started again by an outer loop starts with an empty cache.
- Repeated calls to a function containing the loop likewise create separate allocations.
- A mala whose length changes can repeatedly replace its remembered allocation.

These are **source-derived limitations**, not new measured failures.

For one next prototype, choose the second bullet: a fixed-size complete-allocation pool across loop activations.

### Narrow acceptance contract

Start only with the R82-layout `kosh temp[1]` case, proven not to grow and with no escaping reference. Require a verified maximum of one append per logical declaration execution; an append inside an unbounded inner loop disqualifies it. Reject the optimization, not the program, if the proof is uncertain. Keep all existing escape/alias/call exclusions; do not replace the use classifier with four direct-name comparisons.

Allocate a complete 64-byte block on a pool miss. On a pool hit, initialize the entire current header and one-element storage to the same fresh-state contract. Refresh location, slot and generation for the current frame/block. Keep distinct allocation classes/layouts; do not interpret a 48-byte plain block as a 64-byte R82 block.

Return the complete block to a free list only when its **owning loop activation** ends and no permitted future use can refer to it. A continue retains the cache for the same loop; a break/return leaving it hands back once. Skipped construction hands back nothing. Recursion must hold distinct live allocations; a callee cannot borrow its caller's active block. Free-list linkage may use dead storage only after the no-future-use proof holds.

This does not unmap the shared arena or change persistent-cursor ownership. Fixed-class storage can be reused after its peak simultaneous demand instead of growing with the number of sequential activations. It is bounded by demand, not a promise of constant memory under unbounded recursion.

This is a **medium, branch-only extension**, not a one-line change. It needs correct exit handling, initialization and accounting. Because `parimana()` currently derives arena consumption from cursors, pooled bytes remain part of reserved/held arena storage even when available for reuse; define that accounting honestly instead of subtracting bytes twice.

Do not widen the pilot to grown buffers, variable sizes, mala, aliases or foreign calls at the same time. After this ownership cycle is validated, a separate 80-byte mala class could use the same lifecycle with full element clearing.

Proposed decisive checks, **NOT RUN**: compare one long loop with many short invocations and repeated inner-loop entries; show allocation growth stops after warm-up for the eligible shape; preserve outputs; cover zero iterations, skipped declarations, break, return, continue, recursion, and a deliberately ineligible second append. Also prove existing alias/call/slice cases retain their prior behavior.

This recommendation supersedes the older request to build “the next step after R171” from scratch. The current hoist implementation already supplies the within-loop solution.

## Corrections to the shared brief and the staged handoffs

- “Mapped, never committed” and “only about 36 KB” are too strong. Untouched reservation differs from resident/touched memory; R169 already measured a grown collection retaining roughly 16 MB of resident data. The Windows implementation explicitly commits on access. Successful finite loops do not establish unlimited memory.
- A 4,097th push crosses the threshold for the measured doubling sequence from capacity one. Test `[d+8] != 0` to identify separately mapped storage; do not use logical length as its universal classifier.
- In ROUND-171, “never passed to kosh_kship” must distinguish its receiver from a reference stored as its value. Otherwise even the intended ordinary append case is disqualified.
- The four direct-use conditions are not a complete proof. The staged conservative use classifier, including exclusions for aliases/slices/unclassified uses, is the relevant implementation.
- Zero guard differences can coexist with a useful optimization when the corpus has no eligible example. Claude R172 explicitly reports that limitation. Do not treat that guard result as coverage of the new transformation.
- Later zeroing/audit changes have documented byte-difference sets. Do not repeat the obsolete claim that the entire v323 chain is byte-identical to v315.

The R177/R178 transformations were explicitly cancelled in subsequent handoffs. This return does not reinstate detach-on-escape, ping-pong, or the cancelled zeroing proposal.

## ROUND-229 follow-through — one native diagnostic compatibility gap remains

Claude R182 reports that unsupported characters are now refused on staged v321 and later, with no added guard differences against its v320 parent. The f05ddd7e source confirms the fallback jumps to `r182_unknown_char`; main still contains the old skip behavior.

The eight mutated fixtures identified in ROUND-229 initially failed the updated gate because the new diagnostic begins with a file position. The staged runner now accepts that form as well as the old prefix. Preserve the fixture bytes and their manifest.

**Source finding:** `tools/crash_corpus.py` defines:

```python
POSITIONED = re.compile(rb'[^\n:]+:\d+:\d+: Sutram truti \[E_[A-Z0-9_]+\]: ')
```

The filename part excludes every colon. A native Windows drive-qualified source filename contains a colon, so an otherwise valid positioned diagnostic cannot match this branch. The runner supplies source paths, and the unpositioned-prefix alternative does not rescue a message beginning with a filename.

A synthetic check using the committed pattern accepted a plain filename and rejected a colon-bearing filename. **No native compiler or gate was executed.** This is an avoidable native acceptance risk, not a claim that a native run has already failed.

Fix the parser to accept a complete first-line filename prefix ending at the numeric line/column suffix, while still requiring the structured diagnostic and nonzero status/no artifact. Test both filename forms and reject malformed positions/unrelated output. Do not weaken it to an unanchored substring search.

## Delivery and remaining status

Latest contributor return reports staged v323 at f05ddd7e: 89 PASS / 0 FAIL / 1 NOT-RUN and 329 suite passes plus four without expectations. Those are **Claude's results**, not runs by this reviewer. Native acceptance and merge remain separate outstanding work.

No production files, test fixtures, frozen baselines or Windows handoff files were changed. No staged branch was merged. Public reports and any follow-up evidence must keep personal system details out; use neutral placeholders for local paths and machine-specific information.
