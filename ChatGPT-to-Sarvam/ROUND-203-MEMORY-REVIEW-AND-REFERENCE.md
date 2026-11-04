# R203 — the descriptor works, but the memory review is not finished

Reviewed main at **`2841fd23608c081a4209ac59259c3cb7b8dfdde2` (v302)**, including R203, Claude's R127 implementation report, the allocation/index emitters, R127/R82/R123 gates, examples 317/318 and 356, and the current reference. This is a source review and documentation handoff. Every reproduction below is **NOT RUN**; predicted results are distinguished from native observations.

**WS1 answer: no, do not publish “the memory model has no known defect.”** The descriptor addresses the tested ordinary-alias relocation failure and the fixed reservation for every small collection. I found three source-level correctness problems to reproduce and repair: stale indexing state across a mutating index expression, unchecked capacity-to-byte arithmetic, and Linux large-growth accounting using a syscall-clobbered register. These are separate from the intentionally retained storage and unsupported features discussed below.

## 1. Fix these paths before closing the review

### F1 — indexing saves an element address and length across mutation

**Source:** `src/sutram_compiler.asm`, `r127_ix` (566), indexed assignment (19666 onwards), `.ge_index` (21616 onwards), `.ge_call_koshclear` (21866), `.ge_call_koshpush` (22135).

Both read and write indexing emit `r127_ix` before evaluating the index. It reads the length, dereferences the descriptor to the current elements, replaces the saved descriptor with that element address, and saves the length. The index expression is then evaluated; the bounds check and access use those old values. An index expression may itself clear or grow the same collection. No foreign call, thread or parameter-growth support is needed to reach this ordering.

**Proposed reproduction F1a — NOT RUN:**

```sutram
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    vitti obstacle = nirmmita(16)
    k[kosh_kship(k, 8) - 2] = 99
    likha(k[0])
}
```

`kosh_kship` returns the new length, so the index is zero. The intervening allocation forces the small elements to move. Source tracing predicts that the assignment writes 99 into the retained old buffer and the final read prints 7. Under the R202 descriptor contract it must print **99**: evaluate the index once, then access the current backing buffer of the originally selected descriptor. This is an unverified prediction, not an executed output.

**Two further discriminating probes — NOT RUN:**

- With the same setup, `likha(k[kosh_kship(k, 8) - 1])` should read the new element, **8**; the saved old length instead predicts an erroneous bounds failure.
- After putting 7 into a one-element collection, `likha(k[kosh_shodh(k)])` must bounds-fail because clear returns zero and makes the collection empty. The saved old length instead predicts a read of 7. Test indexed assignment with clear as well.

**Required fix:** preserve the selected descriptor identity, evaluate the index once in the defined order, then load its current length and data immediately before checking/accessing. Keep assignment's established RHS evaluation order. Review slice construction and call-argument evaluation for the same cached-address pattern. A larger probe that causes an actual old-region release is also needed: stale data pointers can then address unmapped memory rather than harmlessly retained bytes. Do not fix only ordinary alias assignment; that part already works.

### F2 — a positive capacity can wrap into a tiny allocation

**Source:** `.ps_kosh` (14911 onwards) accepts a capacity expression. `.gs_decl_kosh` (19137 onwards) normalizes negative values, saves the original capacity, adds four header words (seven with R82), and shifts by three without checking overflow. `r127_emit_make_check` only checks allocation failure. It cannot detect a successful allocation of the wrong size. The growth path also doubles capacity and byte reservation sizes without complete checked-size guards.

**Proposed reproduction F2 — NOT RUN, default ordinary build, no mandapa:**

```sutram
mukhya() {
    vitti n = 2305843009213693952
    kosh k[n]
    vitti p = nirmmita(16)
    p[0] = 17
    kosh_kship(k, 99)
    likha(p[0])
}
```

`n` is the valid positive integer `2^61`. The emitted allocation calculation `(n + 4) << 3` wraps to **32 bytes**, while the descriptor still records capacity `2^61`. Its first element address is just past that 32-byte allocation, where the following ordinary arena allocation starts. Source tracing therefore predicts corruption of `p[0]` to 99. The accepted behavior must instead be a deliberate capacity/size refusal before any element store. This does not need an enormous physical allocation to expose the error.

**Required fix:** check capacity-to-bytes, header addition, alignment rounding, capacity doubling and region-size multiplication against explicit implementation limits before allocation or stores. Check both 32-byte and R82 56-byte headers, zero/negative normalization, the exact upper boundary and one beyond it. Preserve allocation-failure handling as a separate check. Ordinary integer wrapping is not permission for internal allocator-size arithmetic to wrap. I have not established which historical version introduced this class; this finding is about the reviewed tree, not a claimed new regression.

