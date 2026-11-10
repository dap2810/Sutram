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

# ROUND-230 - to ChatGPT

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

## WS1 - and this is the round: one design for "when is a `kosh` dead"
**Both defect 1 and defect 2 need the same answer.** **A dead big `kosh` must give back its 64 MiB region; a loop-local `kosh` must be reclaimed each pass.** **Neither is possible until the compiler can tell when a `kosh` is dead.**

**So design that one thing.**

**The constraints are fixed: no GC, no runtime, one NASM file, single pass, no borrow checker.**

**And the existing facts:**
- **a `kosh` descriptor is four qwords, 32 bytes, and never moves**
- **a `kosh` above 4,097 elements gets its own 64 MiB region**
- **`mandapa` already saves and restores an arena cursor for `nirmmita`**
- **the escape rule already refuses a slice after growth, at compile time, by construction**

## WS1 questions
1. **What makes a `kosh` dead — scope exit, last name going out of scope, or something else?**
2. **Is there a version where the answer is "the scope it was declared in", and the compiler can prove that at declaration time without escape analysis?** **A `kosh` declared inside a block, not assigned outward, not returned, not stored in a container — can that be proven in one pass with a `decl_depth` comparison?**
3. **For the 64 MiB region specifically: is the fix simply "free the region when the descriptor is freed", and does that need the same liveness knowledge or less?** **A region is one `munmap`; a descriptor is a slot in a table. They may not need the same mechanism.**
4. **What is the cheapest thing that fixes defect 1 alone?** **It is the worst of the three, and it may be a one-line change if a region's address is recorded and released at scope exit.**

## WS2 - and defect 3, which is a different question
**A block never gives memory back.** **Reuse is worth 2.4x. So returning is a trade, not a free win.**

**Should a block ever return memory by itself, or only when told?** **And if told, is a threshold better than a marker?** **The compiler already has `R127_BIG` — a size rule could decide without any syntax.**

## WS3 - and the order
**Three defects, one team, finite time.** **What order, and what is the smallest first step that proves the approach?**

**Say it as a sequence with a size for each.** **If the answer is "fix 1 with a one-line change, then measure, then decide about 2 and 3", say that.**
