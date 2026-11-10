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

# ROUND-170 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Your R169 is the clearest measurement of the stretch: *"The only `munmap` in the compiler is on growth, never on death."***

**ChatGPT is designing the liveness question. Muse is reading for what the design assumes. This round is the one thing that needs no design.**

## WS1 - and the smallest possible first step
**Defect 1 is the worst: a dead big `kosh` keeps 64 MiB of address space.**

**Two questions before anything is built:**

1. **Is that 64 MiB reserved or committed?** **`PROT_NONE`/`MEM_RESERVE` costs address space only. If it is reserved only, defect 1 is an address-space leak, not a memory leak — and the severity changes, though a thousand passes still exhausts the address space.**
2. **Is the region's address recorded anywhere the compiler could find it at death?** **If it is in the descriptor, freeing is a change to one place. If it is nowhere, recording it is the first step.**

**Answer both by reading, and report the line numbers.**

## WS2 - and if it is a one-line change, make it
**If the region's address is in the descriptor and the descriptor is released at scope exit, then freeing the region is one `munmap` beside the descriptor's release.**

**Is that true?** **If yes, make the change on a branch, test it, and report the guard result.** **If no, say what is missing and do not guess.**

**Do not merge it. Stage it, as you did with v316.**

## WS3 - and measure what it buys
**If the change is made: run the loop that creates a big `kosh` every pass and report address space (`VmSize`) and RSS at four points, over 1,000 passes.**

**Before the change, 1,000 passes should exhaust address space.** **After, it should not.** **That is the proof.**

**And state the method, as you did in R169 — current RSS and VmSize sampled, pages touched, baseline stated.**

## WS4 - and the 16 bytes a block adds to a `kosh`
**A `kosh` leaks 48 bytes a pass, 64 inside a `mandapa`.** **The block adds 16 and reclaims nothing.**

**What are those 16 bytes?** **If the block allocates something per `kosh` it cannot reclaim, that is a defect with a line number, and it may be cheaper to fix than the whole reclamation design.**
