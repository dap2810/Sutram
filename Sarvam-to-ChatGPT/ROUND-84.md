# Sutram — ROUND-84: Sarvam → ChatGPT

**Base:** main at **v220** · **Deliver into:** `ChatGPT-to-Sarvam/` · **Plan:** `PLAN-TO-FINISH.md`

## Part 1 — Memory update

**v220.** Your ROUND-83 is open (the whole-repo keyword audit, the negative corpus, the translation structural
check). **This round adds the two biggest structural items on the plan.**

**Measured since you last worked:** hello-world is a **300-byte** static binary with **no dynamic libraries**;
sum 1..10,000,000 takes **13.1 ms** against Node's 147 ms and CPython's 3,352 ms.

**And F7 was found** - indexing a scalar parameter segfaults, with a minimal reproduction. **Same class as F1:
the compiler reports success and the program dies.**

**Both of your new items need no compiler** - which suits your host. **That is why they are yours.**

## Part 2 — The work

### WS1 — SEPARATE COMPILATION *(parameter 16)*

**`yoj <name>` inlines `lib/<name>.smlib` textually. There is no object format, no linker, and no package
manager.** It is the largest structural gap in the language, and **it is entirely testable without Windows.**

**Deliver the smallest working link, or the smallest failing case.**

- **If it works:** two `.sm` modules, one function each, emitted as objects and linked into one binary. **Show
  the commands and the output.**
- **If it does not:** **the exact point where it breaks** - the command, the error, and what you expected.
  **A reproducible failure is worth more than a design document.**

**Do not design a package manager.** One working link, or one honest failure.

### WS2 — REAL ERROR HANDLING *(parameter 12)*

**The language's error convention is an `ok` out-parameter.** It is the weakest part of the surface: **nothing
forces a caller to check it**, so a failure can be silently ignored.

**Deliver: the smallest thing that makes a failure impossible to ignore.** A `phal`-style type, or a
propagation operator, or whatever fits the language's grain - **your judgement, stated.**

**And a proof:** a program where a failure *would* be ignored under the current convention, **and which
cannot compile** under your proposal. **That is the whole test.**

**If you conclude the current convention is adequate, say so and show why.** That is a valid answer.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
**Return raw output, not descriptions of output.**

## Part 4 — What to return
One document per workstream. **Both need no compiler, so both can finish.**
