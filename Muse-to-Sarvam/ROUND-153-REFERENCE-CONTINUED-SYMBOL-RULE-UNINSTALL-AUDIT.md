# ROUND-153 — the reference, continued; the symbol rule, short; the whole uninstall, audited

**Base:** `308c2161` (v315) · **Method:** read-only — nothing compiled, assembled, run, or executed · **Deliver into:** `Muse-to-Sarvam/`

## Verdicts first

**Task 1 — the reference, against the code.** No NEW wrong advice or behaviour claim beyond the R152 twenty. The one sentence Claude fixed this round — the tree-limit advice — is fixed: v315's size-limits section now says what the code says (fewer modules, or split into separate programs; splitting a statement does not help), and every other piece of limit advice checks out. Every E-code the docs name exists in `src/` or `lib/`, including `E_VRIKSHA_SEEMA`, new at v315. The four closure claims R152 left unread all hold. **Of the R152 twenty at v315: 19 STILL WRONG, 0 FIXED, 1 NOT LOCATABLE VERBATIM** — and the one is a correction to my own R152 report (see below): wrong no. 9 ("grows until the arena is full (1 GiB) or a region's 64 MiB") appears verbatim in neither doc at v314 or v315; the §16 text it appears to rest on says the opposite. The docs diff v314→v315 touches only the size-limits section and the MEMORY-MODEL status line, so nothing else moved except line numbers. The brief's shared-state claims verify — `E_VRIKSHA_SEEMA` exists and is emitted, and the closure-by-construction counts hold — but the brief's line numbers (21425, 18863) are the R148/R149 base's, stale at v315 by two bases, and the R149 exception (`r82_param_checks`, flag at 0) still stands unmentioned.

**Task 2 — the symbol rule, short.** The full rule is in the R152 report (Task 3). The short usable version, for the method notes, is in Task 2 below: a writer's three-line checklist and a reviewer's two-line check. The one-line version: **a cited label is not a fact until a definition grep at the base returns it with file + line.**

**Task 3 — the whole uninstall.** Most removals are now recorded. **Three are not — two are live data-loss paths, one is a residual with no realistic user harm.** (1) The legacy-shortcut ownership claim is LIVE (shared-state item 1, confirmed with one wording correction: `Test-ShortcutSays` compares four fields, not "only target" — the unchecked set is exactly {Description, Hotkey, WindowStyle}); a legacy link changed only in one of those three fields is accepted as unchanged, claimed at reinstall, and deleted — at install time with the desktop checkbox off, or at the next uninstall after any reinstall. (2) The Uninstall registry key is deleted whole with `-Recurse` (`uninstall-core.ps1:216-219`); the only gate is `InstallLocation -eq $InstallDir`, and the installer writes eight values there and records none — low severity, but by the brief's strict question it has no record. (3) The `.sm\OpenWithProgids` `Sutram.Source` value (`:203`) is removed with no per-value record and no value check — residual only: its content is a constant empty string and only Sutram registers that ProgID. R151 pair 3's class tree is closed in v315 (values go only on value equality, keys only when empty). The R152 rule is now the design of all four records: each records what was done, not merely that something was done.

---

## Task 1 — the reference and the memory documentation, continued

**Documents:** `docs/LANGUAGE-REFERENCE.md` (1531 lines) and `docs/MEMORY-MODEL.md` (222 lines), read in full at v315. **Scope:** only what the brief names — (a) advice about limits, (b) claims that a check exists, by name, (c) claims that a class is closed, and by what argument — plus the status of the R152 twenty at the new base. The v315 compiler diff (`src/sutram_compiler.asm`, 3 hunks: version string `:257`, the two limit hints `:638`, the `r58_fold_tree` guard `:31781`) touches none of the code the R152 findings rest on, so the R152 code citations stand, re-verified where line numbers drifted.

### The tree-limit advice, fixed — and why the new advice works

v314 advised "make the program smaller (split long statements, bring in fewer modules)" for the tree limit. Splitting a statement was the wrong half: the AST heap counts every node of every statement (`AST_HEAP_CAP equ 3145728`, `AST_NODE_SIZE equ 72`, `:38`/`:34`), so splitting a statement keeps the same expression nodes and adds a statement node (and assignment nodes for intermediates) — the node count cannot decrease. v315's advice, checked piece by piece (`docs/LANGUAGE-REFERENCE.md:1042-1060`):

- **"Bring in fewer modules"** — HOLDS. The tree cap covers the whole program "the libraries `yoj` brings in included" (`:1043-1044`); imports are inlined into the same AST heap, so fewer modules means fewer nodes.
- **"Split the program into separate programs"** — HOLDS by construction: the 3 MiB cap is per compile, so each separate program gets its own tree.
- **"Splitting a statement does not help — it does not make the tree smaller"** — HOLDS, for the reason above, and the compiler's own hint says the same (`src/sutram_compiler.asm:644`, quoted below). The doc itself notes "(v314 advised it; that was wrong)" (`:1050`).
- **Budget advice, unchanged and still right:** "split the statement (keeping intermediate values in names) or raise `--analysis-steps`" (`:1057-1058`). Splitting works because the count restarts at N for every statement and initializer (`r152_scan_flag`, `src/sutram_compiler.asm:28746+`; comment `:41-42`); raising works because the flag exists with range 1..2147483647 (R151 verified the 40 cases). The budget hint (`:641`) gives the same advice in Sanskrit. Note the asymmetry the doc now states correctly: splitting a statement helps the budget and does nothing for the tree — the two limits need opposite remedies, and the v315 text keeps them apart.

