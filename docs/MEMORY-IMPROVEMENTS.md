# Two improvements to the memory design — one of them unblocks the `kosh` fix

**Written 29 October 2026, after Step 0 was stopped.** **Both are design changes, not implementations.**

---

## Improvement 1 — fix the aliasing at the LANGUAGE level, and the recycling bins become safe again

### The chain of reasoning that got us here
**The recycling bins were unsafe because a `kosh` buffer can have two owners.**

```
kosh k[1]
kosh_push(k, 7)
vitti a = k            # the compiler marks a as a kosh variable too
kosh_push(k, 8)
kosh_push(k, 9)        # k grows; a still points at the OLD buffer
likha(a[0])            # 99
likha(k[0])            # 7     - two live buffers
```

**So when `k` grows, the old buffer is NOT dead — `a` is still using it.** **Recycling it would hand it to another `kosh`, and `a` would then read and write that vector's header.**

**That is why the bins were dropped.** **But the bins were dropped for a reason that is a LANGUAGE bug, not an allocator constraint.**

### The bug, stated plainly
**`vitti a = k` silently makes two variables own one buffer.** **After growth they disagree, and the program has two vectors where it thought it had one.** **That is surprising on its own — before any question of recycling.**

**The same hazard exists today, with no bins.** **It just manifests as a stale copy instead of a use-after-free.** **Today it is odd; with recycling it would be fatal.** **So the aliasing is the root, and the bins are only the thing that would make it visible.**

### The fix
**Make `kosh` assignment explicit, and refuse the silent one.**

**`vitti a = k` becomes a COMPILE ERROR, with a message that says what to write instead.** **To share a vector you pass it to a function or store it in a container deliberately; to copy one you call a copy function.**

**And a copy function is not a new concept — `vartani_pratilip` already exists as a copy builtin, so the naming pattern is established.** **A `kosh_pratilip(k)` follows it directly.**

### What this buys
1. **The surprising behaviour disappears.** **Two variables no longer silently own one buffer.**
2. **The old buffer becomes genuinely dead after growth** — **because the only way to reach it was the alias, and the alias is now a compile error.**
3. **Which means the recycling bins become SAFE.** **The invariant that was false becomes TRUE, by removing the thing that made it false.**
4. **And the leak can then be fully fixed, not half-fixed.**

### What it costs
- **One check in the assignment path** — is the right-hand side a `kosh` variable and the left a different one?
- **One builtin: `kosh_pratilip`.**
- **And it changes the language**: **programs that do `vitti a = k` stop compiling.** **That is a break, and it must be measured — how many programs in the tree do it?**

**This is a real cost, and it is the first thing to measure.** **If it is zero programs, the fix is free. If it is twenty, we decide with the number in front of us.**

---

## Improvement 2 — no fixed ceiling: reserve at link time, `mmap` chunks after

### The problem with the current design
**"Reserve a range in `.bss` and abort when it is exhausted"** has an unpalatable shape: **a program that needs slightly more than we guessed dies, and a program that needs less wastes address space.**

**And nobody has decided the number.** **64 MB? 1 GB? 16 TiB?** **Every answer is a guess about someone else's program.**

### The fix
**Two tiers, and the second tier is still cheap.**

1. **A `.bss` reservation** — modest, say 64 MB. **Free in file size, and it covers the overwhelming majority of programs with no syscall at all.**
2. **When it is exhausted, `mmap` a new CHUNK** — **say 64 MB again — and continue bumping inside it.** **The old chunk is never freed, and never needs to be.**

**So the syscall count is one per 64 MB, not one per allocation.** **That is a ~1,000,000× reduction in syscalls for a program that allocates small objects, and there is no ceiling.**

### Why this is better than either alternative
- **Better than a fixed ceiling:** **no program dies for being slightly bigger than we guessed.**
- **Better than `mmap` per allocation:** **one syscall per 64 MB instead of one per 64 bytes.**
- **And better than `MAP_NORESERVE` at 16 TiB:** **a 64 MB chunk is a number we can defend, and the growth path means we never have to defend a bigger one.**

### What it costs
**A chunk list — but a chunk is never freed, so the list only ever grows, and it only needs to hold the current chunk's end.** **One extra pointer and one compare on the slow path.**

**And the Windows story gets simpler too:** **`VirtualAlloc` a 64 MB chunk is the same call we already make, just far less often.** **The `MAP_NORESERVE` question — which nobody has answered — stops being a blocker, because the reservation is small enough that ordinary `MEM_COMMIT` is fine.**

---

## What to do with these

**Improvement 2 is safe, small, and unblocks Windows.** **It should go into Step 1 as designed.**

**Improvement 1 is the one that matters, and it is the one that needs a decision, because it changes the language.** **So the first thing to do is MEASURE: how many programs assign one `kosh` to another?**

**If the answer is zero, the fix is free and the leak gets fully solved.**
**If the answer is more than zero, we decide with the count in front of us rather than on principle.**

**And either way, the honest position today stands: a bounded leak is better than a use-after-free.**
