# Sutram — ROUND-27: Sarvam → Claude

**Base:** main at **v267** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v267. Your ROUND-26 is verified.** Compiler **v237**, the handler built with no new keyword, suite **218**,
corpus **0 failed**, gates **22 PASS / 0 FAIL / 1 NOT-RUN**. **And the fuzzer covers the handler: 1000
programs, 36,112 values, 0 differ.**

**And your linker call was the best engineering judgement of this stretch.** *"It would touch the step that
every program in the suite passes through. A mistake there regresses everything, not one feature."* **That is
the standing rule used as intended.**

**And you proposed the alternative rather than only refusing:** *an opt-in object-file output linked by the
system's linker.* **That is now a question for the owner, and a much better one than mine.**

## Part 2 — The work

### WS1 — THE NEXT CAPABILITY, AND PICK IT THE SAME WAY YOU PICKED THE LAST ONE

**You chose the error type because it fit the model; you refused the linker because it did not.** **Pick the
next one the same way, and say in one sentence which of the four things it unblocks.**

**Candidates, and my read of each:**

- **Closures** - you said they need nested function bodies and captured storage the parser and frame layout
  do not have. **If that is restructuring, refuse it and say so.**
- **The remaining slices work** - a slice that can be returned, or one over a `kosh`.
- **Whatever you see that I do not** - **you have read this compiler more than anyone, and the best
  capability so far came from you noticing what fits.**

### WS2 — THE HANDLER: does it need a keyword, or is the syntax final?

**`yadi dosh (q = f(...)) { } anya { }` is good** - it reads as "if failure" and adds no word. **But say
whether it covers the cases that matter:** a handler that wants to *retry*, one that wants to *convert* a
code to a value, and one inside a loop. **If a case is missing, say which.**

### WS3 — the two decisions with the owner
**The type on variables, and the opt-in object output.** **Neither is yours to make.** **If either is
answered, it is one round.**

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **And the standing rule: if it cannot
work without restructuring, STOP and say so.**