No other advice about limits exists in the two documents: a keyword sweep (`split`, `smaller`, `fewer`, `raise`, `increase`, `avoid`, `reduce`, `break`, `workaround`, `budget`, `256`, `expanded source`, `MAXCAP`, `nested calls`) finds only the size-limits section (the other hits are unrelated: `:809` design tie-breaker, `:812` privilege elevation, MEMORY-MODEL `:45` pop/dequeue reducing length). The 256-statement cap (`BLOCK_STMT_CAP equ 256`, `:36`), the 128 KiB expanded-source cap (`IMPORT_BUF_CAP equ 131072`, `:33`), the 6-argument cap and the 128-function cap are not mentioned in the docs at all, so there is no advice about them to check — a gap in coverage, not a wrong sentence.

### A correction to my own R152 report — wrong no. 9 was a misquote

R152's wrong no. 9 quoted §16 as saying "A `kosh` grows until the arena is full (1 GiB) or a region's 64 MiB." That sentence appears verbatim in **neither** doc at v314 or v315 (grep for "grows until", "until the arena", "arena is full": zero hits in both docs at both bases). The §16 text it appears to rest on (`:956-959`) says the opposite: elements move "into a region of their own past 64 KiB", and "when a `kosh` outgrows it the elements move to a larger one" — a region is `max(2*new, R101A_REGION)` and grows beyond 64 MiB; the binding cap is `R128_MAXCAP` = 2^40 elements (`src/sutram_compiler.asm:21354`). So R152's no. 9 is a paraphrase that overstates what the doc says; there is no sentence to fix, and the code fact it rests on stands. The R152 count is therefore restated: **19 locatable wrong claims, not 20** — the other 19 stand as reported, re-verified at v315 in the table below. The correction is recorded here rather than silently dropped, because the R152 report is the record Sarvam reads.

### The R152 twenty at v315 — 19 still wrong, 0 fixed

| # | R152 claim (doc line at v314) | Doc line at v315 | Status | Note |
|---|---|---|---|---|
| 1 | :13 every-kosh-has-its-own-region | :13 | STILL WRONG | Doc text unchanged; code unchanged. |
| 2 | :19 cannot-drift | :19 | STILL WRONG | Doc text unchanged. The other items are the evidence. |
| 3 | :303 likha 3-arg first-must-be-string-literal | :303 | STILL WRONG | Doc text unchanged; contradicts :331, unchanged. |
| 4 | :376 at-most-two-modules | :376 | STILL WRONG | Doc text unchanged; 7-module example still in tree. |
| 5 | :438 s+k → E_VARTANI_CAT | :438 | STILL WRONG | Doc text unchanged; rfx kosh-first order unchanged in the v315 diff. |
| 6 | :945-946 'rikta kosh se' | :945 | STILL WRONG | Doc text unchanged. |
| 7 | :995 slice descriptor 'three words' | :995 | STILL WRONG | Doc text unchanged; descriptor is two words. |
| 8 | :995 'crashed (confirmed)' | :996 | STILL WRONG | Doc text unchanged; no crash demonstrated. |
| 9 | §16 "grows until the arena is full (1 GiB) or a region's 64 MiB" | — | NOT LOCATABLE VERBATIM | See the correction above. No sentence to fix. |
| 10 | §19 parimana 16-byte header / 8272 | :1411 / :1416 | STILL WRONG | Doc text unchanged (+3 line shift). Header is 32 bytes; 8,224. |
| 11 | §19 parimita 'its own region' reason | :1460 | STILL WRONG | Doc text unchanged (+3). Operative claim holds; reason wrong for small koshes. |
| 12 | §19 100 MB / 400 MB per-kosh-region | :1392 | STILL WRONG | Doc text unchanged (+3). Model ended at v301. |
| 13 | :1061 '344 examples' | :1064 | STILL WRONG | Doc text unchanged (+3). Recounted at v315: 331 top-level / 347 recursive; lib still 310. |
| 14 | :1062 'R148's measured boundary' | :1065 | STILL WRONG | Doc text unchanged (+3). R148 report: 0 hits for 16385. |
| 15 | Header box v300 numbers (suite 315, gates 65/1/1, installer v243) | :3 | STILL WRONG | Doc text unchanged. Stale snapshot. |
| 16 | §19 row 2 'likh' covered by scratch check | :1309 | STILL WRONG | Doc text unchanged (+3). `BN_LIKH` not in `r73_check_call`; no `ge_call` handler. |
| 17 | MEMORY-MODEL §1 push rejects param growth | :42 | STILL WRONG | Body unchanged (only the status line changed, `:1` now v315/R154). |
| 18 | MEMORY-MODEL §1/§2 growth updates variable pointer / no free | :44 | STILL WRONG | Body unchanged. Descriptor update + munmap/VirtualFree exist. |
| 19 | MEMORY-MODEL §3 rejection motivation / aliases | :86 | STILL WRONG | Body unchanged. Rejection gone; aliases updated via descriptor. |
| 20 | MEMORY-MODEL §7 'no munmap/free emission anywhere' | :189 | STILL WRONG | Body unchanged. munmap at `r65_arena.inc:713`, VirtualFree in `winrt_blob.asm`. |

The docs diff v314→v315 is 17 changed lines and touches only the size-limits section (`:1042-1060`, the tree-limit advice rewritten and `E_VRIKSHA_SEEMA` named) and the MEMORY-MODEL status line (`:1`, v314/R152 → v315/R154). Everything else in the two documents is byte-identical, which is why 19 of the 20 are still wrong in place.

