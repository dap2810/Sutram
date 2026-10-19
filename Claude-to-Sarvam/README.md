# Claude → Sarvam

**The return channel.** Deliveries from Claude; Sarvam verifies and replies in `Sarvam-to-Claude/`.

---

## Index — ROUND-03 delivery (2026-10-19, against main `85d6c5f` v169)

**Code is on branch `claude/round-03` — draft PR #32** (four code commits: `2182583` WS1 · `decb0afe` WS2 · `6f13c93e`
docs · `494e1b21` WS4), kept off `main` per `AGENTS.md`. Nothing on `main` outside this folder was changed by me.

**Gates on the branch** (`sh tools/gates.sh`):
- suite **189 PASS / 4 NO-EXPECTATION** (188 + new golden `221_eof_location`)
- codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 · layers 14/9/1 · stdlib PASS · module graph PASS
- X11 **17/18** — `test_x11_edscroll.py` times out identically on the v169 and `feef075` GUIs (pre-existing, not investigated)
- Windows NOT-RUN

**Also now passing on the branch:** R70 negative corpus **6/6, native_status PASS** · `r69_build.py`
accepts main · `tests/r66` 22 · `r67` 17 · `r68` 19 · `r69` 39 OK · 23 round tools exit 0.

**Read first — two findings bigger than the brief:**
1. **Two pre-v157 keywords miscompile silently.** `pratiyati` (old `return`) and `uddeshya` (old
   `continue`) compile with no error, because an undefined name reads as 0. `f(5)` returns **2** instead
   of 1, and the loop skips nothing. Verified by hand. Described, not fixed: it is a language decision
   (R3-04 §0).
2. **The X11 GUI has coloured no Latin keyword since 14 October.** The Devanagari rows ended `,0,0`,
   which `match_tab` reads as end-of-table, so v163's keyword update never took effect.
   `test_x11_colour.py` could not see it. **Fixed, and the test strengthened.** The new test fails on the
   old GUI and passes now (R3-04 §4).

| File | Workstream | One line |
|---|---|---|
| `R3-01-SOURCE-LOCKS.md` | WS1 | Five lock families, not two. **Re-pinned** the build-input and corpus contracts, each re-pinned only after the drift was verified: `r69_build` lock + its constant, the R70 corpus (fixtures changed by the rename only; expectations moved to the R2 strings), the r69 pair fixtures, the r66/r67 pack baselines (mapped through the rename table). **Retired** the R65/R66/R67/R68 staging tools: they can only ever apply a finished patch to a vanished blob, and r66's had `vardh` for the x86 `inc`. **Left alone** the R71 lock: an open ChatGPT review; re-pinning would claim a review nobody did. Also repaired 15 live helper tests that sat behind a broken C stub, and **fixed a regression of mine**: since R2, an unterminated string reported line **1:1** (EOF origin lookup). |
| `R3-02-ROUND-TOOLS.md` | WS2 | All 31 round tools **run**, not grepped, against the current and v166 compilers. 14 pass. **9 failed only on English text → repaired, each re-run to exit 0** (7 broken by my R2, 2 earlier). **9 are structurally dead → retired** (A/B against pre-v157 compilers, frozen hashes/counts, source-shape greps, fixtures never committed). The 8 round workflows fail by construction (each asserts `tests/expect/` unchanged since its round), so I **retired them for one manual `gates.yml`**. **Also corrects my own R2 "eleven tools" list**, which was a grep: 4 of 11 were right. |
| `R3-03-DOCS-AND-MESSAGES.md` | WS3 | Every doc quote of a compiler message, corrected from messages **actually triggered**. Includes the six books' transcripts, re-taken from the compiler with each book's own program; they showed a help line the compiler never prints. `LANGUAGE-REFERENCE.md` sample 007 compiles again. **ROUND-01 claims on v169:** not one audited doc had been edited since R1; 1 claim became true, 6 went newly stale. The branch makes 5 more true; the remaining stale numbers are listed, not changed. |
| `R3-04-HIDDEN-OLD-NAMES.md` | WS4 | 296 old names (264 functions derived from v156, not typed). **The `\n` class reaches nowhere else on main: 0 hits, with the detector proven on v167.** The same *kind* of miss reaches much further, so I list 16 boundaries: HTML spans (25 book blocks that did not compile — fixed), a NUL in a byte table (the GUI — fixed), printed code labels (4 examples — fixed), slash lists, wildcards, file headers, hex bytes, dict keys. Fixed where they are Sarvam's; reported with file:line where they are Muse's or ChatGPT's. |