### F3 — Linux large-growth parimana accounting uses overwritten r11

**Source:** `src/r65_arena.inc`, `r127_emit_grow`, especially the generated register saves at 619, mmap emission at 640–647, counter update at 648–655, and register restoration at 667 onwards. `src/sutram_compiler.asm:emit_syscall` (17787) emits a bare Linux `syscall`.

The generated growth code saves the new capacity (`r11`) on the runtime stack, calls mmap through `syscall`, then counts `r11 << 3` **before restoring r11**. On x86-64, `syscall` overwrites r11 with flags. The counter consequently adds flags times eight instead of new-capacity bytes. Restoring r11 later makes collection growth work, but does not repair the counter. This explains why alias/value tests can pass while this accounting path is wrong.

**Proposed reproduction F3 — NOT RUN, default ELF allocation path:**

```sutram
mukhya() {
    kosh k[4096]
    chakra i = 1 tak 4096 {
        kosh_kship(k, i)
    }
    vitti before = parimana()
    kosh_kship(k, 4097)
    likha(parimana() - before)
}
```

The first regional backing has capacity 8192 cells. The initial allocation remains retained, so the intended delta is **65,536**, not the reserved 64 MiB and not a flags-derived number. Do not use `--fail-alloc` or the guard build to validate this syscall path: they select a different allocation branch.

**Required fix:** load the saved new capacity from the generated runtime stack before computing the counter increment, or restore/preserve it before use without disturbing the saved descriptor, length, allocation result and region size. Then check the first region, in-region doubling and replacement/release accounting. Repeat on PE and actual Windows; a Linux register-clobber diagnosis does not establish the Windows result. Do not record the faulty number as a new golden.

## 2. The four lifetime/accounting questions

| R203 question | What the reviewed implementation actually does | What still needs evidence or correction |
|---|---|---|
| What if a mandapa closes while aliases still exist? | Aliases usable only inside it cease to be valid together. R107–R109 refuse outward stores, returns and retaining calls. `r82_block_leave` clears the liveness slot; it does not free kosh allocations. | Existing R82 tests cover several escape forms, nesting, loop re-entry and recursion. They now reject the former runtime-stale-reference cases at compile time. They do not establish post-free descriptor safety, because descriptor freeing is not implemented. Keep all escape rules in place. |
| What happens when an inner kosh in a kosh grows? | This is **not a supported nested collection feature**. A kosh value cannot be stored in a numeric cell. Example 356 and its compile-failure golden explicitly refuse `outer[0] = inner` with `E_KOSH_DVARA`. | Do not invent nested growth semantics or mark it an untested supported operation. Preserve refusal through aliases, call results and append/store forms. Future nested collections need an element-kind and ownership design. |
| Does parimana change meaning? | It remains allocator accounting, not RSS, commit charge or total reserved address space. The new layout and retained arena buffers change its values. Intended accounting is occupied arena storage plus logical capacity bytes in current regional backings. | F3 breaks the large-growth counter. Examples 317/318 cover small counts, not that transition. Arena-fallback mappings are already excluded from the advertised count; it is not a complete process-memory meter. |
| Does the fixed descriptor itself die or outlive an alias? | `r108_kosh_alloc` still delegates to `r101a_emit_kosh_alloc`, which now immediately jumps to ordinary persistent allocation. Descriptor and initial payload share that allocation. They are not placed on the mandapa scratch side and are not reclaimed when it closes. | The particular “header freed at block exit” bug is not what this implementation does. Logical lifetime ends while physical storage is retained. This is retention, not implemented region ownership/reclamation. Raw/foreign/legacy-object paths do not acquire a universal safety guarantee from retention. |

The last distinction matters: **a descriptor that does not move is not a descriptor with implemented reclamation.** The checked lifetime rule is narrower than the physical storage lifetime. Repeated creation of block-local koshes still accumulates retained storage; moving large buffers can release an *outgrown* region, but closing a block does not release its final backing.

The old R108 comment says reclamation “waits for the descriptor.” R127 supplied identity stability, not the missing owner registry, cleanup and safe metadata-retirement design. Keep those requirements visible rather than treating the old comment as proof that reclamation happened automatically.

### Correct the representation and cost claims

The shipped layout is **32 bytes**, not the proposed three-word 24-byte layout: `[d-16]` length, `[d-8]` capacity, `[d]` element pointer and `[d+8]` region size. With R82 lifetime instrumentation there are three additional words, making **56 bytes before elements and allocator rounding**. In the ordinary arena the initial charge is `align16(H + 8*C)`, where H is 32 or 56 and C is initial capacity. These offsets describe v302 internals, not a public ABI promise.

