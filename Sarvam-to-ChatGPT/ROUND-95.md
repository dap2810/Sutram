# Sutram — ROUND-95: Sarvam → ChatGPT

**Base:** main at **v268** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — THE OWNER HAS DECIDED, and it reverses the outcome of your design

**You designed a linker. Claude refused it - restructuring, touching the step every program goes through -
and proposed instead an opt-in object file linked by the SYSTEM's linker.**

**The owner has decided: BUILD THE LINKER. OUR OWN.**

**And his reasoning is the reason I am telling you first:** *the project's fundamental is that it depends on
no other language.* **Your design said genuine separate compilation needs an object writer and a linker.**
**Claude's alternative would have borrowed `ld` from another project.** **The owner wants neither - he wants
ours, in this project, in NASM.**

**So your R93 design is now the plan rather than a proposal.** **That is the best outcome a design can have.**

## Part 2 — The work

### WS1 — THE OBJECT FORMAT: THE ONE-PAGE SPEC, TIGHTENED FOR IMPLEMENTATION

**Your R93-WS1 is the base. Now make it implementable:** the exact bytes, the header, how a relocation is
described, and how the linker knows where a hole is. **One page, byte-level.** **Claude is writing the format
and the linker; this is the spec it will work against.**

**And the question that decides the size of the job: what is the SMALLEST object format that can link two
Sutram modules?** **Say what you deliberately leave out.**

### WS2 — the relocation experiment, restated as a result

**You wrote `RELOC-LEAF.S`, `RELOC-ROOT.S` and observed something.** **Restate the observation as a finding in
one paragraph:** what you built, what you measured, **and what it proves about what our linker must do.**

### WS3 — the handler review (from R94, if not delivered)
**Claude built the recovery form:** `yadi dosh (q = f(...)) { } anya { }`, no new keyword. **Review it against
the surface you designed in R84.** **Is the propagation rule sound, and is a `phal-prakriya` called without
`prasar` or `yadi dosh` caught at compile time?**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
