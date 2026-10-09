# Sutram Windows handoff

## Current working Windows milestone

The Windows compiler host has already built successfully on the target Windows 11 machine and passed its native smoke-test suite. The compiler source and native host source in this package are based on that known-good compiler-host milestone, with the parser fix retained.

## Installer architecture

The installer is a native 64-bit Win32 wizard built directly with MinGW GCC. It does **not** use IExpress, Inno Setup, NSIS, or `windres`.

After GCC creates the PE32+ setup executable, the build appends four package parts to the PE overlay: the Sutram payload ZIP, install script, uninstall script, and Sutram icon. A fixed footer records offsets, sizes, and SHA-256 hashes. The setup's `--self-test` reopens its own EXE and validates every appended part before release or installation.

## Installer behavior

- Welcome / license / destination / options / ready / progress / finish wizard flow.
- Default installation under `Program Files\Sutram`.
- Optional machine PATH entry for `Sutram\bin`.
- Start Menu shortcuts and optional Desktop shortcut.
- Apps & Features uninstall registration.
- SHA-256 package and payload verification before copying files.
- Pre-install and post-copy `sutram.exe` validation.
- Rejects unrelated non-empty destination folders.
- Supports safe same-folder upgrade.
- Rejects a second registered install in a different folder.
- Tracks PATH ownership so uninstall never removes a pre-existing manual PATH entry.
- Tracks Desktop-shortcut ownership so uninstall does not delete a user-owned shortcut.
- Removes only manifest-owned payload files on uninstall.
- Preserves user-created/unknown files in the installation directory.
- Deletes the uninstaller itself only after the process exits.

## Build command

Double-click `BUILD-WINDOWS-SETUP.cmd`, or run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build-windows-setup.ps1
```

Expected output:

`windows-installer-native\output\Sutram-Setup-0.1.0-native-x64.exe`

## Remaining compiler work

The compiler executable itself is native Windows. The generated-program backend still emits the transitional ELF format and must be ported separately to PE64/WinAPI before `.sm -> native Windows .exe` is complete.
