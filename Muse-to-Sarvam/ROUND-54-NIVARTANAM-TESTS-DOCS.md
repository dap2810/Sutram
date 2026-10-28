# Sutram — ROUND-54 (final): finish `nivartanam` in `tests/` and `docs/`

**Base worked on:** `origin/main` at `16fc16ba` (changelog v400, compiler v257). This is the half
R53 deliberately left: R53 migrated `lib/` (677) and `examples/` (814 total), and counted `tests/`
and `docs/` without touching them. **Delivered as patches plus this report, NOT applied to main.**
Apply in order, after the R52 and R53 patches or on their own — the two patches below touch only
`tests/` and `docs/`, so they do not conflict with the R53 lib/examples patches either way.
Verified both ways: on a fresh `HEAD` checkout, and on a fresh `HEAD` + R52 + R53 checkout.

**Two count corrections to the brief, measured on this base, not copied from R53:**
- `tests/` is **316 source occurrences in 101 files, not 389.** The 389 counted `.pyc` bytecode
  (73 occurrences in 6 files: module_graph 17, r23 18, r25 28, r28 5, r29 1, r30 2). Bytecode is
  generated, never edited, and regenerates on the next test run — it is not a migration target.
- `docs/` is **154 occurrences in 22 files, not 146.** The extra 8 are the v400 changelog entries
  added after R53 (CHANGELOG now holds 47, not 39).
- `tests/negative/` is **106 occurrences in 37 files, not 108 files** (101 in r15-original, 2 in
  r70 cases, 3 in the r70 manifest prose). The brief's "108 files" was an occurrence count
  rounded to files; the real file count is 37.

## WS1 — the danger, stated first and measured

**Tests whose EXPECTED OUTPUT contains `prati`: exactly one.**

| Test | Expected output containing `prati` | Decision |
|---|---|---|
| `tests/r25/test_phal.py:85` | `Sutram Error: phal-prakriya: prati siddhi va dosh bhavet` | **KEPT, deliberately.** The compiler still emits exactly this string in v257 (`src/sutram_compiler.asm:381`, `r25_msg_phal_return`). The brief says the error message does not change in this round, and it has not. Changing the expected string to `nivartanam` would make the test fail against the real compiler. This is the only expected-output string in `tests/` that contains `prati`. |

**No golden file contains `prati`:** 0 files under `tests/expect/`, `tests/stdlib/*.out`, or any
`.out`/`.exit` in `tests/` contain the word. That matches R53's finding and is why **no expected
output changed in this round** (see WS4).

**`tests/r53/test_nivartanam.py` (13 occurrences) — checked separately, as the brief requires:**
this is the alias equivalence test itself. It writes three programs in `prati`, mechanically
replaces `\bprati\b` with `nivartanam`, and asserts byte-identical binaries and identical
output; it also asserts `vitti prati = 1` and `vitti nivartanam = 1` are both refused as
keywords. Migrating its programs to `nivartanam` would make it compare `nivartanam` with itself
and lose the alias coverage entirely. **Left whole, 13/13.** It still passes: 9 checks, 0 failed
(see WS4).

## WS2 — migrate `tests/`, carefully

**Rule applied, per occurrence, not per file:** a `prati` that is a return statement in a program
text becomes `nivartanam`; a `prati` that is an alias input, an expected error string, a pinned
fixture byte, a pack-mapping value, or a test-subject keyword stays. Program text includes
`.sm`/`.smlib` files and Python string literals that are Sutram programs.

**Migrated: 180 occurrences in 57 files.**
- `.sm`/`.smlib`: 96 in 47 files — `tests/r29/proj/` (5), `tests/r30/proj/` (4), `tests/r32/`
  (3), `tests/r33/` (1), `tests/r35/` (1), `tests/r44_pending/` (7), `tests/r49_check/` (1),
  `tests/r51_check/` (4), `tests/r55_check/` (14), `tests/r56_check/` (14), `tests/r57_check/`
  (2), `tests/r58_check/` (1), `tests/r65_check/` (1), `tests/sandesh/cases/` (1),
  `tests/stdlib/` (37, including `strconv_overflow` 28).
- Python program strings: 84 in 10 files — `tests/module_graph/` (19), `tests/r23/` (19),
  `tests/r25/` (27 of 28; the 28th is the error string above), `tests/r28/` (5),
  `tests/r29/` (1), `tests/r30/` (2), `tests/r32/` (1), `tests/r34/` (7), `tests/r45/` (1),
  `tests/r46/` (2).
- The `r49_check`/`r51_check` faulty fixtures were migrated too: their `prati 0;` lines become
  `nivartanam 0;` on the same line, so the diagnostic audit's expected error lines (line 2 for
  `faulty_r49`, line 2 for `broken_ns_r51`, etc.) do not move, and the fixtures are still
  faulty in exactly the same way.

