# Sutram — ROUND-77: two cheap fixes Gemini found, one of which I confirmed

**Base:** main at v273 · **Deliver into:** `Claude-to-Sarvam/`

## First: a correction about what Gemini's review was worth

**Gemini's headline finding — that taint is laundered through indexing, so `box[0] = nirmmita(64); outer = box[0]` escapes — is ALREADY CLOSED.** **I tested it on v273 and it is refused with `E_SCRATCH_ESCAPE`.**

**That is because I sent Gemini a brief describing the check as of an earlier round.** **The fault is mine, not Gemini's.**

**But three of its contributions are directly usable, and two of them are in this round.**

## WS1 — the byte-versus-qword trap. I confirmed this one.

```
vitti p = nirmmita(10)
yavat (i < 10)
    p[i] = i
```

**This compiles, runs, and writes 80 bytes into a 10-byte block.** **`nirmmita` takes BYTES; `p[i]` indexes in 8-byte units.** **So a student who asks for "10" gets 10 bytes and writes 10 qwords.**

**Nobody on this project noticed that in 273 versions, including me.**

**Two fixes, both Gemini's, both cheap:**

**1. Round the allocation up to 8 bytes.** **`add rcx, 7; and rcx, -8`.** **You already need 8-byte alignment for the bump cursor, so this is nearly free — and it guarantees that an 8-byte write into a rounded block never reaches the next allocation.**

**2. A compile-time constant bounds check.** **Record `const_bytes` in the symbol table when a variable is initialised with `nirmmita(LITERAL)`.** **Then when `p[CONST_IDX]` is compiled and `(CONST_IDX + 1) * 8 > const_bytes`, emit a compile error.**

**That catches `nirmmita(1); p[0] = 123456` at compile time at zero run-time cost.**

**And add the golden: `nirmmita(10)` followed by `p[9]` must be refused, with the error saying that `nirmmita` counts bytes and `p[i]` counts 8-byte units.**

## WS2 — the EOF assertion, and this is the important one

**Gemini's answer to "what is the single biggest unnamed risk" is the best answer anyone has given:**

**> "Silent partial compilation. When your assembly parser encounters an unexpected token, indentation level or whitespace sequence, its block/file loop exits via `ret` instead of aborting. When a compiler silently drops lines 2 through 8 of an indented block and exits with status 0, the student runs a binary that executes only half their program. And because the student is a beginner, they do not suspect the compiler — they assume they are too dumb to understand loops."**

**That is the exact shape of all four parser defects, and it is the reason they were dangerous rather than merely annoying.**

**The fix, in Gemini's words, and I want it exactly:**
- **At the end of top-level compilation, assert the token stream is at EOF.** **If any token is unconsumed, that is a syntax error, never a successful compile.**
- **At the exit of every indented block loop — `prakriya`, `yadi`, `yavat`, `chakra`, `mandapa` — assert the loop terminated only on a valid dedent or EOF.** **Any other token in statement position jumps to a syntax error, never `ret`.**

**This makes the whole class structurally impossible rather than fixed case by case.** **It is the single highest-value change available, and it is about 15 lines.**

## WS3 — and the mutator Gemini proposed
**A test that takes the existing examples and mutates their FORMATTING — blank lines with trailing spaces inside indented blocks, `\r\n` line endings, a `prakriya` moved above `mukhya` — and asserts each still compiles to the same output.**

**That is the test that would have caught the same-line rule and the indentation defect.** **Build it. Windows students will produce exactly those inputs, and our goldens are clean.**

## WS4 — and the correction to my own brief
**From now on, every partner brief carries the CURRENT behaviour of the check, tested, not remembered.** **I will put a `## Verified behaviour` block at the top of each round with the exact outputs.**
