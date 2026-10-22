# R34-02 — `Sutram-Setup.exe` rebuilt, and Windows acceptance passed as documented

**Asked by the owner: "fix and rebuild Sutram-Setup.exe and fix other stuff."** Done on his Windows 11 PC.

## The installer

`Sutram-Setup.exe` **`285470a4a51c14eed7c23bd3342e068b4610f91301da1877f98fa0cfbe8c0c5b`** (1,530,970 bytes),
`Sutram-Setup.sha256` updated. Built by the project's own `windows\native-installer\build-installer.ps1`,
**from a fresh clone of `claude/windows-linker` at `71dad56b`** - so the payload is the committed files, with
`.gitattributes`' line endings, not a working tree's. Its embedded SHA-256 self-test passes.

| In the payload (508 files) | SHA-256 | = the committed file |
|---|---|---|
| `bin\sutram.exe`, `win\sutram.exe` - compiler **v243** | `4533c46c…` | yes |
| **`bin\sutram-link.exe` - new** | `b53dcbbd…` | yes |
| `sutram-ide-gui.exe` - the fixed IDE (R34-01) | `829f8658…` | yes |
| `examples\`, `lib\`, `lang\`, `docs\` | per file | the fresh clone's |

**The compiler is the committed one, not relinked.** `windows\build-windows-setup.ps1` would relink
`win\sutram.exe` with the machine's MSYS2 ld 2.47 (same code, different header bytes) and its preflight checks
`windows\windows-build-integrity.sha256`, which is stale on `main` (its `sutram_gui.asm` and
`sutram_wizard.asm` lines predate R34). So, as R33 did, `build-installer.ps1` was run directly; it takes
`win\sutram.exe` as committed (reproducible from the sources: `evidence-r34/reproducible-build.txt`).

## Fixed

| # | Found | Fix |
|---|---|---|
| 1 | **R4-03 s3: every install left `%TEMP%\STM*.tmp` with `payload.zip` and the scripts** (R3 measured six folders, 4.8 MB). `install-core.ps1` even said *"the wizard deletes its temporary staging directory after success"* - it never did | `sutram_wizard.asm`: after `install-core.ps1` exits 0 (it has already copied the log into the install folder), the files are deleted and the folder removed. **On a failure it stays**: the failure message sends the user to its log. The *uninstall* folder still stays, by design - the uninstaller exits at once so it can delete itself, and its PowerShell writes `uninstall.log` there |
| 2 | `accept-windows.ps1` read `install.log` only from the staging folder | it falls back to the install folder's copy |
| 3 | The acceptance did not know about the linker | `bin\sutram-link.exe` in the install footprint and the uninstall list; a new **required** check, `linker-installed`: the installed compiler's `--object`, the installed linker, the program runs |
| 4 | `tools/check_accept_windows_log.py` **crashed on Windows** printing the log's Devanagari to a cp1252 console | its stdout is UTF-8 |
| 5 | (R34-01) `accept-windows.ps1` did not run on PowerShell 5.1 at all | fixed; this run used the documented command, no `-Root` |

## Windows acceptance - the documented command, real Windows 11

`powershell -NoProfile -ExecutionPolicy Bypass -File tools\accept-windows.ps1`, a standard user, not elevated:

**VERDICT PASS - required 16 PASS / 0 FAIL / 0 NOT-RUN.** Advisory: `install-staging-removed` **PASS** (new);
`shift-tab-keyboard` NOT-RUN (needs `-Keyboard`); `temp-staging-cleaned` FAIL - only the uninstall folder
(`uninstall-core.ps1`, `uninstall.log`), by design.

`tools/check_accept_windows_log.py` on that log: **"ACCEPTED: Windows, not elevated, every required check PASS,
binaries match this tree."** Afterwards: no uninstall key, no install folder, no PATH entry.

The installed IDE's status line, from that run: `पङ्क्तिः 1  स्तम्भः 1 | भाषा: स्वयम् (संस्कृतम्) | अक्षराणि: 476`
(the v290 installer's showed `???????? 1 ??????? 1 | ????: ...`). Evidence: `evidence-r34/accept-windows/`.

## Not done here

- **`windows\windows-build-integrity.sha256` is stale, on `main` too:** `windows\preflight-windows.ps1` (the
  first step of `build-windows-setup.ps1`) refuses on main at c062434f - *"Source integrity mismatch:
  docs/BUILDING.md"* - and on this branch (*"... docs/_newchapter_en.html"*; it hashes every file under `docs/`,
  `examples/`, `windows/` ... as the working tree has it, CRLF on a Windows checkout). So the documented full
  chain cannot run today. Regenerating the manifest is the owner's/Sarvam's call: it is the build's trust root.
- `shift-tab-keyboard` needs a run with `-Keyboard` and hands off the keyboard.
- The uninstall folder (`%TEMP%\STM*.tmp` with `uninstall-core.ps1` and `uninstall.log`, ~12 KB) is left by
  design. Removing it means the uninstall script deleting its own folder at the end, and the acceptance
  harness reading the log from somewhere else.
- This PC's `%TEMP%` still holds 9 `STM*.tmp` folders from earlier installer runs (the old installer). Not
  removed: they are the user's to delete.
