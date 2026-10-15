# Round 65 — Windows installer security comparison

**Source audit only (2026-10-15):** this document compares two existing implementation paths; neither was executed. Only the native, per-user installer should be presented as the supported installation route.

| Concern | Legacy `windows/sutram-installer.nsi` | Supported `windows/native-installer/install-core.ps1` |
| --- | --- | --- |
| Elevation | `RequestExecutionLevel admin` | Runs as a standard user, no UAC requested by the supported native launcher |
| Default destination | `$PROGRAMFILES64\Sutram` | `%LOCALAPPDATA%\Programs\Sutram` |
| Installation metadata | Writes `HKLM\Software\Sutram` and `HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram` | Writes uninstall information under **HKCU** (current user) |
| PATH integration | `EnVar::SetHKLM`, system-wide PATH modification | User `HKCU\Environment\Path` only, optional; broadcasts environment change |
| File associations | Writes to `HKCR\.sm` and `HKCR\Sutram.SourceFile` | Per-user associations only where configured; no HKLM writes |
| Shortcuts | Uses default NSIS `$SMPROGRAMS` and `$DESKTOP` while elevated | Only per-user Start Menu and optional per-user Desktop shortcuts |
| Compiler | NSIS script bundles `bin\sutram_compiler` and `sutram.cmd`; its own finish page says WSL is required | Supported native package embeds the Windows compiler `sutram.exe` and IDE; no WSL needed |
| Integrity / failure | No equivalent manifest verification or bounded self-test visible in legacy .nsi script | Hash-checked overlay, `--self-test`, bounded 8-second compiler pre/post tests, persistent successful `install.log` |
| Uninstall | Removes HKLM uninstall key, `HKCR` associations, system PATH, installed files/shortcuts | Current-user cleanup through `uninstall-core.ps1` / bundled native uninstaller; preserves system-wide state |

## Evidence and scope

The legacy file explicitly contains `InstallDirRegKey HKLM`, `RequestExecutionLevel admin`, `WriteRegStr HKLM`, `WriteRegStr HKCR`, and `EnVar::SetHKLM` in both installation and removal. It must **not** be used as a least-privilege fallback or silently re-enabled.

The supported installer is documented at `windows/native-installer/README.md`, with concrete mutation code in `windows/native-installer/install-core.ps1` and matching uninstall script. It installs under the current user, uses HKCU, and avoids admin. The R62 PowerShell harness remains the Windows acceptance procedure; source inspection and packaging do **not** prove successful installation or icon/GUI display.

**Do not follow legacy WSL/admin guidance from `windows/WINDOWS-README.md` for the current supported native installer.** That document refers to an older path and is not an instruction to elevate, change security policies, or edit system settings. No installer executable, security control, or registry entry was changed by Round 65.

## R67 — the single supported shipping route

The supported builder is `windows/native-installer/build-installer.ps1`. Its
output is `windows/native-installer/output/Sutram-Setup-0.1.0-native-x64.exe`.
It packages `win/sutram.exe` and the repository-root `sutram-ide-gui.exe`,
checks both as PE64, writes a payload manifest, and includes the per-user
install/uninstall scripts. The historical `windows/sutram-installer.nsi`
is NOT the supported shipping path; do not use it as a fallback.

The convenience wrapper `windows/build-windows-setup.ps1` is corrected in
R67 to call `native-installer`, not the nonexistent `windows-installer-native`.
It rebuilds the linked GUI before packaging so it cannot silently pick an
old GUI merely because a file is present. Explicit execution-policy bypass
flags are removed from this wrapper. A machine policy rejection must be
reported, not bypassed or worked around with elevation.

From the approved, standard-user Windows build environment, run the wrapper
with ordinary PowerShell `-NoProfile -File`. This is a source-level correction;
the wrapper and installer have NOT been executed by ChatGPT in R67.
The wrapper's package checks and hashes do not certify window open/close,
Unicode rendering, menu actions, or successful installation.

Nothing here identifies an already-distributed `Sutram-Setup.exe` as freshly
built. Sarvam must record the actual compiler, GUI, payload and setup hashes
from the reviewed build and perform real Windows acceptance. No HKLM,
registry, installed files or OS security settings were changed during R67.
