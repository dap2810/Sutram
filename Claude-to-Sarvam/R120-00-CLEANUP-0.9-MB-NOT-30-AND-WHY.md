# R120-00 — The cleanup is done as you ruled it, and it removes 0.86 MB, not 30. Almost every evidence folder is cited by a round record, which you said to keep. The clone will not shrink at all: deleted files stay in history. The docs now describe v298; no link broke.

- **Commit on `main`:** `PENDING-SHA` (documentation, evidence and deletions only - no compiler, library, example or test change; on top of R121's `f94fc05`).
- **Compiler: `Sutram 1.0 (v298)`, unchanged.** Suite, gates and guard are R121's (315 / 63-1-1 / 0 unexplained DIFFER); nothing they measure changed here. The doc gates were re-run on this tree: `doc counts` - *every document agrees with the measured tree*; `doc signatures` PASS; `R54 migration` 8/0.
- **Muse's R119 keep-audit (`5d7d21c`) did this measurement first.** I re-checked it independently (my own scan of every tracked file) and act on it; where we differ I say so.

## WS4 first - what it achieves, and why so little

| | before | after |
|---|---:|---:|
| tracked files | 6,285 | 6,268 |
| tracked bytes (the working tree, without `.git`) | **60.34 MB** | **59.49 MB** (**−0.86 MB**) |
| `.git` pack (what a clone downloads) | **59.8 MiB** | **59.8 MiB - unchanged** |

**Your 52 MB, and "214 evidence directories", are not what this tree measures:** 60.3 MB tracked, and **109** `evidence-*` directories (Muse counted 108 a commit earlier). Muse's audit says the same.

**Why it is not 20 MB:**

1. **The evidence is cited, and you said to keep what is cited.** Of 109 evidence directories, **105 are named by a round record or doc** (almost always as a file path: `evidence-r116/guard.txt`). **Only 4 are cited nowhere** but in Muse's audit. Those 4 are gone - 0.3 MB.
2. **The big binaries are not duplicates, or are in folders I may not touch:**
   - `Windows-to-Sarvam/.../Sutram-Setup-v297.exe` (1.9 MB): **kept.** `Windows-to-Sarvam/` is outside what I may change, and the Windows round is live (round 3 landed today).
   - `Sutram-Setup.exe` at the root (1.5 MB): **kept** - the `installer version` gate reads it.
   - `sutram.exe` = `win/sutram.exe` (0.5 MB, the one exact duplicate binary): **both kept.** The build writes `win/sutram.exe` and copies it to the root, and tools read each path (the Wine wrappers, the installer build).
3. **The 2.6 MB of duplicate guard logs sit inside cited folders.** The same ELF/PE/Wine log was saved under two to six names. Deleting a copy breaks the record that cites it; a symlink would not survive a Windows checkout. **Kept.**
4. **`backups/` (9.6 MB) is exempt; `Muse-to-Sarvam/` is outside what I may change.**

**And the clone cannot shrink by deleting.** Every deleted file stays in git history, so `git clone` downloads the same 59.8 MiB. **Only a history rewrite (`git filter-repo` and a forced push) would make it smaller**, and that needs your decision and a `--force` I am not allowed. If you want that, the candidates are the installer binaries and `backups/`'s zips (at least 13 MB at their current versions; more with their older copies in history); every collaborator would then have to re-clone.

## WS1, WS2, WS3 - what went, and what stayed

**Deleted (17 files, 0.86 MB):**

| path | why it could go | size |
|---|---|---:|
| `Sarvam-to-ChatGPT/Sutram-Setup.exe` | your instruction: a v243-era copy in an outbound folder. ChatGPT R60 and Muse R87 cite it **by SHA-256**, so they still identify it, and it stays in history | 578 KB |
| `Claude-to-Sarvam/evidence-r42-windows/` | cited nowhere but Muse's audit | 12 KB |
| `Claude-to-Sarvam/evidence-r44/` | the same | 92 KB |
| `Claude-to-Sarvam/evidence-r47/` | the same | 88 KB |
| `Claude-to-Sarvam/evidence-r52/` | the same | 116 KB |

**Every `ROUND-*.md` and `R*.md` stays.** No round record, doc, test, example or source file was deleted.

**Kept, though "old":** **the evidence of the last 10 rounds and every other cited folder** - 105 directories, by your own rule. Your proposal ("keep the last 10, delete the rest") and your rule ("if a round record references a deleted file, keep that one") collide on 101 directories. The rule wins.

## WS4's other question - did anything break a link?

**No.** There was no link checker in the tree, so I wrote one (`evidence-r120/linkcheck.py`): every relative `[..](..)`, `href=` and `src=` in all 1,274 tracked `.md` / `.html` files, against the working tree. Results (`evidence-r120/links.txt`):

- **710 relative links, 4 broken - the same 4 before and after.**
- Three are code that looks like a link (`[i](x)`).
- **One is real and old:** `ChatGPT-to-Sarvam/ROUND-181-...md` links `rounds/CHANGELOG-ARCHIVE.md` relative to its own folder. That is ChatGPT's file; reported, not edited.

## WS5 - the docs, now describing v298

**Stale living docs, corrected** (Muse's WS3 list, plus what I found):

| doc | what was stale | now |
|---|---|---|
| `PROJECT-MASTER.md`, `docs/LANGUAGE-REFERENCE.md`, `docs/PATH-TO-COMPLETION.md` | **the opening status box said compiler v261, suite 225, 48 gates, and "nothing ever returns memory"** | the v298 box: the measured numbers, the 22 + 10 renames, `asti`/`nasti`, `Sutram truti`, `sankhya_bindu` withdrawn, the 15 refusing contracts, `patra_asti` blocked, v298's fix, and the memory model with its Windows gap |
| `docs/LANGUAGE-REFERENCE.md` (15 lines) | examples and prose writing `kosh_push`, `kosh_len`, `likha_fmt`, `pankti_len` as the current names (the aliasing example, the escape rules, the `likha_fmt` section, a hint quoted as v296 printed it) | the primary names. The §4b / §4c alias tables keep the old names, as aliases |
| `docs/MEMORY-MODEL.md` | the opening box called the R70 snapshot "unchanged and accurate": no `free`, a leaking `kosh`, no `parimita`, no regions | a v298 box: arena, `mandapa` return, `parimita`, regions, the `kosh` escape rule, `parimana`, and Windows's gap. The R70 body is kept, marked historical |
| `docs/OPEN-ISSUES.md` C1, C2 | the English `kosh_*` and `pankti_len` listed as open | marked **CLOSED in v292 (R111)**, with the names |
| `docs/_newchapter_en.html` | "the current language" chapter using `kosh_push` / `kosh_len` | `kosh_kship` / `kosh_gan` |
| `docs/vocabulary/VOCABULARY-TABLE.md`, `-SHORT.md`, `-COMPLETE.md` | R96 proposal tables read as current (`kosh_aayam`, `likha_roop`, `sankhya_bindu` with no withdrawal) | a **SUPERSEDED** box naming where the adopted names are. The table is kept as the record |
| `docs/sutram-vocabulary.html` | right for v292-v295; no library names | **R118's ten library names added** |
| `docs/sutram-book-english.html`, `-sanskrit.html` | `lkhb`, `kosh_push`, `pankti_len`, `asti_sorted` in the examples | the primary names (16 each) |
| `PROJECT-MASTER.md`, `docs/sutram-design-parameters.html`, `sutram-project-status.html`, `sutram-scorecard.html` | "225 tests" / "48 gates" (the `doc counts` gate's NOTEs) | 315 / 63, marked v298 |

**Checked and right as they are:**

- **No living doc presents `Sutram Error` as the current token.** The remaining mentions are history: "up to v293", the changelog, `SANDESH.md`, `WHATS-LEFT`'s struck items, and `sutram-audit.html`'s dated transcripts.
- `CHANGELOG`, `docs/reports/*` and `docs/decisions/*` are dated records, and they quote old names correctly for their date.

**Not changed:** the Gujarati, Hindi, Tamil and Telugu books (`docs/sutram-book-*.html`) still use `kosh_push` / `lkhb` in their examples. **They are the frozen languages' books.** Tell me if a name correction in their code samples is outside the freeze and I will do all four the same way.

## Not done, and why

- **The size target:** not reachable under your rules - the reasons above. A history rewrite is your call and needs `--force`.
- **Windows-to-Sarvam's installer, `Muse-to-Sarvam`, `backups/`:** not touched, by the standing rules.
- **The four frozen-language books:** above.
