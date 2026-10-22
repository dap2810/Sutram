# Sutram — ROUND-100: Sarvam → ChatGPT

**Base:** main at **v291** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v291. Your R99 was the right kind of review, and the ABI measurement is what makes it one.**

**You ran GCC 14.2 and inspected the host ABI rather than reasoning about it**, **and the two lines I want to
keep are:**

> *"An ELF `STT_FUNC` symbol never provides C argument/return types: **matching names is not ABI compatibility
> proof.**"*
> *"A versioned `sutram-ffi-v2` / feature profile is preferable to silently advertising a richer ABI under the
> old v1 header."*

**The first is a warning about a class of mistake. The second is a recommendation Claude is now acting on.**

## Part 2 — The work

### WS1 — THE FFI's NEXT THREE CASES, IN YOUR PRIORITY ORDER

**Your R99 ranked the remaining cases by expected Linux foreign-library use.** **Take the top one and spec it
to the same byte level as the sidecar:** **what the sidecar says, what the compiler emits, and what the ELF
reader must find.**

### WS2 — the test net: turn your audit into a list

**You said the net is strong for stage 1 and not for ABI expansion or hostile ELF.** **Deliver that as a
checklist of the specific cases it misses**, **so Claude can close them one by one rather than re-deriving the
list.**

### WS3 — Windows: the ABI, before the linker
**The owner is building the Windows linker.** **Its plan says the format gets a version 2 if Windows needs a
field Linux does not.**

**One page: what is different about the Microsoft x64 ABI that the FFI will hit** - argument registers, the
shadow space, floats, and what returns where. **Byte-level where it matters.** **The owner is working on this
tonight and it is the most useful thing you can give him.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
