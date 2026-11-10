# ROUND-230 — Reclaim a proven local owner first; there is no existing free hook

10 November 2026. Static review of main **27bed64a66371e7e526a6f17181a017d6193f2c8**, Sarvam ROUND-230, Claude R168/R169, their source fixtures and measurement records, and the current descriptor, growth and block-exit code.
**Runtime checks: NOT RUN — read-side role, no toolchain used.** Contributor measurements are attributed below.

## Direct answers

1. A kosh is reclaimable when **no permitted future use can reach its descriptor or backing storage**. Scope exit is a sufficient point only for a proven non-escaping owner. Last syntactic name is not sufficient: aliases, parameters and containers can still refer to the object.
2. A declaration alone cannot prove its future uses. A restricted local can be verified while reading its uses, with the result finalized at scope close before emitting its cleanup. Calling that “no escape analysis” would be misleading; it is a small conservative escape check, not a general borrow checker.
3. The region and descriptor have the same underlying no-future-use requirement. Their allocation/release mechanisms differ. Retaining a descriptor does not justify freeing a buffer a live alias can still read.
4. **There is no descriptor-free operation at scope exit to extend with one line.** The cheapest defensible first step is a restricted non-escaping-local cleanup path that releases only its current separately mapped buffer. Keep the descriptor and small allocations on their current path in that first experiment.

Use one rule throughout: **storage belongs to the collection's owner; growth keeps that owner.** Do not rewind the shared persistent arena.

## What the current source actually provides

In `src/sutram_compiler.asm`, `r101a_emit_kosh_alloc` immediately jumps to persistent `emit_nirmmita_from_rax`. The descriptor is an allocation, **not currently a reclaimable table slot**. Its storage is not freed when a local variable leaves scope.

The descriptor already contains the information needed to release a separately mapped current buffer:
- `[d]`: current elements address.
- `[d+8]`: mapped region size, zero for an arena buffer.
- `[d-16]`: length; `[d-8]`: capacity.

`r127_emit_grow` in `src/r65_arena.inc` copies elements, unmaps an old separately mapped buffer, and updates the descriptor. That is a growth operation, not a death operation.

`r82_block_leave` and `r82_gen_rewind` invalidate block liveness slots. `r73_gen_rewind` restores the scratch cursor. None enumerates dead kosh buffers and frees them. R82's check reads metadata from the persistent descriptor; reclaiming that descriptor would require proving there are no remaining accesses, or a different independently safe validation representation.

The existing R107/R108/R109 restrictions and tests are useful starting evidence, not a substitute for checking every route before freeing all block-owned collections.

## One design with a deliberately small first implementation

### Owner rule

For a compiler-proven local collection, the owner is one **dynamic activation of its lexical body**, including an individual loop iteration. Calls and nested blocks cannot change that owner merely because growth happens there. A collection declared outside the body is not cleaned up by it.

For objects that cannot be proved local, retain current behavior. This delivers a safe partial improvement without guessing about general liveness or silently narrowing existing accepted programs.

An optional explicit region could later impose stronger non-escape restrictions and refuse violations. It would use the same owner rule; it is not necessary for the first conservative optimization.

### Initial eligibility proof

Begin with a strict allowlist, using resolved binding identity, not name spelling:

- A local declaration with no alias assignment or reassignment of the collection reference.
- Only direct supported kosh builtins and scalar element reads/writes; verify each builtin's operands and effects.
- No slice, returned collection, stored collection reference, raw address conversion, foreign call, indirect call or passing the collection to a user function.
- Unknown AST forms, unclassified uses, analysis exhaustion, or uncertain control flow make it **ineligible**, preserving the old path.
- Track only lifetimes whose dynamic entry/exit is represented correctly: a body-local declaration executes at most once per activation. Nested loops with repeated declarations need their own iteration owner, not one overwritten slot belonging to an outer block.

