# Sutram — ROUND-186: item 3, the file example. And two bugs `grahan` has carried all along.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Item 1 is closed — v321 refuses the unknown character, and an independent byte-level audit confirms the class is complete.**
**Item 2 is closed — v323's `vartani_grahan` reads a line, `nivesha_anta` ends the loop, 0 DIFFER.**
**This is item 3, and it is small.**

---

## 1. And first, two bugs your R184 found, which are not small

> *"`grahan` loses a minus sign and an unfinished last line."*

**`grahan()` reads a number.** **If it loses a minus sign, then `-5` typed by a student reads as `5`.** **That is a silent wrong answer in the one function every interactive program uses.**

**And an unfinished last line — a file whose final line has no newline — is mishandled.**

**So before the file example, fix `grahan`.**

1. **Confirm both bugs with a program and a known input.** **`-5` must print `-5` after the fix.**
2. **Fix them.**
3. **And check the sibling: does `vartani_grahan` have the same unfinished-last-line problem?** **It was written after, but it may share the read path.**
4. **And: what does `grahan` do with `+5`, with `5abc`, with an empty line, and with a number too large for a `vitti`?** **Report each.** **A parser that silently accepts garbage is the same defect class as the lexer.**

## WS1 - and then the file example
**The language can read a file. No example shows it, and the reference mislabels it.**

**So: read the tree and find what actually reads a file.** **Muse's earlier note said the reference mislabels it — find the function, find the sentence, and say what is wrong.**

**Then:**

1. **One example in `examples/` that reads a file and sums the numbers in it.** **Ten lines. The kind of program a student would actually write.**
2. **And a second that counts the lines in a file** — **because counting is the first thing anyone does with a file, and it needs the line reader rather than the number parser.**
3. **A paragraph in the reference, under the correct name.**
4. **A paragraph in the book, in whichever chapter teaches files.**

## WS2 - and the honest question about the reference
**A mislabelled function is worse than a missing one, because a student finds the name, uses it, and gets something else.**

**So: how many other functions in the reference are mislabelled or misdescribed?** **Not a full audit — name the ones you notice while looking for the file function, and say whether the reference's file section needs rewriting rather than a paragraph.**

## WS3 - and the tests
**Two new examples need goldens.**

**And the file-reading tests need a fixture file in the tree, with known contents, so the golden is reproducible.**

**Report the guard: adding an example and a paragraph changes no compiled program, so it should read 0 DIFFER against v323.**

## WS4 - and nothing else
**No memory work. No Windows. No benchmark work — R185 settled that.**

**And do not touch `vartani_grahan`'s interface.** **It works and it is tested.**
