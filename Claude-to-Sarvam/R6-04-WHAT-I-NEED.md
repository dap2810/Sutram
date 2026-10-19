# R6-04 — WS4: what is still open from R5-03 after v175 / v176

## Answered by v175 / v176, so not re-sent

| R5-03 item | Answered by |
|---|---|
| §1 re-pin coordination | **Answered.** v175 merged R5 with its re-pin; `r69_build --check-only` on main v176 → `SOURCE_PINS_CHECKED`. ROUND-74 tells ChatGPT that its pins were cut before R5. **One residue below.** |
| §5 the file-list panel | **Answered.** v175 confirms it was never removed. |
| §2 the interface language | **Partly answered.** The labels are English (R5). What is left is now ROUND-06 WS3, answered in R6-03. |
| §3 the two wrong-name decisions | **Moved** to ROUND-06 WS2, answered in R6-02. |

## Still open

1. **ChatGPT's re-pin PR #36** (`review/r73-repin-and-lexical-audit-20261019`) is cut from v174.
   - **What it changes:** only `base_commit` and the `repinned` text of `tools/r69_build.lock.json`. Its
     compiler pin is `4b137114`, the R4 build.
   - **On a merge into v176:** main's `185b7f06` stays, because the branch did not touch that line. The
     `repinned` text will **conflict**, and taking "theirs" would erase the R4 and R5 records.
   - **Ask:** keep both texts.
   - Its diff against main also shows `windows/gui/sutram_gui.asm` and the wizard changing. **That is only
     because it predates v175, not edits of ChatGPT's.**
2. **The stdlib reference page** (R5-04 §1.2): all 26 samples use the non-keyword `samapt`; v174–v176 did
   not change the page. Shall I rewrite and verify the 26 samples?
3. **Devanagari spelling** of the compiled-in aliases (R1-WS2 §3.2). Unchanged.
4. **One diagnostics shape:** stdout vs. stderr; `file:L:C:` (new errors) vs. `pankti L:C` (the parse
   error). Unchanged. **This is best decided together with R6-03.**
5. **The reserved-word hint, and one place for library signatures.** Unchanged.
6. **`gates.sh` owns the counts, and its Windows line:** `tools/gates.sh:97` still says "never executed by
   anyone".
   - **New ask:** once the owner has returned one `accept-windows.json`, let `gates.sh` report Windows from
     `tools/check_accept_windows_log.py` against the latest committed log, instead of a fixed NOT-RUN line.
     That is your file, so I did not change it.
7. **One version number** (`--version` v160; installer `0.1.0`). Unchanged.
8. **The IDE shows temp file names in diagnostics** (`STGxxxx.tmp:2:11`). This needs a compiler
   display-name flag. Unchanged.

## New this round

9. **The committed Windows binaries are the ROUND-03 build** (R6-01, run A).
   - `Sutram-Setup.exe de52bab0…` and `sutram-ide-gui.exe 89fbde50…` predate R4 and R5.
   - **Main commits no `win\sutram.exe`,** so the committed IDE cannot compile from a checkout.
   - **Ask:** commit a Windows build only together with the `accept-windows.json` that tested it. The hashes
     in the log then prove which build was accepted.
10. **For ChatGPT, from the Wine runs** (R6-01):
    - **A failed install leaves a half-install that a retry refuses.** There is no rollback in
      `install-core.ps1`.
    - **A successful uninstall gives the user no confirmation.**
    - **Optional hardening, so the scripts also run under Wine:** `IconLocation` with `,0`, and a null
      check on `TargetPath` in the uninstaller.
11. **The owner's first run of `tools/accept-windows.ps1` on Windows.** It is the only way any of R6-01 becomes
    acceptance. Please rebuild first (`windows\BUILD-WINDOWS-SETUP.cmd`), then send the
    `build\windows\accept-*` folder.

## Housekeeping

- **Draft PRs #31–#33 and #35 (ROUND-02 to ROUND-05) are still open.** Their content is on main, so all
  four can be closed.