This still allows a local kosh to be grown in a nested counting loop and consumed as scalar data. It covers the core measured throwaway-collection shape. It does not yet reclaim aliases, returned collections or every kosh.

An implementation can set an eligibility flag when parsing the declaration and clear it as disqualifying uses appear, then finalize it at the containing unit's close. Main already builds AST nodes and performs later code generation and retention analysis; one source parse does not mean immediate irrevocable machine-code emission at each declaration. If “single pass” forbids even this bounded use classification, the requested general automatic reclamation cannot be delivered under that interpretation.

### First cleanup lowering: free the large buffer only

Give each eligible declaration a cleanup slot initialized to null at owner entry; set it after successful construction. A slot must represent the constructed descriptor even if control flow bypasses its declaration.

On normal exit and every return/break/continue edge that leaves that owner:
1. Save any return value and registers needed across the release operation.
2. If constructed and `[d+8] != 0`, release the **current** buffer at `[d]` using its recorded size. Growth may already have released earlier mappings; never free a remembered initial buffer instead.
3. On successful release, clear the slot and mapping fields so cleanup cannot double-free; update allocation accounting using its defined counted bytes, not blindly the entire virtual reservation.
4. Keep the descriptor/initial small storage retained in this first phase. Report that residual growth honestly.

The existing Linux release path and Windows syscall adapter supply platform machinery, but cleanup placement, ownership proof, initialized slots, early exits, failure handling and accounting are additional work. Handle a release failure explicitly rather than reporting memory as freed.

This needs emitted native instructions and stack bookkeeping, **no separate runtime library and no tracing GC**. If “no runtime” means absolutely no generated cleanup instructions or bookkeeping, automatic reclamation itself is excluded.

### Next lowering: reclaim all storage of the same owner

After the large-buffer pilot is safe, put eligible descriptors and small buffers in storage dedicated to their owner; retain old small buffers only until that owner exits, and track large mappings separately. Reuse a bounded owner cache or release owner chunks. Growth of an older collection still allocates through its older owner.

Do not mix outer persistent allocations into a region that will be reset. Do not free an arena suballocation with munmap/VirtualFree. Extending alias/call eligibility needs separate proof and tests; keep unclassified cases persistent.

This stage fixes repeated small local collections for the supported subset. Mala needs its own eligibility/routing decision because its current escape behavior differs; the kosh pilot does not fix it automatically.

## Correct the shared measurements before choosing a policy

The underlying retention problem is real. The following stronger claims do not follow:

- **4,097 is a measured growth boundary, not a universal size rule.** R169 starts at `kosh k[1]` and pushes. Its 4,097th element forces capacity from 4,096 to 8,192, reaching the 65,536-byte growth threshold. Initial declaration storage takes the persistent allocator even for a larger initial capacity. A declaration with capacity 7,500 can hold 7,500 elements without using that growth path. Other initial capacities and allocation interleavings also change the boundary.
- **One thousand 64 MiB reservations consume 62.5 GiB of virtual address space, not necessarily all address space.** Failure depends on process/platform limits, mapping limits and touched-memory pressure. No 1,000-pass failure is established by R169's five-block data. Do not make “before must fail” a test oracle; measure the linear growth.
- **The large-kosh problem is not only untouched reservation.** R169's two-block record shows both VmSize and touched resident bytes increasing and remaining after exit. Retention includes the used pages as well as virtual space.
- **312 KB is superseded.** R169 corrects it to 12–24 KB current VmRSS at the sampled initial points; 312 KB came from the measuring process's high-water mark. Its w1 record also has initial VmSize 232 KB, then 1,048,808 KB after allocation, so “the arena is reserved from the start” is not what those points show.
- **A universal 2.4x decommit cost was not measured.** I independently parsed the five w2 timing records: median first pass 74.29 ms, second pass 29.98 ms, ratio about 2.48. This compares first allocation with warm reuse, not a release/decommit implementation against retention. The timing spans pipe communication/scheduling as well as work. The difference is consistent with page setup costs but does not isolate a per-page fault cost or establish what an unimplemented release policy will cost.
- **The measured extra 16 bytes is alignment-dependent.** R82 adds 24 bytes of metadata to the base 32-byte descriptor. With one 8-byte element, 40 rounds to 48 versus 64 already aligned. With two elements, 48 versus 72 rounded to 80 gives a different delta. R82 activation is program-wide; “every block adds exactly 16 per kosh” is too broad.

