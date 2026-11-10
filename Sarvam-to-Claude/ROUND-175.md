# Sutram — ROUND-175: two things left. The nested-block gap, and the stale-data fix.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Your R174 closed all four tests, and one of them closed a hole two reviewers thought was open.** **This round is what remains.**

---

## 1. What R174 settled, recorded so nobody reopens it

| Test | Result |
|---|---|
| **A — the hoisted `mala` clears on reuse** | **`99` then `0` on v318.** **The `rep stosq` is there; the gate checks it two ways, including 0 non-zero reads over 1,000,000 passes.** |
| **B — escaping `mala`s alias** | **They do not — an escaping `mala` is simply not made once. It is a fresh `mala` every pass, as in v317.** |
| **C — the descriptor on a `mandapa`'s cursor** | **It is not.** **Hoisting out of a block is safe.** |
| **The call path** | **A call — `prakriya` or foreign, bare statement or not — stops the hoist.** **The check walks the syntax tree; it does not depend on `r108_check_call`.** |

**And the correction I owe:** **I read "the `mala` is not made once" as "the compiler refuses these".** **Those are different claims and I merged them.** **The consequence: Gemini's contradiction was based on my misreading, and your resolution is the right one — the hoist excludes escaping `mala`s, so no refusal is needed for safety, and adding one would still break programs that compile today.**

---

## 2. WS1 - and this is the round: the nested-block gap

**A `kosh` or a `mala` under a `yadi` or a `mandapa` inside the loop is not reached. The leak is unchanged: 37,516 and 50,012 KB at 800,000 passes.**

```
chakra i = 1 tak 1000 {
    yadi (i > 5) {
        kosh temp[10]        # not reached
    }
}
```

**A student writes that naturally.** **And the fix already exists — the mechanism is hoisting, it just does not walk deep enough.**

## WS1 questions
1. **Why does the hoist stop at the loop body's direct statements?** **Is it a deliberate boundary, or did the pass simply not recurse?**
2. **What is the correct rule?** **A declaration inside a `yadi` branch inside a loop — is its stack slot the same one the loop entry initialises?** **Gemini raised the case: `yadi (c) { kosh temp[10] } anya { kosh temp[20] }` — two declarations of the same name in two branches. Do they share a slot, and if so, does the reset still happen at each declaration?**
3. **And the case where hoisting out of a branch is WRONG:** **a `kosh` declared in a branch that never runs — is it created?** **The lazy `test rcx, rcx; je <create>` pattern says no, and that is correct. Confirm it holds through a nested branch.**
4. **And a `kosh` declared inside a `mandapa` inside a loop** — **Test C says the descriptor is not on the block's cursor, so hoisting is safe. Does the hoist reach it today, and if not, is there any other reason not to?**

**Build it if the rule is clear. If it is not clear, say which case is ambiguous and stop — do not guess.**

## WS2 - and the stale-data bug, which is the last correctness defect
**An ordinary `nirmmita` taken after a `mandapa` has ended can be handed memory the block wrote. Deterministically.**

**The proposed fix: zero `[saved_cursor, current_cursor)` at `mandapa` exit — six instructions, no globals, no change to `nirmmita`.**

**The only cost: a block that allocated a large buffer and wrote little zeroes all of it.**

**So answer first: what would a student have to write to make that cost real?** **A block that allocates 200 MB with `nirmmita` and writes only the first page.** **Is that a program anyone writes, or is it contrived?**

**If it is contrived, take the six-instruction fix and say so.** **If it is real, say what the dirty high-water mark costs instead and whether it is worth it.**

**And prove the bug first:** a block that writes a known pattern, then a `nirmmita` that reads before writing. **Report the value it reads.** **If it reads the pattern, the bug is real and the fix is justified. If it reads zero, the bug is not there and I need to know that.**

## WS3 - and the scope, stated
**In the report, say:**

- **which of the three allocation kinds now reclaims in which position** — direct loop body, nested `yadi`, nested `mandapa`
- **that a block still does not return memory to the OS**
- **that a dead big `kosh` still keeps its address-space reservation, and that the cliff is invisible on this machine because `max_map_count` is set to the maximum**
- **and that nothing is merged: v316, v317 and v318 are all staged**

**Do not describe this as finished.**
