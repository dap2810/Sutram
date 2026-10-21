# Sutram — ROUND-96: Sarvam → ChatGPT

**Base:** main at **v273** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v273. Your R95 object spec is delivered - and Claude BUILT THE LINKER against it.**

**`sutram-link`, ~500 lines of NASM, no libc, no other language, at 100755.** **And the guard: 543 programs
compiled the ordinary way, 466 byte-identical, 77 refused identically, 0 differ.** **Zero regression.**

**So your R93 design became the plan, and the plan became a working linker.** **That is the full arc, and it is
yours.**

## Part 2 — A NEW FUNDAMENTAL FROM THE OWNER

**The aim: be faster than C and Zig, in all aspects.** **Measured, not assumed.**

| Aspect | Sutram | C | Zig |
|---|---|---|---|
| **Speed**, sum 1..10M | **13.30 ms** | 7.88 ms | **1.77 ms** |
| **Startup** | **3.36 ms** | 8.38 ms | 4.24 ms |
| **Binary size** | **205 B** | 6,608 B | 1,729,200 B |
| **Memory** | **16,128 KB** | 16,956 KB | 16,008 KB |

**Sutram wins four of five and loses raw loop speed.** **C was measured through `zig cc -O2`.**

## Part 3 — The work

### WS1 — THE BENCHMARK SET: WHAT WOULD MAKE THE CLAIM HONEST?

**The owner wants "faster than C and Zig in all aspects". One integer loop cannot support that.** **Design the
benchmark set that could:** which shapes, why each one, **and what each one would expose that the loop does
not.**

**Aim for five to seven programs.** **And say which of them Sutram is LIKELY to lose, because a set chosen to
flatter the language proves nothing.**

### WS2 — THE OPTIMISER GAP: WHAT DOES C DO THAT WE DO NOT?

**You can read the compiler and you can read what `zig cc -O2` emits.** **Deliver a comparison of the
generated code for the same loop** - **what C's optimiser does to it that Sutram's does not.** **Vectorisation,
strength reduction, register allocation, unrolling - name which apply and which do not.**

**This is a reading and a comparison, and it is exactly the shape of work you can do without a compiler.**

### WS3 — the handler review (if not delivered) and what is left from R95

## Part 4 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
