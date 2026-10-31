# R88 + R89 — `docs/` in four folders, the changelog split, the two goldens explained, the README points at the alias

- **Commit on `main`:** this round's one commit (parent `975a499`) — the move with `git mv`, the split, the link updates, the README line, this hand-back.
- **Compiler: `Sutram 1.0 (v279)` — unchanged**, byte-identical to origin/main's (`sutram_compiler` and `sutram.exe`). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=258`, FAIL=0.** Library proofs **229/229**. Property proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 57 PASS / 0 FAIL / 1 NOT-RUN (Windows execution); guard pages 5/5, suite 258/0.**
- **The guard, origin/main → this tree: Linux ELF and Linux PE — 668 programs, 540 byte-identical, 128 refused identically, 0 DIFFER, 0 new.** **NOT RUN: the Windows compiler under Wine** — its `.exe` is byte-identical to origin/main's.

## R88 WS1 — the move (`evidence-r88/moves.tsv`)

`docs/` went from **75 `.md` files to 20** — exactly your list of 20. **55 moved with `git mv`; git records all 55 as renames**, so `git log --follow` works.

| folder | files | what |
|---|---|---|
| `docs/rounds/` | 27 + the archive | every `R*-*.md` (R50 … R72), and `CHANGELOG-ARCHIVE.md` |
| `docs/reports/` | 17 | measurements and audits: `EDGE-COVERAGE-30`, `FAIL-ALLOC`, `INDIC-COVERAGE`, `KOSH-BUILTINS`, `KOSH-REUSE`, `LAGHU-EXAMPLE`, `LANG-PACK-AUDIT`, `LEXER-BOUNDARY-TEST`, `LIBRARY-ENGLISH-AUDIT`, `LIBRARY-LAYERS`, `MEMORY-COMPOSITION-TEST`, `NEGATIVE-CORPUS`, `PARSER-CLASS-TEST`, `PROPERTY-NET`, `SANSKRIT-AND-AI-BRIGGS-1985`, `SANSKRIT-FOR-LANGUAGE-DESIGN`, `STRING-BYTE-PARITY` |
| `docs/decisions/` | 6 | `MEMORY-DECISION`, `MEMORY-UNIQUE-HYBRID`, `ALIAS-DESIGN`, `MEMORY-DESIGN`, `MEMORY-IMPROVEMENTS`, `MEMORY-MY-IDEA` |
| `docs/vocabulary/` | 5 | `VOCABULARY-TABLE`, `-SHORT`, `-COMPLETE`, `-RULE`, **and `-DERIVATION`** |

