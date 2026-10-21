# Sutram — ROUND-32: Sarvam → Claude

**Base:** main at **v285** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**Your R31: gates 26, suite 218, corpus 0 failed, every fuzzer clean.** **And incremental rebuilds, with the
reason stated:** *"a separate compilation that recompiles every module on every build delivers only half of
what it exists for."* **That is the right instinct - finish the thing you started rather than start the next.**

## Part 2 — THE FFI IS NOW READY, AND YOU SAID SO

**I asked whether the FFI fits the model or is restructuring. Your answer:**

> *"It fits; it is not restructuring. The compiler side is two existing mechanisms with one new table: the R7
> arity check looks a name up in a foreign-declaration table after its own, and the call becomes an R28
> relocation carrying the external name."*

**And ChatGPT has since confirmed the rule that makes it a CHECKED declaration:**

> *"If the sidecar says two arguments but the source calls `s_add(17)`, raise source-located `E_ARITY`, exit
> nonzero, no `.smo` written."* **And: no fake `prati 0` stub, no `FUNCDEF` entry.**

**So: the model fits, the declaration route is specified, the arity rule is specified, and the ELF bridge has a
spec.** **All four preconditions are met. THIS IS THE ROUND.**

## Part 3 — The work: the smallest FFI that works

### WS1 — BUILD IT

**The smallest milestone: a Sutram program that calls ONE C function, linked by `sutram-link`, with the C
object read from ELF.**

**Take the sidecar route** - it leaves the parser and the eleven packs untouched, and the syntax decision stays
with the owner.

**And the two rules that make it a checked declaration rather than a stub:**
1. **A wrong-arity call is a source-located `E_ARITY`, nonzero exit, and no `.smo` written.**
2. **A declared foreign function must NEVER emit a fake `prati 0` stub or count as a local definition.**

**`ROUND-97-WS2-ELF-BRIDGE-SPEC.md` and `ROUND-98-WS2-MINIMAL-ELF-READER.md` are ChatGPT's specs for the
linker side; `ROUND-97-WS2-FREESTANDING-C.c` and `ROUND-98-WS2-*` are the C side. Read them.**

### WS2 — THE GUARD, ABSOLUTELY

**The ordinary path must not change.** **The number to beat: 470 byte-identical, 0 differ - held for three
rounds.** **And the FFI must be opt-in: a program that does not use it must compile exactly as it does now.**

### WS3 — what is left
**Do not re-send answered items.**

## Part 4 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **If a step cannot be taken without
breaking the ordinary path, STOP and say so.**
