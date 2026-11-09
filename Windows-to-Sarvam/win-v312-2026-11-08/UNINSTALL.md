# v312 uninstall — Settings → Apps → Installed apps

The Settings uninstall succeeds, removes the canonical installation and active registration, and creates no new visible console/PowerShell window in the observation. **The strict “nothing survives” criterion fails:** its temporary directory, script and log remain. Nothing was manually deleted before, during or after this uninstall test.

## B1 — timeline and visible result

The monitor started at 2026-11-08T11:21:57.0884463-05:00, before opening the uninstall menu. The v312 entry and Settings confirmation were verified with UI Automation. [Confirmation screenshot](settings-uninstall-confirmation.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*.

- Final Settings confirmation invoked: `2026-11-08T11:25:01.5597599-05:00`.
- Native launcher's child PowerShell engine began: `2026-11-08T11:25:01.7228332-05:00`. Parent PID 25268 is reported by Windows; the short-lived launcher itself was not sampled, so no launcher exit code is claimed.
- The Sutram row disappeared between 4.256 and 4.788 seconds after confirmation.
- Engine PID 16088 exited 0 at `2026-11-08T11:25:08.3593592-05:00`: **6.637 seconds of engine lifetime**, **6.800 seconds from final confirmation**. Observation noticed completion at 6.922 seconds. Menu preparation/approval pauses are excluded from these durations.
- Last product result: Settings has no matching app. [Verified final screenshot](settings-uninstall-final-recheck.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*. No separate uninstall progress bar, completion window or error dialog was observed.

**Console:** zero new visible console/Terminal windows in the WinEvent create/destroy/show/hide hook and repeated top-level sampling. **PowerShell window:** none attributable to uninstall; its child ran without one. Event hook used a dedicated message-pump thread; process/window sampling is not a continuous video. [Observer record](uninstall-observer.json), [engine log](uninstall-engine.log), [Settings timing](settings-uninstall.json).

The account already had a PowerShell pseudoconsole and Windows Terminal hosting this Codex session. They were baselined before uninstall, and their pre-test creation times are recorded in [final-check.json](final-check.json). That existing terminal covered the first post-completion screenshot; it is not evidence of an uninstall-created console. That invalid image is retained locally, not published. Settings was focused again for the valid final image. Thus the precise supported finding is **no new uninstall console**, not that no console existed anywhere on the desktop.

## B2 — commands and active state

All four requested command outputs, with exit codes and the complete Programs listing, are in [after-uninstall-state.json](after-uninstall-state.json). The shell ran from the isolated build directory with PATH freshly read from the machine/user registry, avoiding an inherited stale PATH and a repository-local `sutram.exe`.

| Check | Actual |
| --- | --- |
| `dir "%LOCALAPPDATA%\Programs"` | Canonical `Sutram` absent; 58 earlier preserved Sutram backup/test roots remain, all predating this run |
| `reg query "HKCU\Software\Classes\.sm" /s` | Exit 1, key not found; `.sm\OpenWithProgids` also absent |
| `reg query "HKCU\Environment" /v Path` | Sutram entry removed; user PATH exactly equals the pre-install baseline |
| `where sutram` | Exit 1, `INFO: Could not find files for the given pattern(s).` |
| Sutram.Source / uninstall registration | Both absent |
| Start Menu Sutram folder / desktop shortcut | Both absent; the desktop shortcut was not selected for this installation |
| Transaction directory / lock file | Both absent |
| Machine PATH | Unchanged |

## B3 — exact new survivors

The complete new residue found in the package/transaction/temp inventory is:

- `%USERPROFILE%\AppData\Local\Temp\STM7C1C.tmp` — directory.
- `%USERPROFILE%\AppData\Local\Temp\STM7C1C.tmp\uninstall-core.ps1` — 14901 bytes, SHA-256 `eb53ebd2f9eb817314237bf941bd09e02feee81233b5269d61eaf70b44fc0479`.
- `%USERPROFILE%\AppData\Local\Temp\STM7C1C.tmp\uninstall.log` — 289 bytes, SHA-256 `f766a8cd0f17eebb123301ed6608145f52943f10400e0d9ec0008933d5f87b6a`.

The script hash equals this candidate's `windows/native-installer/uninstall-core.ps1`. The log records removal of the two empty Classes keys, then successful completion. The files were still present at the final check. The new v312 installation was subsequently restored as Task D requests; the after-uninstall snapshot above is the state **before** that reinstall.

## Pre-existing survivors, separately attributed

The following Explorer history keys also survive and are byte/value-identical to the before-uninstall inventory:

- `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.sm` — no direct values, two subkeys.
- `...\.sm\OpenWithList` — `a = sutram-ide-gui.exe`, `MRUList = a`.
- `...\.sm\OpenWithProgids` — `Sutram.Source`, REG_NONE.

These are **different** from the repaired `HKCU\Software\Classes\.sm\OpenWithProgids`. The pre-existing `%TEMP%\STM1E91.tmp` directory also remains with `uninstall-core.ps1` (13,794 bytes) and `uninstall.log` (117 bytes), unchanged by this round. The older preservation registry archive and 58 backup/test roots remain untouched. Every inspected surviving registry key, with its values/empty state, and all 58 root names are listed in [SURVIVORS.md](SURVIVORS.md); exact values/hashes are in the [before](before-uninstall-inventory.json) and [after](after-uninstall-inventory.json) inventories.

This is an existing-account package/state inventory, not a whole-disk or all-Windows-telemetry forensic audit. Older backup trees are named, not recursively rehashed in this round. No clean-machine or absolute machine-wide erasure claim is made.
