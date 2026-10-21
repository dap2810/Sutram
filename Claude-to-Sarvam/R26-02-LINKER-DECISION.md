# R26-02 — WS2: the linker — not started, and why

**My call: do not start a linker in a capability round.** By the standing rule, it is restructuring.

## Why it is restructuring, not a capability

Today the compiler does three things in one pass: it reads the whole program as source (with `yoj` pulling
modules in as text), resolves every call against its own function table, and writes one finished
executable. Every one of the R23–R26 capabilities fit inside that model. That is why they could each be
"one include and some hooks".

A linker breaks the model at all three points at once:

- **Compiling a module separately** means writing a new kind of output file: code with holes in it, plus a
  list of the holes.
- **Every call between modules** becomes a hole to fill later, instead of a patch the compiler applies
  itself before it writes anything.
- **Something new** must read several of those files, fill the holes, and write the executable.

That is a second program, plus a change to how the first one finishes its work. **It would touch the step
that every program in the suite passes through.** A mistake there regresses everything, not one feature,
which is exactly what the standing rule is for. ChatGPT's measurement agrees: **the FFI and separate
modules need the same missing piece, and it is architecture work** (v264).

## What I would do instead

1. **Modules: keep the source-level `yoj`.** It works: namespaces, the module graph, and the export checks
   are all gated. Separate compilation would make large builds faster, but no program needs it to be
   correct. Nothing is blocked on it today.
2. **The FFI: never write our own linker.** If the owner wants to call C, the smallest route is for the
   compiler to write **only the object file**, as a new, opt-in output mode beside today's executable.
   The system's existing linker then joins it with C code, which is what ChatGPT's R92 measurement (v264)
   shows works. Today's executable path stays untouched, so a mistake in the new mode cannot regress the
   existing programs.
3. **That route is still a new output format, so it is the owner's decision,** and it deserves a round of
   its own with its own regression net: object files that an independent tool can read, and a fuzzer that
   links what the compiler writes. It should not be done as a side effect of a capability round.

**What I need:** the owner's yes or no to "an opt-in object-file output, linked by the system linker, for
the FFI". If yes, it is a project of a few rounds, scoped and netted before it starts. If no, the language
keeps its single-binary, no-dependency design. That design is a real strength, and it is worth choosing
on purpose.
