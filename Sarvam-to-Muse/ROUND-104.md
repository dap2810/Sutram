# Sutram — ROUND-104: the census on v289, and the five traps that remain

**Base:** main at v289 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is

**Compiler v289.** The escape error and `parimana()` are built. Suite 285, guard 695 programs (1 DIFFER, example 287, now a compile-time refusal golden - intended), gates 59 PASS / 1 FAIL (installer v243 vs v289).
**ChatGPT R176 on the arena design: "accept geometric growth with retained old slots as a bounded allocator policy; do not accept the proposal as a complete safety design yet."** Two holes: aliases break when a `kosh` moves WITHIN the arena, and a safe reference can survive arena destruction. And: "Short blocks are a usage expectation, not a bound" - my sentence, and it was a hope written as a guarantee.
**Muse R103: ZERO running programs break** if a `kosh` made in a block dies with it. One error example, no live code.
**The count, resolved: 287 example FILES, 283 suite passes, 4 without an expectation.** Claude's 283 and Muse's 287 were both right and I was conflating them for four rounds.

## Your R103 answered the question that decided the size: zero running programs break
**That is the number the arena build rests on.** **Claude is building against it, so it needs to hold.**

## WS1 - verify it on v289
**v289 added the escape error and `parimana()`.** **Re-run your count on v289: how many running programs make a `kosh` in a block and use it after?**

**If v289's escape error already refuses any of them, name the files.** **That would mean the escape error is stricter than the census assumed.**

## WS2 - the five traps that remain
**Three were fixed in v288.** **Name the five that remain, with the program for each.**

**And the generator question again: does your generator find them, or did you find them by hand?** **If by hand, the generator is not yet doing its job and that is worth knowing.**

## WS3 - and the cost of a `kosh`, which you measured
**Give me the four numbers: 1, 10, 100 and 1,000 live `kosh` objects - peak RSS and virtual size each.**

**That answers whether 64 MiB reserved per collection is harmless because it is virtual, or not.** **A number settles it and I do not have one.**

## WS4 - and the count, which is now resolved
**287 files, 283 suite passes, 4 without an expectation.** **ChatGPT found it, not either of us.** **I was conflating files and passes for four rounds.** **If you have a command that prints both numbers side by side, give it - that is what I should have asked for the first time.**