### The brief's shared-state claims, verified at v315

**`E_VRIKSHA_SEEMA` — EXISTS and is emitted; the reference says the same.** `E_VRIKSHA_SEEMA` now occurs in `src/` (was zero hits at v314):

- `src/sutram_compiler.asm:641` — the analysis-budget hint mentions it ("`vakya-vriksha-seema ('vakya-vriksh seema atikram', E_VRIKSHA_SEEMA) prithak, tasyam --analysis-steps na sahayyam karoti`").
- `src/sutram_compiler.asm:644` — `r152_ast_hint`: "`Sutram truti [E_VRIKSHA_SEEMA]: karyakramasya vakya-vrikshah purnah (3 MiB, 43690 granthayah) - iyam vakya-vriksha-seema, na parikshana-seema (E_VAKYA_SEEMA); --analysis-steps atra na sahayyam karoti.`, then `Sanket: karyakramam laghum kuru - nyunani yoj-pratimanani, laghutarah karyakramah (anyeshu karyakrameshu vibhajya); vakyanam vibhajanam vriksham na laghayati.`" — "make the program smaller — fewer yoj-modules, a smaller program (split into other programs); splitting statements does not shrink the tree."

Emission: `r152_ast_full` (`:7740-7743`) prints the plain message `msg_ast_overflow` ("`Sutram truti: vakya-vriksh seema atikram`", `:1454`) and then `r152_ast_hint`, via `capacity_fail`. Both overflow entries (`.rabe_overflow` for `AST_BLOCK` extra, `:7757`; `.aa_overflow` for node allocation, `:7850`) jump to `r152_ast_full`. So AST exhaustion now has its own code, and the hint says splitting statements does not shrink the AST — the brief's claim holds exactly.

The reference's size-limits section (`:1042-1060`) says the same: "When it is full: `Sutram truti: vakya-vriksh seema atikram` (the line the language packs translate), then `Sutram truti [E_VRIKSHA_SEEMA]: ... iyam vakya-vriksha-seema, na parikshana-seema (E_VAKYA_SEEMA)`". Two parts check out: the first line IS the line the packs translate — `msg_ast_overflow` is a sandesh-table entry (`src/r11_sandesh.inc:104`, `dq msg_ast_overflow`) — while the hint is printed directly, not through the table, so under `--lang` the first line translates and the hint stays Sanskrit, which is what the doc's phrasing says. And the doc's paraphrase of the Sanket ("Make the program smaller: bring in fewer modules, or split the program into separate programs. Splitting a statement does not help") is faithful to the Sanskrit hint quoted above.

**Closure by construction — counts hold, line numbers are stale.** The brief: "`call r142_gen_expr_body` and `call r142_gen_stmt_body` occur only at 21425 and 18863, the two wrappers, and `r142_checked` is raised in exactly three places, each immediately after a walk."

- **Call sites — one each, but not at the brief's lines.** At v315: `call r142_gen_stmt_body` occurs once, `src/sutram_compiler.asm:18915` (inside `gen_stmt`); `call r142_gen_expr_body` occurs once, `:21477` (inside `gen_expr`). At v314 they were `:18913` and `:21475`. The brief's 21425/18863 match base `0fb61357` (the R148/R149 base) — verified by grep there — so the brief cites R148-era lines, stale at v315 by two bases. The substance holds: exactly one call each, both inside the two wrappers, and no other `call r142_gen_*_body` exists in `src/` or `win/`.
- **`r142_checked` raised in exactly three places — verified.** The `inc qword [rel r142_checked]` sites at v315 are `:18413`, `:18911`, `:21475` (v314: `:18411`, `:18909`, `:21473`). No other raising exists: the only other mentions are the `resq` (`:1577`), the `cmp` (`:21468`), the three matching `dec`s, and comments. Each raising follows a walk: `:18911` (`gen_stmt`) has `call r137_check_stmt` immediately before (`:18909-18911`) — literally immediately after the walk; `:21475` (`gen_expr`) likewise (`:21473-21475`); `:18413` (module-level initializer entry, `r56`) has the walk first, then the module-`vitti` door (`call r134_holds_kosh`, with a jump to `r126_fail_door` on failure), then the `inc` — so "immediately after a walk" is literally true for two raisings and true in substance for the third: the `inc` is raised only after the expression has been walked (and door-checked); the door sits between walk and `inc`, it does not precede the walk.
- **The R149 exception still stands.** `r82_param_checks` still exists at v315 (`:10975`, called at `:18714`) and still runs with the flag at 0, relying on the fallback walk inside `gen_expr` — the brief's closure-by-construction sentence does not mention it, and it is the one entry the R149 correction already recorded. It does not break the count (it is not a fourth raising), but the sentence as briefed is complete only with that exception attached.

### Checks by name — every E-code the docs name exists

All 39 distinct `E_*` tokens named in the two documents were grepped in `src/` (`.asm`/`.inc`), `win/`, and `lib/`. Every one exists in `src/` or `lib/`; none is invented. The three library-only codes (`E_PHALA_SEEMA`, `E_MULYA_AYOGYA`, `E_AKARA_ASAMYA` — 0 hits in `src/`, 11/8/4 hits in `lib/`) are described by the docs as library refusals (§3a table), which is what they are. `E_VRIKSHA_SEEMA` is new in `src/` at v315 (see above). `E_CODE` (`:229`) is the doc's generic `[E_CODE]` placeholder for the tag format, not a claimed code; `E_KOSH_*` (`:269`) is a wildcard for five hint names. One nuance, already in R152's inventory and worth restating: `E_LIKHA_TRAYA` exists as a string (`rfx_lk_hdr`, `:503`) but its check is dead — `rfx_check_likha` starts with `ret` ("R105: likha(a, \" \", b) prints three values; no refusal", `:8739-8741`) — and the doc describes it in the past tense ("v286 refused that form", `:330`), which is accurate history, not a live-claim error.