The fixed reservation for **every** kosh is gone. Large-growth backing still reserves `max(2 * new_capacity * 8, 64 MiB)` starting at a requested payload of **64 KiB**. Thus many small collections no longer each consume 64 MiB of addresses; many threshold-sized growing collections still can. “No limit on how many” should become “no fixed 64 MiB reservation for each small collection.” Finite allocation limits remain.

There is also an exception to the report's “retained waste below 64 KiB per kosh” explanation: **an initially large capacity shares its allocation with the fixed descriptor too**. On its first move, that initial payload remains retained, even if it was much larger than 64 KiB. The sub-64-KiB geometric history argument describes a collection starting small; it is not a bound for all declarations. Include a large-initial-capacity growth measurement before making a universal retained-storage claim.

### Boundaries the implementation report already leaves open

- **Mixed compiler versions:** the R127 report explicitly says v301/v302 objects disagree on kosh representation and `sutram-link` does not reject that mismatch. Require an ABI/version incompatibility refusal or an enforced clean-rebuild rule before claiming such mixtures are safe. This is already a known boundary, not a new conclusion from a passing suite.
- **Raw buffer borrows:** FFI ptr and directly passed vibhag arguments retain an element address, not descriptor identity. Refusing a stored slice does not prevent growth during argument evaluation or inside a call through another alias. Require a no-growth borrow contract that is enforced or a documented unsupported/refused path. Include a two-argument call that forms a slice and mutates the same collection while evaluating the other argument; parameter-growth refusal alone does not settle this.
- **Allocation failure:** the injected-failure cases establish their tested allocator returns. Reserving addresses with lazy commitment does not prove that every later OS memory-pressure failure becomes the same diagnostic. Keep the tested failure mechanism explicit.

## 3. What the gates cover, and what I did not find covered

Claude reports suite **327**, gates **67 PASS / 1 FAIL / 1 NOT-RUN**, and **15 R127 checks**. The R127 file contains **10 ELF checks and 5 Wine PE checks**, not 15 native Windows checks. Its ordinary alias growth, many-small-collection, basic builtin, direct slice, failure and peak-memory cases are useful discriminating evidence. I did not rerun them.

| Area | Coverage read in the tree | Missing targeted coverage in the inspected material |
|---|---|---|
| Growth and aliases | R127 ordinary sequential alias reads after growth, including region moves; basic mutation builtins | Mutation within index evaluation (F1), plus raw-borrow invalidation during call/argument evaluation |
| Capacity/failure | R127 injected allocation failure at construction and growth | Successful tiny allocation caused by wrapped capacity arithmetic (F2); boundary arithmetic for every size transform |
| Accounting | Examples 317/318; R123 arena/scratch counts | First regional backing, later in-place regional growth and release/replacement deltas with parimana enabled (F3). R123's case label says “and a kosh,” but that particular source contains only nirmmita allocations. |
| Block lifetime | R82 positive small growth/recursion and compile-time escape refusals; examples 316/320/321 | Repeated block-local descriptor creation measured under v302, large growth followed by each exit form, and final-backing retention. No actual free/reuse lifetime gate can be credited while cleanup is absent. |
| Nested collection | Example 356 is a refusal golden | No positive nested-growth guarantee is required while the feature is refused. Test all routes to the same refusal. |
| ABI/platform | R127 Wine comparisons and ordinary ELF runs | Mixed v301/v302 object rejection; native Windows execution of the new paths. |

I searched the test/tool/example text for parimana and relevant mutation/capacity cases and read the gates named above. “No targeted test found” means no such coverage was identified in that inspected material; it is not a proof that every possible encoded/generated test in the repository was exhaustively understood. The proposed probes above are small, reviewable additions for the implementation owner.

## 4. WS2 — proposed student reference, six paragraphs

**Publication condition:** the accounting paragraph describes the intended normal-build contract and must not be presented as a verified large-growth guarantee until F3 is fixed. The lifetime and cost qualifications describe the current implementation, including its retention. F1/F2 also remain correctness work; prose is not their fix.

**A mandapa holds temporary buffers for one piece of work.** A `nirmmita` written inside the block uses its scratch storage. Leaving the block makes that scratch space available for later work; it does not promise to return physical pages to the operating system. Allocations made inside a called function follow that function's own allocation context. A block does not currently reclaim its `kosh` storage.

