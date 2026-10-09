# Sutram Native Windows Installer

The setup wizard is a native 64-bit Win32 executable built with MinGW GCC only. The release path deliberately avoids resource-compiler dependencies (`windres`), IExpress, and Inno Setup.

After the base PE executable is linked, the build appends:
- `payload.zip` containing Sutram, languages, examples, docs, and payload hashes
- `install-core.ps1`
- `uninstall-core.ps1`
- the Sutram icon
- a fixed package footer containing offsets, sizes, and SHA-256 hashes

`--self-test` validates all four appended package parts against the footer before release. The installer validates them again before extraction.

The PowerShell scripts use Windows PowerShell 5.1 built into supported Windows 10/11 systems; end users do not install PowerShell, MinGW, NASM, Visual Studio, `windres`, Inno Setup, IExpress, WSL, or Linux.

Wizard pages:
1. Welcome
2. License acceptance
3. Install directory and Windows integration options
4. Ready to install
5. Progress
6. Finish / launch Sutram Terminal

The installer is deliberately **per-user and least-privilege**. It never requests UAC elevation: Sutram installs under `%LOCALAPPDATA%\Programs\Sutram`, registers uninstall metadata under `HKCU`, updates only the current user's `PATH`, and creates only current-user Start Menu/Desktop shortcuts. `--self-test` remains elevation-free and validates the hash-protected package overlay.
