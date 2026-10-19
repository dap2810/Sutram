# R7-02 — WS2 (Step 2): the diagnostics language. The numbers for the owner's decision

**Nothing changed.** The counts below come from the branch tree (v180 + R7), on Linux. The commands are at
the end.

## What the decision touches

| Thing | Count | Language today |
|---|---|---|
| Compiler message strings, user-visible and single-language | **90** (66 of them `Sutram Error …`) | Sanskrit, romanised |
| Compiler parse messages per pack (5 messages × 10 packs) | 50 | already the pack's own language and script |
| IDE status line, output messages, language names | **22** (8 + 10 + 4) | Sanskrit |
| IDE menus, buttons, dialogs, installer | — | English (R5) |
| Goldens that print a compiler message (`tests/expect/*.out`) | **41** (35 are `compile_fail`) | follow the compiler |
| R70 corpus cases matching exact text | **4** | follow the compiler |
| Python tools and tests that match message text | **16 files** | follow the compiler |
| Docs and books quoting a message (outside the partner folders) | **18 files, about 255 lines** (6 books, the spec, 9 design notes) | follow the compiler |
| `tools/test_windows_gui.py` checks on status words | 3 | Sanskrit |

## The options

| | Option | What a user of the English IDE sees | Cost, counted | Fits "an error message in their own language" (`ROADMAP-TO-V1.0.md`, What v1.0 is) |
|---|---|---|---|---|
| **A** | Keep it as it is | English menus; Sanskrit status line and errors | 0 | partly: Sanskrit for everyone |
| **B** | Everything English | English throughout | 90 + 22 strings; **41 goldens, 4 R70 cases, 16 tool files, 18 docs (~255 lines)** re-recorded or re-quoted; locks re-pinned. About one round, mechanical. | **no**: it drops the aim |
| **C** | Both on every error (English line plus Sanskrit `Sanket:`) | everything twice | B's cost, plus every golden grows | yes, but noisy for a learner |
| **D** | **Selectable, default unchanged:** `--sandesh en` (or an env variable). The English IDE passes it; its 22 strings follow. | English end to end | One two-column message table and one lookup per message site (90 sites). **Default goldens, R70 and docs unchanged.** Add English goldens for a sample (about 10). IDE: 22 strings plus the flag. About 1–2 rounds. | yes, for English and Sanskrit |
| **E** | **Follow the pack for every message:** `--lang hindi` gives Hindi errors, as 5 parse messages already do | the user's own language and script | D's mechanism, **plus 90 messages × 10 packs = 900 translations.** Needs translators; I can draft, not vouch. | **yes, literally** |

**E is D plus translations.** The table D builds is the table E fills, so doing D first loses nothing.

## Recommendation

**D now, E as translations arrive.**

- D makes the English IDE consistent without taking Sanskrit away from anyone.
- D leaves the 41 goldens, the R70 corpus and the 18 docs alone.
- D is the mechanism E needs anyway.
- E is the roadmap's own definition of v1.0 ("read an error message in their own language"), but its cost
  is translation, not code.

**The one choice to make:** A, B, C, D or E. **And:** should the IDE's 22 strings follow the same answer?
I recommend yes, or the IDE stays mixed.

## Commands (branch tree)

```
python3 (regex over db strings in src/)                    → 90 user-visible single-language strings
grep -hc 'Sutram Error' src/sutram_compiler.asm src/*.inc   → 66
grep -lE "Sutram Error|Sanket|Chetavani|Bhasha pak" tests/expect/*.out | wc -l   → 41
ls tests/expect/*.compile_fail | wc -l                       → 35
manifest cases with diagnostic.text (tests/negative/r70)     → 4
grep -rlE "Sutram Error|Sanket|vyakaran dosh|agyat" --include=*.py tools tests | wc -l   → 16
grep -rlE "Sutram Error|Sanket:" --include=*.md --include=*.html . (outside the partner folders) → 18 files, 255 lines
```

**Note on the counts.** R6-03 said "about 85 strings / 32 goldens". These are this branch's counts after
R7 added 9 goldens and about 12 strings. The roadmap's "83 strings and 28 goldens" is the R2 count.