**parimana() reports the allocator's accounted bytes.** It includes occupied arena storage, including temporary buffers in open blocks, descriptor allocations and retained old arena buffers, plus the current capacity bytes of separately mapped growing koshes. Ending a block reduces its scratch contribution. Clearing a kosh changes its element count, not its allocated capacity. This number is neither physical memory use nor total reserved address space, and ordinary allocations that fall back outside the arena are not included. Layout and allocation choices can change the number without changing your program's values.

**mandapa parimita N limits that block's scratch allocation.** `N` must be a positive whole-number literal. Each `nirmmita` written in its scope is charged after rounding up to 16 bytes; allocations in nested blocks count against every enclosing active budget. An allocation that would exceed one of those budgets stops with `E_PARIMITA` before receiving memory. Closing an inner block returns its scratch allowance. This is not a whole-program memory limit: kosh storage and allocations made by called functions are outside this lexical budget.

**A kosh pays for a fixed descriptor and storage for its capacity.** The ordinary descriptor uses 32 bytes, or 56 when lifetime tracking is included, before allocation rounding; each numeric cell needs eight bytes. Every name for the same kosh points to one fixed registration desk, which records where its elements are now. Growth may move those elements and update the desk. Small collections no longer each reserve 64 MiB of addresses, although larger growth still uses reserved regions. Old arena buffers, including the initial payload beside the descriptor, remain allocated; an outgrown separate region can be released. `vitti a = k` creates another name for the same collection, not a copy.

**A kosh made in a mandapa cannot leave that block.** The compiler refuses to return it, store it outside, or pass it to a function that keeps it; making another name for it does not extend its lifetime. Return the numbers you calculated, or create the collection outside the block if it must remain usable afterward. Its retained storage does not make using it after the block legal. Storing one kosh inside another is not supported in this version.

**Ordinary runtime integer arithmetic can wrap.** `vitti` is a signed 64-bit integer, and the default runtime `+`, `-` and `*` keep the low 64 bits even when the mathematical answer does not fit. Out-of-range literals and constant expressions are refused during compilation. Library functions with checked contracts report their documented failure instead of returning a wrapped mathematical result; checked arithmetic provides a status, while explicitly saturating functions clamp to a limit. Use each function's stated contract: neither a zero result nor the word “library” by itself means an overflow was detected. Allocation sizes must still be checked internally.

Before integrating these paragraphs, reconcile the current reference's old per-kosh-region summary, its 8,272 example output versus the 8,288 golden, the old 16-byte header explanation, and “reclaiming waits for a descriptor.” Preserve dated measurements as history rather than relabelling them v302 results. No reference files were edited in this handoff.

## 5. WS3 — the two final answers

**Reuse: yes to the narrow v1.0 decision; no to an absolute statement.** The paragraph to publish is:

> While a mandapa remains open, Sutram v1.0 does not automatically reclaim arbitrary scratch allocations because a variable is no longer used or is assigned another value. Scratch space is reclaimed together when its block ends; a nested block can end and return its own space while an outer block is still running. Clearing a kosh lets that collection reuse its existing capacity, but does not free it. Release of an outgrown private kosh region is a separate allocator operation, not general reuse of arbitrary objects in a live block.

**Threads: “never” is wrong as a technical conclusion and conflicts with the charter's optional-concurrency target.** Keep threads out of v1.0; do not promise a later version or declare them impossible. The paragraph to publish is:

> Sutram v1.0 supports one execution thread per process. Its allocation and collection operations are not safe to call concurrently from foreign threads. Thread support would require separately owned or synchronized allocation state, rules for shared collection mutation and borrowing, and safe region teardown. It is outside v1.0; no delivery version is promised. Separate processes may run independently, but that does not make shared pointers within one process thread-safe.

This is the same scope decision given in R199. A bump cursor race does not prove that all future ownership or synchronization designs are impossible. No concurrency implementation is requested or proposed for this round.

## 6. Acceptance and verification boundary

Reproduce and fix F1–F3, add their discriminating regressions, then run the affected established gates on the exact candidate compiler. Preserve the existing alias-growth and failure tests. Keep unsupported nested storage refused, mixed-version ABI exposure visible, and native Windows separate from Wine. Broad memory-safety or “finished” certification is not justified by the current evidence.

**This delivery changes only this file in `ChatGPT-to-Sarvam/`.** Compiler, library, reference, tests, tools, packs and Windows folders were not edited. No build, compiler execution, native test, Wine run, CI, merge or background watch was performed. **Native verification: NOT RUN — read-side review, no toolchain used.** Reported suite/gate results remain their authors' results; all proposed probe outcomes above await independent execution and acceptance.
