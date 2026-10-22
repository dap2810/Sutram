# Sutram — Windows acceptance, 2026-10-21 (after R34)

- **Where:** the owner's real Windows 11 Pro 10.0.26300 (build 26300.9711), AMD Ryzen 7 7700X, a standard
  user, **not elevated**; Windows PowerShell 5.1.26100.9711.
- **What:** branch `claude/windows-linker` (R34) - compiler v243, `sutram-link.exe`, the fixed IDE, and
  `Sutram-Setup.exe` `285470a4a51c14eed7c23bd3342e068b4610f91301da1877f98fa0cfbe8c0c5b` rebuilt from it.
- **Command, exactly as documented:** `powershell -NoProfile -ExecutionPolicy Bypass -File tools\accept-windows.ps1`

| Check | Result |
|---|---|
| runner-not-elevated, setup-hash-file, setup-self-test | PASS |
| install-wizard (6 pages), install-no-elevation-prompt, install-footprint | PASS |
| devanagari-cli (installed compiler: `योगः = 15`) | PASS |
| **linker-installed** (installed `--object` + `sutram-link.exe`, runs) - new | PASS |
| ide-launches, ide-menus-english, ide-buttons-english, devanagari-ide, tab-indent, shift-tab-dedent, unsaved-guard | PASS |
| uninstall-removes-install, uninstall-folder-gone | PASS |
| install-staging-removed (advisory, new) | PASS |
| shift-tab-keyboard (advisory) | NOT-RUN - needs `-Keyboard` |
| temp-staging-cleaned (advisory) | FAIL - only the uninstall folder holding `uninstall.log`, by design |
| **VERDICT** | **PASS - required 16 PASS / 0 FAIL / 0 NOT-RUN** |

`tools/check_accept_windows_log.py` on the log: **"ACCEPTED: Windows, not elevated, every required check PASS,
binaries match this tree."** The machine was clean before and after (no uninstall key, no install folder, no
PATH entry).

**Compared with the first real run (`WIN-RUN-2026-10-21.md`):** that run needed `-Root` (the script did not
start on PowerShell 5.1), installed v242, showed `????????` in the IDE's status line, and left the install
staging in `%TEMP%`. All four are fixed.

**This is one machine, one run.** It is not a release, and the installer is on a review branch until
Sarvam accepts it. Evidence: `Claude-to-Sarvam/evidence-r34/accept-windows/` (the JSON log, both install and
uninstall logs, the wizard and IDE screenshots, the checker's output). Details: `Claude-to-Sarvam/R34-02-INSTALLER.md`.
