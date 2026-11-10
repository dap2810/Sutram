# Sutram — ROUND-177: five transformations, and one of them removes the escape proof entirely.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**ROUND-176 is still open and it asked the zeroing decision.** **An independent review came back and it changes that decision — there is a better answer than either option I gave you.**

---

## 1. And first: your R175 answers a worry I raised wrongly

**I wrote "eight unrolled stores" for the `mala`. That was my phrase, and it was wrong.** **Your R175 says the zeroing is a plain loop up to 1 KiB and `rep stosq` above — so it scales with `N`.**

**So a `mala small[2]` is not overrun and a `mala big[100]` is not under-cleared.** **Confirm it in one line: the zeroing emits exactly `N` qwords, never a fixed count.** **If that is true, say so and the worry is closed.**

---

## 2. WS1 - and this is the transformation: detach on escape

**The current design proves non-escape by walking the syntax tree.** **A reviewer points out that in a single-pass compiler this is backwards — the declaration comes first in the source and the escape comes later, so you are proving something about code you have not read yet.**

**So stop proving it.**

**The hoisted slot holds a descriptor pointer that is reused next pass. At the moment the compiler emits an escape — `best = temp` where `best` was declared outside the loop — emit one extra instruction:**

```
mov  rax, [rbp - temp_slot]
mov  [rbp - best_slot], rax     ; best now owns that descriptor
mov  QWORD [rbp - temp_slot], 0 ; DETACH the hoisted slot
```

**Then the next pass sees zero and creates a fresh descriptor. `best` keeps the old one.**

**What that buys, in the reviewer's words:** *"You need zero AST lookahead walk to prove non-escape. Every `kosh` in every loop is hoisted unconditionally. Even a `kosh` that conditionally escapes on 3 out of 800,000 passes reuses its memory on the other 799,997."*

### Build it, and answer
1. **Does the detach break the current escape checks?** **They can stay — refusing is still correct. But if the detach makes them unnecessary, say whether they should go or stay.**
2. **And the loop-carried case:** **`curr = next` where both are loop-local — recycle the old `curr` descriptor into `next`'s slot instead of detaching it.** **Two descriptors for 800,000 passes.** **Is that safe, and is it the same instruction count?**
3. **And: does the detach make the hoist unconditional, so the nested-block work in R175 becomes the only rule?**

## WS2 - and this removes the 2.4x cost AND restores the guard
**A reviewer asked the question I should have asked: why is `mandapa` exit zeroing at all?**

- **A `kosh` cannot read stale bytes — it bounds-checks against `length`, which starts at 0.**
- **A `mala` cannot — it zeroes at creation.**
- **Only `nirmmita` can ever observe stale bytes.**

**So: leave `mandapa` exit untouched — one cursor restore, exactly as v315 — and zero inside `nirmmita` instead.**

**That should make all 38 guard programs byte-identical again, and take the block exit back from 13.2 ns to 5.6.**

**And zero only when the allocation is below the block's mark** — a `nirmmita` into virgin pages needs nothing, because the kernel already zeroed them.

**Measure both: the guard count, and the block-exit time.**

## WS3 - and a `nirmmita` in a loop should not need a block at all
**A reviewer's point: the book tells a student to wrap a loop body in a `mandapa` because `chakra` did not reclaim `nirmmita`. Now that `chakra` hoists a `kosh` and a `mala`, that advice is an artifact of the old design.**

**So: hoist a loop-local `nirmmita` the same way — `E_SCRATCH_ESCAPE` already guarantees it does not escape.** **Then a student never needs a dummy block inside a loop.**

**Is that safe?** **A `nirmmita` buffer is written by the program, not by the runtime — so reuse means pass 2 sees pass 1's bytes unless it zeroes. Zero 64 bytes with unrolled stores, or `N` qwords.**

**Answer, and build it if the rule is clear.**

## WS4 - and a block CAN return memory, for one comparison
**A reviewer's fifth option, and it solves the 200 MB one-off without slowing the loop:**

**At `mandapa` exit, check one threshold. If the rewound span is 16 MiB or more, call `madvise(MADV_DONTNEED)` — or `VirtualAlloc(MEM_RESET)` on Windows. Below that, one comparison and nothing else.**

**A block under 16 MiB keeps its hot pages. A 200 MB one-off hands all 200 MB back, and the kernel zeroes them on next access for free — which also removes the need to zero that span.**

**Is that right, and is the syscall cheap enough that a 16 MiB threshold is sensible?** **Answer; build it after WS1 to WS3 are clean.**

## WS5 - and one restriction to remove
**A reviewer: *"In `kosh temp[n]`, `n` is nothing more than the initial capacity. The only reason it is not hoisted today is that the compiler's check requires `n` to be a compile-time constant."***

**So a data-dependent `kosh temp[n]` can be hoisted by removing that restriction.** **The slot holds a descriptor that grows via `[d]`; only `length` is reset, so a pass needing more just grows the buffer.**

**Is that right?** **If it is, remove the restriction.**

## WS6 - and the scope
**In the report, say what the guard reads after each step.** **The project's rule is 0 DIFFER; the zeroing change broke it to 38, and WS2 should restore it.**