**Left alone in `tests/`: 136 occurrences in 45 files, every one with a reason.**

| Files | Occ. | Why left |
|---|---|---|
| `tests/negative/r17/r15-original/` (34 files) | 101 | SHA256-pinned crash corpus inputs (ROUND-21 pin in `tests/negative/r17/SHA256SUMS`). These are fuzzer mutations that must stay byte-identical to remain the corpus; changing them breaks the pin and changes the crash identity. They are invalid programs by design, and under the alias they still reject identically. Crash corpus still passes: 227 cases, 0 failed. |
| `tests/negative/r70/cases/bad_type.sm`, `bad_arity.sm` | 2 | Manifest-pinned fixtures (`tests/negative/r70/manifest.json` holds `file_sha256`/`program_sha256`, and `bad_type` is an `inherited_exact_golden` whose git blob is asserted by `tests/r70/test_negative_corpus.py`). Their diagnostic texts do NOT contain `prati` (bad_type: `kosh tark: tatv prakar bhinn`; bad_arity: empty), so leaving them changes no expected output. Migrating them would require re-pinning the manifest, which is a separate fixture decision, not a rename. r70 tests still pass: 36 tests, OK. |
| `tests/negative/r70/manifest.json` | 3 | Historical repin prose only (the v157 `pratiyati->prati` rename note and the R53 alias note). Not a program, not an expectation. |
| `tests/r25/test_phal.py:85` | 1 | Expected error string, see WS1. Compiler message unchanged. |
| `tests/r53/test_nivartanam.py` | 13 | Alias equivalence test, see WS1. |
| `tests/r43/test_keyword_boundary.py` | 6 | Keyword-boundary test: `prati` is the test subject (a `prakriya` named `pratilekha_kuru` beginning with `prati`, and the keyword itself as a name refused). Migrating its programs would change what the test is about. Still passes: 686 checks, 0 failed. |
| `tests/r50/test_devanagari_default.py` | 3 | Devanagari-form test for `prati` (W2: `prati` has one Devanagari form, प्रति; old spellings are not keywords). Migrating its program to `nivartanam` would lose the `prati`-form coverage. Still passes: 9 checks, 0 failed. |
| `tests/r66/baseline_packs.json`, `tests/r67/baseline_packs.json` | 5 | Pack-mapping snapshots: the VALUE `"prati"` is what other-language words map to in the pack at snapshot time, and the pack still contains `prati` as an alias mapping. Changing the snapshot value would falsify the snapshot. |
| `tests/r66/test_prepare_review.py` | 1 | Comment only: "prati has one Devanagari form, प्रति" — a note about the R50 finding, not code. |
| `tests/gui/test_win_gui_colour_tables.py` | 1 | Comment only, listing old keywords. |

**Code-vs-error-string split, in one line:** 180 code returns migrated, 1 error string kept,
136 kept for the reasons above (101 pinned crash inputs + 2 pinned r70 cases + 3 manifest prose
+ 13 alias test + 6 keyword-subject test + 3 Devanagari-form test + 5 pack snapshots + 2
comments + 1 error string = 136; the 73 `.pyc` occurrences are bytecode, not counted).

## WS3 — migrate `docs/`

