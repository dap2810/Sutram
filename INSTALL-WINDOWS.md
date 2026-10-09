# Installing Sutram on Windows 11

## The quick way

Double-click **`Sutram-Setup.exe`**.

A window opens showing what will be installed and where. Click **Install**.

That is the whole process. No administrator prompt appears, no Windows
security setting is changed, and no reboot is needed.

If the window cannot be created — for example on a session with no
interactive desktop — the installer falls back automatically to a single
Yes/No dialog, so it still works.

**Version note:** the first build you were given had no window at all (it
showed only a Yes/No dialog), and its entry point had a stack-alignment
fault that could stop it running. Both are fixed in this build.

## What gets installed, and where

Everything goes into your own account:

| Thing | Where |
|---|---|
| Program files | `%LOCALAPPDATA%\Programs\Sutram` |
| `sutram` on your PATH | your user PATH only |
| Start Menu | your Start Menu, a folder called *Sutram* |
| Desktop shortcut | optional, a *Sutram Terminal* icon |
| Uninstall entry | `HKCU` (Settings → Apps) |

Nothing is written to `Program Files`, `HKLM`, or any system location. If you
are not the only person using the PC, your install does not affect anyone else.

## What you get

- **Sutram IDE** — a native Windows GUI editor with syntax highlighting,
  including native-script keywords in all ten supported Indian scripts.
- **Sutram Terminal** — a console where `sutram file.sm` compiles and runs.
- The compiler itself, `bin\sutram.exe`, with **no toolchain required**.
  You do not need NASM, Python, Visual Studio, or MinGW.
- Language packs, the standard library, 180 examples, documentation, and the
  six book editions.

## After installing

Open **Sutram Terminal** from the Start Menu and try:

```
sutram --version
sutram examples\hello.sm
```

Or open the **Sutram IDE** and use Ctrl-R to run.

## If the installer does not work

The installer is a thin native launcher; the real work is done by a
PowerShell script it carries inside itself. If the exe is blocked by your
antivirus or by a policy, you can do the same job by hand:

1. Right-click **`install-core.ps1`** in this folder and choose
   *Run with PowerShell*.
2. If that is blocked, open PowerShell in this folder and run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-core.ps1 `
    -PayloadZip .\payload.zip `
    -InstallDir "$env:LOCALAPPDATA\Programs\Sutram" `
    -SetupExePath .\Sutram-Setup.exe `
    -LogPath "$env:TEMP\sutram-install.log" `
    -AddPath -DesktopShortcut
```

Both scripts are per-user and unelevated, exactly like the installer.

## Uninstalling

Settings → Apps → *Sutram* → Uninstall. Or run
`Sutram-Uninstall.exe --uninstall` from the install folder, or use the
Start Menu entry *Uninstall Sutram*.

Your own `.sm` files are never touched, and a PATH entry you added yourself
by hand is left alone.

## Honest status

The installer is a native PE32+ x86-64 Windows executable. It has been
verified on Linux by building it, inspecting its PE header, and checking that
the payload and both scripts are embedded byte-for-byte. It has **not** been
run on a real Windows machine yet — this build is the first one you are
testing. If something goes wrong, the log file named in the error dialog
has the details, and the manual path above always works.
