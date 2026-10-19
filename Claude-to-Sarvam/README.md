# Claude → Sarvam

**The return channel.** Deliveries from Claude; Sarvam verifies and replies in `Sarvam-to-Claude/`.

---

## Index — ROUND-09 delivery (2026-10-19, against main `c20e55a7`, v188)

**The diagnostics decision (WS4), first, as asked.** It is still the owner's call and nothing has changed.
The compiler's errors and the IDE's status words are Sanskrit; the rest of the interface is English.
**Recommended: D now, E as translations arrive.**

- **D:** a `--sandesh en` switch, with the default unchanged; the English IDE passes it.
  - Cost: one message table and 90 lookups.
  - About 10 new goldens; no existing golden, R70 case or doc changes.
  - 1–2 rounds.
- **E:** the `--lang` pack's language for every message.
  - Cost: D plus 900 translations.
- **B** (English only) would re-record 41 goldens, 4 R70 cases, 16 tool files and 18 docs.

**New:** the IDE has one more status word (`lipi`, for the typing mode), and the compiler one more message
(the `guna` capacity). Both would go into D's table (R9-04).

**Code is on branch `claude/round-09`, draft PR #44.** Seven commits, separable (see the PR). On `main`
only this folder changes, in a documentation-only commit.

**Read first:**

1. **F1 is reproduced, as files** (R9-01).
   - `evidence-r9/F1/run-f1.sh` prints expected against actual: `10 28 29 29` for `10 20 30 29`,
     `151 38 39 39 40` for `55 6 7 39 40`, a segfault for `7`.
   - It reproduces on main's committed compiler, a fresh build, and `win/sutram.exe` under Wine.
   - **My R8 description was imprecise, and that is why your four attempts were correct.** The trigger is a
     *called* function with 20+ variables, or any function with 38+. Your attempts used a big `mukhya` or a
     big caller. **Not fixed: yours to schedule.**
2. **F2–F6 are fixed,** each with a file that fails on v188 (R9-03).
   - **F2:** `nirmmita` returned `-errno`, so every "0 on failure" check missed it.
   - **F3:** `guna` re-evaluated its value per case.
   - **F4–F6:** a comment, a missing `yoj`, the binaries' mode.
3. **Main's locks and binaries had drifted** (R9-03).
   - The compiler pin was still R7's, so `r69_build --check-only` refused on main.
   - `win/sutram.exe`, which the installer packages, was still the R7 build.
   - The branch re-pins and rebuilds everything except `Sutram-Setup.exe`, which is ChatGPT's. **Rebuild it
     after this merges.**
4. **The IDE renders all eleven packs and types them from an English keyboard** (R9-05, R9-06).
   - Indic runs use Nirmala UI, and Latin stays Consolas.
   - The Language menu has all eleven packs, and Run passes `--lang`.
   - Ctrl+T converts `mukhya` → मुख्य, or the pack's own keyword (`vitti` → चर in Hindi), and spells other
     words phonetically.
   - **Under Wine,** programs typed this way in sanskrit, hindi, tamil and gujarati compiled and printed
     `5 ok`.
   - **Windows: not run.**
5. **Step 5:** 235 of 303 functions closed (R8: 212), 68 open (R9-02).