**Migrated: 92 occurrences in 16 files** — live references, guides, and book examples where
`prati` was the return keyword in prose or in a code example:
`LANGUAGE-REFERENCE.md` (21), `ERROR-CONVENTION.md` (2), `KOSH-BUILTINS.md` (1),
`LAGHU-EXAMPLE.md` (1), `LIBRARY-BOUNDARY.md` (1), `R56-MODULE-GLOBALS.md` (1),
`SPECIFICATION.md` (2 of 3), `_newchapter_en.html` (1), `sutram-book-english.html` (6),
`sutram-book-gujarati.html` (10), `sutram-book-hindi.html` (13), `sutram-book-sanskrit.html`
(6), `sutram-book-tamil.html` (11), `sutram-book-telugu.html` (13),
`sutram-keyword-words.html` (1), `sutram-vocabulary.html` (2).
In the books, both the code examples and the tooltips were migrated (e.g. "संस्कृत: prati ·
return" → "संस्कृत: nivartanam · return"); the other-language pack words in the same tables
(Gujarati પાછા, Hindi वापस, etc.) are concept translations, not the Latin keyword, and stay.

**Three places where a blind rename would have been wrong, handled by hand:**
- `LANGUAGE-REFERENCE.md` pack table row: the Latin `prati` became `nivartanam`, and its
  Sanskrit column changed from प्रतियाति to निवर्तनम्. The old row was already stale (R43:
  `prati`'s Devanagari is प्रति, not प्रतियाति); migrating only the Latin would have left
  `nivartanam | प्रतियाति`, which is false in both scripts.
- `sutram-vocabulary.html` row 83: Latin `prati` → `nivartanam` and Devanagari प्रति →
  निवर्तनम् in the same row, for the same reason.
- `SPECIFICATION.md:227` kept as `प॰ -> prati`: that line records a pack alias entry for the
  abbreviation प॰, which R50 removed and which never mapped to `nivartanam`. Changing it
  would invent a pack entry that never existed.
- `LANGUAGE-REFERENCE.md:249` error example migrated consistently: the program's `prati x`
  became `nivartanam x`, and the quoted error word `shabd 'prati'` became
  `shabd 'nivartanam'`, so the example still matches its own program.

**KEEP_HISTORICAL — 62 occurrences in 7 files, deliberately left, so the decision is visible
and not a miss:**

| File | Occ. | Why historical |
|---|---|---|
| `docs/CHANGELOG.md` | 47 | Dated record, including old decisions ("`prati` stays", v396 `nivartan`, v399/v400 migration notes). Rewriting it would falsify the record of how the rename happened. |
| `docs/LEXER-BOUNDARY-TEST.md` | 4 | Document's subject is `prati`'s prefix behaviour (`prati_test`, `pratiX`, `vartani_pratilip`). Migrating to `nivartanam` would break its argument, since `vartani_pratilip` does not begin with `nivartanam`. |
| `docs/VOCABULARY-TABLE.md` | 5 | Vocabulary review table with KEEP/CHANGE decisions for the old word, including the "Fix: `prati` in both" row. A proposal record, not a live reference. |
| `docs/VOCABULARY-DERIVATION.md` | 2 | Derivation note: "`prati` is `return`, so `vartani_pratilip` looked like it might not lex" — the reasoning depends on `prati` being the prefix. |
| `docs/VOCABULARY-SHORT.md` | 2 | Short-word proposal table: `prati` listed as "already short" (5 letters). `nivartanam` (9 letters) is not short, so the table needs separate review, not a blind rename. |
| `docs/WHATS-LEFT.md` | 1 | Old decision record F4: "`prati` stays — decided". Now superseded by R53/R54, but the supersession belongs in a new changelog entry, not by editing the old decision line. |
| `docs/SPECIFICATION.md:227` | 1 | Pack alias record, see above. |

## WS4 — deliver as a patch, and prove it

**Patches:**
- `ROUND-54-tests.patch` (51,023 bytes): 57 test files, 180 occurrences.
- `ROUND-54-docs.patch` (62,721 bytes): 16 doc files, 92 occurrences.
- Both apply cleanly in order on a fresh `HEAD` checkout and reproduce this round's tree
  byte-for-byte (diff empty except generated `__pycache__`). They also apply cleanly on top of
  R52 + R53, in order, with no conflicts — the file sets do not overlap.

**Suite: PASS=225, NO-EXPECTATION=4 (215, 216, 217, 219), 0 FAIL — unchanged.**
**Tests whose expected output changed: none.** No golden contained `prati`, and the one
expected error string containing `prati` was kept, so no `.out`, `.exit`, or assertion string
was altered. The only `.py` assertion text that changed is program text and test labels in the
10 migrated test files, whose expected outputs are unchanged.

**Other verification, all on the migrated tree:**
- Proofs: 226/226 (on this base, where lib is still `prati` — the cap issue does not arise
  here). On R52+R53+R54 combined, proofs are 225/226 with the same single r11 cap failure
  from R53; R54 adds nothing to it, because no R54 file is imported by that proof.
- Gates that touch `prati`: r53 nivartanam 9 checks 0 failed; r43 keyword boundary 686 checks
  0 failed; r50 Devanagari default 9 checks 0 failed; module graph unittest 18 tests OK.
- Migrated tests: r23 23/0, r25 21/0, r28 208/0, r29 260+152/0, r30 8/0, r32 50/0, r45 8/0,
  r46 20/0; r34 Windows is NOT-RUN on Linux, as before.
- Crash corpus: 227 cases, 0 failed; r70 unittest: 36 tests OK (pinned fixtures untouched).
- **Pre-existing failure, NOT caused by this round, NOT fixed here:** `tests/r66/test_prepare_review.py`
  fails on clean `HEAD` too (58 pack rows vs expected 57 — the v257 pack gained a row when
  `nivartanam` was added, and the r66 expectation was not updated). It fails identically with
  and without the R54 patches. Fixing a pack-count expectation is a separate round, not a
  rename, so I left it failing and visible rather than quietly adjusting the expectation.

**NOT RUN:** Windows/WSL execution (owner's test, as always).
