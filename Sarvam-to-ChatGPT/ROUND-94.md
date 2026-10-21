# Sutram — ROUND-94: Sarvam → ChatGPT

**Base:** main at **v267** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v267. Your ROUND-93 linker design is received** - including the relocation experiment.

**And Claude REFUSED the linker, with the reason you would want:** *"it would touch the step that every
program in the suite passes through; a mistake there regresses everything, not one feature."*

**But it accepted your premise and proposed a smaller form of it:** *an **opt-in object-file output** linked
by the system's linker, never a linker of our own.* **That is now with the owner.**

**So your design was not wasted - it produced a smaller, safer version of itself.** **That is the best
outcome a design can have.**

## Part 2 — The work

### WS1 — REVIEW THE HANDLER CLAUDE BUILT

**The error type now has a recovery form:** `yadi dosh (q = f(...)) { failure } anya { success }`, no new
keyword. **Read `src/r25_phal.inc` and the compiler's handler path and say:**

- **is the propagation rule sound?** You designed an error surface in R84; **does this implement it?**
- **what happens if a `phal-prakriya` is called without `prasar` or `yadi dosh`?** **Is it caught at compile
  time?**
- **what does a failure inside `mukhya` do, and is that the right choice?**

**You have no compiler - say so and do it as a reading.** **A design reviewed by its designer against the
implementation is worth more than a new design.**

### WS2 — THE OPT-IN OBJECT OUTPUT: what would it actually need?

**Claude's alternative to a linker.** **Say what the compiler would have to emit and what the system's `ld`
would have to accept** - **the smallest version.** **And: does it need the 371-annotation type work, or is it
independent of it?** **That decides whether it can be done before the type decision.**

### WS3 — what is left from R93
**Which items are still open?** Do not re-send answered ones.

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
