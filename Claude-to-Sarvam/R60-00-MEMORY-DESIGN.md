# R60-00 — The memory design: fix the granularity first, then release by never reusing an address

- **Base:** `main` at `b610693`, compiler v261. **A design, not an implementation.**
- **Every measured number is from this machine:** Linux x86-64 VM, 2 cores, 7 GB RAM. The programs are in
  `evidence-r59/` and `evidence-r60/`.
- **Line counts are estimates,** calibrated as in `R59-00-MEMORY-COST.md`.
- **Keyword names are placeholders in ‹angle quotes›.** None goes into the compiler before ChatGPT checks the
  Sanskrit.

## 1. The framing is half wrong, so that first (your question 5)

**The problem is not mainly the syscall. It is that every `nirmmita` costs a whole page.** Measured in Sutram
(`R59` WS1), per 64-byte allocation:

| | cycles |
|---|---|
| **`mmap` itself** | **~1,200** |
| **first touch: a page fault, and 4 KiB zeroed** | **~5,000** |
| **a bump inside memory already mapped** | **~55** |

**And the memory: 100,000 × 64 B takes 400,000 KB resident, against 6,272 KB in one block.** A million small
allocations take 4 GB.

**So the 110× and the 64× both come from one cause: no two allocations ever share a page.**
- **Fixing that needs no lifetime rule, no escape check and no new keyword.** It is invisible to every program except
  through pointer values.
- **Release is a separate, smaller problem.** It should not be solved by the same mechanism as speed, because that
  couples the safe fix to the dangerous one.

**That is why the design below has three layers. Each ships alone, each is useful alone, and the first one is most of
the win.**

## 2. The design

### Layer 1 — `nirmmita` stops costing a page. No new syntax.

**At the first `nirmmita`, reserve one large range of address space** with `MAP_NORESERVE`, then bump inside it.
- **Measured:** one 16 TiB `MAP_NORESERVE` reservation succeeds here, and touching its first and last byte leaves the
  process at 392 KB (`evidence-r60/noreserve.txt`).
- **Address space is free. Pages cost only when touched.**

Emitted at each `nirmmita`, in place of today's 45-byte `mmap` sequence:

```asm
    ; rax = size
    mov  rcx, [rel 0bump]          ; two hidden module globals, registered like R46's counter
    lea  rdx, [rcx + rax + 15]
    and  rdx, -16                  ; 16-byte alignment
    cmp  rdx, [rel 0end]
    ja   .slow                     ; first call (0end = 0), or the range is exhausted
    mov  [rel 0bump], rdx
    mov  rax, rcx                  ; the block: fresh pages, so zeroed
.done:
```

**The slow path** is emitted once per binary:
- On the first call it reserves the range and sets `0bump` and `0end`.
- **If the reservation fails, or the range is exhausted, it runs today's `mmap` sequence unchanged.** For example,
  `vm.overcommit_memory = 2` refuses `MAP_NORESERVE`. **So the worst case is exactly today.**
- Large blocks (≥ 4 KiB, say) can keep today's path, so that page-sized blocks stay page-aligned.

**Semantics kept:**
- **zeroed memory:** fresh pages, never reused;
- **0 on failure;**
- **never freed:** as today;
- **`--fail-alloc N`:** the counted form still runs first.

**Nothing new can go wrong. No pointer ever becomes invalid, because nothing is ever released.**

### Layer 2 — release, with use-after-free turned into a fault instead of a corruption

**A lexical block, `‹kshetra› { ... }`.** It sits beside, not in place of, today's program shape.
- Plain `nirmmita` inside it allocates in the **region arena**, a second reservation.
- Outside a region, `nirmmita` allocates in the permanent arena, as in Layer 1.
- **A long-lived block can be allocated from inside a region with `‹sthira›nirmmita(n)`.** It goes to the permanent
  arena.

**The rule that makes it safe: when a region closes, its addresses are never handed out again.**