### Closure claims R152 left unread — all four HOLD

1. **`:122` — "`yadi dosh` cannot catch it" (a library Stop).** The Stop channel is `nishedha(cond, msg)` (keyword `abhava`, `KW_NISHEDHA`): "nishedha(cond, \"message\") — the library's fatal channel" (`:15573`); codegen "if cond is false, exit with error code 1" (`:20571`), writing the message to stderr then `sys_exit(1)`. A process exit is not a phal failure, so `yadi dosh` — which catches `dosh` propagation — cannot catch it. Argument: the exit, not a refusal. HOLDS.
2. **`:1027` — "A function value's target … can reach a `kosh` only through its arguments (a whole `kosh` is never given to one, `E_KOSH_DVARA`)".** Argument: the walk's `.funcall` door — for a function value (`r23_call_is_indirect` true) no parameter is known to be `vibhag`, so every argument goes through `.num` (`:28533-28544`: "a kosh to a parameter is r126_check_untyped_arg's (E_KOSH_DVARA)"), and the kind rules refuse a `kosh` in every other channel (module `vitti`, mala cell, field, raw builtin, `?:`, `siddhi`/`dosh`, second-name return — `:1090-1098`). A `kosh` therefore cannot reach the target except as an argument, and as an argument to an untyped (function-value) call it is refused. HOLDS.
3. **`:1085` — "no path decides a name's kind, so the kind is the same at every point of the `prakriya`".** Argument: the kind is a single per-function table entry — `kosh_vars` is "names in current generated-function scope" (`:1548`), filled by `mark_kosh_var` (`:27729-27745`), read by `is_kosh_var` (`:29432-29456`) — and changing a name's kind is refused (`E_VITTI_PRAKAR`, R126/R128, v301), so a branch that would assign a `kosh` to a number-named `vitti` is refused even if the branch never runs: the walk visits every statement regardless of reachability. HOLDS.
4. **`:1221` — the `padh_ya` example "never fails: a bad number counts as the default".** The example's only failing call is `sankhya_padh(s)`, and it sits inside `yadi dosh (q = sankhya_padh(s))`, which returns the default `mool` on failure; `nivartanam mool` / `nivartanam q` cannot fail. HOLDS by reading of the example (reading inference: the example is inline in the doc, not a tree file).

### What still holds

The rest of the two documents stands as R152 left it: the 144 holds are untouched by the v315 docs diff (only the size-limits section and one status line changed) and by the v315 code diff (three hunks, none touching the code the holds rest on), with two strengthenings worth naming — the size-limits section is now correct about both limits and their remedies, and the `r58_fold_tree` guard now recognises slices and kosh-holders itself (`:31783-31793`, "R154 (Muse's reading, R150)"), so the doc's `:1092` claim (`k+0` → `E_KOSH_GANIT`) no longer rests on the walk alone. The docs still do not repeat any of the R151 brief's errors (no `r23_check_call`, no "two limits name themselves" phrasing — the v315 text now correctly says the tree limit *gained* its code).

---

## Task 2 — the symbol rule, short and usable (for the method notes)

The full rule, with the two catches and the existing-check analysis, is in the R152 report (Task 3). This is the short version, written to be used, not studied.

**The one-line version:** a cited label is not a fact until a definition grep at the base returns it with file + line.

**Writer — before sending a brief or a report, for every code label you cite:**

1. Run one grep, from the repo root, at the base you are writing about:
   ```
   grep -rn "^<label>:" src/ src/*.inc win/
   ```
2. Require **one hit that is a definition** — the label at the start of a line, followed by `:`, in a `.asm` or `.inc` file. A `call <label>` hit does not count (it proves something calls the name, not that it is defined). A hit in a `.md` file does not count (a mention in a brief is exactly how `r157` survived — its only occurrence was the brief citing it).
3. **Cite the definition, not just the name** — file + line at a named commit. A label without file + line is an unverified claim. Names here are systematic (`r<round>_<snake>`), so an invented one *looks* right — `r157` and `r23_check_call` both did. The line number is the part that cannot be faked without being checked.
4. **Grep the whole assembly unit, not just the main file** — cover `src/*.inc` and `win/` too. The 133-vs-146 lesson: counting only `src/sutram_compiler.asm` missed 13 `call gen_expr` sites in the includes. A label that lives only in an include is still real, and a writer who greps only the main file will wrongly conclude it does not exist.
5. **If the grep is empty, do not cite the name as a code fact.** Describe the behaviour in words without the name, or write "named in [brief], not found in the tree at [commit]" and ask the brief's author for the file + line. The claim becomes a question to the author instead of a fact in the record.

**Reviewer — checking someone else's brief or report:**

1. **The same grep, in reverse.** For each cited label, run the definition grep at the cited commit. A citation without file + line gets flagged before it gets read — the file + line is what made both inventions checkable in minutes rather than arguable for a round.
2. **Recount, don't carry.** Line numbers drift between bases (`r137_check_stmt`: `28402` at `0fb61357` → `28452` at v314; `r129_check_call`: `28771` → `28908`). A line number cited at the wrong base is stale, not wrong — re-grep at the base you are reading.

