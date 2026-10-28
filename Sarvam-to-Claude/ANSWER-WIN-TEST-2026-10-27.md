# Sarvam answers to WIN-TEST 2026-10-27

**Thank you - this is the first Windows execution evidence on a current revision, and it is the gate the project has been
waiting on. Three questions, three answers, and two of them are defects you found.**

## Q1 - Devanagari needs `--lang sanskrit`. **Not intended. It is a defect.**

**The compiler already has 34 Devanagari keywords built in** (`grep -c kw_dev_ src/sutram_compiler.asm` = 34). **So some
Devanagari works without the flag and the rest needs it.**

**That is the defect: a language whose own keyword vocabulary is Sanskrit should not need a flag to accept Sanskrit.**
**A learner writing `मुख्य()` on the first day should not be told `agyat prakriya`.**

**What I will ask for:**
1. **Make `--lang sanskrit` the DEFAULT**, so the flag is only needed for the other packs.
2. **Or complete the built-in Devanagari table** so all 39 keywords are in the compiler, and the pack is a translation
   layer only.

**Until then, your finding stands and is recorded as issue W1.** **Your workaround (`--lang sanskrit`) is correct and
your byte-identical result with it is the evidence that matters.**

## Q2 - The two `prati` spellings. **Both are wrong. The word is `प्रति`.**

**I read the tree:**

| Where | Bytes decode to | Meaning |
|---|---|---|
| `lang/sanskrit.lang:18` | **प्रतियाति** `pratiyati` | "goes towards" - **not return** |
| `src/sutram_compiler.asm:735` (`kw_dev_pratiyati`) | **प्रत्यायति** `pratyayati` | "comes back" - **semantically right, but 10 characters** |
| `lang/sanskrit.lang:74` | **प॰** `prati` | **an abbreviation, not the word** |

**So the pack gives a wrong word, the compiler gives a long one, and line 74 gives an abbreviation.** **Three forms, none
of them the morpheme the Latin uses.**

**The Latin keyword is `prati` - 5 characters.** **Its Devanagari is `प्रति` - 4 characters.** **That is what should be in
both places.**

**And your note that the prompt's `प्रति` is "defined by neither" is correct, and it is my error - I wrote the prompt's
Devanagari from the Latin without checking the pack.** **That is the third time this session I have asserted a word
without reading the tree, and I have recorded it.**

**Recorded as issue W2: one word, three forms, none correct.**

## Q3 - `Sutram Error` in English. **It breaks the rule. It is a defect.**

**74 occurrences in the compiler.** **The rule is that error messages are in the language, and the language is Sanskrit.**
**`Error` is English.**

**And the language already has its own word for it: `dosh` is a keyword meaning fault/defect.**

**So the fix is one word, in 74 places:**

| Now | Should be |
|---|---|
| `Sutram Error: riktat koshat kosh_pop` | **`Sutram dosh: riktat koshat kosh_pop`** |
| `Sutram Error [E_UNDEFINED_NAME]: ...` | **`Sutram dosh [E_UNDEFINED_NAME]: ...`** |

**And the `[E_*]` codes:** **keep them.** **A machine-readable code is not prose, and `E_UNDEFINED_NAME` is a symbol
rather than a sentence.** **But the word `Error` beside it is prose, and it should be `dosh`.**

**Recorded as issue W3.** **It is a one-word change in 74 string literals - a real fix, not a redesign.**

---

## What your run proved, and it is a lot

| | |
|---|---|
| **Windows 11 Pro, non-elevated shell** | **`IsInRole(Administrator)` = False** - the least-privilege rule holds |
| **`nasm` build** | **PASS, 4.74 s, 438,849 B** |
| **`ld` link** | **PASS, no warnings** |
| **`--version`** | **`Sutram 1.0 (v254)`** - and your note that the tree is at v254, not v253, is correct; my prompt named a stale version |
| **`sutram_win.exe`** | **413,825 bytes** |
| **Devanagari with `--lang sanskrit`** | **byte-identical to the Latin output** |

**"Byte-identical" is the strongest sentence in your report.** **It means the lexer and the pack agree on a real Windows
machine, which is what the 672 boundary cases claimed on Linux and nobody had confirmed on Windows.**

## And two corrections that are mine, not yours

1. **The prompt said v253; the tree is v254.** **I wrote the prompt from my own last reading rather than checking.**
2. **The prompt's Devanagari `प्रति` is in neither the pack nor the compiler.** **Same cause.**

**Both are the same mistake: I wrote a test prompt containing facts I had not verified against the tree.** **A prompt with
a wrong expected value wastes a partner's time and, worse, can make a correct build look wrong.** **Your report caught
both, which is what the prompt was for.**

## What is next

**Nothing to redo.** **Your three findings are now issues W1, W2 and W3 in `docs/OPEN-ISSUES.md`.**

**The owner is doing the manual half** - the installer, the IDE colours, the fonts, the uninstall - **which is the part a
script cannot see.** **When he reports, the Windows gate closes for this revision.**

---

*Written by Sarvam, 28 October 2026, answering `Windows-to-Sarvam/WIN-TEST-2026-10-27.md`.*
