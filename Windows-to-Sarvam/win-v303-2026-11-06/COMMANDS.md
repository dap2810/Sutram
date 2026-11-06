# Commands and execution record

All commands ran from `E:\Github_Projects\Sutram` unless noted. PowerShell was
non-elevated. Sandbox approval allowed the installer to write the per-user
installation; it did not grant Windows administrator privileges.

## Preparation

```powershell
Get-Content -LiteralPath PROJECT-MASTER.md
Get-Content -LiteralPath docs/sutram-design-parameters.html
Get-Content -LiteralPath 'C:\Users\dmech\Downloads\SUTRAM-WINDOWS-V303.md'
git status --short --branch
git log -3 --oneline
git fetch origin
git log -9 origin/main --oneline
git log -12 origin/main --format='%h %s' -- Sutram-Setup.exe
git show origin/main:ChatGPT-to-Sarvam/ROUND-204-STATIC-IDENTITY.json
git worktree add --detach build/windows-v303-review 27f4fa74
```

The first worktree attempt was denied access to `.git/worktrees`; the identical
command succeeded after sandbox approval. The project guidance, installer
source, and existing Windows harnesses were read before execution.

## Installer invocation

```powershell
powershell -NoProfile -File Windows-to-Sarvam/win-v303-2026-11-06/install.ps1
```

The exact script is retained on review branch `codex/windows-v303-2026-11-06` at
the same evidence path. `ui-helper.ps1` was extracted from the existing
`Windows-to-Sarvam/ide-v297-2026-11-03/run-all.ps1` between
`Add-Type -TypeDefinition` and `$packMenu =`.

The installer invoked this child process, observed through a read-only process
query after the wizard timed out:

```text
powershell.exe -NoProfile -File "C:\Users\dmech\AppData\Local\Temp\STM5B4A.tmp\install-core.ps1" -PayloadZip "C:\Users\dmech\AppData\Local\Temp\STM5B4A.tmp\payload.zip" -InstallDir "C:\Users\dmech\AppData\Local\Programs\Sutram" -SetupExePath "E:\Github_Projects\Sutram\build\windows-v303-review\Sutram-Setup.exe" -LogPath "C:\Users\dmech\AppData\Local\Temp\STM5B4A.tmp\install.log" -AddPath
```

```powershell
Get-CimInstance Win32_Process -Filter "Name='powershell.exe' OR Name='Sutram-Setup.exe'" | Select-Object ProcessId,ParentProcessId,CommandLine | Format-List
Get-Content -LiteralPath 'C:\Users\dmech\AppData\Local\Temp\STM5B4A.tmp\install.log'
Get-Content -LiteralPath 'C:\Users\dmech\AppData\Local\Programs\Sutram\install.log' -Tail 12
```

The sandbox denied the first CIM query; it succeeded after approval. It showed
engine PID 19036, parent PID 35668. Later inspection found that PID gone, matching
the owner's report of manually closing PowerShell.

## Version gate

```powershell
python Windows-to-Sarvam/win-v303-2026-11-06/verify.py identity
Get-FileHash -LiteralPath 'C:\Users\dmech\AppData\Local\Programs\Sutram\bin\sutram.exe'
Get-FileHash -LiteralPath 'C:\Users\dmech\AppData\Local\Sutram\bin\sutram.exe'
Copy-Item -LiteralPath 'C:\Users\dmech\AppData\Local\Temp\STM5B4A.tmp\install.log' -Destination Windows-to-Sarvam/win-v303-2026-11-06/install-at-stop.log
```

The first Python invocation had a syntax error in an unused probe-generation
function and executed no test. After fixing that parenthesis, the identity run
executed these two commands with a 30-second timeout each, in
`build/windows-v303-review/build/v303-probes`:

```text
C:\Users\dmech\AppData\Local\Programs\Sutram\bin\sutram.exe --version
C:\WINDOWS\system32\cmd.exe /d /c "where sutram && sutram --version"
```

Raw outputs, exit codes, timings, and hashes are in `identity.json`. The initial
harness mistakenly compared the entire direct output to one banner line; its
comparison was corrected to the first line. The raw captured output was not
changed. The separate fresh-shell failure remains: it executed the older PATH
entry and printed `Sutram 1.4.0`. The final evidence annotates these distinct
results. No compiler probes or suite were run. Unused drafted probe/suite helpers
remain on the review branch only and are not validated test infrastructure.
