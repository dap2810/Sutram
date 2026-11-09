# Commands and provenance

All Windows commands below ran from `<repo>\build\windows-v309-fixes` on 7 November 2026. Source edits were committed as 664ff188; generated executables stay local. The process-local linker preference was `C:\Program Files\mingw64\bin` prepended to PATH. The ordinary native build scripts and the canonical NASM entry were used; the frozen source-pinned release build was not re-pinned.

```powershell
python tests/r137/test_global_initializers.py --compiler win/sutram.exe --report Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/global-before-expanded.json
& windows/build-windows-native.ps1
Copy-Item win/sutram.exe sutram.exe -Force
python tests/r137/test_global_initializers.py --compiler win/sutram.exe --report Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/global-after.json
python tests/r137/test_slice_number.py --compiler win/sutram.exe
python tests/r134/test_one_predicate.py --compiler win/sutram.exe
python tests/r137/test_analysis_limit.py --nasm nasm --linker 'C:\Program Files\mingw64\bin\ld.exe' --report Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/analysis-limit.json
$env:SUTRAM_EVIDENCE=Join-Path $PWD 'Windows-to-Sarvam\win-v309-final-fixes-2026-11-07'
python tools/test_windows_native.py
& tests/windows/test_installer_lock.ps1
& tests/windows/test_installer_reuse.ps1
& windows/native-installer/build-installer.ps1
python tests/r130/test_installer_engine.py
python tests/r134/test_install_transaction.py
python Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/pin-fix-package.py
```

The original host's first narrower run was 38 cases/19 failures; expanded baseline was 42/21. Baseline tests precede the native rebuild. Commands, source programs, compiler diagnostics, absence/presence of output, and positive native runs are recorded in `global-*.json`. `analysis-limit.json` records the disposable forced-budget build's argv. `native-cases.json` records all suite argv. Build logs are original PowerShell UTF-16 output.

`prepare.py` copies prior proven native harnesses to this round with new backup/setup paths and pins, and copies the actual lock fixture evidence. `prepare-ide.py` derives the isolated IDE test. Subsequent observer corrections are in the final scripts; `recovery-attempt1` retains the earlier scripts. Do not regenerate these scripts over archived executed versions.

```powershell
& Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/initial-install.ps1
python Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/probes.py arithmetic
python Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/probes.py oom
& Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/recovery-tests.ps1
# First attempt was preserved; corrected observer; complete controller repeated once.
& Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/recovery-tests.ps1
& Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/ide.ps1
& Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/run-install.ps1 -Name final-upgrade
python Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/installed-smoke.py
& Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/verify-saved.ps1
```

The recovery controller copies/verifies the known-good install, vacates only guarded canonical paths, stops only its own captured process handles, preserves edited trees, and restores the working backup. Every actual engine command is in the phase JSON. No broad process termination, recursive deletion of user installations, security-policy change or security-suspended-thread resume occurred. GUI windows are visible only for these requested UI tests; helper processes use hidden windows. Final process verification matches PID and start time, including the failed attempt.

```powershell
wsl -d Ubuntu -- git -C /mnt<repo>/build/windows-v309-linux-checkout fetch /mnt<repo> codex/windows-v309-fixes
wsl -d Ubuntu -- git -C /mnt<repo>/build/windows-v309-linux-checkout checkout --detach 664ff188
wsl -d Ubuntu --cd /mnt<repo>/build/windows-v309-linux-checkout python3 /mnt<repo>/build/windows-v309-fixes/Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/linux-check.py
python Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/compare-payloads.py
```

`linux-check.json` contains every nested NASM/linker/build/test argv and full output. The same PE compiler input is copied into the Linux checkout for payload parity. Windows LF sample checkout remains at 8321f843; the three sampled source files are unchanged at final 664ff188. Existing stale CRLF worktree files are normalized only in staging; fresh checkout samples are LF. All 657 files and the manifest are compared, including compiler/linker/GUI/icon bytes.

Observed harness/environment errors: initial Python temporary-directory access was denied by the sandbox and approved reruns succeeded; the initial static-gate filename was mistakenly `test_installer_identity.py` (retained as `r130-command-error.txt`), then the actual `test_installer_engine.py` passed 16/16. The first process-check error was initially suspected to be sandbox access; the same error outside the sandbox established the actual JSON-array/PID-0 observer defect. Logs retain the original filenames and errors. The screenshot guard failure is described in RESULTS and its archived raw record. These are separate from product test results.

No full CI was launched. No automatic workflow was added. Release acceptance and artifact/source-pin promotion remain with Sarvam after independent review.
