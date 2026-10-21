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


---

## PRIORITY CHANGE FROM THE OWNER (read before starting)

**The owner's words: *"first focus on development and then we can refine the project to outperform other
languages."***

**So the performance work in Part 3 is DEFERRED.** **The fundamental stands and the measured gap is recorded,
but it is not this round's work.**

**DEVELOPMENT COMES FIRST - and your own finding made it possible.**

**You proved the FFI technique by measurement, and you found that genuine separate compilation needs an object
writer and a linker.** **Claude has now built both: `sutram-link`, in NASM, and it works - 186 programs
byte-identical through the new path.**

**So the two capabilities you said were blocked are now reachable. THIS ROUND:**

### WS1 - THE FFI: THE SMALLEST SUTRAM PROGRAM THAT CALLS A C FUNCTION

**You proved a freestanding C function can be called with no libc and no dynamic loader.** **Now design the
smallest Sutram-side version:** what `yoj`-style declaration a program needs to name an external function,
**and what the object must carry so `sutram-link` can fill that hole.**

**You have no compiler - a design is the deliverable, and say so.** **Claude has the compiler.**

### WS2 - SEPARATE COMPILATION: WHAT `yoj` MUST BECOME

**`yoj` is textual inclusion. The object format and linker now exist.** **Say what has to change in the module
graph so a module is compiled ONCE rather than pasted - and what breaks in the existing 543 programs if it
does.**

**That last part matters most: the guard is absolute.**

### WS3 - and the benchmark set: KEEP IT, but as a document, not a task

**Your R96-WS1 ask still stands - design the set, name where Sutram is likely to lose - but it is a
deliverable for the NEXT phase, not this round's work.**
