# R43-00 — Hand-back to Sarvam: the first lines

- **Commit on `main`:** this hand-back's commit. It carries the tests, the checker, the gates and the one document
  line. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v249) - sampurna sutra`, UNCHANGED.** No lexer fix was needed.
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=223`, FAIL=0.** Linux x86-64 (cloud).
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud, with a display (Xvfb): 41 PASS / 0 FAIL / 1 NOT-RUN.**
  - The NOT-RUN is Windows execution.
  - **The 2 new gates are "keyword boundary" and "keyword prefix".** Both PASS.
- **The guard:**
  - **Committed v249 against a rebuild from this tree:** 573 programs, **480 byte-identical, 93 refused
    identically, 0 DIFFER.**
  - **v248 against this tree:** 475 / 93, and **5 DIFFER: exactly the 5 alias tests**, as in R42.
- **`fuzz_robust`:** **CRASH or HANG: 0.** That is 171 fixed cases and 2000 mutations (`evidence-r43/fuzz_robust.txt`).

## WS1 — the two-minute test: IT WORKS, so there is nothing to fix

**A `prakriya` named `vartani_pratilip`, called as `vartani_pratilip(8)`, compiles and returns 9.** Your v361 test
used a `vitti` with that name. This one is the `prakriya` the round asked for.

**Then I ran the Devanagari direction, which v361 named as the open case.**

- Every keyword in `lang/sanskrit.lang` was followed by every kind of word character.
- The Latin keywords: 52 keywords × letter / `_` / digit / a Devanagari letter.
- The Devanagari keywords, under `--lang sanskrit`: 58 keywords × a letter, letter+virama, anusvara, a vowel sign,
  a Latin letter, `_`, a Devanagari digit and an ASCII digit.

**All 672 are ordinary names.** That includes the two directions the round singled out:

- **`प्रतियातिक`:** a Devanagari keyword, then a Devanagari letter.
- **`प्रतियातिX`:** a Devanagari keyword, then a Latin letter.

**One candidate was refused at first: `शब्दम्`.** It is not a prefix case. **`शब्दम्` is itself a keyword**, a
builtin alias in the table (`शब्दम् shabda`), so the compiler was right. The test skips any candidate that is
itself a keyword.

**Why it is correct, read from the source** (`src/sutram_compiler.asm`, the identifier scan, `.store_id` →
`.id_done` → `lookup_keyword`):

- **The lexer collects the whole word first.** That means ASCII letters, digits, `_`, and every 3-byte UTF-8
  scalar whose first byte is `0xE0` (U+0800–U+0FFF, the Indic blocks, Devanagari among them).
- A combining vowel sign, anusvara or virama is such a scalar, so it is part of the word. **That makes the scan
  character-aware, not byte-naive.**
- **Only then does it compare the complete word with the keyword table, with a full-string compare.**
- **A keyword cannot match a prefix, because there is no prefix compare anywhere.**

**So WS2 and WS3's lexer change were not made.** The round said: if it already works, say so and stop. That
applies to the compiler.

**The words the project avoided are available:**

- `vartani_pratilip` instead of `anuk`.
- The library already ships 19 such names: `mala_pratilip`, `purna_yoga`, `chakravala`, `satya_tak_ank` and the
  rest (see WS4).

## What I did add, so the answer stays true

### The permanent test: `tests/r43/test_keyword_boundary.py`

**681 checks, 0 failed.** It is the gate "keyword boundary".

- It is **generated from `lang/sanskrit.lang`**, so a keyword added later is tested automatically.
- **9 controls make it able to fail.** Each keyword itself, Latin and Devanagari, must be **refused** as a name.
  Without these, a lexer that recognised no keyword at all would pass.
- **It writes no `.sm` into the tree.** That keeps the guard's program set unchanged.

### WS4: `tools/check_keyword_prefix.py`

It is the gate "keyword prefix", **as a report**, in the shape of `check_doc_signatures.py`.

- **What it lists:** every name declared in `lib/*.smlib` that begins with a keyword: **19 of 542.**
- **It FAILs only if a declared name IS a keyword**, which could not compile. That count is 0.

**`PROJECT-MASTER.md`:** the gate line now reads 41 / 0 / 1 with a display. Without one, the X11 gate is also
NOT-RUN. **I did not measure a no-display run this round, so no no-display number is quoted.** `doc_counts_gate`:
every document agrees.

## One thing outside Sanskrit, reported and not fixed

**Only UTF-8 scalars that start with `0xE0` count as word characters.** Those are U+0800–U+0FFF, which covers every
Indic script the packs use.

- **A 2-byte letter such as Latin `é` is not a word character.** Measured: `vitti pratié = 1` is refused with a
  grammar error (`vyakaranam`), not compiled as a name.
- **No pack uses such letters.** The frozen packs are all Indic, so this is a note, not a defect.

## What I did NOT do

- **No compiler change.** It was not needed.
- **No `.lang` change.** The non-Sanskrit packs are unchanged.
- **`docs/reports/LEXER-BOUNDARY-TEST.md` is yours.** I left it, though its open item 2 (the Devanagari direction) is now
  answered.
- **The `pankti` question (34 occurrences, "line" against the retired array sense): NOT RUN this round.** It is
  separate from the lexer.
- **Windows: NOT RUN for R43.** The compiler did not change, so R42's Windows run still describes this binary.
- **`backups/` is untouched.**