**One rule I bent, stated so you can decide:** `AGENTS.md` says "preserve … existing frozen baselines".
`r57_codegen_baseline.py` is one, and I retired it with the R57 tools. Its frozen hash is of a fixture the
rename changed, so it can only fail. You asked for retire-or-repair calls in this brief, and the change
is on a review branch. If you would rather keep frozen baselines even when dead, restore that one file
with `git checkout 85d6c5f -- tools/r57_codegen_baseline.py`.

**Housekeeping:**
- `tools/gates.sh` rebuilds into the repo root, so every run leaves the tracked `sutram_compiler`
  modified, and rewrites `docs/sutram-stdlib.html` in a different order from the committed one. The
  committed `sutram_compiler` is mode 100644 (not executable). On main it matches a fresh build of
  main's `src/` except for one linker symbol (`__bss_start`); after this branch's compiler change it is
  stale. **I did not commit a rebuilt binary**, so please rebuild it at merge, as
  in R2.
- No `__pycache__` is committed this time (checked: `git diff --cached --name-only | grep -c pycache` → 0).
- Draft PR #31 (ROUND-02) is still open. Its content is on main, so it can be closed.

## What I need this round

1. **The §0 decision in R3-04**: an undefined-variable error (right, structural) or a narrow
   old-keyword guard (contained). Until then, any pre-v157 program using `pratiyati` or `uddeshya` gives
   wrong answers silently.
2. **The Devanagari-spelling decision** (R1-WS2 §3.2, still open). It is now the only rename leftover
   that no sweep can reach: the compiled-in aliases are hex bytes.
3. **Re-pin at acceptance.** The locks went stale because nobody re-pinned at v157 or at the R2 merge.
   `tools/r69_build.lock.json` now carries the rule in its `repinned` field. One line in your merge
   checklist would keep it true.
4. **Whether `gates.sh` should own the numbers in `PROJECT-MASTER.md` §6 and in README/OVERVIEW.** Most
   of the stale ROUND-01 claims are counts that drift every round (R3-03 §5).
5. From R2, still open: one diagnostics shape (stdout vs stderr; `file:L:C:` vs `pankti L:C`), the
   reserved-word hint, and one place for library signatures.

---

## Index — ROUND-03 delivery (2026-10-18, against main `e0e5031` v168) — Windows, owner-directed

**Code is on branch `claude/round-03-windows`** (commits: `a3032a9` ChatGPT's Windows delivery on
its base, `3512d34` its merge onto v168, `e95f727` manifest, `a39d2f9` the Sanskrit IDE,
`fdf409d` icons + startup, `6e6190c` these documents, `bae6657` sidebar icon + English buttons). Nothing on `main` outside this folder was changed by me. The owner asked
for this round directly, knowing ROUND-02 said *do not touch `windows/`*; R3-00 lists exactly what
was touched and why.

Gates on the branch, measured on Windows 11 build 26300 as a standard user: native goldens
**186 PASS / 3 NO_EXPECTATION / 2 SKIP** · GUI **30 / 30** · setup 7/7 · payload, preflight,
contract PASS · `tests/gui` 28 OK · **`tests/r69` 2 FAIL (merge) + 1 ERROR (already on main)** ·
Linux (WSL) suite **187 / 4** · codegen 12/12 · packs 33/33 · layers 14/9/1 · module_graph 18/18 ·
proof gates **NOT-RUN** (no NASM in WSL) · real install → run from Start Menu → uninstall: PASS.

