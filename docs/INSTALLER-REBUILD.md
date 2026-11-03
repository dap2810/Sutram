# Rebuilding the installer's payload (Windows)

R109. This is the procedure that makes `python3 tools/check_installer_version.py` (the `installer version`
gate) pass. It is run on a real Windows machine by the maintainer; nothing here has been run on Windows by
Claude.

## What the gate reads

`Sutram-Setup.exe` is two things: the **wizard** (the native program that runs) and the **payload** (a zip
the wizard carries and unpacks). The gate reads the version string of the two compilers *in the payload*,
`bin\sutram.exe` and `win\sutram.exe`. The wizard has no version string of its own, so the gate cannot
say "the installer is vNNN" - it says:

```
FAIL payload v243 inside Sutram-Setup.exe (the wizard has no version of its own); compiler v291, packed 2026-10-21; 108 of its 138 lib/lang files differ from the tree: ...
```

That means: the compilers this installer would install are v243, packed on 2026-10-21, and most of the
library and language files it would install are older than the tree's. `Sutram-Setup.sha256` matching the
file proves only that the hash file belongs to this `Sutram-Setup.exe`, not that its payload is current.

## Why rebuild only the installer step

`windows\native-installer\build-installer.ps1` copies the tree's **`win\sutram.exe` unchanged** into the
payload as both `bin\sutram.exe` and `win\sutram.exe`. That binary is the one the guard verified (cross-built
on Linux with `--no-insert-timestamp`, so its bytes are fixed), and its SHA-256 is known in advance.

The full `windows\BUILD-WINDOWS-SETUP.cmd` first runs `build-windows-native.ps1`, which **re-links
`win\sutram.exe`** with the Windows `ld` and no `--no-insert-timestamp`. The program is the same, but its bytes
and hash are not, and it overwrites the tree's verified binary. For this job, do not use it.

## The commands

Requirements: Windows 10 or 11 x64; a checkout of `main` at or after the R109 commit; `nasm.exe` and `ld.exe`
(mingw-w64 binutils) on `PATH` - the wizard is assembled and linked; the compiler is not rebuilt.

In `cmd.exe`, from the repository root:

```
git pull
win\sutram.exe --version
certutil -hashfile win\sutram.exe SHA256
powershell.exe -NoProfile -ExecutionPolicy Bypass -File windows\native-installer\build-installer.ps1
```

`-ExecutionPolicy Bypass` applies to that one PowerShell process only.

**Expected before building** (the v291 tree, R109):

| check | expected |
|---|---|
| `win\sutram.exe --version` | `Sutram 1.0 (v291) - sampurna sutra` |
| `certutil -hashfile win\sutram.exe SHA256` | `324b31da0edbacc2863166fcc5c9485280a01ac3df0622b36c11a7126df2ac28` |

(`certutil` prints the hash in groups or in capitals on some Windows versions; compare the hex digits.) If
either differs, stop: the checkout is not the R109 tree, or `win\sutram.exe` was rebuilt locally.

**Expected after building:** the script ends with `SETUP PASS: embedded SHA-256 self-test. Built ...` and
`Payload staging/evidence retained at <folder>`. Then:

```
certutil -hashfile <folder>\payload\bin\sutram.exe SHA256
certutil -hashfile <folder>\payload\win\sutram.exe SHA256
certutil -hashfile Sutram-Setup.exe SHA256
type Sutram-Setup.sha256
```

- Both payload compilers: **`324b31da0edbacc2863166fcc5c9485280a01ac3df0622b36c11a7126df2ac28`**, the same as
  `win\sutram.exe`.
- `Sutram-Setup.exe`'s hash must equal the first field of `Sutram-Setup.sha256` (the script writes it).
  **Its value cannot be given in advance:** `Compress-Archive` stores each file's time in the zip, and the
  wizard's link stamps the time, so every build has a different hash. The payload compilers' hash is the
  fixed one.

Other inputs the payload copies from the tree unchanged, for reference: `sutram-link.exe`
`5f7a8e202a5d04df88fbbc299b077b114c29a7dd50447194dd2e95ff4a848aa9`, `sutram-ide-gui.exe`
`829f8658de55be045c6273339244d099022b373725ead3681228c00ba3d5c051`, `icons\sutram.ico`
`b48aeb52516433c3cce51ffe436fa04355cb938aa0b5188c60fe7c02f2923ec1`.

Then commit `Sutram-Setup.exe` and `Sutram-Setup.sha256`. On Linux, `python3 tools/check_installer_version.py`
should end:

```
PASS payload v291 = compiler v291 (bin/ and win/sutram.exe, packed <today>; the wizard has no version of its own; 0 of its N lib/lang files differ from the tree; ...)
```

**This goes stale again at the next compiler version.** Each round that bumps the version makes the payload one
version behind until this is run again; the gate will say so in the words above.
