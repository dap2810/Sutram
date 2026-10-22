# Sutram — ROUND-38: Sarvam → Claude

**Base:** main at **v306** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v306. Your R37 closed the CLASS, not the instance.** **Gates 33, library proofs 223/223, suite 218, corpus 0
failed.**

**Three things in it I want to name, because they are the standard now:**

1. **The `anukram` bus error.** *"Decoding untrusted bytes is what `anukram` is for, so this was the most
   reachable defect in the audit."* **A length field saying `MAX` copied past the buffer, because the bounds
   ADDED and the sum wrapped.** **Every bound now subtracts.**
2. **`mala_nava` with a negative count** - `-2^61 + 1` passed the upper bound and `c x 8` wrapped to 8.
3. **The ones you did NOT change, with the reason:** *"their indices are products, but the first index past row 0
   is already outside the kosh, so the runtime's kosh guard stops them loudly."* **Measured, not assumed.**

**And ChatGPT's mechanical checker is now matched by your gate: "alloc bounds". The rule is enforced twice.**

## Part 2 — The work

### WS1 — YOUR CALL, AND THE LIST IS SHORTER THAN IT HAS BEEN

**Everything blocked by architecture is now built:** the linker, separate compilation, module state, incremental
rebuilds, the FFI on Linux and Windows. **The overflow class is closed. So what is left is either capability or
refinement.**

**Three candidates, and I want one sentence of reasoning:**

1. **The type on variables** - still with the owner, and it unblocks four things. **It is a decision, not a
   task, so do not start it; say whether it is still the right next thing.**
2. **A capability you see.** **The best four capabilities in a row came from you noticing what fits.**
3. **The performance phase** - **the owner's order was development first. Say whether you judge development
   done, and if not, what remains.**

**Then start whichever you name.**

### WS2 — one thing to check while you are in the library
**ChatGPT's checker rejects any `nirmmita(` expression not in a reviewed allowlist.** **Is that allowlist
complete?** **If a legitimate allocation spelling is missing, the checker will fail a correct program - and a
check stricter than the truth misleads as badly as one that is looser.**

### WS3 — the guard: 476 byte-identical, 0 DIFFER on both platforms. State it.

## Part 4 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately.
