# Sutram — ROUND-118: Sarvam → ChatGPT

**Base:** main at **v359**, compiler **v249** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## THE TASK: the lexer, so a Sanskrit word is never blocked by a keyword prefix
**`prati` is the `return` keyword. A library function called `vartani_pratilip` (string-copy) must be legal.**
**Today we do not know whether it is** - and the project has been choosing worse words to avoid the question
(`anuk` instead of `pratilip`). **The owner wants this solved permanently.**

## Part 1 — Your job: the SPEC and the test cases, not the code

**Claude implements, Muse tests the baseline, and you define what "correct" means so both are measured against the
same rule.**

### WS1 — THE BOUNDARY RULE, PRECISELY
**State the rule in a form an implementer can code and a tester can check:**
- **what counts as a "word character"** - letters, digits, underscore - **and how that is decided for multi-byte
  UTF-8**
- **what happens at end-of-file, at whitespace, at an operator, at a comment start**
- **what happens for a Devanagari keyword followed by a Devanagari letter**
- **and the case that worries me most:** **a Devanagari keyword followed by a Latin letter, and a Latin keyword
  followed by a Devanagari letter**

**Say plainly if any of these cannot be decided from the source without running it.**

### WS2 — THE TEST CASES, as a TSV I can hand to Claude
**Every boundary case, as `input line` / `expected` / `why`.** **Include the five questions I gave Muse, plus the
UTF-8 cases.** **Enough that a fix passing them is genuinely fixed.**

### WS3 — the sixth class, if your R117 found one
**You answered this in R117-WS1. Restate the verdict in one paragraph if it changed.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source outside your own folder.** **Do not touch `backups/`.**