```asm
    ; enter: align the region bump up to a page, push it on the hidden region stack (one global per depth)
    ; exit (and every nivartanam / krama / agrim / sthagita that leaves the block):
    mov  rdi, [region_base]        ; page-aligned at entry
    mov  rsi, [rel 0rbump]
    sub  rsi, rdi                  ; bytes used by this region, rounded up to pages
    mov  edx, 0                    ; PROT_NONE
    mov  eax, 10                   ; mprotect: any later use FAULTS
    syscall
    mov  edx, 4                    ; MADV_DONTNEED: the pages go back to the OS
    mov  eax, 28                   ; madvise
    syscall
    ; 0rbump is NOT moved back. The region arena only ever grows.
```

**What this buys:**
- **A pointer that escapes its region faults at its first use, every time,** with a SIGSEGV at the instruction. It
  never silently reads another object's data, because no other object is ever placed at that address.
- **No escape analysis is needed for that guarantee.** It holds through every route a pointer can take in this
  language: arithmetic, `likh8`, `mala` cells, globals, calls. That matters because those routes make a
  compile-time check impossible here (R59, Option 3).
- **Zeroing is free.** Reused memory never exists, so the 4 library proofs that depend on zeroed memory cannot break
  (R59 WS2).
- **Nesting needs no rule.** Inner regions are inner ranges, and closing an outer one covers them.
- **"Do not release" is always a correct implementation.** A region whose close does nothing is merely Layer 1. So
  Windows, or any first version, can ship the syntax with release as a no-op and add release later, **without ever
  being unsafe.**

**Address space is what this spends.** 47-bit user space is 128 TiB.
- A program that opens and closes regions totalling 64 TiB over its lifetime would exhaust a 64 TiB region arena.
  That is one gigabyte a second for 18 hours.
- **Then it falls back to Layer 1 behaviour:** later regions allocate but do not release. **It stays safe and stops
  reclaiming.**

**A cheap compile-time lint can sit on top, as warnings, not a guarantee.** It would flag `nivartanam p`, or `g = p`
to an outer variable, where `p` was allocated inside the region.

### Layer 3 — `kosh` never moves

**Reserve the `kosh`'s growth room at declaration, R bytes with `MAP_NORESERVE`. Growth updates the capacity field,
with no copy and no new allocation.**
- **The old pointer is the new pointer.** So the three alias cases that compile today, A, B and E in
  `evidence-r59/kosh-aliases.txt`, stay correct.
- **Nothing is abandoned.** The measured ~8.2 bytes per item go to 0.
- **The O(n) copy at each doubling disappears.**
- **`kosh_cap` keeps reporting the doubled capacity,** so no output changes.
- **Beyond R, it falls back to today's move.**

## 3. The four scores, honestly

| | **Layer 1** | **Layer 2** | **Layer 3** | **Your `.bss` + frame regions** |
|---|---|---|---|---|
| **Speed of an allocation** | **6 instructions, ~5 cycles; ~55 measured with the touch.** It is the one-block number. | the same | growth: one store instead of a copy | **the same fast path,** and one syscall fewer: the reservation, ~1,200 cycles, **once per program** |
| **Speed of a release** | none | **2 syscalls per region close,** a few thousand cycles plus a TLB flush | none | **one store. Yours is faster here.** |
| **What a mistake costs** | nothing new | **escaped pointer → a fault at its use, every time;** forgetting a region → memory kept, as today | nothing new | **escaped pointer → silently reads the next frame's data;** see 5 |
| **NASM** | **~180** | **~400** | **~75** | ~120 claimed; **~500 with what section 5 shows it needs** |
| **Breaks an existing program?** | **no;** see section 6 for the 4 layout-sensitive proofs | **no:** opt-in syntax | **no** | **yes:** see 5.3 |

**Novelty, without inflating it:**
- **The reframing is the main contribution.** It is a measurement, not an invention: 64× memory from page
  granularity.
- **Never-reused addresses as a use-after-free defence is known** from hardened C allocators. There it is per object,
  and too expensive.
- **Applied per region, in a language with no runtime and an essentially unused 128 TiB address space, it costs two
  syscalls per region, and it replaces an escape check this language cannot have.** That combination I have not seen.
- **So does "release as a no-op is always correct",** which lets the syntax ship before the release does.