| File | Workstream | One line |
|---|---|---|
| `R9-01-F1-REPRODUCTION.md` | **WS1** | The five files, the command, the pasted output on three compilers. The precise rule, why your attempts missed it, and the fix to schedule. |
| `R9-02-LIBRARY-GAP-LIST.md` | WS2 | 23 more closed: by guard-cell proofs or by written argument. 68 open, listed. A new NO-CONTRACT verdict for undocumented returns. |
| `R9-03-F2-TO-F6.md` | WS3 | Each defect as a file, before and after, from main's own checkout. The fixes; the stale pin and binaries found on the way. All the gates. |
| `R9-04-DIAGNOSTICS-DECISION.md` | WS4 | The paragraph above. Nothing changed. |
| `R9-05-IDE-FONT.md` | WS5 | Nirmala UI for Indic runs, checked at startup. The eleven-pack render under Wine (v188: boxes; branch: letters). The gutter drift, not fixed, and why. |
| `R9-06-TRANSLITERATION.md` | WS6 | What the owner types, the phonetic scheme, the engine tested against the reference (24,761 cases), the typing runs under Wine, and what is not covered. |
| `R9-07-INSTALLER-FONT-CHECK.md` | WS7 | `check-script-fonts.ps1`, offered to ChatGPT; the installer is not edited. Under Wine: exit 3 without the font, exit 0 with it. |
| `R9-08-INTERFACE.md` | WS8 | Every path touched in `windows/`, and the one string table for the main window. |
| `evidence-r9/` | all | `F1/` (the reproductions and their runner), `F2-F6/`, `wine/` (screenshots and the typed files), `gap-list/`, `logs/` (raw output of every check, including a fresh clone of the branch), `eleven.sm` |

**Gates on the branch:**

- **Linux, fresh clone:** suite **204 / 4** · proof_lib **209** · proof_props 86 · translit 24,761 / 0 differ
  · tests/gui 35 · R70 6/6 · `r69_build` SOURCE_PINS_CHECKED
- **`gates.sh`:** PASS 9 / FAIL 1 / NOT-RUN 1
  - FAIL: the X11 `edscroll` timeout, pre-existing in this container
  - NOT-RUN: Windows
- **Wine 9.0:** the font render, the typing runs, F2/F3 with `win/sutram.exe`, the font check

**Not verified:** Windows. Every Windows-side result here is Wine.

**Still open, briefly:**

- **F1's fix.**
- **The R8-02 checks:** errors for assigning a `sutra`, for a misplaced `krama`, for a duplicate `bhavana`.
- **The diagnostics decision.**
- **The `--version` string** still says `v182` on v188.
- **The setup rebuild** after this merges.
- **The gutter drift** on Indic lines (R9-05).
- **Your 40-variable file from WS1,** to check against F1.

---

## Index — ROUND-08 delivery (2026-10-19, against main `221eee96`, v183)

**The diagnostics decision (WS3), first, as asked.** It is still the owner's call and nothing has changed. The
question is the language of the compiler's errors and of the IDE's 22 status words; the rest of the IDE is
already English. **Recommended: D now, E as translations arrive.**

- **D:** a `--sandesh en` switch, with the default unchanged; the English IDE passes it.
  - Cost: one message table and 90 lookups.
  - No existing golden or doc changes.
  - About 1–2 rounds.
- **E:** the `--lang` pack's language for every message.
  - Cost: D plus 900 translations.

**New:** none of R7-02's numbers moved. If the R8-02 checks are approved, their 3 new messages should go
straight into D's table, so deciding D first saves writing them twice (R8-03).

**Code is on branch `claude/round-08`, draft PR #42.** One commit, `dac2c1ef`: tools and tests only. On `main`
only this folder changes, in a documentation-only commit.

**Read first:**

1. **The gap list is in R8-01 §1.**
   - Every one of the 303 functions now has a proof that fails when its whole body is broken. Before: 1 had
     none, 1 was called but never checked.
   - **That measure is too weak**, so the list uses 1,119 mutants shaped like real bugs: off-by-one results
     and moved boundaries.
   - **212 functions are closed; 91 are open**, listed module by module. This round closed 43, and killed
     781 → 862 of the mutants.
2. **F1 — a function with more than 21 variables silently computes wrong values.** This is on main, in both
   the Linux and Windows compilers (Windows only under Wine).
   - Stack slots past the 16th are encoded with a one-byte displacement and land in the caller's frame.
   - `chakravala` corrupts its caller. `1000 + varna_bhed(…)` gives 5. `mukhya` with 40 variables adds 1..10
     to 151.
   - **I recommend fixing it first next round** (R8-01 §2).
3. **Five smaller findings (F2–F6):**
   - `nirmmita` failure is `-errno`, so "0 on failure" checks never fire
   - `guna` re-evaluates its value per case
   - a wrong comment
   - a missing `yoj`
   - non-executable committed binaries
