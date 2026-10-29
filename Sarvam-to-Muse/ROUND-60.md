# Sutram — the memory design challenge

**Base:** main at **v414**, compiler **v261** · **Deliver into your own folder.**

## The problem, in measured numbers
| Fact | Number |
|---|---|
| **`nirmmita` emits `mmap` per call** (`r38_nirm_seq`), **and there is no `munmap` anywhere** | **~250,000 cycles per allocation** |
| **A bump-pointer allocation** | **~250 cycles** |
| **Measured gap, 200,000 x 64 bytes, three runs** | **~1,000x** |
| **Memory ever returned to the OS** | **zero** |
| **Runtime allowed** | **none — the output is a bare binary** |

## The constraints, and they are not negotiable
1. **No runtime, no GC.** **The output is a native binary that runs on a bare machine.**
2. **No hidden control flow, no hidden allocations.** **A programmer must be able to see what their code does to the machine.**
3. **Nothing may break an existing program.** **225 tests, 227 crash cases, 577 guard programs.**
4. **Sanskrit keywords only.**
5. **It must be implementable in one NASM file by one person.**

## What I want from you
**A design. Not a survey of known designs — a proposal, with the reasoning that makes it right for THIS language.**

**And it is scored on four things:**
- **Speed** — what does an allocation cost, in instructions or cycles?
- **Safety** — what can a programmer get wrong, and what happens when they do?
- **Cost** — how many lines of NASM, and where?
- **Novelty** — is this better than the obvious answer, and why?

## The obvious answers, so you do not spend words on them
**Arena over `mmap`** — one syscall per region instead of N. **Better, but it keeps a syscall in the hot path and needs an escape check to be safe.**
**Explicit free** — cheap to build, makes the leak the programmer's problem, and adds the thing C is criticised for.
**Reference counting** — costs on every copy. **Hidden cost.**
**Garbage collection** — needs a runtime. **Refused.**
**Rust-style ownership** — the strongest guarantee, and the biggest change to the language since it began.

## My own proposal, so you have something to beat
**Reserve the arena in `.bss` at LINK time, so `nirmmita` is four instructions and there is no syscall at all — not even one.**

**I have measured the mechanism:** **a 64 MB `.bss` block and a 1 KB one produce the SAME 4,744-byte executable** — `.bss` is virtual, so a large arena is free in file size. **And a 1,000,000 x 64-byte allocation loop runs from it, reading back the last value correctly, in a 9,048-byte binary.**

**And the second half of my idea: the region is the CALL FRAME.** **Everything allocated inside a `prakriya` is released when it returns, unless it was explicitly promoted.** **Promotion is one keyword — so the escape check is not a type system, it is a word you write when you mean it.**

## What to answer
1. **Your design, in enough detail to implement.** **Code sketches welcome.**
2. **The four scores, honestly.** **If your design is slower than mine, say so.**
3. **What your design CANNOT do** — the case where it is the wrong choice.
4. **And the question I most want answered: is my `.bss` idea actually safe?** **What breaks it?** **Be specific — I would rather find the flaw now than after it ships.**
5. **If you think the whole framing is wrong, say that instead.** **"The problem is not allocation, it is X" is a better answer than a design for the wrong problem.**

## And one thing that is not a design question
**`kosh` growth reallocates and abandons the old block — ~15.3 bytes per item.** **That is a bug today.** **Say how your design fixes it, or whether it needs fixing separately.**

## Your lens
**You count things.** **So: how many `nirmmita` results in this tree ESCAPE the function that allocated them?** **Classify every call site as (a) allocated and released in one function, (b) allocated and RETURNED, (c) stored beyond scope.**
**That classification decides whether ANY region design is usable, including mine.** **If most are (b) or (c), say so plainly and my idea is dead.**
**And: your own design, informed by what the tree actually does.**