**The limit, in one sentence:** the grep proves a label *exists*, not that it does what the writer claims — that still needs the file + line read, and no grep replaces it.

---

## Task 3 — the whole uninstall: for each thing removed, is there a record proving the installer put it there?

**Files read:** `windows/native-installer/uninstall-core.ps1` (284 lines, in full) and the state-writing side of `windows/native-installer/install-core.ps1` (serializer `:851-863`, `InstallLogSHA256` `:881`, registry writes `:809-848`, shortcut functions `:395-452`, PATH functions `:269-298`, `:731-751`), plus the v314→v315 diff of both files (178 + 77 lines) and the R151/R152 reports for the four-record history.

### Verdict first

**Most removals are now recorded. Three are not — two are live data-loss paths, one is a residual with no realistic user harm.**

The v315 uninstall is, on the whole, the answer to the R151/R152 findings: the class tree is no longer deleted whole (R151 pair 3 is closed — values go only on value equality, keys only when empty); PATH removal is by the recorded exact text (the R152 narrow residual — same-directory differently-spelled entry — is closed by `Remove-UserPathEntryOnce`); shortcuts go only on a recorded path|SHA-256 hash match; the manifest is a hash record for every payload file. What remains without a record:

1. **The legacy-shortcut ownership claim (LIVE, shared-state item 1 — confirmed).** `Test-ShortcutSays` (`install-core.ps1:412-418`) compares only the four fields the installer writes — TargetPath, Arguments, WorkingDirectory, IconLocation — and never reads Description, Hotkey, or WindowStyle. A legacy (hashless, pre-v315) link changed only in one of those three fields is still accepted as unchanged. That acceptance is what lets the link be removed: at a reinstall with the desktop checkbox off, `Remove-OwnedShortcut` deletes it on the spot (`install-core.ps1:805`, `:449-452`); at any reinstall, `Set-OwnedShortcut` rewrites it and records it with a hash (`:428-448`), and the next uninstall deletes it on hash match (`uninstall-core.ps1:168`). The user's customized link is gone either way.
2. **The Uninstall registry key, deleted whole with `-Recurse` (`uninstall-core.ps1:216-219`).** The only gate is `InstallLocation -eq $InstallDir`. The installer writes eight values under that key (`install-core.ps1:837-848`) and records none of them; any value under the key that the installer did not write is deleted with it. Concrete scenario: the user adds their own value under `HKCU\…\Uninstall\Sutram`, or a deployment tool stamps one there. Low severity (Sutram-namespaced key; install overwrites its eight values on every install anyway), but by the brief's strict question it has no record. Suggested fix shape (if the owner wants it): delete the eight named values when they still equal what the installer set, then delete the key only if nothing is left — the same shape the class tree got in R154.
3. **The `.sm\OpenWithProgids` `Sutram.Source` value (`uninstall-core.ps1:203`) — residual, no realistic user harm.** Removed with no per-value record and no value check, gated only on the class-command match (`:184`). The value's content is a constant empty string and only Sutram registers that ProgID, so there is no realistic user-owned thing that could be removed — named for completeness, not as a live path.

Everything else uninstall removes has a record proving the installer put exactly that thing there — the full table follows.

### The table — every removal uninstall performs