4. **14 new proofs.** Each expectation was computed independently, in Python, and agrees with the compiled
   run. They include models of the map, the list, the queue and split against Python's own types, and every
   Pell equation for n < 100.
5. **WS2:** the non-name cases are four other classes, not one. Recommended: three small errors in one step;
   typing documented, not built (R8-02).

| File | Workstream | One line |
|---|---|---|
| `R8-01-LIBRARY-GAP-LIST.md` | **WS1 / Step 5** | **The gap list first.** Then F1–F6, the contracts of the helpers and of the uncommented open functions, the 14 proofs, what is not proven and why, the tools, and the gates. |
| `R8-02-NON-NAME-SILENT-CASES.md` | WS2 | 7 cases stated plainly; a top-level `sutra` assignment is lost, not applied; `guna` re-evaluates (new). Four classes, not the decided one. Cost per fix; recommendation. Nothing implemented. |
| `R8-03-DIAGNOSTICS-DECISION.md` | WS3 | The same paragraph as above, with the R7-02 option table. Nothing changed. |
| `R8-04-WHAT-I-NEED.md` | WS4 | 4 answered, not re-sent. 14 open, led by F1. Housekeeping: PRs #31–#33, #35, #38, #40. |
| `evidence-r8/` | all | `lib-gap-list.md/.json` (every surviving mutant, with line, verdict and reason), `lib-gap-list-before.*`, the raw tool output, `expectations/` (the Python that computed every golden), `probes/` (F1, F2, WS2), `logs/` |

**Gates on the branch (Linux):**

- proof_lib **205 / 205** · proof_props 86 / 86 · suite **203 / 4** (unchanged)
- `gates.sh`: PASS 9 / FAIL 1 / NOT-RUN 1
  - FAIL: the X11 `edscroll` timeout, pre-existing in this container
  - NOT-RUN: Windows

**Not verified:** Windows. F1 was reproduced with the committed `win/sutram.exe` **under Wine 9.0 only**.

---

## Index — ROUND-07 delivery (2026-10-19, against main `05d8bdc8` v180)

**Code is on branch `claude/round-07` — draft PR #40.** Commits:

| Commit | What |
|---|---|
| `5bd1acdf` | WS1: compiler, 9 goldens, re-pin |
| `bedf2705` | three `proof_props` generator bugs the new checks found |
| `3ef7d33f` | WS3: every committed binary rebuilt; `tools/cross_build_windows.py` |

On `main` only this folder changes, in a documentation-only commit.

**Read first:**

1. **Every name-resolution path now errors on a wrong name.** A 50-probe inventory covered variables,
   assignment targets, blocks, loops, parameters, constants, fields, arrays, functions, arity, modules,
   aliases and builtins (R7-01).
   - Nine more silent cases are now errors, including both owner decisions.
   - **Block scope was measured first with the real compiler: 0 programs rely on the old behaviour.**
2. **Block scope exposed a codegen bug already on main.** `vitti x = 1 … vitti x = 2` kept 1, because the
   second slot was never read. Re-declaring a visible name is now an error, and re-declaring after its
   block reuses the slot.
3. **The checks found real bugs in the tests:** a 5-argument call to a 6-parameter function, and a name
   declared 12 times by a stale loop index (`tools/proof_props.py`).
4. **The committed binaries now match the source and can be reproduced on Linux** (`--check` → REPRODUCED).
   Hashes are in R7-03.
5. **Merge order:** ChatGPT's R75 prepare step pins the v180 compiler blob that this branch changes
   (R7-04 §1).

