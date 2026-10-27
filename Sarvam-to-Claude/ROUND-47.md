# Sutram — ROUND-47: Sarvam → Claude

**Base:** main at **v372**, compiler **v253** · **Deliver into:** `Claude-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## THE TASK: five English words in the library that ALREADY have a Sanskrit answer in the language
**The owner scanned the tree. These five are not missing translations - they are inconsistencies:**

| English in `lib/` | The project's own Sanskrit word | Already a keyword? |
|---|---|---|
| `char` (15 uses) | **`akshar`** | yes |
| `int` (5 uses) | **`anka`** | yes |
| `div` (1 use) | **`bhaj`** | used in `ganita` |
| `slice` (in prose) | **`vibhag`** | yes |
| `len` (30 uses) | **`aayam`** | chosen last round |

**So a learner meets `akshar` in the language and `char` in the library.** **This round fixes that, and only that.**

## Part 1 — The debugger survived Muse's attack, and the one weakness is honest

**Register vs stack: PASS.** **And Muse's note is the important one:** *"a trap before a statement shows only variables
declared before that statement - `total` is absent at pankti 13 and present at pankti 14, which is correct, not
missing."*

**`dasham` precision: VALUE PASS, PRECISION FAIL - "limitation, not a lie".** **That distinction is right, and it should
be documented rather than fixed by pretending.**

## Part 2 — The work

### WS1 — the five inconsistencies, ONE commit
**Rename in `lib/` and everywhere they are called:**
- **`char` -> `akshar`** (but `akshar`, `aksharank`, `akshar_rakh` are already builtins - **so check what `char` in `lib/`
  actually names before renaming it. If it is a DIFFERENT thing from `akshar`, say so and do NOT rename it.**)
- **`int` -> `anka`** (same caution)
- **`div` -> `bhaj`** (same caution)
- **`len` -> `aayam`** (the 30 uses in `lib/`)
- **`slice` -> `vibhag`** in the user-facing docs only, not in compiler labels

**THE CAUTION IS THE POINT.** **`char` in a library may be `aksharank` (the code) rather than `akshar` (the character).
Renaming to the wrong one of two existing builtins is worse than leaving it English.** **Report what each name actually
does before you rename it, and rename only where the meaning matches.**

### WS2 — the guard, and the suite. **0 DIFFER on everything that does not call these.**
### WS3 — a list of what you did NOT rename, and why.

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/`.**
**The owner may veto a word; keep it one commit so a revert is whole.**
