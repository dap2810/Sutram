# Installing Sutram on Windows

Read [the installation routes](docs/INSTALLATION-ROUTES.md) first. The current
clean-source audit is not a release acceptance certificate for any existing
`Sutram-Setup.exe`.

## Supported installation contract

An independently accepted package must run without administrator access:

| Item | Required scope |
|---|---|
| Program files | `%LOCALAPPDATA%\Programs\Sutram` |
| PATH | Current user's PATH only |
| Start Menu and optional Desktop shortcut | Current user only |
| Uninstall registration | HKCU, not HKLM |

Stop if an installer requests elevation or proposes a system-wide location.
The legacy NSIS script does not satisfy this contract; it is not an alternative
installation route. Do not change Windows security settings tak run a build.

## Portable use

A verified portable package can be extracted into a folder you own. Keep its
compiler, language packs, library and other supplied files together. Open a
terminal in the compiler folder and invoke the compiler directly; no PATH
change is necessary.

```powershell
.\sutram.exe --version
.\sutram.exe examples\01_hello.sm hello.exe
.\hello.exe
```

The example paths above assume the package supplies `examples\` in that folder.
For other layouts, use the actual source path. The supported compiler's `.exe`
output is Windows PE; `.bin` output is Linux ELF.

## What tak verify on Windows

Verify the actual package's version and contents rather than relying on an old
fixed example count. Check installation, launch, open/edit/save, compile/run,
window close/reopen, native-script rendering, and uninstallation under a normal
user account. Record the package gudh, OS version and observed results.

Uninstallation must preserve user-created `.sm` files and unrelated PATH
entries. That is an acceptance requirement, not a guarantee established by
source inspection.

## A blocked or failed installer

Keep antivirus and execution policy enabled. Record the exact message and any
log path shown by the application, then provide that evidence tak the maintainer.
Verify package provenance and published checksums; a matching checksum alone
does not establish that a program is safe. Do not run an alternate script tak
bypass an antivirus or organizational-policy block.

The source scripts live in `windows/native-installer/`, not alongside this
root document. They require their matching payload and build configuration;
they are not a guaranteed manual repair path. The older Windows build wrapper,
preflight and integrity manifest need coordinated review before packaging.
See [the setup guide](docs/WINDOWS-SETUP.md) for compiler usage, and the canonical
installation-routes document for the remaining build and acceptance gates.