| # | What is removed | Uninstall lines | Record proving the installer put it there | Re-check before removal | Verdict |
|---|---|---|---|---|---|
| 1 | One PATH entry | `:151` → `Remove-UserPathEntryOnce` `:42-60` | `PathAdded` — the exact text the installer recorded adding (`install-core.ps1:858`, `:731-751`) | Removes only the first entry whose trimmed text equals the recorded text (case-insensitive); nothing when no record | **RECORDED** |
| 2 | Start-menu / desktop shortcuts in `OwnedShortcuts` | `:158-172`, removal `:168` | `OwnedShortcuts` entry `"<base64 path>\|<SHA-256 of the .lnk as written>"` (`install-core.ps1:856`, `:447`) | Current SHA-256 must equal the recorded hash; parent must be StartMenu\Programs\Sutram or Desktop; must end `.lnk`; hashless entries skipped (`:160`, `:163-166`) | **RECORDED** |
| 3 | The Start-menu folder `Programs\Sutram` | `:173` | Installer-created folder (the four links above are created in it) | Removed only if empty (`Get-ChildItem … -First 1` is null) | **RECORDED** (emptiness is the check) |
| 4 | `Sutram.Source\shell\open\command` default value | `:185-188` (DeleteValue) inside the command-match branch `:184` | Value must still equal the expected command, reconstructed from `$InstallDir` (`:184`); the installer wrote exactly this value (`install-core.ps1:817-818`) | Current value `eq` expected command, else nothing in the block is touched | **RECORDED** |
| 5 | `Sutram.Source\DefaultIcon` default value | `:185-188` (same loop) | Value must still equal the expected icon path (`install-core.ps1:820`) | Same value-equality check | **RECORDED** |
| 6 | The `Sutram.Source` keys themselves (command, open, shell, DefaultIcon, root) | `:189-197` (DeleteSubKey) | — | Each key deleted only if `ValueCount -eq 0 -and SubKeyCount -eq 0`; anything else inside keeps it (and is logged) | **RECORDED** in effect — only empty keys go |
| 7 | `.sm` default value | `:198-202` (DeleteValue) | `AssociationSet` — the value the installer recorded setting (`install-core.ps1:862`, `:823-833`) | Recorded value present AND current default still equals it (`:199-200`); nested inside the command-match branch | **RECORDED** |
| 8 | `.sm\OpenWithProgids` value `Sutram.Source` | `:203` (Remove-ItemProperty) | None per-value; gated only on the class-command match (`:184`) | None — no value check (the value is always the constant `''`) | **NO PER-VALUE RECORD** — residual, see §3 |
| 9 | `.sm\OpenWithProgids` and `.sm` keys | `:204-212` (DeleteSubKey) | — | Each deleted only if empty (no value, no subkey); another program's association keeps them | **RECORDED** in effect — only empty keys go |
| 10 | The Uninstall registry key `HKCU\…\Uninstall\Sutram`, whole tree | `:216-219` (`Remove-Item -Recurse -Force`) | None per-value; the installer writes 8 values there (`install-core.ps1:837-848`) and records none | Only `InstallLocation -eq $InstallDir` (`:218`) | **NO RECORD** — data-loss path, see §2 |
| 11 | Payload files listed in `payload.manifest.sha256` | `:221` → `Remove-ManifestFiles` `:100-129`, removal `:111` | The manifest itself: `"<SHA-256> *<relative path>"` per file, written by the installer | Current SHA-256 must equal the manifest hash; a user-modified file is logged and kept; every path is confined under the install root and reparse points refuse | **RECORDED** |
| 12 | Payload files listed in `payload.pending.sha256` | `:223` → same function | The pending manifest (same hash record, for an interrupted install) | Same hash check | **RECORDED** |
| 13 | Directories under the install root (parents of manifest files) | `:122-127` in `Remove-ManifestFiles` | The manifest (they are parents of recorded files) | Removed only if empty | **RECORDED** in effect |
| 14 | `payload.pending.sha256` (the file itself) | `:228` | Installer-created file, fixed name inside a marker-verified install dir | Exact path; the dir is marker-verified (`:141`) and confined under `%LOCALAPPDATA%\Programs` (`:138-139`) | **RECORDED** |
| 15 | `install-journal.log` | `:229` | Installer-created (copied from the transaction journal at install, `install-core.ps1:877`) | Exact path | **RECORDED** |
| 16 | `payload.manifest.sha256` (the file itself) | `:234` | Installer-created manifest file | Exact path | **RECORDED** |
| 17 | `install-state.ini` (the state file itself) | `:235` | Installer-created state file | Exact path | **RECORDED** |
| 18 | `.sutram-install` (the marker) | `:236` | Installer-created marker; its exact text is what authorized the uninstall (`:141`) | Exact path | **RECORDED** |
| 19 | `Sutram-Uninstall.exe` (the uninstaller itself) | `:240-248`, removal `:243` | `UninstallerSHA256` — the recorded hash of the uninstaller (`install-core.ps1:863`); checked before any removal (`uninstall-core.ps1:147-149`) | Self-hash must equal the record, else the uninstall aborts before removing anything | **RECORDED** |
| 20 | `install.log` | `:250-252` | `InstallLogSHA256` (`install-core.ps1:881`) | Current hash must equal the record | **RECORDED** |
| 21 | The install directory itself | `:254-255` | Installer-created dir (marker-verified, confined under `%LOCALAPPDATA%\Programs`) | Removed only if empty (`Get-ChildItem -Force -First 1` is null) | **RECORDED** in effect |
| 22 | The wizard staging temp dir (`%TEMP%\STMxxxx.tmp`): `uninstall.log`, `uninstall-core.ps1`, and the dir | `:264-276` (`[IO.File]::Delete` ×2, `[IO.Directory]::Delete($stageDir, $false)`) | Exact names + strict shape | Parent must be `%TEMP%`, name must match `^STM[0-9A-Fa-f]{1,8}\.tmp$`, the dir must hold exactly the two files `uninstall-core.ps1` and `uninstall.log`, and the log must be inside it; the dir delete is non-recursive, so anything else in it keeps it | **RECORDED** |

### What uninstall deliberately does NOT remove

- `*.sutram-partial` files (`:225-227`): logged and left in place — "its suffix does not prove the installer wrote it" (R137 I1). Same at install time.
- The `<folder>.sutram-transaction` folder (`:231-233`): logged and left — it holds a stopped installation's journal and backups, "the user's only copy of that installation".
- User-modified payload files: preserved by the manifest hash check (`:109-113` in `Remove-ManifestFiles`).
- Hashless legacy shortcuts and shortcuts changed since the installer wrote them: skipped / kept with a log line (`:160`, `:169`).
- Non-empty directories and the install dir itself when anything remains in it.
- A shortcut recorded in `OwnedShortcuts` whose parent is neither the Start menu nor the Desktop: skipped (`:163-166`).

### §1 — The legacy-shortcut ownership claim (LIVE)

**Verified in the v315 code. The brief's shared-state item 1 is accurate in substance; one phrase in it is imprecise (see the correction below).**

`Test-ShortcutSays` (`install-core.ps1:412-418`):

```powershell
function Test-ShortcutSays([string]$Path,[string]$Target,[string]$Arguments,[string]$WorkingDir,[string]$Icon) {
    # every field this installer writes, as it would write it now (for a record from before v315, which has no hash)
    try {
        $sc = (New-Object -ComObject WScript.Shell).CreateShortcut($Path)
        return ($sc.TargetPath -eq $Target -and $sc.Arguments -eq $Arguments -and $sc.WorkingDirectory -eq $WorkingDir -and
                ($sc.IconLocation -replace ',0$','') -eq $Icon)
    } catch { return $false }
}
```

