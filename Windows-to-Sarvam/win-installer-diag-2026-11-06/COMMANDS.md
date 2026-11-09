# Installer diagnostic commands

Repository: `<repo>`, main `f77a7464`.
The current package was hashed before launch. Its native wizard was used with
the existing default per-user destination, Add to user PATH selected and Desktop
Shortcut deselected. This was an upgrade attempt, not a fresh installation.

```powershell
Get-FileHash Sutram-Setup.exe -Algorithm SHA256
& .\Windows-to-Sarvam\win-installer-diag-2026-11-06\run.ps1
```

The script verifies a non-elevated token, captures the before state, starts a
PowerShell transcript inside this evidence folder, and starts the visible
wizard. It uses the existing native controls to advance through the license,
destination and component pages. It records the installer's descendants with:

```powershell
Get-CimInstance Win32_Process
Get-Process | Where-Object { $_.ProcessName -match 'powershell|sutram|wscript|cscript' } |
    Select-Object Id,ProcessName,StartTime,CPU
```

Only descendants of the recorded wizard have their command lines retained.
The retry captured its child at one second, observed it absent at ten seconds,
then waited another 60 seconds. The original attempt observed at ten and seventy
seconds and missed the short-lived child. Its unchanged raw records are under
`attempt1/`. `console.py <child-pid> read <output.json>` attaches to that child's
console to read it; no Enter/Y injection was performed because the child had
already exited at the stalled-state observation.

The first script invocation had a PowerShell parser error before any execution;
the missing brace was corrected before either counted installer attempt. The
first attempted window capture after its wrapper had ended returned no windows.
The retry captures within its lifetime; the owner's supplied screenshot records
the modal error itself. Those capture limitations are not installation evidence.

`snapshot.ps1` records raw registry values and types, directory/file hashes,
ownership metadata, installed registration, inherited PATH resolution, and
resolution with PATH reconstructed from persisted machine/user values:

```powershell
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path
reg query "HKCU\Environment" /v Path
where.exe sutram
cmd.exe /d /c sutram --version
Get-ChildItem -LiteralPath "$env:LOCALAPPDATA\Programs\Sutram" -Force
Get-ChildItem -LiteralPath "$env:LOCALAPPDATA\Programs\Sutram\bin" -Force
Get-ChildItem -LiteralPath "$env:LOCALAPPDATA\Programs\Sutram" -Filter '*uninstall*'
```

Environment reconstruction is local to the diagnostic process and restored
afterward. No PATH or registry write was made by the diagnostic script. The
installer's own preflight invokes `--version`/`--help`; no compiler probes were
rerun. No execution-policy change, admin elevation, antivirus change, installer
rebuild, source patch, repair, or uninstall was attempted.

The retry engine log was copied verbatim from its argv `-LogPath` to `engine.log`.
`transcript-tail.txt` is the final 30 lines of `transcript.txt`. The owner's
`Screenshot 2026-11-06 204321.png` is copied unchanged as `owner-error-dialog.png`.
The generated `payload-audit.json` compares the current embedded ZIP manifest
with the before-snapshot file hashes without extracting/installing another copy.

Cleanup checked only the two recorded wizard PIDs against their executable
paths; both had already exited. No unrelated process was closed.

The default staged diff check flags the trailing space after PowerShell's empty
`Configuration Name:` transcript field, including its copied tail. Those raw
lines are preserved as captured. The remaining whitespace check uses
`git -c core.whitespace=-blank-at-eol diff --cached --check` for this commit only;
no repository configuration or test expectation is changed.
