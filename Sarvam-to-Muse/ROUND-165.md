# Sutram — ROUND-165: five transformations, attacked before they are built.

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**An independent review came back with a verdict — *"you are at the right architectural answer, do not redesign"* — and five transformations. Claude has been asked to build them. You are being asked to break them first.**

**This is the order that has worked: design, attack, build. Not build, then find out.**

---

## 1. What is proposed

### A. Detach on escape — removes the escape proof entirely

**The current design proves non-escape by walking the syntax tree.** **The reviewer's argument: in a single-pass compiler that is backwards — the declaration comes first in the source and the escape comes later, so you are proving something about code you have not read yet.**

**So stop proving it. Emit the hoist unconditionally, and at the moment the compiler emits an escape, detach the slot:**

```
best = temp            where best was declared outside the loop
  mov  rax, [rbp - temp_slot]
  mov  [rbp - best_slot], rax      ; best owns the descriptor
  mov  QWORD [rbp - temp_slot], 0  ; DETACH
```

**Next pass sees zero and creates a fresh descriptor. `best` keeps the old one.**

**The claim: *"You need zero AST lookahead walk. Every `kosh` in every loop is hoisted unconditionally. Even a `kosh` that conditionally escapes on 3 out of 800,000 passes reuses its memory on the other 799,997."***

### B. Ping-pong for loop-carried `curr = next`

**Instead of detaching, recycle: write the old `curr` descriptor into `next`'s slot.**

**Claim: two descriptors for 800,000 passes.**

### C. Move the zeroing from `mandapa` exit into `nirmmita`

**Argument: a `kosh` cannot read stale bytes (length check), a `mala` zeroes at creation, so only `nirmmita` can observe stale data.**

**Claim: this restores all 38 guard programs to byte-identical and takes block exit from 13.2 ns back to 5.6.**

### D. A `madvise(MADV_DONTNEED)` threshold at block exit

**If the rewound span is 16 MiB or more, hand the pages back; below that, one comparison and nothing.**

**Claim: a block can return memory for one comparison, and the kernel zeroes on next access for free.**

### E. Remove the compile-time-constant restriction on `kosh temp[n]`

**Argument: `n` is only the initial capacity; the slot holds a descriptor that grows via `[d]`, and only `length` is reset.**

---

## 2. Task 1 - and this is the round: attack A, because it is the biggest

**Detach-on-escape removes a proof and replaces it with a runtime convention.** **That is exactly the kind of change that works on the cases you think of and fails on the one you do not.**

**Find the program that breaks it.**

**Think about:**

- **two names for one loop-local `kosh`, then one of them escapes** — `kosh b = temp` then `best = b`. **Does the detach happen on `b`'s slot, on `temp`'s, or both?** **If it detaches one and not the other, the next pass reuses a descriptor that is still live.**
- **a detach inside a branch that runs twice** — `yadi (c) { best = temp }` on pass 5 and pass 500. **Does the second detach detach a slot that is already zero?**
- **a `kosh` that escapes by being passed to a `prakriya`** — the escape is a call, not an assignment. **Where is the detach emitted?**
- **a `kosh` that escapes by being stored in an outer `kosh`** — `kosh_kship(outer, temp)`. **Same question.**
- **`temp` read after it has been detached** — `best = temp` then `likha(temp[0])` on the same pass. **Is `temp` still valid for the rest of that pass?**
- **recursion** — the same slot at two depths.
- **and the one I would check first: a detach inside a `mandapa`.** **The `mandapa` rewinds the cursor. Does the detached descriptor's buffer survive that rewind?**

**Name the program, or say A is closed and why.**

## Task 2 - and attack B
**Ping-pong recycles a finished descriptor into a slot that will be reused.** **That is a write into a slot the next pass will read.**

**Find the case where the recycled descriptor is not finished.** **`curr` is read after the swap?** **`next` escapes before the swap?** **Three names?**

## Task 3 - and C, which should be easy to check
**The claim is that only `nirmmita` can observe stale bytes.**

**Is that true?** **Read the `kosh` read path and the `mala` read path and confirm:**
- **does a `kosh` read ever look past `length`?**
- **does a `mala` zero at creation, or only at the top of a hoisted pass?** **If a `mala` is created fresh each pass in the current code, it may rely on fresh memory being zero — and if memory stops being zeroed at block exit, a fresh `mala` in a block reads stale bytes.**

**That last one is the case C could miss.**

## Task 4 - and D and E, briefly
**D:** **is `madvise(MADV_DONTNEED)` correct for a span that a later `nirmmita` will use?** **Does it leave the mapping in place so the cursor can still walk into it?** **And on Windows, is `VirtualAlloc(MEM_RESET)` the equivalent?**

**E:** **is there any case where `kosh temp[n]` with a runtime `n` behaves differently when hoisted?** **A pass with a smaller `n` after a pass with a larger one — does it shrink the buffer or keep it?**