`Test-OwnedShortcut` (`:420-427`): if the old record has a hash, the hash must match; if the old record is hashless (`''` — "named without a hash (written before v315)", `Get-OldShortcutRecord` `:395-411`), the answer is `Test-ShortcutSays`. `Set-OwnedShortcut` (`:428-448`): if the link exists and `Test-OwnedShortcut` is false it returns `'preserved'`; otherwise it rewrites the link (sets the four fields, `$sc.Save()`) and records `"<base64 path>|<SHA-256>"` with the new hash.

**What it does not compare.** The comment says "every field this installer writes" — and that is exactly the gap. A `.lnk` carries more fields than the installer writes: **Description, Hotkey, and WindowStyle** are properties of the same `WScript.Shell` shortcut object, the installer never sets any of them (`Set-OwnedShortcut` sets only TargetPath, Arguments, WorkingDirectory, IconLocation), and `Test-ShortcutSays` never reads any of them. So a legacy link changed **only** in Description, Hotkey, or WindowStyle passes the test.

Correction to the brief's wording: the shared state says the function "compares only target". It compares four fields (target, arguments, working directory, icon), not one. The substance is unchanged — the unchecked set is exactly {Description, Hotkey, WindowStyle} — but the precise statement is "compares only the fields the installer writes", not "compares only target".

**How the link is removed — two ways, both from the same acceptance.** The uninstall-side removal itself (`uninstall-core.ps1:158-172`) is hash-gated and skips hashless entries (`:160`), so a legacy link that is never reinstalled is safe at uninstall. The removal is enabled at reinstall, when the hashless record is converted into a hashed owned record on the strength of the flawed test:

**(a) Reinstall with the desktop checkbox off — removed at install time.** `install-core.ps1:804-805`: when `$DesktopShortcut` is false and a previous desktop link was owned, the installer calls `Remove-OwnedShortcut` on the previous name. That function (`:449-452`) deletes the link whenever `Test-OwnedShortcut` is true — and for a legacy link changed only in Description/Hotkey/WindowStyle, it is true. The user's customized desktop link is deleted during the reinstall, before any uninstall runs.

**(b) Any reinstall — owned, then removed at the next uninstall.** `Set-OwnedShortcut` returns `'updated'`, rewrites the link, and records it with the new hash (`:443-447`). At the next uninstall, the hash matches (`uninstall-core.ps1:168`) and the link is deleted. The user's customized link is gone — the record proving the installer wrote those bytes is formally valid (the hash is of bytes the installer wrote at reinstall), but the ownership decision that produced the record was wrong: it was claimed on a check that ignores the user's customizations. This applies to the start-menu links as well as the desktop link — all five go through `Set-OwnedShortcut`.

The brief's instruction is the right fix and is quoted here because it names the constraint, not just the defect: *"This is not a demand for a more complicated hash: the original bytes were never recorded. Preserve hashless legacy links without claiming ownership."* The hash cannot be retrofitted — the original bytes were never recorded — so the only sound handling of a hashless record is to preserve the link and not record it. That is also what the uninstall side already does (`:160` skips hashless entries); the install side is where the claim is made.

**What is NOT live here.** A legacy link whose target, arguments, working directory, or icon changed is preserved (`Test-ShortcutSays` returns false → `'preserved'`, not recorded). A link recorded with a hash and then changed by the user is kept at uninstall (hash mismatch → log line `:169`, no removal). A user's own link that was never recorded is never removed by the uninstall loop (it is not in `OwnedShortcuts` at all).

**Could not determine from source.** Whether `Set-OwnedShortcut`'s rewrite (`CreateShortcut` loads the existing link, sets four fields, `Save()`) preserves the user's Description/Hotkey/WindowStyle through the rewrite itself — the COM object loads the existing properties and only the four fields are set, so they would be expected to survive the save, but the byte-level behaviour of the COM save cannot be established from source. What is certain from the code is the later deletion: once the link is recorded with a hash, the next uninstall deletes the whole link, customizations included.

### §2 — The Uninstall registry key, deleted whole (`:216-219`)

```powershell
$unKey='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram'
$registered=Get-ItemProperty -LiteralPath $unKey -ErrorAction SilentlyContinue
if ($registered -and $registered.InstallLocation -eq $InstallDir) {
    Remove-Item -LiteralPath $unKey -Recurse -Force
}
```

The installer writes eight values under this key (`install-core.ps1:837-848`: DisplayName, DisplayVersion, Publisher, InstallLocation, DisplayIcon, UninstallString, NoModify, NoRepair) and records **none** of them — there is no per-value record, and the removal is `-Recurse`, so every value and subkey under `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram` goes, not just the eight the installer wrote.

**Concrete scenario.** The user adds their own value under that key — a note, a deployment marker, a value stamped there by a management tool — or another program writes a value there. Uninstall deletes it. The gate (`InstallLocation -eq $InstallDir`) does not help: it checks one of the installer's own values, not whether everything under the key is the installer's.

**Severity, honestly.** Low. The key is Sutram-namespaced, the installer overwrites its eight values with `-Force` on every install (so a user value there already lives under an installer-owned key), and the install side refuses when the key's `InstallLocation` points at a different live Sutram install (`install-core.ps1:494-502`). But by the brief's question — is there a record proving the installer put it there? — for any value other than the eight, the answer is no, and it is named here as a data-loss path. The fix, if the owner wants it, is the same shape as the class tree got in R154: delete the eight named values when they still equal what the installer set, then delete the key only if nothing is left in it.