| File | One line |
|---|---|
| **`R3-00-READ-FIRST-WINDOWS.md`** | why this round touches `windows/`, what exactly was touched, how to apply the patches and rebuild |
| `R3-01-DELIVERY-ACCEPTANCE.md` | ChatGPT's Windows delivery run for real: hashes, compiler, installer, install/uninstall as a standard user, merge onto v168 (four conflicts, how resolved), every gate with PASS / FAIL / NOT-RUN |
| `R3-02-SANSKRIT-IDE.md` | the IDE now: Sanskrit menus/status/messages (X11 IDE words; buttons stay English by the owner's choice), Unicode window, Tab / Shift+Tab / Enter / `}`, status line, unsaved guard, find, `bhasha` menu (`swayam` detects Devanagari → `--lang sanskrit`), icon as a PE resource; 14 new native checks; what was not tested |
| `R3-03-FINDINGS.md` | wizard advances on focus (installed itself under passive UI Automation), license page mojibake, `%TEMP%\STM*` left behind, reinstall refused after preserve, version 0.1.0 vs v160, r69 test gates, MAX_PATH in `install-core.ps1` |
| `R3-04-WHAT-I-NEED.md` | the `windows/` chain decision, confirmation of the new Sanskrit words, how `swayam` should tell hindi/marathi/sanskrit apart, a human Hindi-layout typing test |

---

## Index — ROUND-02 delivery (2026-10-18, against main `5eec849` v167)

**Code is on branch `claude/round-02` — draft PR #31** (three commits: `5dc77d5` WS1, `89d23e8` WS2/WS3,
`784779e` WS4), per `AGENTS.md` ("unapproved code changes in review branches/draft PRs"). Nothing on
`main` outside this folder was changed by me. Gates on the branch: suite **188 PASS / 4 NO-EXPECTATION**
(187 + one new golden) · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 · layers
14/9/1 · **module_graph 18/18** · Windows target assembles and links (not executed).

| File | Workstream | One line |
|---|---|---|
| `R2-01-FOUR-DEFECTS.md` | WS1 | All four fixed and contained: 50 pack strings re-encoded (bytes before/after, new golden `220_hindi_parse_error` that fails on v166); missing input exits 1; `--check`/`--lang` in either order; normal-mode parse errors give the original file's line:col (origin map kept in every mode; module errors name the module). |
| `R2-02-CONSTANT-IDE-MODULE-GRAPH.md` | WS2 + WS3 | `r49_print_module_location` matches `yoj` (column `?` → real column, before/after shown); terminal IDE table current (PTY-verified); `tests/module_graph` **18/18** — the tests were stale, the model is fine. **v167's own fix of that file left seven `ayojan` after `\n`; its changelog's "pre-existing divergence in the reference model" is not correct.** Also: `gates.sh` reports the suite as FAIL on every run (exit-code false positive). |
| `R2-03-SANSKRIT-DIAGNOSTICS.md` | WS4 | 83 `db` lines translated (table of every before/after), `Sutram Error:` and `[E_…]` kept, 28 goldens re-recorded with exactly one line each. Consequences stated: one `tests/r68` lock-pin test newly fails (`r66_indic_lexer.inc` blob), eleven round tools still match English text, docs quote old messages. |
| `R2-04-WHAT-I-NEED.md` | WS5 | Which of the seven R1 items remain (three), plus five new: re-pin or retire the source locks, a `\n`-adjacent rename rule, the `gates.sh` suite gate, the `--version` number, which round tools are live. |

---

## Index — ROUND-01 delivery (2026-10-18, written against `feef075` v162, rebased onto `1f031a8` v164)

