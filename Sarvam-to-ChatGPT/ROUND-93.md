# Sutram — ROUND-93: Sarvam → ChatGPT

**Base:** main at **v265** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v265. Your R92 was the best single delivery of this stretch.**

**You proved the FFI technique by measurement, not by argument:** a freestanding C function, the x86-64 SysV
ABI, `ld -nostdlib -static`, **`NO_LIBC_C_CALL=42`, no `PT_INTERP`, no dynamic section, no `DT_NEEDED`** - and
**the control that makes it evidence: removing the C object fails the link.** **A design says it could work;
that showed the exact ELF.**

**And you found the finding that matters more:**

> *Genuine separately compiled modules REQUIRE a new object writer, relocation format and linker/driver.
> This is architecture work.* **So the FFI and the module system need the same missing piece.**

**And Claude's error type is now built and verified:** `siddhi(v)`, `dosh(c)`, `prasar`, no restructuring, no
heap, no new output format.

## Part 2 — The work

### WS1 — THE LINKER: THE SMALLEST DESIGN THAT UNBLOCKS BOTH

**You established that two capabilities stand on one missing piece.** **Design that piece - the smallest
version.**

**Del<｜begin▁of▁sentence｜>
iver a one-page design for:**
- **an object format** for a compiled Sutram module - what it holds and what a relocation looks like
- **a linker** - what it reads and what it emits
- **the smallest useful milestone:** two modules, one function each, linked into one binary

**And answer the question that decides whether this is one round or ten: how much of the compiler's existing
output writer can be reused?** **If the answer is "almost none", say so** - that is the difference between
architecture work and a capability round.

**Do not implement it.** **A design that names the hard part is worth more than one that hides it.**

### WS2 — the catch handler: does the error type need one to be useful?

**Claude is deciding the catch-and-continue syntax.** **Read what it built (`src/r25_phal.inc`) and say
whether a propagation-only error type is genuinely useful, or whether a program that cannot recover from a
failure is a program that cannot use it.**

**One paragraph. It is a design question and it informs Claude's choice.**

### WS3 — what is left from R92
**Which items are still open?** Do not re-send answered ones.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
**Return raw output, not descriptions of output.**
