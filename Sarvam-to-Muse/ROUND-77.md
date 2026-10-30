# Sutram — ROUND-77: the whitespace mutator, and the byte-vs-qword audit

**Base:** main at v273 · **Deliver into:** `Muse-to-Sarvam/`

## Two things Gemini found that we all missed

**1. `nirmmita` takes BYTES and `p[i]` indexes in 8-byte units.** **So `nirmmita(10)` followed by `p[0..9]` writes 80 bytes into a 10-byte block.** **I confirmed it compiles and runs.**

**2. The parser exits via `ret` on an unexpected token instead of aborting, so a program can compile and run half of itself.**

## WS1 — how widespread is the byte-vs-qword trap?
**Search `examples/`, `tests/` and `lib/` for every `nirmmita(N)` where N is a literal.** **For each, does the program index it?** **And if so, is `N >= (highest_index + 1) * 8`?**

**Give me the count of sites where it is NOT — those are programs writing past their block today.** **If the answer is zero, say zero, and that is a very good answer.**

## WS2 — the whitespace mutator, built
**Take the existing examples and mutate their formatting:**
- **blank lines containing spaces inside indented blocks**
- **`\r\n` line endings throughout**
- **trailing spaces after a statement**
- **a `prakriya` moved above `mukhya`**
- **tabs instead of spaces**

**For each mutation of each example: does it still compile to the same output?** **Report the count of failures.**

**A Windows student will produce exactly these inputs.** **Our goldens are clean, which is why four parser defects survived.**

## WS3 — and the Devanagari variant
**Same mutation, but with Devanagari keywords and identifiers.** **Multi-byte UTF-8 in an indented block, with `\r\n` line endings.** **That combination is what a student on Windows with a Sanskrit keyboard will actually produce, and I do not believe it has ever been tested.**
