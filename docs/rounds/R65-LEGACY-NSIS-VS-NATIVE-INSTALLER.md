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
