# My proposal — the arena that costs nothing and calls nothing

**A design for Sutram's memory, and why it is different from the obvious answers.**

---

## The problem, stated in numbers

| Fact | Number |
|---|---|
| **`nirmmita` is an `mmap` syscall** | **~250,000 cycles per allocation** |
| **A bump-pointer allocation** | **~250 cycles** |
| **The gap** | **~1,000x** |
| **Memory ever returned** | **zero — there is no `munmap`** |
| **Runtime allowed** | **none. The output is a bare binary.** |

**So the question is not "how do we free memory".** **It is "why is every allocation a kernel call, and why does nothing come back".**

---

## The obvious answers, and why each is wrong here

**Arena over `mmap`.** **Better — one syscall instead of N.** **But it still calls the kernel once per region, and it still needs a region to be scoped, and scoping needs an escape check, and an escape check is a type system.**

**Explicit free.** **Cheap to build and it makes the leak the programmer's problem.** **For a language whose selling point is that a beginner can read it, adding a manual free is adding the one thing C is criticised for.**

**Reference counting.** **Costs on every copy.** **Hidden cost, which violates the rule we already agreed: no hidden control flow, no hidden allocations.**

**Garbage collection.** **Needs a runtime. Refused.**

---

## My proposal: reserve the arena at LINK TIME, in `.bss`

**Here is the idea.** **`.bss` is the part of a binary that occupies address space but NOT file space.** **A 64 MB `.bss` block adds roughly zero bytes to the executable** — **the loader just maps anonymous zero pages for it.**

**So: put one arena in `.bss`, and make `nirmmita` a bump inside it.**

```asm
; the entire allocator
nirmmita:
    mov  rax, [bump]        ; current position
    add  rdx, rax           ; rax + size, aligned
    cmp  rdx, [arena_end]   ; past the end?
    ja   .out_of_memory     ; clean error, no corruption
    mov  [bump], rdx        ; commit
    ret                     ; rax = the block
```

**Four instructions. No syscall. Ever.**

**And the release is one store:**

```asm
kosa_close:
    mov  rax, [region_base]
    mov  [bump], rax        ; everything above it is gone
```

---

## Why this is different from a normal arena

**1. There is no `mmap` at all, not even one.** **Every arena design I know of calls the kernel once per region.** **This calls it zero times, because the kernel maps `.bss` before `_start` runs.**

**2. The binary does not grow.** **`.bss` is virtual.** **A 64 MB arena and a 64 KB arena produce executables of the same size.** **That is the property that makes a large arena free.**

**3. Failure is clean and detectable.** **`cmp` before the bump means running out is an error with a line number, not a segfault.** **Today, an `mmap` failure returns 0 and the program dereferences it.**

**4. The memory arrives ZEROED, for free.** **`.bss` is zero-filled by the loader.** **So the `samskara` problem — reused memory carrying the previous occupant's data — does not exist until a region is closed and reused.** **And when it is reused, we know exactly where the boundary is, so zeroing on reuse is a choice, not a hope.**

---

## The part that is genuinely new: regions are the CALL FRAME

**Every other region design makes the region a block you write by hand.** **Sutram has `prakriya` — a function.** **So the region is the function call:**

```
prakriya yog(a, b)
    vitti t = nirmmita(64)     ; comes from THIS call's region
    ...
                               ; the call returns, the region closes
```

**Everything allocated inside a call is released when the call returns — unless it was explicitly PROMOTED.**

**And promotion is one keyword.** **That is the whole escape check: not a type system, not inference, not a borrow checker — one word you write when you mean it.**

**The safety property is exact:** **nothing can dangle, because anything that outlives its region was promoted out of it deliberately.** **And if you forget to promote, you get a compile-time error, not a runtime corruption — because the compiler knows the region's lifetime at compile time.**

---

## What it costs and what it cannot do

**Cost:** **a `.bss` block, a bump pointer, a region stack, and one check. Maybe 120 lines of NASM.**

**Cannot do:** **a program that needs more than the reserved arena.** **That is the trade — a fixed ceiling for zero syscalls.** **Mitigation: the ceiling is a build flag, and running out is a clean error that names the flag.**

**Cannot do:** **freeing a single object inside a region.** **That is what `pratyarpana` is for, and it should exist as the escape hatch for the 5% that needs it.**

---

## Why I think this is better than the three options I wrote earlier

**My earlier document said "regions over `mmap`", which is the textbook answer.** **It is also the answer that keeps a syscall in the hot path and needs an escape analysis to be safe.**

**Reserving in `.bss` removes the syscall entirely, and making the region the call frame removes the analysis.** **Two simplifications, and both come from a property Sutram already has — a bare binary with no runtime — rather than from a technique borrowed from a language with one.**

**That is the part I would defend: this design is only possible BECAUSE there is no runtime.** **A language with a runtime cannot reserve its arena at link time, because the runtime decides the layout.** **Sutram can, because the linker does.**

---

## The experiment that would prove or kill it

**Write a Sutram program that allocates 1,000,000 blocks of 64 bytes in a loop.** **Time it today.** **Then time it with the `.bss` arena.** **If it is not at least 100x faster and the binary has not grown by 64 MB, the idea is wrong.**

**And check the executable size before and after — that is the claim most likely to be false, and it is measurable in one `ls -l`.**
