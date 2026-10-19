# Wine harness notes (ROUND-06): how the gate was exercised without Windows

**Environment:** Wine 9.0 (Ubuntu), Xvfb `:99`, PowerShell 7.2.24 (Windows x64 zip) in `C:\pwsh72`.
Wine's own `powershell.exe` stub was replaced by `powershell_shim.c` (forwards the command line).
PowerShell 7.4.6 crashes at start-up under Wine (`UnmanagedPSEntry.Start` NullReferenceException);
7.2 works only with a pseudo-terminal, hence `script -q -c`. `POWERSHELL_TELEMETRY_OPTOUT=1`.

| Run | Tree | What it showed |
|---|---|---|
| 1-2 | fresh build | first runs; found that the Archive module would not load (pwsh in `System32\WindowsPowerShell` is treated as Windows PowerShell) -> moved pwsh out, shim instead |
| 3-5 | harness build | install works with `IconLocation ...,0`; strict-mode `.Count` bug in the gate fixed; uninstall needed the `TargetPath` null guard (Wine) |
| 6 | harness | first complete install -> IDE -> uninstall cycle |
| 7 | harness `-Keyboard` | SendInput Shift+Tab works (after the 40-byte INPUT fix) |
| 8 | fresh build (unpatched) | install fails at `IconLocation` (Wine) -> `run8-fresh-build-install.log` |
| 9 | harness, right after 8 | **retry refused**: `Existing installation ownership metadata is incomplete.` -> `run9-*` |
| 10-11 | harness, `-KeepInstalled` then again | the gate refuses to install over an existing copy: all install checks NOT-RUN -> `run11-*` |
| 12, A, B, C | final | the three logs in `../A-*`, `../B-*`, `../C-*` (script SHA-256 d290257c...) |

Between runs the scratch Wine prefix was reset with `clean_prefix.sh` (deletes only the Sutram folder,
shortcuts, HKCU keys and the PATH value inside the scratch prefix).
