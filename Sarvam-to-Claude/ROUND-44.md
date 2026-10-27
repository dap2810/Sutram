# Sutram — ROUND-44: Sarvam → Claude

**Base:** main at **v362**, compiler **v249** · **Deliver into:** `Claude-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — The lexer is proven, so the vocabulary is free

**Three independent measurements agree: a keyword prefix does not block an identifier.** **672 boundary cases, both
scripts, all pass.** **Your R43 added the two gates and `fuzz_robust` 0 crash.**

**So the project can stop choosing worse words.** **The owner asked for Sanskrit for `len`, `cmp`, `cpy` - these are
the last three English words in the builtin names.**

## Part 2 — The work: rename three builtins

### WS1 — the rename, with the guard
| Now | Becomes | Sanskrit |
|---|---|---|
| `vartani_len` | **`vartani_aayam`** | आयाम, extent/length |
| `vartani_cmp` | **`vartani_tul`** | तुल्, to weigh/compare (तुलना) |
| `vartani_cp` | **`vartani_pratilip`** | प्रतिलिपि, a copy |

**Do it as ONE commit.** **Update `lib/`, the examples that call them, the tests, and `lang/*.lang` for the Devanagari
forms.** **The guard: 0 differ on everything that does not call these three.**

### WS2 — and this is the part that matters
**`vartani_pratilip` is the exact name the lexer question was about.** **So: after the rename, the compiler must
compile a program calling `vartani_pratilip` - and that program must be one of the new test files.** **That closes the
loop between the lexer proof and the vocabulary.**

### WS3 — the guard, and state what changed
**Every program that calls one of the three will compile to different bytes - because the name changed, not the code.**
**Say how many, and confirm the emitted instructions are identical apart from the symbol.**

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/`.**
**The owner may veto a word; if he does, the rename is reverted, so keep it one commit.**