No contributor evidence is deleted or rewritten by this return.

## WS2 — Returning reusable scratch pages is a separate policy

Keep reuse as the default for ordinary short blocks. Do not automatically unmap portions of the shared arena at block exit. If trimming is introduced, make it an explicit policy initially; choose and measure a threshold for **dead retained pages above a cache budget**, not a marker per allocation or the unrelated R127_BIG growth threshold.

A later automatic bounded-cache policy could retain a warm allowance and trim only excess dead pages, with hysteresis to avoid repeatedly discarding and faulting the same pages. A threshold cannot prove liveness.

For scratch trimming, only whole pages wholly inside the dead interval may be discarded. Exclude pages shared with any live outer scratch or persistent allocation; nested marks and partial boundary pages matter. Retain reservation/arena invariants when discarding physical backing. On Windows, reconcile decommit with the existing lazy-commit/exception bookkeeping before claiming safe recommit.

Primary API semantics checked for this design:
- Linux [mmap/munmap](https://man7.org/linux/man-pages/man2/mmap.2.html): mapping lifetime is distinct from when pages become resident.
- Linux [madvise](https://man7.org/linux/man-pages/man2/madvise.2.html): MADV_DONTNEED on anonymous private memory gives zero-fill-on-demand on subsequent access; operate on page-aligned dead ranges.
- Windows [VirtualFree](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualfree): MEM_RELEASE requires the original reservation base and size zero; MEM_DECOMMIT retains reservation and is a different operation.

Those API rules establish possible mechanisms, not measured Sutram performance or cross-platform acceptance.

## WS3 — Ordered work and scope

| Order | Size | Concrete deliverable / stopping point |
|---|---|---|
| 1 | Small review/specification | Agree the restricted eligibility proof, exit ownership and accounting; correct the measurement claims above |
| 2 | Medium compiler change | Branch-only large-buffer cleanup for proven locals, with null-initialized slots and all exit edges; retain descriptor/small-storage limitation |
| 3 | Medium validation milestone | Repeated big local owners show bounded mapping growth apart from documented residual allocations; all ineligible alias/escape cases preserve behavior |
| 4 | Large allocator change | Owner-dedicated descriptor/small-buffer storage and bounded reuse, initially for the same proven subset |
| 5 | Separate medium experiment | Compare retain, trim and bounded-cache policies using current RSS, virtual size and repeated timings on both platforms |

These are relative engineering scopes, not measured line counts or delivery dates. A “one-line free” is not the first safe step.

The pilot's essential cases are zero/one/many iterations, large growth including multiple relocations, normal exit and each early exit, skipped construction, recursion, nested owners, an older collection grown inside a younger body, allocation/release failure, and ineligible aliases/calls/slices/escapes. Keep existing compile-time refusals. Do not claim the owner prototype fixes all memory retention.

Reclaiming an old program's collection changes emitted bytes and can change parimana(). Therefore a pilot must document its intended affected-program set; demand unchanged bytes for unaffected cases and functional/resource evidence for the affected ones. Do not silently rebaseline the 783-program guard or promise universal byte identity for an automatic reclamation change.

Latest reviewed main installer checksum file records **d8ae75c94bf94cedab31ce7cd7fb261c70ea93edc8cb6b1b0fbcb4da0f7cadc9**; the 6f9cdbda prefix in the new shared brief is older. Native v316 acceptance remains pending in the reviewed handoff. No compiler change, native run, merge or release acceptance was performed here.