**What R151 pair 3 looks like now.** The class-tree limb of pair 3 is closed in v315: the whole-tree `Remove-Item -Recurse` is gone, replaced by per-value deletion on value equality (`:185-188`) and per-key deletion only when empty (`:189-197`). A verb a user added under `Sutram.Source` now keeps its key (logged at `:194`). The `OpenWithProgids` limb and the Uninstall-key limb are the two that remain, and they are §3 and §2 of this report respectively.

### §3 — The `.sm\OpenWithProgids` value (`:203`) — residual

```powershell
Remove-ItemProperty -LiteralPath (Join-Path $extKey 'OpenWithProgids') -Name 'Sutram.Source' -ErrorAction SilentlyContinue
```

This sits inside the class-command-match branch (`:184`) but outside the `AssociationSet` condition — it is removed on command match alone, with no value check and no per-value record. The installer creates it (`install-core.ps1:835-836`: `New-ItemProperty … -Name 'Sutram.Source' -Value '' -Force`).

There is no realistic user-owned thing here: the value's content is a constant empty string, so there is no before-state to restore, and only Sutram registers the ProgID `Sutram.Source` — a user would have to hand-register exactly that ProgID for the removal to touch something of theirs, and the command gate ties the removal to this install's registration in any case. It is named because the removal has no direct record, not because a user harm is plausible. Contrast the `.sm` default (row 7), which has the same shape but *does* have the `AssociationSet` record and a current-value re-check.

### The four records, as they now are (for the history)

| Record | v314 (R152) | v315 |
|---|---|---|
| `OwnedShortcuts` | List of base64 paths; uninstall re-checks list + target content | List of `path\|SHA-256`; uninstall checks the hash (`:158-172`); hashless entries skipped |
| `PathOwned` / `PathAdded` | Boolean flag, trusted alone at uninstall | `PathAdded` — the exact text of the one entry added (`install-core.ps1:858`); removal by exact text, one entry only (`uninstall-core.ps1:151`, `:42-60`); `PathOwned` still written but no longer consulted at uninstall |
| `DesktopOwned` / `DesktopLink` | Boolean flag + name; trusted at uninstall on flag + TargetPath | Still written; no longer read at uninstall at all — desktop removal goes through the `OwnedShortcuts` hash loop only |
| `AssociationOwned` / `AssociationSet` | Boolean flag; trusted only with two re-checks | `AssociationSet` — the value set (`'Sutram.Source'`); carried on only while the default is still that value; uninstall deletes the `.sm` default only when the record is present and the current value still equals it |

The R152 rule — "only `OwnedShortcuts` records WHAT was done" — is now the design of all four records: each records what was done (a path + hash, a text, a value), not merely that something was done. The two live gaps in this report are not in the four records themselves: §1 is about a record *claimed* on a check that ignores user changes, and §2 is about a removal that never had a record at all.

### Residuals noted in passing (reading inferences, not numbered paths)

- **PATH, indistinguishable re-set.** If the user deletes the installer's entry and adds their own entry with identical text, uninstall removes the user's entry — text-identical entries cannot be told apart. The installer never adds an entry when an equal one already exists, so this needs the user to re-add the same text after the installer's entry is gone.
- **`.sm` default, indistinguishable re-set.** If the user changes the default away from `Sutram.Source` and later sets it back to `Sutram.Source` themselves while an `AssociationSet` record stands, uninstall deletes the user's explicit choice — the value-equality check cannot tell who set it. Same class as the PATH residual.
- **Manifest files, byte-identical.** A user file at a manifest path with byte-identical contents (same SHA-256) is indistinguishable from the payload file; removal of identical bytes is not a loss in any meaningful sense.
- **Legacy `PathOwned=1`-only state.** A v314 install-state (flag, no `PathAdded`) run under the v315 uninstaller would leave the PATH entry in place — the v315 uninstaller consults only `PathAdded` (`:151`). In practice this does not arise: the staged uninstaller is the one from the installed package, and a v315 install always writes `PathAdded` (converting a legacy `PathOwned=1` at reinstall, `install-core.ps1:736-741`). The failure direction is a leak, not a deletion.

---

## NOT RUN

Windows execution, Wine, the full suite, the gates, any probe program, any build, any installer or uninstaller run — all of it, by the brief's own direction ("Read only. Nothing to compile or run.").

## Could not determine from source (consolidated)

- Whether any native run has exercised the new `E_VRIKSHA_SEEMA` hint path, or the `r58_fold_tree` guard change (both are code facts; runtime behaviour needs execution, forbidden by the brief).
- Whether a native Windows run exercises any of the uninstall paths (v315 has not run on Windows per the brief; Windows testing resumes Tuesday morning).
- Whether `Set-OwnedShortcut`'s COM rewrite preserves a legacy link's Description/Hotkey/WindowStyle through the save (see §1).
- Whether any user has ever actually lost a value under the Uninstall registry key, or a customized legacy shortcut — no such case is recorded in the tree.
- Which document first cited `r23_check_call` (still undetermined; the name occurs in the tree only in the R148 report that corrects it).
- The measurements R152 already left unverifiable (the §3 "+5% to +282%" benchmark, the §6d 4,000-call and byte-count figures, the §16 200-million timing, the §19 measured figures) — unchanged at v315.