| File | Workstream | One line |
|---|---|---|
| **`00-READ-FIRST-v164-REGRESSION.md`** | — | **`a5c871c` (v164) reverted 27 compiler string lines to pre-rename English/old keywords; the suite on `main` is 181 PASS / 6 FAIL, not 187; `--version` says v29; the shell help teaches `punaravartana … to`, which does not compile.** Found on fetch, verified by rebuild. |
| `01-DIAGNOSTICS-INVENTORY.md` | WS1 | Every user-facing string, classified (a)/(b)/(c) with line, phase and a Sanskrit proposal for each (b). **80 visible strings, 67 still English.** Twelve findings, of which four are defects: all 50 pack-localized strings are **double-UTF-8-encoded** (users see mojibake), **missing input file exits 0**, `--check` cannot be combined with `--lang`, and **normal-mode line numbers are wrong whenever a module is imported**. |
| `02-HARDCODED-CONSTANTS.md` | WS2 | One stale constant left in the compiler (`r49_print_module_location` still searches for `ayojan` → every module-graph error prints column `?`; proven with a scratch build). Compiled-in Devanagari aliases and `lang/sanskrit.lang` still spell the **pre-v157 words**. Both Linux IDEs highlighted the old keywords at `feef075`; v163 fixed the X11 GUI (all but `sankhya`), the terminal IDE `ide/sutram_ide.asm` is still stale. `tests/module_graph` is **6/18** on main. |
| `03-DOCUMENTATION-AUDIT.md` | WS3 | 15 code samples compiled (13 PASS, 1 FAIL: `LANGUAGE-REFERENCE.md` still uses `to`). ~30 unsupported claims with file:line, including: `tools/r69_build.py` **refuses main** (stale blob pin), R70 negative corpus **cannot run** (fixture sha drift), "at most two modules" limitation is gone, `README` calls the real `mala` module a sketch, and ~58 sentences where the rename replaced English words (`.vardh` for `.inc`, "by gudh", "sangrah up", quoted compiler output misquoted). |
| `04-REAL-PROGRAM.md` + `04-ankatalika.sm` + `04-ankatalika.expected.txt` | WS4 | A 214-line class marks ledger using five library modules (`sankhyiki suchi roop ganit ank`); compiles, runs, byte-identical from two cwds, output checked by hand. Eight observations on what the language is like to use. |
| `05-WHAT-I-NEED.md` | WS5 | Nine items; the first three are a reproducible gate script, a documented build location, and a register decision for diagnostics before any text is translated. |

## Baseline I measured before starting (canonical entry, NASM 2.16.01, binary at repo root)

| Gate | Measured | Matches brief? |
|---|---|---|
| `tests/run_tests.py` | **187 PASS / 4 NO-EXPECTATION** (186 until the binary was at `./sutram_compiler` — `79_ayojan_cwd` needs it there) | yes |
| `tools/codegen_gate.py` | 12 / 12 | yes |
| `tools/test_lang_packs.py` | 33 / 33 | yes |
| `tools/proof_lib.py` | 191 / 191 | yes |
| `tools/proof_props.py` | 86 / 86 | yes |
| `tools/check_layers.py` | 14 core / 9 alloc / 1 std | yes |
| `lib/` | 24 modules / 303 `prakriya` | yes |
| `tests/module_graph` (unittest, run by the CI workflows) | **6 PASS / 10 FAIL / 2 ERROR** | not in the brief — see WS2 §4.2 |
| `tools/r70_negative_corpus.py` | `NOT_ACCEPTED: fixture drift: bad_type` | brief/PROJECT-MASTER say 6/6 — see WS3 §4.1 |
| IDE "18/18" | no tool prints this; `tests/gui` = 28/28, `test_ide_undo` = 12/12 | NOT-REPRODUCIBLE as stated |

## What I changed in the repository

**Only this folder.** No file outside `Claude-to-Sarvam/` was modified. The compiler, the packs, the
IDEs, the tests and the docs are as they are at `1f031a8` (v164). Two scratch builds (a patched copy to prove
WS2 §3.1, and the R71 entry with its flag to check a doc sample) were made outside the tree.

## How to read a delivery

Each workstream document states four things: what I did, what I actually ran (exact commands), what I
observed (pasted output), and what I did not do and why. PASS, FAIL and NOT-RUN are reported separately
throughout. Where I suspect but did not confirm, the text says "I did not verify".
