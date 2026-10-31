# Sutram — ROUND-66: two design improvements, and one measurement that decides the first

**Base:** main at v416, compiler v261 · **Deliver into:** `Claude-to-Sarvam/`

**Read `docs/decisions/MEMORY-DESIGN.md`'s CORRECTION section first, then this round's brief.**

## Improvement 2 goes into Step 1 unchanged — no fixed ceiling

**Instead of "reserve a range and abort when full":**
1. **A `.bss` reservation, modest — say 64 MB.** **Free in file size, covers most programs with no syscall.**
2. **On exhaustion, `mmap` a new CHUNK of the same size and continue bumping inside it.** **The old chunk is never freed and never needs to be.**

**So the syscall count is one per 64 MB, not one per allocation.** **No ceiling, and a ~1,000,000× reduction in syscalls for small-object programs.**

**And it fixes the Windows blocker:** **`VirtualAlloc` of a 64 MB chunk is the call we already make, far less often — so the unanswered `MAP_NORESERVE` question stops being a blocker.**

**Build this into Step 1 alongside the contiguous bump and in-place `kosh` extension.**

## Improvement 1 — measure before designing, and this is the whole round

**The recycling bins were unsafe because a `kosh` buffer can have two owners: `vitti a = k` makes `a` a second live `kosh`, and after growth there are two buffers.**

**So the aliasing is a LANGUAGE bug, not an allocator constraint.** **Remove the alias, and the old buffer becomes genuinely dead, and the bins become safe.**

**The proposed fix: `vitti a = k` becomes a COMPILE ERROR, and a copy becomes explicit via a new builtin following the `vartani_pratilip` naming pattern.**

**Before any of that, MEASURE:**

**1. How many programs in `examples/`, `tests/` and `lib/` assign one `kosh` variable to another?** **Name the files.**
**2. How many pass a `kosh` to a `prakriya` that stores it?** **That is a deliberate share and should stay legal.**
**3. How many store a `kosh` inside a `mala`, a `rachana`, or a global?** **Those are deliberate aliases too.**
**4. And how many `kosh` declarations in the tree would still work if assignment were banned?**

**If the answer to 1 is zero, the fix is free and the leak can be fully solved.** **If it is twenty, I decide with the number in front of me.** **Give me the number.**

## And do NOT build improvement 1 yet
**Measurement only this round.** **The design change needs the count first, and the language change needs a decision that is not mine.**

**Step 1 — the bump, the chunks, the in-place extension — is the build. Improvement 1 is the measurement.**
