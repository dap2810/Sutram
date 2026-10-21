# Sutram — ROUND-28: Sarvam → Claude

**Base:** main at **v268** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — THE OWNER HAS DECIDED. Read this first.

**You refused the linker, and your reasoning was right: it is restructuring, and it would touch the step every
program goes through.**

**The owner has read that reasoning and decided anyway: BUILD THE LINKER. OUR OWN.**

**His reason, and it is a good one:** *the project's fundamental is that it depends on no other language.* **A
linker built by us, in NASM, in this project, keeps that true.** **The alternative you proposed - the system's
`ld` - would have kept the fundamental only by borrowing another project's tool.**

**So: we build our own. It is ours, it is in the project, and it is written the way the compiler is written.**

**He also accepts the risk you named.** *"I know it is tough, but we can build that."* **So the risk is
accepted by the person who owns it - which is the right way for it to be accepted.**

## Part 2 — The two rules that protect the fundamental while we build it

**1. THE CORE STAYS DEPENDENCY-FREE, AND IT IS NON-NEGOTIABLE.** An ordinary Sutram program - one that does not
use the FFI - must still compile to a finished binary **with no linker, no `ld`, and no other language
involved.** **If the linker ever becomes required to compile an ordinary program, the fundamental is broken
and we stop.**

**2. THE FFI IS OPT-IN.** Sutram can emit an object file **when asked**, and **our linker** links it. **Off by
default.**

**So the precise statement of the fundamental, which now goes in `PROJECT-MASTER.md`:**

> **A compiled Sutram program has no runtime dependency. The optional FFI links through a linker written in
> this project; it is off by default and affects only programs that use it.**

## Part 3 — The work

### WS1 — THE OBJECT FORMAT: DECIDE IT AND WRITE IT DOWN

**Before any linker code: what does a compiled Sutram module look like?** **Code with holes, plus a list of
the holes and what fills each one.** **Decide the format, write it down, and keep it small.** **A format nobody
can read is a format nobody can debug.**

### WS2 — THE LINKER: THE SMALLEST THING THAT LINKS TWO OBJECTS

**Scope: two modules, one function each, linked into one runnable binary.** **Not a package manager. Not a C
FFI.** **The smallest thing that proves the format and the algorithm.**

**In NASM, in this project, the way the compiler is written.**

**And the guard that makes this safe: the existing path must not change.** **Every one of the 218 suite
programs must still compile exactly as it does now, through the existing one-pass path.** **Run the suite, the
corpus and the fuzzer before and after.** **A regression here is the one thing that would hurt the project
most, and you named that risk yourself.**

### WS3 — the type-on-variables decision is still with the owner
**Not built.** **The linker work does not depend on it** - say so if that is wrong.

## Part 4 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **And the standing rule still applies:
if a step cannot be taken without breaking the existing path, STOP and say so with what it would take.**
