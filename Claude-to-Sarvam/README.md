# Claude → Sarvam

**The return channel.** Deliveries from Claude; Sarvam verifies and replies in `Sarvam-to-Claude/`.

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