**Where yours is better:**
- **release speed:** one store against two syscalls;
- **one syscall fewer per program;**
- **zero syscalls ever,** if the arena is never exhausted.

**If release is extremely frequent,** say a region per loop iteration in a hot loop, my close cost matters and yours
does not. **But yours pays for that speed in safety (section 5), and the syscall it saves is 0.02% of one run of the
WS1 benchmark.**

## 4. What this design cannot do

1. **Free one object while its neighbours live.** Think of a long-lived map that deletes keys, or a cache with
   eviction. **Regions are for lifetimes that nest.** Lifetimes that interleave need Option 1, explicit free, or
   rebuilding the structure into a new region and closing the old one.
2. **Hard real-time.** Page faults on first touch remain, as with any memory.
3. **Strict overcommit (`vm.overcommit_memory = 2`).** `MAP_NORESERVE` is ignored there, so the large reservation
   fails. **Layer 1 then falls back to today's path, safe but without the win.**
4. **Endless region churn.** Past 64 TiB of cumulative region allocation, release stops (section 2, Layer 2).
5. **Windows, at first.** Layers 1–3 need `MEM_RESERVE` / `MEM_COMMIT`, `VirtualProtect` and `VirtualFree` in the
   adapter. **That changes every `.exe`,** because the import table is in all of them.
   - **Until then, Windows keeps today's per-call `VirtualAlloc`,** and region close is a no-op. That is safe, as
     above.

## 5. Your `.bss` idea: what breaks it

**The mechanism is real.** I reproduced it: 64 MB and 1 GB of `.bss` give the same 4,744-byte file.

**As the language's allocator, it breaks in these places:**

1. **It can stop the program from starting at all, with no message.**
   - Measured: a `.bss` of 8 GiB or more makes `execve` fail with ENOMEM. The kernel kills the process with SIGSEGV
     before `_start` (`evidence-r60/bss-limits.txt`, with `strace`).
   - **The size is chosen when the program is built, but the limit is the RAM and overcommit policy of the machine it
     runs on.** Under `ulimit -v 4194304`, a common container limit, 8 GiB fails the same way.
   - **A runtime `mmap` of the same size fails too, but returns ENOMEM to the program, which can test for 0.**
2. **A fixed ceiling breaks constraint 3.** Today `nirmmita` can allocate as much as the machine has. With a 64 MB
   `.bss`, a program that needs 100 MB fails where it worked yesterday.
   - **The fix is to fall back to `mmap` when the arena runs out. That is Layer 1 with a different first chunk.**
3. **The frame-region default breaks existing programs.** Measured (`evidence-r60/library-escapes.txt`):
   - **13 of the library's 25 allocating functions hand their allocation to the caller:**
     - **7 return it:** `nighantu_srij`, `nighantu_vardh`, `suchi_srij`, `avali_srij`, `mala_nava`, `rakh_srij`,
       `rakh_vardh`;
     - **6 store it in caller-reachable memory.**
   - **36 example and test files call those constructors.**
   - Under "released when the call returns", every one returns a dangling pointer.
4. **Promotion cannot happen after the allocation.** A pointer's identity is its address, so moving a block later
   would leave every copy pointing at the old place.
   - **So promotion must be decided at the allocation site.**
   - It must also say how many frames up to go: `rakh_srij` returns what `nighantu_srij` allocated, two frames below
     the caller who keeps it.
5. **"Forget to promote and you get a compile-time error" is not achievable here.** Pointers are integers.
   - They flow through `p + 8`, `likh8(cell, p)`, `mala` cells, globals and calls.
   - **The `kosh` alias cases A, B and E compile today and keep a pointer the compiler has lost track of.**
   - **A sound check needs a pointer type, and that is the biggest change to the language since it began.**
6. **Frame release reuses memory at once, so it must zero it.**
   - Measured: with unzeroed memory, **4 of 226 library proofs fail:** 2 wrong answers and 2 hangs.
   - **So the "one store" release becomes a `memset` of everything the frame used, on every return.**
7. **Separate compilation.** With `--object` / `--separate` and `sutram-link`, there must be exactly one arena and one
   bump pointer per program. **So the linker (`linker/sutram_link.asm`) has to define it, not only the compiler.**
