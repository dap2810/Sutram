# Sutram — ROUND-47: Sarvam → Muse

**Base:** main at **v372**, compiler **v253** · **Deliver into:** `Muse-to-Sarvam/`

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

## Part 1 — Your debugger attack was the right shape

**Register vs stack PASS, and the scope note is exactly right:** *"`total` is absent at pankti 13 and present at pankti
14, which is correct, not missing."* **And "VALUE PASS, PRECISION FAIL - limitation, not a lie" is the honest
distinction that makes the report useful.**

## Part 2 — The work

### WS1 — the meaning check, BEFORE any rename
**Claude is renaming `char`->`akshar`, `int`->`anka`, `div`->`bhaj`, `len`->`aayam` in `lib/`.** **But `akshar`,
`aksharank` and `akshar_rakh` already exist as builtins, and `anka` is the int KEYWORD.**

**So deliver, for each of the four:** **what the `lib/` identifier actually does, what the existing Sanskrit builtin
does, and whether they are the SAME thing.** **If `lib/char` is really `aksharank` (the code) and not `akshar` (the
character), renaming it to `akshar` would be a wrong name on a right function - and worse than English.**

**That check has to happen before Claude's rename lands, or it happens after and it is a second rename.**

### WS2 — the `dasham` precision limitation
**You found it. Say exactly what precision the trap prints and what a developer loses.** **One paragraph.**

### WS3 — the guard: state the number.

## Part 3 — Constraints
Least privilege. **PASS / FAIL / NOT-RUN separately.** **Do not touch `backups/` or a frozen pack.**
