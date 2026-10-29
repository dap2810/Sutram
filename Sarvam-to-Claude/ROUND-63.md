# Close the last three items — then development starts

**Base:** main at v414, compiler v261 · **Deliver into your own folder.**

**Steps 3 and 4 are designed. Three things block the start of development, and all three are small and specific.**

## Item 1 — the word `kshetra` collides with "struct field"

**Claude found it in the source:**

| Line | Existing text |
|---|---|
| `src/sutram_compiler.asm:313` | **`Sutram Error [E_UNKNOWN_FIELD]: agyat kshetra 'w'`** |
| `:317` | **`Sutram Error [E_AMBIGUOUS_FIELD]: kshetra 'x'`** |
| `:827` | **`Sutram Error: rachana kshetra seema atikram`** |

**Three goldens and `tests/r23/test_capabilities.py` pin those texts.**

**So `kshetra` already means "a field of a `rachana`" in three error messages, and would also mean "a memory region".** **That is the same class of error as `kosa`/`kosh`, and it was missed because the dictionary check and the compiler check are different checks.**

**My recommendation: keep `kshetra` for the memory region — a struct field is "a place within a structure" and the region is the better fit for the word — and reword the three field diagnostics in a later round.**

**But that needs a replacement word, checked against the compiler this time, not only against a dictionary.**

## Item 2 — `nivartanam` inside a region: Gemini bans, ChatGPT allows

**Gemini's reasons for banning:**
1. **It removes the return-escape path in two lines of compiler code.**
2. **`nivartanam helper(buf)` reads `buf` DURING evaluation, so the cursor cannot be rewound until after the expression is computed — but the expression may allocate.**
3. **It breaks zero existing programs, because the block is new.**

**ChatGPT's position: allow it, at two MOV instructions, restoring "before the existing jump/return".**

**The question that decides it, and it is one question: does "restore before the jump/return" actually handle Gemini's evaluation-order case?** **If the return expression itself allocates, restoring before the return is too early; restoring after the expression is too late to be simple.** **Answer that specifically.**

## Item 3 — the check: Gemini's documented contract vs ChatGPT's "unknown is rejection"

**Both agree the mechanism is value-level (`origin_depth` and `taint_depth`).** **They disagree on how much to refuse.**

**Converge on one rule set, and state for each rule what it catches and what it lets through.** **And price it — instructions and compiler lines — and confirm it emits ZERO extra bytes for programs that do not use a block, because the guard must stay at 0 DIFFER.**

## Your lens
**You found the collision, so you own item 1's mechanics.**
**Price both options: (a) reword the three field diagnostics — which goldens, which tests, how many files change, and can it be done without breaking any program? (b) rename the memory region instead.**
**And: is there a THIRD word already in the compiler that means "field" and could take over cleanly?** **Search the source for what the field diagnostics could become.**
**Then: price the whole of steps 3 and 4 together — total lines, total locations, and which existing code paths get touched. That is the number the owner needs before saying go.**