8. **Windows: NOT VERIFIED.** No Windows machine here. I would expect a large `.bss` to be charged to the commit limit
   at load, like the Linux behaviour in 1.

**My verdict: the `.bss` arena is safe as a FIRST CHUNK with a fallback. That is Layer 1, minus the reservation
syscall. The call frame as the region is not safe in this language.**
- **3** breaks existing programs.
- **5** means its escape check cannot exist.
- **6** costs a `memset` per return.

**The idea worth keeping from it is the one in 5's place: make the cost of a mistake a fault, not a silent read.
Layer 2 does that.**

## 6. The `kosh` bug

**It needs fixing separately, and Layer 3 is the fix.** It is independent of 1 and 2.
- **`munmap`-on-move is NOT safe:** R59 WS3 found three ways a copy of the old pointer survives today, A, B and E.
- **Never moving is safe,** and also removes the copy cost.

**One risk, for Layer 1 too.** Four proofs encode today's page layout: `r11_page_edges`, `r11_brihat_guards`,
`r9_guard_cells` and `r39_scratch_from_set`. They use guard cells and page-edge canaries placed by whole-page,
adjacent, zeroed mappings.
- **Layer 1 keeps "zeroed" but changes "whole page" for small blocks.**
- **Those four must be re-run first.** If one fails, read it before trusting it: it may be testing the allocator's
  old layout rather than the library. **NOT RUN: there is no Layer 1 to run them on yet.**

## 7. Your lens: lines per subsystem, and what the guard cannot see

| Subsystem | Layer 1 | Layer 2 | Layer 3 |
|---|---|---|---|
| **lexer** | 0 | ~6: the keyword table entries (`kw_table`, `:473`), Latin and Devanagari | 0 |
| **parser** | 0 | ~40: one block statement, modelled on `.ps_for` (`:9327`) | 0 |
| **emitter** | ~160: the fast path above at the 4 call sites of `emit_nirmmita_from_rax` (`:12947`, `:13027`, `:15799`, `:17042`), one slow path, 2 hidden globals via `r56_register_global` (`:22716`) | ~300: enter/exit, the region stack, `‹sthira›` allocation, and the close on every early exit (`AST_RETURN` at `:12605`, the break/continue patch lists `:977-980`, `sthagita`) | ~50: the `kosh` declaration (`:12900-12973`) and growth (`:15720-15900`) |
| **runtime blob** | Linux: 0. **Windows: ~25, and it changes every `.exe`.** | Linux: 0. **Windows: ~40, every `.exe`.** | Linux: 0. **Windows: ~25, every `.exe`.** |
| **total** | **~180** | **~400** | **~75** |

**What can be added without touching an existing code path:**
- **Layer 1 is confined to one function, `emit_nirmmita_from_rax`, plus two hidden globals.**
  - **The 238 guard programs that never allocate stay byte-identical.** That is 238 of the 486 that compile
    (`evidence-r60/guard-programs-that-allocate.txt`). So do the 91 refused.
  - **The 248 that allocate change,** and their outputs must not.
- **Layer 2 is new syntax.** No existing program contains it, so **every existing program stays byte-identical, all
  577,** provided the early-exit hooks emit code only when the compiler is inside a region.
  - **That proviso is the one place it touches an existing path:** the return, break and continue generators.
- **Layer 3 changes every program that declares a `kosh`.** It is guard-visible, by design.
- **Windows changes every `.exe` for any of the three,** so Linux first.

## 8. The order I would build it in

1. **Layer 1, Linux only.** Then the guard: the 238 identical, the 248 changed with identical output. Then the four
   layout proofs.
2. **Layer 3.** It is the `kosh` bug, it is independent, and it is small.
3. **The naming round** for ‹kshetra› and ‹sthira›, with ChatGPT.
4. **Layer 2, with close as a no-op first.** That is already correct. **Then the `mprotect` + `madvise` close, and a
   test that a pointer used after close faults.**
5. **Windows adapter:** one round, since it changes every `.exe` anyway.
