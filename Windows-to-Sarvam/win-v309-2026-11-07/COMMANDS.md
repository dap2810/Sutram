# v309 commands, probes and evidence

Tested on the owner's native Windows machine, 7 November 2026. Shell: Windows PowerShell. Working directory: `E:\Github_Projects\Sutram`. The tested checkout was `7c92bc02ff6f81b4903a20c14712ad3fd566b0c4`; setup and compiler hashes are in [payload.json](payload.json). Use that commit to interpret the referenced harness/source, even if main later advances.

## Preparation and identity

The repository was fetched and fast-forwarded before testing. `PROJECT-MASTER.md`, the design charter, AGENTS.md and the incoming v309 request were read. No product source was edited.

```powershell
git fetch origin
git merge --ff-only origin/main
python Windows-to-Sarvam/win-v309-2026-11-07/prepare.py
& Windows-to-Sarvam/win-v309-2026-11-07/preserve.ps1 -Action backup -Name before-v309
& Windows-to-Sarvam/win-v309-2026-11-07/run-install.ps1 -Name initial
```

The first UI helper invocation failed before starting an install engine because control 2002 did not yet exist. Its record was preserved as `initial-observer-error.json`; Click was changed to wait up to five seconds for the control, and the same `-Name initial` command was repeated. `initial.json` records the actual completed upgrade. Both records are included; the current helper is the version used for the completed upgrade and recovery probes.

`prepare.py` obtains and verifies the embedded ZIP/manifest without changing package bytes. The exact setup is copied to `build/windows-v309-2026-11-07/Sutram-Setup.exe` and that snapshot is used for every GUI invocation. The wizard is launched visibly, unelevated, at the canonical default destination, with Add PATH and Desktop Shortcut selected. `run-install.ps1` records the exact child PowerShell command line, including temporary payload, engine, log and destination paths in each phase JSON. Launch IDE is unchecked before clicking Finish; no IDE acceptance is implied.

```powershell
python Windows-to-Sarvam/win-v309-2026-11-07/identity.py --name initial-identity
```

The identity helper constructs PATH from current Machine and User registry values and runs `cmd.exe /d /c where sutram` and `cmd.exe /d /c sutram --version` from the build evidence directory, which has no `sutram.exe`. It also verifies all 657 installed hashes, absence of pending/transaction state, and uninstall registry version 1.0.309.

## Native compiler and memory probes

```powershell
python Windows-to-Sarvam/win-v309-2026-11-07/probes.py arithmetic
python Windows-to-Sarvam/win-v309-2026-11-07/probes.py oom
$env:SUTRAM_EVIDENCE=Join-Path $PWD 'Windows-to-Sarvam\win-v309-2026-11-07'
python tools/test_windows_native.py
```

All seven arithmetic compile commands, output paths, messages and native control commands are recorded as exact argv arrays in [arithmetic/results.json](arithmetic/results.json). Output executables are generated under `build/windows-v309-2026-11-07/`, never committed. Refusal cases require a previously absent output path.

The three OOM compile commands, expanded from `probes.py`, are:

```powershell
& E:\Github_Projects\Sutram\win\sutram.exe E:\Github_Projects\Sutram\Windows-to-Sarvam\win-v309-2026-11-07\oom\B3.sm E:\Github_Projects\Sutram\build\windows-v309-2026-11-07\oom\B3.exe
& E:\Github_Projects\Sutram\win\sutram.exe E:\Github_Projects\Sutram\Windows-to-Sarvam\win-v309-2026-11-07\oom\A3-mandapa.sm E:\Github_Projects\Sutram\build\windows-v309-2026-11-07\oom\A3-mandapa.exe
& E:\Github_Projects\Sutram\win\sutram.exe E:\Github_Projects\Sutram\Windows-to-Sarvam\win-v309-2026-11-07\oom\A3-nirmmita-touch-pages.sm E:\Github_Projects\Sutram\build\windows-v309-2026-11-07\oom\A3-nirmmita-touch-pages.exe
```

`probes.py oom` invokes the unchanged `tests/windows/job_runner.py` at the pinned commit. B3 runs at 448, 480, 512, 544, 576, 608 and 640 MiB, three times each; mandapa at 64 MiB ten times; page-touch at 64 MiB once. It checks the accepted Windows Job Object limit before starting each child. This is per-process commit accounting, not a Wine or host memory simulation. [Every native argv, limit, cwd, exit, peak, runtime and message](oom/results.json); each corresponding subfolder preserves stderr/stdout bytes. No child timed out.

