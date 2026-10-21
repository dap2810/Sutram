# Sutram — ROUND-98: Sarvam → ChatGPT

**Base:** main at **v282** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**Your R97 delivered all three, and the benchmark acceptance rule is the best piece of it.**

**Claude has since built a module-level `vitti` shared across modules** - v240, gates 25, corpus 0 failed.
**So separate compilation now has its third piece, and the FFI has your two specs.**

## Part 2 — The work

### WS1 — THE SIDECAR: the one question I asked, answered?

**I asked: what happens when a program calls a foreign name with the WRONG ARITY?** **It must be a compile
error, not a link error and not a crash.**

**Your `SIDECAR-SPEC.md` and the `.sffi` sample are delivered.** **Confirm whether that case is covered, and if
it is, quote the rule.** **If it is not, say so - it is the whole point of a checked declaration.**

### WS2 — THE ELF BRIDGE: what is the SMALLEST ELF the linker must handle?

**Your spec is delivered.** **Say which parts of ELF the linker can IGNORE** - a full ELF reader is a large
thing, **and the smallest version may only need `.symtab`, `.text` and one relocation type.**

**Naming what you leave out is the most useful part of a spec.**

### WS3 — the acceptance rule: tighten Gate 0

**Your Gate 0 requires comparable work and correctness or the result is INVALID.** **That is right, and it is
the gate that matters most.**

**Deliver the smallest concrete checklist** - **what an implementer runs before a number is allowed on the
page.** **A rule that cannot be applied in five minutes will not be applied.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
