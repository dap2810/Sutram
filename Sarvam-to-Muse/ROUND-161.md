## THE SHARED STATE - 10 November 2026

**`Sutram 1.0 (v315)` on main · 81 gates · 327 suite · 783 guard programs, 0 DIFFER · installer `6f9cdbda`.**
**v316 staged on `v316-ready` (`59d60353`), waiting on one Windows command.**

### THE THREE MEASURED MEMORY DEFECTS, IN ORDER OF SEVERITY

**1. A dead big `kosh` leaks 64 MiB of ADDRESS SPACE and its pages, and is not reused.**
**A `kosh` above 4,097 elements gets its own 64 MiB region.** **When it dies, the pages stay and the address space stays.** **A loop creating one per pass exhausts address space — after about a thousand passes, 64 GB is gone and the program fails with an allocation error unrelated to real memory.**
**And the only `munmap` in the compiler is on GROWTH, never on DEATH.**

**2. A `kosh` made every pass leaks 48 bytes; inside a `mandapa` it leaks 64 - the block makes it worse.**
**At 800,000 passes: 37.5 MB without a block, 50 MB with one.** **A `mala` leaks 80 bytes, block or not, 62 MB at 800,000.** **Against `nirmmita` in a block: 312 KB, flat.**

**3. A block never gives memory back to the OS.**
**A 200 MB `nirmmita` inside a block is kept and reused - and the second pass is 2.4x faster.** **So reuse is worth 2.4x, and returning memory would cost that on the next use.**

### AND THE MEASUREMENT FACTS
**Baseline is 312 KB with an empty environment.** **Peak RSS (`ru_maxrss`) can only rise, so it cannot show a return — current `VmRSS` must be sampled.** **`nirmmita` inside a block zeroes its bytes (`rep stosb`), so pages are committed.**

### THE DESIGN HISTORY, SO NOBODY REPEATS IT
**Scope rewind at every lexical scope exit: REJECTED — a `kosh` may escape, so a cursor restore would destroy it.**
**Three earlier designs solved one level too low: the arena, value semantics, and the descriptor. The descriptor succeeded at a different problem (aliasing) and reclaims nothing.**
**A `~` region marker was proposed and reviewed: it does not replace ownership; it is a spelling.**
**`mandapa` already does growth-and-reuse for `nirmmita` — proven flat at 312 KB over 800,000 passes.**

### THE HONEST RECORD
**Fifty false claims by Sarvam.** **Two measurement errors in two days: a baseline that was the measuring process, and peak RSS used to answer a question peak cannot answer.**

---

# ROUND-161 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**Two defects are measured and both need one thing: the compiler knowing when a `kosh` is dead.** **ChatGPT is designing it. You are the reader who finds what the design assumes and never checks.**

## Task 1 - and the 64 MiB region
**A `kosh` above 4,097 elements gets its own 64 MiB region. When it dies, nothing releases it.**

**Read `src/r65_arena.inc` and the descriptor allocation and answer:**

1. **Where is the 64 MiB reserved, and where is the pointer to it recorded?** **Is it in the descriptor, in a side table, or nowhere?**
2. **If the address is recorded nowhere, then freeing it is impossible without first recording it.** **Is that true?**
3. **What does `munmap` currently release — an old buffer on growth, the whole region, or both?** **The comment at `win/winrt_blob.asm:184` says *"a `kosh`'s old region; `VirtualFree` releases the whole reservation"* — which is it?**
4. **And: is the 64 MiB reserved or committed?** **`PROT_NONE` and `MEM_RESERVE` cost address space, not memory. If it is reserved only, then defect 1 is an address-space leak and not a memory leak — and that changes its severity.**
5. **And the boundary: 4,097 elements.** **Where is that number in the source, and is it documented anywhere?**

## Task 2 - and the loop-local `kosh`
**A `kosh` made every pass leaks 48 bytes; inside a `mandapa` it leaks 64.** **The block adds 16 bytes and reclaims nothing.**

**Read the block's entry and exit code and answer: what are those 16 bytes?** **A descriptor slot, bookkeeping, a mark record, something else?**

**If the block is allocating something for a `kosh` it cannot reclaim, that is a defect with a specific line.**

## Task 3 - and the question I would ask last
**Every design so far has assumed the compiler can tell when a `kosh` is dead.** **Three designs failed because they assumed it and it was not true.**

**So: read the symbol table and the scope handling and answer — what does the compiler actually know, at the point it would need to decide?** **`decl_depth` exists in the proposals. Does the compiler already track a depth per variable today, or would that be new?**

**And: is there any case where a `kosh` is dead but the compiler cannot know, or alive but the compiler would think it dead?** **One example of each is worth more than a list.**
