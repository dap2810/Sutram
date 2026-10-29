# The `kshetra` block — critique it, break it, improve it, or replace it

**Five designs were proposed and compared.** **This is the synthesis, and I want it attacked before anything is built.**

## What the five established

| Who | Finding |
|---|---|
| **Me** | **`.bss` costs nothing in file size — measured: a 64 MB block and a 1 KB block both produce a 4,744-byte executable.** |
| **Claude** | **The cost is page faults, not syscalls: 1,200 cycles for the `mmap`, 5,000 for the first touch and 4 KiB of zeroing, 55 for a bump in memory already mapped.** **No two allocations share a page.** |
| **Muse** | **313 of 322 `nirmmita` sites allocate and release inside one function.** |
| **Gemini** | **Programs have time phases, and the loop iteration is one.** |
| **ChatGPT** | **Aliases defeat escape analysis: *"a keyword saying promote cannot repair aliases already copied to arrays, structs, module globals or callers."*** |

## The tension, stated exactly

**Muse and Gemini want automatic release.** **ChatGPT proves automatic release is unsafe, because a copied pointer survives it.**
**ChatGPT wants explicit marks — but a mark and a rewind are two calls that can be forgotten or mismatched.**

**Both are right.** **So the answer cannot be automatic and cannot be remembered. It has to be STRUCTURAL.**

## My synthesis: `kshetra` is a BLOCK, and the block is the lifetime

```
mukhya()
    kshetra
        vitti buf = nirmmita(1024)
        likha("buf = ", buf)
    # the block ends — the mark rewinds, buf is gone
```

**The programmer writes a block, with the same indentation and closing as `yadi` or `chakra`.** **On entry the compiler takes the mark; on exit it rewinds.** **Two instructions, invisible in the source.**

**No mark call to forget. No rewind to mismatch. One entry, one exit.**

### The safety rule is one sentence

> **A pointer allocated inside a `kshetra` block may not be assigned to a variable declared outside that block.**

**No borrow checker, no lifetimes, no escape analysis.** **One scope check over the AST — the same kind of check that already stops a variable being used after its block.**

**And it catches the alias case ChatGPT raised:**

```
mukhya()
    vitti kept = 0
    kshetra
        kept = nirmmita(64)      # ERROR: kshetra pointer assigned outside its block
```

**ChatGPT's list — arrays, structs, module globals, callers — are all assignments to something declared outside the block.** **So all of them are compile errors.**

### The loop case falls out for free

```
yavat (purna)
    kshetra
        vitti req = nirmmita(2048)
        # handle one request
    # this iteration's scratch released, every iteration
```

**That is the web server that leaks nothing.** **Gemini's insight, with the reset written by the programmer instead of by the compiler.**

### And promotion needs no keyword

**If something must outlive the block, allocate it outside the block with plain `nirmmita`.** **The syntax already says the lifetime.** **Where you write the allocation IS the lifetime.**

### And `nirmmita` never changes

**ChatGPT's Track A, kept.** **Every existing program behaves exactly as today, because the old path is untouched.**

## What I want from you — and I want the flaws, not the praise

**1. Is the scope rule COMPLETE?** **Name a case where a `kshetra` pointer escapes without being assigned to an outer variable.** **I can think of three and I want to know if there is a fourth:**
- **passed as an argument to a function that stores it**
- **stored through a pointer that already points outside** (`*outer_ptr = kshetra_ptr`)
- **returned from the enclosing `prakriya`**

**If any of those escapes the rule, the rule is not enough and I need to know now.**

**2. Nested and interleaved blocks.** **Two `kshetra` blocks nested — the inner rewinds first, which is fine.** **But what about two blocks where the inner allocates and the outer's pointer is used inside?** **And can a `kshetra` block contain a `nivartanam`?** **If yes, the rewind is skipped and the arena leaks until the enclosing block ends.**

**3. What does the block cost in the emitted code, and where does it go?** **Entry: one store. Exit: one restore. But what about `krama` (break) and `agrim` (continue) out of a loop that contains a `kshetra` block?** **Does the rewind happen?** **If not, that is a leak.**

**4. The range size, and what happens when it runs out.** **Claude measured a 16 TiB `MAP_NORESERVE` reservation as possible.** **Is that wise?** **And on exhaustion: a clean error, or a fallback to `mmap`?** **Which is right for a language whose selling point is predictability?**

**5. Windows.** **`MAP_NORESERVE` has no direct `VirtualAlloc` equivalent.** **Nobody has answered this.** **`MEM_RESERVE` without `MEM_COMMIT` is the closest analogue — is that right, and does it behave the same under memory pressure?**

**6. And the question I most want answered: is there a DIFFERENT structural answer?** **I made the region a block because the language already has blocks.** **Is there another existing construct in this language that would carry a lifetime better — the function call, the loop, the struct, the module?**

**7. If you think the whole idea is wrong, say so.** **"The lifetime should not be expressed in the syntax at all, because X" is a better answer than an improvement to something that should not exist.**

## The two tests that would decide it
**A program that allocates 1,000,000 blocks of 64 bytes in a `kshetra` block inside a loop.** **Today it takes 4 GB. It should take a few megabytes and not grow with the iteration count.**
**And a program that assigns a `kshetra` pointer to an outer variable must fail to COMPILE, with a line number.**

**Neither has been run. If you can see why either would fail, that is the most valuable thing you can tell me.**

## Your lens
**You found the alias objection that killed the automatic versions, so you are the one who can tell me whether my scope rule actually answers it or only appears to.**
**Read point 1's three escape cases against the rule and say whether the rule catches them.** **If it catches two of three, say which one it misses.**
**And: is `kshetra` the right word for a BLOCK rather than a region?** **If a block is a scope, is there a Sanskrit word for scope that is better than the word for field?**