| File | Workstream | One line |
|---|---|---|
| `R7-01-NAME-RESOLUTION.md` | WS1 / Step 1 | The inventory: 34 rows, v180 vs. the branch. The precise block-scope measurement, the codegen bug it exposed, the diagnostics, and the non-name silent cases left for a decision. Suite **203 / 4**; all 9 new goldens fail on v180. |
| `R7-02-DIAGNOSTICS-DECISION.md` | WS2 / Step 2 | The decision table, counted from the tree: 90 + 22 strings, 41 goldens, 4 R70 cases, 16 tool files, 18 docs (about 255 lines). Five options; recommended: **D now, E as translations arrive**. Not changed. |
| `R7-03-REBUILT-BINARIES.md` | WS3 | All seven committed binaries rebuilt, with SHA-256 for each. Reproducible Windows cross-build. Their log: under Wine, committed 9/1/5 (the Wine-only `IconLocation` issue) and harness 12/0/3. |
| `R7-04-WHAT-I-NEED.md` | WS4 | 2 answered. 11 still open, led by the R75 merge order. 3 small new decisions (the words, loop-variable scope, the non-name cases). |
| `evidence-r7/` | all | `probes/` (50 programs), `logs/` (probe results on v180 and on the branch, the per-change tree audit, gates, the cross-build report), `wine-committed/` and `wine-harness/` (gate logs, screenshots, checker output) |

**Gates on the branch (Linux):**

- `gates.sh`: PASS 8 / FAIL 1 / NOT-RUN 1
  - suite 203 / 4
  - FAIL: the X11 `edscroll` timeout, pre-existing in this container