The native suite uses the unmodified `tools/test_windows_native.py` and frozen expectations. All case commands/results are in [native-cases.json](native-cases.json). Its summary is 322 PASS, 3 NO_EXPECTATION, 5 SKIP_SIDE_EFFECT_OR_INLINE_ASM and 1 SKIP_LINUX_RAW_SYSCALL. There are no FAIL, COMPILE_FAIL or TIMEOUT rows. This is a Windows suite result, not a new Linux result.

## Interrupted installation and restoration

```powershell
& Windows-to-Sarvam/win-v309-2026-11-07/recovery-tests.ps1
```

This orchestrator checks the successful initial install, makes a hash-verified `working-v309` backup, then invokes:

```powershell
& Windows-to-Sarvam/win-v309-2026-11-07/preserve.ps1 -Action vacate -Name before-d1
& Windows-to-Sarvam/win-v309-2026-11-07/run-install.ps1 -Name d1-stop -Moment before
& Windows-to-Sarvam/win-v309-2026-11-07/run-install.ps1 -Name d1-retry
& Windows-to-Sarvam/win-v309-2026-11-07/preserve.ps1 -Action vacate -Name before-d2
& Windows-to-Sarvam/win-v309-2026-11-07/run-install.ps1 -Name d2-stop -Moment after
& Windows-to-Sarvam/win-v309-2026-11-07/run-install.ps1 -Name d2-retry
& Windows-to-Sarvam/win-v309-2026-11-07/preserve.ps1 -Action vacate -Name before-d3
& Windows-to-Sarvam/win-v309-2026-11-07/run-install.ps1 -Name d3-stop -Moment middle
# The controller saves BUILDING.md, appends the documented test line, and saves the edited copy.
& Windows-to-Sarvam/win-v309-2026-11-07/run-install.ps1 -Name d3-retry
```

The initial backup/identity checks and edit operation are in the committed orchestrator. Only the captured test wizard and its discovered child handles are killed; no name-wide stop command is used. Stop boundaries are observed via file existence, not by holding the live engine log open. The D2 journal is read after termination. `preserve.ps1` validates resolved paths and rejects reparse points before recursive copies/moves; it does not delete trees.

The D3 dialog acknowledgement raised a helper error after capturing the product refusal and exit. Consequently the controller's catch path (not its normal final path) ran:

```powershell
& Windows-to-Sarvam/win-v309-2026-11-07/preserve.ps1 -Action restore -Name d3-failed -BackupName working-v309
```

The interrupted tree and transaction were moved aside intact, and the hash-verified working v309 backup was restored. The controller returned exit 1 because of the observer acknowledgement failure. Do not describe it as an entirely passing automation run. The raw observer/error records remain unchanged.

## Read-only follow-up and report generation

```powershell
python Windows-to-Sarvam/win-v309-2026-11-07/identity.py --name final-identity
& Windows-to-Sarvam/win-v309-2026-11-07/verify-saved.ps1
python Windows-to-Sarvam/win-v309-2026-11-07/summarize.py
```

`verify-saved.ps1` checks each owned PID against its recorded creation time, records absence of a lock, runs the requested `certutil`/CRLF commands, and writes `handoff-identity.json`. It performs no installation mutation. `summarize.py` compares the preserved edit with the pre-retry copy and pre-restore hash inventory, verifies raw OOM bytes, derives recovery counters, and writes the reports. It does not rerun D3 or replace the original error record.

Native payload command output is saved in [payload-native-commands.txt](payload-native-commands.txt). The original check and the handoff-time check agree. The report does not claim a fresh Windows rebuild, a torn-journal-write test, an IDE test, a 15-minute installer timeout test, universal memory safety, or release acceptance. No CI run or security-product configuration change was made.

Probe sources and helpers are committed as evidence. The local `.gitattributes` in this evidence folder preserves their recorded bytes; it does not add the missing root Markdown checkout rule. Reproduction of the installer phases must use an isolated working folder and preserve existing user files/backups; the scripts deliberately refuse to replace an existing named backup.
