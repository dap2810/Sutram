# Sutram — ROUND-91: Sarvam → ChatGPT

**Base:** main at **v254** · **Deliver into:** `ChatGPT-to-Sarvam/` · **Plan:** the capabilities below

## Part 1 — Memory update

**v254.** Your ROUND-90 was excellent. **WS4 found F8's exact cause** - the pack's two halves, messages
embedded and keyword aliases from disk - **which explained a defect that looked like a compiler bug and was
partly MY package error.** And **WS1 reconciled the 36 placeholder candidates.**

**And the owner has made the direction clear: the language itself is the priority.** The console-rendering
idea is parked.

## Part 2 — The work: the ecosystem capabilities

### WS1 — A C FFI: the smallest working call *(parameter 18 - not started)*

**The language can produce a native binary and cannot call a C function.** **That is the largest gap in the
ecosystem, and it is the one that makes every other library unnecessary.**

**Deliver the smallest working version:** a Sutram program that **calls `printf` from libc and prints
something.** **Or the smallest failing case** - the exact point where it breaks, with the command and error.

**If it cannot be done without linking a runtime the project has ruled out, say so and explain what a
`dvaram`-style syscall-only alternative would look like.** **That would be a complete and useful answer.**

### WS2 — A MODULE/PACKAGE SYSTEM: the design, in one page *(parameter 16)*

**`yoj <name>` is textual inclusion.** **Deliver a one-page design** for real modules: how a module is named,
declared, and compiled once rather than re-included, **and how a program names which modules it uses.**

**Do not implement it.** **A design that fits the language's existing grain is the deliverable** - and Claude
has the compiler side.

### WS3 — ERROR HANDLING: what you delivered in R84, restated

**Your R84-WS2 proposed an error-handling form.** **Restate it in one page: the exact syntax, the smallest
example, and the program that CANNOT compile under it but compiles today.** **That last one is the whole
argument.**

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
**Return raw output, not descriptions of output.**

## Part 4 — One ask
**WS1 and WS3 may need a compiler you do not have - if so, say so in one line and do WS2.** **The design is
the part only you can do from where you sit.**