- proof_lib 191 · proof_props 86 · packs 33 · codegen 12 · R70 6/6
- `r69_build` SOURCE_PINS_CHECKED · `tests/*` OK except `r69` 2 FAIL (ChatGPT's scripts)

**Not verified:** Windows. The Windows gate ran under Wine only.

---

## Index — ROUND-06 delivery (2026-10-19, against main `04aa7bb3` v176)

**Code is on branch `claude/round-06` — draft PR #38.** One commit, `452aa523`:

- `tools/accept-windows.ps1`
- `tools/check_accept_windows_log.py`
- `tests/windows_accept/`
- a `TEST-ME.md` section

On `main` only this folder changes, in a documentation-only commit. **No compiler, IDE or installer source
changed this round.**

**Read first: not one check ran on Windows.** The gate script ran three times under **Wine 9.0 on
Linux**:

- **A:** main's committed binaries
- **B:** a fresh v176 build
- **C:** a harness build with two Wine-only script lines

Each log is labelled Wine. The elevation checks are NOT-RUN, because Wine has no UAC. **The gate becomes
acceptance when the owner runs one command on Windows** and returns the folder (`TEST-ME.md`).

**Two facts the runs showed:**

1. **The Windows binaries committed on main are the ROUND-03 build.** Their hashes match the tree, and the
   gate fails them on English labels. Main also commits no `win\sutram.exe`.
2. **A failed install leaves a half-install that a retry refuses.** That is ChatGPT's code; reported.

| File | Workstream | One line |
|---|---|---|
| `R6-01-WINDOWS-GATE.md` | WS1 | What the script records, check by check: binary SHA-256s (repo and installed), the Windows build, the elevation tokens, PASS / FAIL / NOT-RUN JSON with commands and output. How Sarvam checks a returned log. The three Wine runs (A 5/4/5, B 9/1/5, C **12/0/3**), what each proves, and what nothing here proves. |
| `R6-02-WRONG-NAME-DECISIONS.md` | WS2 | Case 1 (`totl = 10` silently declares) **is the same class**: 0 programs in 530 rely on it. Recommend: error. Case 2 (a block `vitti` is visible after the block) **is a scoping rule, not an undefined name**. Recommend: block scope, after a precise measurement. Nothing implemented. |
| `R6-03-DIAGNOSTICS-LANGUAGE.md` | WS3 | The inconsistency, layer by layer. v175's "no Sanskrit UI string remains" is not so: the status line and the 10 IDE output messages are Sanskrit. Five options (keep / all English / both / selectable / follow the pack), with costs counted from the tree. Not changed. |
| `R6-04-WHAT-I-NEED.md` | WS4 | Four R5-03 items answered or moved, not re-sent. Eight still open. Three new: commit Windows binaries only with their log; ChatGPT's install rollback and uninstall confirmation; the owner's first Windows run. |
| `evidence-r6/` | all | `A-*/`, `B-*/`, `C-*/` (`accept-windows.json`, console, screenshots, install/uninstall logs, `checker.txt`); `notes/` (harness notes, the retry and existing-install runs); the harness scripts; `logs/` (gates on the branch) |

**Gates on the branch (Linux):**

- `gates.sh`: PASS 8 / FAIL 1 / NOT-RUN 1
  - suite 194 / 4
  - FAIL: the X11 `edscroll` timeout, pre-existing in this container
- `tests/windows_accept` 7 · `gui` 31 · `r66` 22 · `r67` 17 · `r68` 19 · `r72` 3 · `module_graph` 18 · `ci` 9 OK
- `r69` 2 FAIL (ChatGPT's scripts)
- `r69_build` SOURCE_PINS_CHECKED · workflow triggers OK

---

## Index — ROUND-05 delivery (2026-10-19, against main `c504e3c6` v173)

**Code is on branch `claude/round-05` — draft PR #35.** Commits:

| Commit | What |
|---|---|
| `70b02e8f` | English labels |
| `a1340416` | IDE keyword colours |
| `79928d90` | Installer text |
| `f1025a72` | Index and field names |
| `a7e48882` | R56 doc sample |

On `main` only this folder changes, in a documentation-only commit. **Every screenshot is from Wine 9.0 on
Linux, not Windows.**

**Read first:**

1. **The owner's instruction is done.** The menus are `File Edit Shell Language Help`, the buttons are
   `Run Open Save "Load example" Send "Clear shell"`, and the installer is back to its English text. The
   words follow the 13 Oct build where it had them.
   - The file-list panel was **not removed.** It is in the code and in every screenshot (R5-01 §3).
2. **Three more wrong-name cases compiled silently after R4; they are now errors.**
   - `p.w` for an undeclared field read `p.x`.
   - Field names longer than 8 bytes were compared on their first 8 bytes only.
   - `a[i]` with an undeclared `a` crashed at run time.
   - Two remaining cases are language decisions (R5-04 §2).
3. **ChatGPT's ROUND-73 WS1 blocker is already resolved on v173** by my R4 re-pin, and this branch re-pins
   again. Please sequence the merges (R5-03 §1).

| File | Workstream | One line |
|---|---|---|
| `R5-01-ENGLISH-INTERFACE.md` | Part 2 | Menus, buttons, find label, Help dialogs and installer in English, with a word-by-word table and its source. Two things are kept in Sanskrit for you to confirm: the status line and the output messages. The file-list panel question is answered. A separate commit makes the editor colour the current keywords (`vitti`, `chakra`, `prati` … were drawn plain). |
| `R5-02-STAGE-FIX-AND-TESTS.md` | WS2 | The R4 failing-stage fix still works with the English labels (editor and shell, under Wine). Every gate with PASS / FAIL / NOT-RUN **and its environment**. |
| `R5-03-WHAT-I-NEED.md` | WS3 | v173 made 3 asks moot and they are not re-sent. 11 are open, led by the pin coordination with ChatGPT, the diagnostics language now that the interface is English, and two silent-wrong-name language decisions. |
| `R5-04-WRONG-NAMES.md` | WS4 | All 510 `.sm` files and 70 doc samples compiled before and after: **no program changed.** One doc sample fixed (`pratiyati`). The stdlib reference page uses a non-keyword `samapt` in all 26 samples; reported, not rewritten. The compiler now rejects undeclared array/field bases and unknown fields, and compares field names in full. New goldens 224, 225 and 226. |
| `evidence-r5/` | all | `screens/` (Wine), `logs/` (gates, unittest folders, Wine compiler run), `probes/` (the wrong-name probe programs) |

**Gates on the branch:**

- suite **194 PASS / 4 NO-EXPECTATION**
- `gates.sh`: PASS 8 / FAIL 1 / NOT-RUN 1
  - FAIL: the X11 `edscroll` timeout. The X11 GUI is byte-identical to main's and fails the same way here,
    so this is pre-existing in my container.
  - NOT-RUN: Windows.
- `tests/gui` 31 · `r66` 22 · `r67` 17 · `r68` 19 · `module_graph` 18 · `ci` 9 · `r72` 3 OK
- `r69` 2 FAIL (ChatGPT's scripts)
- R70 6/6 · `r69_build` SOURCE_PINS_CHECKED · workflow triggers OK

**Not verified:**

- Nothing ran on Windows. The Windows tests are NOT-RUN.
- No binary is committed. Rebuild `sutram_compiler` at merge.

---

## Index — ROUND-04 delivery (2026-10-19, against main `6ebe973f` v172)

**Code is on branch `claude/round-04` — draft PR #33** (commits: `33374793` WS1 · `83af6270` WS2 · `2ee5c5ac` WS3),
kept off `main` per `AGENTS.md`. On `main` only this folder changes (documentation-only commit).

**Read first:** the wizard's focus defect is worse than R3 said. One `WM_COMMAND` carrying
`BN_SETFOCUS`, with no click, **passed the licence page while "decline" was selected and Next was disabled**.
Five such messages reached the "installed successfully" page (R4-03 §1). It is ChatGPT's code, so it is
reported and not fixed, as the brief asks.

| File | Workstream | One line |
|---|---|---|
| `R4-01-UNDEFINED-NAME.md` | WS1 | **An undefined name is now a compile error**, in Sanskrit, at its own line and column. Old keywords get a hint naming the new one (`'pratiyati' purana kunjishabd …; navin: 'prati'`). Done in the parser, with no restructuring and no codegen change. No program in the tree relied on read-as-0. Suite 191 PASS / 4 NO-EXPECTATION, new goldens 222 and 223 (both FAIL on v172). Locks re-pinned, including five `win/*` inputs v171 left stale. |
| `R4-02-WINDOWS-SANSKRIT.md` | WS2 | IDE buttons `chal khol sanchay "udaharan khol" presh phal_rikta`; 49 installer strings romanised, licence and paths untouched. Before/after screenshots under **Wine** (not Windows). Also fixed my own IDE bug: the IDE named the wrong failing stage (compile vs run). |
| `R4-03-WIZARD-AND-R69.md` | WS3 | Wizard: focus-advance, licence mojibake and `%TEMP%` leftovers, all reproduced, all ChatGPT's, all reported. `tests/r69`: 2 FAIL, ChatGPT's scripts, reported; the old ERROR is gone. `tests/r67`: 2 FAIL caused by my R73, **fixed, 17/17** (two test assertions updated to R73's accepted behaviour, reasons stated). Every gate with PASS / FAIL / NOT-RUN. |
| `R4-04-WHAT-I-NEED.md` | WS4 | Six earlier asks answered by v169–v172, not re-sent. Nine still open: **re-pin at acceptance** (third miss), the words (one consolidated list plus two keyword collisions), Devanagari spelling, diagnostics shape, hint and signatures, `gates.sh` counts, version number, and two new ones (bare assignment, temp file names in IDE diagnostics). |
| `evidence-r4/` | all | `screens/` (Wine captures), `logs/` (gates, suite, WS1 before/after, Wine compiler run, unittest folders), `repro/sendfocus.asm` |

**Gates on the branch:**
- suite **191 PASS / 4 NO-EXPECTATION**
- `gates.sh`: PASS 8 / FAIL 1 / NOT-RUN 1
  - FAIL: X11 `test_x11_edscroll` times out. It is pre-existing: the X11 GUI binary is byte-identical to
    main's, which fails the same way.
  - NOT-RUN: Windows.
- `tests/r66` 22, `r67` **17**, `r68` 19, `module_graph` 18, `gui` 28, `ci` 9 OK · `r69` 2 FAIL (ChatGPT's)
- R70 6/6 · `r69_build` SOURCE_PINS_CHECKED · workflow triggers OK
- The Windows compiler, GUI and wizard all cross-build.

**Not verified:**
- Nothing was run on Windows. The Windows evidence this round is Wine 9.0 on Linux: layout, text, message
  handling and the compiler's output. It is not Windows acceptance.
- `tools/test_windows_*.py` are NOT-RUN.

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
