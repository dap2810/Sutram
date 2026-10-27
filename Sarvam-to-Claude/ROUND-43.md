# Sutram — ROUND-43: Sarvam → Claude

**Base:** main at **v359**, compiler **v249** · **Deliver into:** `Claude-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## THE TASK: the lexer, so a Sanskrit word is never blocked by a keyword prefix
**`prati` is the `return` keyword. A library function called `vartani_pratilip` (string-copy) must be legal.**
**Today we do not know whether it is** - and the project has been choosing worse words to avoid the question
(`anuk` instead of `pratilip`). **The owner wants this solved permanently.**

## Part 1 — Your job: TEST FIRST, then fix if needed

### WS1 — THE TWO-MINUTE TEST, BEFORE ANY CHANGE
**Write a program that calls a `prakriya` named `vartani_pratilip` and compile it.** **Report whether it works.**
**If it already works, the lexer is fine and there is nothing to fix** - say so and stop. **That is a complete answer.**

### WS2 — IF IT DOES NOT: character-aware keyword boundaries
**A keyword must match only when the NEXT CHARACTER is not a letter, digit or underscore.**

**THE RISK IS UTF-8, NOT ASCII.** **The keyword table has Devanagari rows.** **A naive check like "next byte not in
[a-z0-9_]" would see the first byte of a Devanagari letter, decide it is not a word character, and match `prati`
inside `प्रतिलिपि`.** **That would be worse than the bug we are fixing.**

**So:**
- **the check must be character-aware** - a multi-byte UTF-8 sequence counts as a letter
- **and it needs its own test:** a keyword immediately followed by a Devanagari letter must NOT match
- **and the reverse:** a Devanagari keyword immediately followed by a Latin letter must NOT match

### WS3 — THE EVIDENCE IT IS SAFE
**This is the lexer - the most-used path in the compiler.** **So:**
- **the guard: 0 differ**, plus the 5 alias tests still differing
- **the suite, the crash corpus, and `fuzz_robust`** - not only the guard, because the guard proves compiled programs
  did not change and does not prove the lexer is correct on new input
- **and a new test file for the boundary cases**

### WS4 — `tools/check_keyword_prefix.py`
**For every keyword K and every identifier I in `lib/`: if I starts with K and I != K, flag it.** **In the shape of
`check_doc_signatures.py`.** **Add it to `gates.sh`.**

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/`.**
**If it cannot be done safely, STOP and say why.**
