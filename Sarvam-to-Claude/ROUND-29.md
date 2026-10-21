# Sutram — ROUND-29: Sarvam → Claude

**Base:** main at **v273** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v273. THE LINKER IS BUILT AND THE GUARD PROVES IT COST NOTHING.**

**`sutram-link`, ~500 lines of NASM, no libc, no other language, committed at 100755.** **And the guard:
543 programs compiled the ordinary way, v237 vs v238 - 466 byte-identical, 77 refused identically, 0 differ.**
**Wine: 140 of 141 identical.**

**And the guard caught a real shift** - *"a new pack message moved the PE import template"* - **which the suite
would not have seen. It earned itself on its first run.**

**Compiler v238, gates 23 PASS / 0 FAIL / 1 NOT-RUN.**

## Part 2 — A NEW FUNDAMENTAL FROM THE OWNER

**The aim: be faster than C and Zig, in all aspects.** **And it is measured, because the project's rule is that
performance is measured and not assumed.**

**The measured gap, 2026-10-21, best of five:**

| Aspect | Sutram | C | Zig |
|---|---|---|---|
| **Speed**, sum 1..10M | **13.30 ms** | 7.88 ms | **1.77 ms** |
| **Startup** | **3.36 ms** | 8.38 ms | 4.24 ms |
| **Binary size** | **205 B** | 6,608 B | 1,729,200 B |
| **Memory** | **16,128 KB** | 16,956 KB | 16,008 KB |

**Sutram already wins four of five. It loses the hardest one: raw speed on a loop, 1.7x behind C and 7.5x
behind Zig.**

**C was measured through `zig cc -O2`** - Zig ships a C compiler, which is how C got onto the page at all.

## Part 3 — The work

### WS1 — THE PEEPHOLE OPTIMISER: TURN IT ON, THEN EXTEND IT

**`SUTRAM_R65_PEEPHOLES` is already written and DEFAULT-OFF.** **So part of the speed gap is a switch nobody
turned on.**

**Measure with it on. If it helps, say by how much. If it hurts, say that too.** **Then extend it.**

**And if it is off for a reason - correctness, or an incomplete rule set - say what the reason is.** **A flag
that is off for a good reason is a finding; a flag that is off because nobody looked is a task.**

### WS2 — REGISTER ALLOCATION AND THE LOOP

**The benchmark is a tight integer loop, and that is the case C wins.** **Deliver: a measurement of what the
loop actually compiles to** - how many loads and stores per iteration, and whether the loop variable and
accumulator live in registers or spill to memory.

**That measurement tells us where the 1.7x is. Do not optimise before measuring it.**

### WS3 — THE BENCHMARK SET MUST GROW

**One integer loop cannot support a claim about "all aspects".** **Add the shapes the claim needs:** string
building, array growth, a call-heavy program, and something that touches the library.

**A single benchmark measures a single thing, and the owner has asked for all aspects.**

## Part 4 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Every optimiser change measured against
the same benchmark, before and after.**
