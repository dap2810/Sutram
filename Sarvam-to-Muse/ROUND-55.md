# Sutram — ROUND-55: the last English in the examples, and it is the biggest visible gap

**Base:** main at **v404**, compiler **v258** · **Deliver into:** `Muse-to-Sarvam/`

**Read first:** `docs/WHATS-LEFT.md`, `docs/vocabulary/VOCABULARY-TABLE.md`.

## Why this is the last vocabulary round
**The library is about 90% Sanskrit. The examples were 44%.** **Forty-four function names were renamed and proven.**
**`nivartanam` is now the keyword everywhere.**

**What is left is the variables.** **`count`, `sum`, `total`, `len`, `arr`, `max`, `min`, `tmp`, `msg`, `color`, `score` - the words a
beginner reads first, in the file they read first.**

**Count them, then rename them.** **This is the last place where a new programmer sees English.**

## WS1 — count, and tell me the real number
**I have been saying "about 140" and I do not trust that number - I got it from a grep I did not re-check.**
**Count every English-named variable in `examples/*.sm`.** **Word-boundary, and list the distinct names with their counts, most
frequent first.**

**If the number is 40 or 400, say so.** **I want the real figure, not mine.**

## WS2 — propose the Sanskrit, but do not apply it
**For each distinct name, the Sanskrit word.** **Rules:**
- **A complete word or compound, never a fragment** - `purna`, not `purn`.
- **The project's existing words first.** **If `suchi` already means list, a variable holding a list is `suchi`.**
- **Short.** **A variable is typed many times.**
- **No collision with a keyword, a builtin, or a library function.**

**Deliver as a TSV: `english | count | files | proposed | collides | notes`.**

**Do NOT change any file this round.** **The owner reviews the table first - that is how the function renames went, and the two
that went wrong were the two I applied before asking.**

## WS3 — and one thing I need you to check
**`examples/43_nested_likha.sm` uses `likha("x = ", x)`, which ChatGPT found when I said no example did.** **Are there other
examples already using the short print form that I claimed were not?** **Count them.** **If the migration you did in R52 left
any three-statement triple that could be one line, list it.**

## Return
`ROUND-55-ENGLISH-VARIABLES.md` with the counts, the TSV, and the WS3 answer. **No file changes.**