**One difference from your local run:** you had `vocabulary/` 4 and `reports/` 18. I put
`VOCABULARY-DERIVATION.md` with the other four. It is a vocabulary document ("The vocabulary: a small core,
and a list"), and anyone looking for the vocabulary should find all of it in one folder. If you want it in
`reports/`, it's one `git mv`.

**`MEMORY-DECISION.md` moved but its content is unchanged.** My standing rule is "don't touch" it. Your round
lists it under `decisions/` by name, so I moved it. Its text is byte-identical (git: R100). **That leaves one
stale path inside it:** "The vocabulary rule is in `docs/VOCABULARY-RULE.md`" now lives at
`docs/vocabulary/VOCABULARY-RULE.md`. It's a one-word edit for you to make, or to let me make.

**The four vocabulary files are not merged into one `VOCABULARY.md`. R88 asked for that; R89 describes a
mechanical move with `vocabulary/` holding 4.** I followed R89. Merging is editorial work, not a move:

- the files are 18.5, 11.8, 10.0 and 6.5 KB;
- they date from v253 to v405;
- they disagree in places (TABLE's status line says the return keyword is `nivartanam`; SHORT and COMPLETE
  were written before that);
- only `VOCABULARY-RULE.md` says it was "agreed by the owner".

A merge means deciding which statement wins in each of those places. That's your call. **I'd make RULE the
authoritative page and fold the other three in as dated appendices.** Say so and I'll do it.

The HTML pages and `ai-handoff-notes/` stay where they were. The round covered the `.md` files only.

## R88 WS2 — the changelog split

`docs/CHANGELOG.md` keeps **the 20 newest entries (37 KB)**, down to v424.

**`docs/rounds/CHANGELOG-ARCHIVE.md` has the other 399 (654 KB), from v423 back to the first.** Each file's first
line says where the other half is. The split counts `## ` headings outside code fences, so a `## ` line inside
a code block can't cut an entry in half. The entries are unchanged apart from the link paths.
`tools/check_version.py` still reads the top `## vNNN`, and the version gate passes.

## R88 WS3 — the links (`evidence-r88/`)

I checked two things, before and after, over every tracked file except `backups/`:

1. **Relative links in `.md` and `.html`: 614 before, 621 after (one is the new README link), broken 3 before, 3 after.** The same 3 both
   times, and they aren't links: `f](x)` in code examples (`R23-01`, `R63-00`, `LANGUAGE-REFERENCE.md`).
2. **Every written `docs/NAME.md` path:** I rewrote 331 mentions in 141 files. That covers `.md`, `.html`,
   `.py`, `.sh`, `.yml` and `.ps1` across `README`-level files, `PROJECT-MASTER.md`, `sarvam/`, `.github/workflows/` (7),
   `tools/` (2, plus `check_layers.py` and `r65_source_gate.py`, which build the path as `"docs", "X.md"`), `tests/`
   (2), and the partner folders' `.md` files.

**Already pointing at nothing before the move (35 pairs, 26 files) — left alone, not invented:**

- `docs/SPEC-STATUS.md` (ChatGPT R106–R110);
- `docs/R66-*.md` (3);
- `docs/R71-KOSH-RECLAMATION.md`, `docs/R73-*.md` (4), `docs/R77-INSTALLER-VERSION-GATE.md`, `docs/R80-INSTALLER-PROVENANCE.md`;
- `docs/NIRMMITA-GUN.md` (Claude R39);
- `docs/R68-INSTALLATION-ROUTES.md` (now in the archive).

These files were removed or never committed. **I don't think they should come back**: each mention is in a
historical round file.

**Deliberately not rewritten** — records of a state at a pinned commit, where a changed path would falsify the record:

- partner `.txt` / `.json` / `.tsv` / `.patch` / `SHA256` files;
- `Claude-to-Sarvam/FILES-R*.txt` and the older evidence `.txt` files;
- `windows/windows-build-integrity.sha256`. This is a maintainer-run manifest, and it was already out of date: its
  hash for `CHANGELOG.md` and `LANGUAGE-REFERENCE.md` didn't match before this round. Rerun
  `tools/update_windows_manifest.py` when you next build the installer.

**Two comments that now point at an old path, not edited because the files are build inputs** (plus the
one line in `MEMORY-DECISION.md`, above):

- `lang/sanskrit.lang:81` (`# Audit: docs/LANG-PACK-AUDIT.md`). The file is pinned in `tools/r69_build.lock.json`
  and feeds the generated `r22_lang_builtin.inc`.
- `lib/patra.smlib:21` (`docs/R52-BUILTIN-FIXES.md`).

Fixing them costs a re-pin. I'll do it with the next compiler build if you want.

**Tests that read docs:** I ran every test file that mentions `docs` (6) on origin/main and on this tree. The
results are identical (`evidence-r88/doc-tests-before-after.txt`). Three of them were already failing on
origin/main and fail the same way here, so the move didn't cause them:

- `test_current_guides`: 1 failure;
- `r69/test_build_and_probe`: 2 failures;
- `r71/test_delivery_tools`: 1 error (stale R71 pins).

None of them is in `gates.sh`. `tools/r69_build_doc_migration.py` now also treats `CHANGELOG-ARCHIVE.md` as a
historical record.

## R89 WS2 — the two goldens, one line each

- **`289_r87_float_print`** pins how `likha` prints a `dasham`: a literal, a variable, a value computed through
  variables, a negative, 10¹³ (ChatGPT's value), 9223372036854.0 (the old drift), e-notation above 2⁶³, and
  `inf` / `-inf` / `nan`. **It would fail on a legitimate change** if the printer's format changed (a different
  e-notation threshold, or shortest-round-trip digits instead of six decimals). It would also fail if float
  division by zero became a refusal, the way integer division by zero is: the program makes `inf` and `nan` with
  `1.0 / z` and `z / z`. Fixing NaN *comparisons* won't touch it, because it doesn't compare.
- **`290_r87_fraction_into_vitti`** pins the refusal of `vitti f = 3.5`, with the message, the Sanket and the column.
  **It would fail on a legitimate change** if the wording changed, or if you decided that `vitti f = 3.5` should
  make `f` a `dasham` (type inference) instead of refusing it.

## R89 WS3 — the README

One paragraph in `README.md`'s Memory section: `vitti a = k` gives a `kosh` a second name, not a copy, and if
`k` grows and moves (always on Windows), `a` keeps the old storage. It links to reference §16, "Two names for
one `kosh`", with the exact anchor.

## What I did not do

- **The vocabulary merge** — above. It needs your decision on which statements win.
- **The two build-input comments** and **the Windows integrity manifest** — above.
- **Not run:** real Windows; the Windows-compiler guard path (identical binary). **Not touched:** `backups/`,
  `Windows-to-Sarvam/`, the frozen packs. `MEMORY-DECISION.md` moved but is unchanged.
