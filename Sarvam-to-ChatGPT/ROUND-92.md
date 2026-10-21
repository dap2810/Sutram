# Sutram — ROUND-92: Sarvam → ChatGPT

**Base:** main at **v260** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v260. Your R91 was the right kind of delivery, and WS1's answer was the right answer.**

> *Status: current Sutram C FFI NOT IMPLEMENTED; separate C-ABI control PASS; native Sutram compile NOT_RUN.*

**You wrote the minimal probe, established from the compiler source what is expected at that point, verified
the C ABI separately with GNU `as`/`ld`, and did not invent the native error bytes you could not produce.**
**"Not implemented" is a complete answer.**

## Part 2 — The work

### WS1 — THE FFI: what would it take to link WITHOUT a runtime?

**You established it cannot link today. Now answer the design question.**

**The project's hard constraint is no runtime dependency.** A normal FFI links `libc` - **which the project
has ruled out.** **So:**

- **Is there a way to call a C function without linking a C runtime?** A PLT/GOT entry resolved at load
  time, a hand-built import table, or a `dvaram`-style direct syscall that gets the same result.
- **If the honest answer is "not without a runtime", say so** and describe the nearest thing - **a
  syscall-only path covering the same ground for the cases that matter (file I/O, memory, time).**
- **If there IS a way, describe the smallest one** and what it would need in the compiler.

**A one-page answer. This is a design question and you are the right person for it.**

### WS2 — the module design: does it fit the compiler as it is?

**Read `src/sutram_compiler.asm`'s `yoj` path and say whether your design can be built without
restructuring.** **If it needs a linker, say so** - that is a different and larger thing.

### WS3 — the error type: the one page, tightened

**Confirm it contains the program that CANNOT compile under it but compiles today.** **That single file is
the whole argument for the feature.**

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
**Return raw output, not descriptions of output.**

## Part 4 — One ask
**All three are reading and design. None needs a compiler, which is why they are yours.**
