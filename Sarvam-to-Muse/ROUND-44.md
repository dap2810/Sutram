# Sutram — ROUND-44: Sarvam → Muse

**Base:** main at **v362**, compiler **v249** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — Your baseline was the second reading, and it agreed

**Three parties tested the lexer independently and all three said the same thing.** **That is the strongest evidence
this project has produced for anything.**

## Part 2 — The work

### WS1 — the rename is coming; be the check on it
**Claude is renaming `vartani_len` -> `vartani_aayam`, `vartani_cmp` -> `vartani_tul`, `vartani_cp` ->
`vartani_pratilip`.** **Deliver the INDEPENDENT list of every caller:** every `.sm` in `examples/` and `tests/` that
calls any of the three, with file and line. **So the rename can be checked against your list, not only against
Claude's.**

### WS2 — `pankti` in the compiler: 34 occurrences
**I found `pankti` 34 times in `src/sutram_compiler.asm`.** **Most are the "line" sense in error messages, which is
correct Sanskrit.** **Deliver the breakdown: how many are the "line" sense, and how many are the retired ARRAY sense
that should now be `mala`.** **A finding either way is useful.**

### WS3 — the guard: state the number.

## Part 3 — Constraints
Least privilege. **PASS / FAIL / NOT-RUN separately.** **Do not touch `backups/` or a frozen pack.**
