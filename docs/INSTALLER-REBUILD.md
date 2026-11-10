# Rebuilding the installer's payload (Windows, or Linux)

> **R128 (v302): there is now a Linux route as well** - `python3 tools/build_installer_linux.py`, a step-for-step
> port of `windows\native-installer\build-installer.ps1` (payload, manifest, zip with backslash names, embedded
> hashes, icon resource, `nasm -f win64` + mingw `ld`, `--self-test` under Wine 64, `Sutram-Setup.sha256`).
> It built the v302 installer: payload compilers `bin\sutram.exe` = `win\sutram.exe` =
> `b5edcf19101b4baf...` (the tree's `win\sutram.exe`), `sutram-link.exe` rebuilt from `linker/sutram_link.asm`
> (`nasm -f win64 -DWINDOWS`, `ld -mi386pep --entry=_start --no-insert-timestamp`), `Sutram-Setup.sha256` written
> by the script. The differences from the Windows build: text files keep LF line endings, and the link uses
> mingw's import libraries. **Install and uninstall on a real Windows machine stay the owner's acceptance test.**
> The Windows procedure below is unchanged; its expected hashes are v291's.


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
`814cb11ae1c9111be3cfaf0812a3a4e40ba8fd26f24a48ae263a11282defde2d`, `sutram-ide-gui.exe`
`635c276b354c672925d460eaf6717c69333ed347eaa6084eda08ae6b40a55ad0`, `icons\sutram.ico`
`b48aeb52516433c3cce51ffe436fa04355cb938aa0b5188c60fe7c02f2923ec1`.

Then commit `Sutram-Setup.exe` and `Sutram-Setup.sha256`. On Linux, `python3 tools/check_installer_version.py`
should end:

```
PASS payload v291 = compiler v291 (bin/ and win/sutram.exe, packed <today>; the wizard has no version of its own; 0 of its N lib/lang files differ from the tree; ...)
```

**This goes stale again at the next compiler version.** Each round that bumps the version makes the payload one
version behind until this is run again; the gate will say so in the words above.

**R130-R131 (v306):** the payload's `sutram-link.exe` and `sutram-ide-gui.exe` are rebuilt from source too (the
runtime and the IDE changed). On Linux: the linker with `nasm -f win64 -DWINDOWS -I./ linker/sutram_link.asm` and
`x86_64-w64-mingw32-ld -mi386pep --entry=_start --no-insert-timestamp`, the IDE with `python3 tools/build_ide_linux.py`
(the port of `windows/gui/build-gui.ps1`). The wizard now runs the engine with `-NonInteractive -ExecutionPolicy Bypass`
and no console window, and stops it after 15 minutes (`ENGINE_WAIT_MS` in `sutram_wizard.asm`).

**R133 (v307):** the runtime changed again (the handler registration is checked), so `sutram-link.exe` is rebuilt
the same way. The engine (`install-core.ps1`) and uninstaller changed; the wizard did not.

**R134-R135 (v308):** the runtime and the PE layout changed (a 64 KiB commit reserve), so `sutram-link.exe` is rebuilt
again; the engine, the uninstaller and the wizard (it logs its 15-minute stop) changed.

**R137-R138 (v309):** the runtime's shipped bytes and `sutram-link.exe` are unchanged; the engine and the uninstaller
changed (the lock beside the installation, the re-check before each replacement).

**R140:** the Linux build is deterministic - LF text, fixed ZIP dates, no link timestamp - so building the same tree
twice, from checkouts with different file times, gives the same `Sutram-Setup.exe`. Gate `R140 package` checks
the built file. The Windows builder normalizes text to LF but does not fix the ZIP dates.

**R141 (v310):** compiler and engine changed (the lock before every state read); the runtime and `sutram-link.exe`
are unchanged. Built with `tools/build_installer_linux.py` as in R140.

**R142 (v311):** compiler and engine changed (a target deleted only when its kept copy has the same full SHA-256;
a reused target that changed or disappeared is refused before it is moved, from PR #68); the runtime and
`sutram-link.exe` are unchanged. Built with `tools/build_installer_linux.py` as in R140.

**R143 (v312):** the wizard changed (the licence decoded as UTF-8 with CR LF line ends; the uninstall script
started with CREATE_NO_WINDOW) and the uninstaller (no empty `.sm` keys; a failure shown in a message box). The
runtime and `sutram-link.exe` are unchanged. Built with `tools/build_installer_linux.py` as in R140.

**R147 (v313):** the wizard (the licence instruction two lines high) and the uninstaller (its staging folder
removed on success) changed; the runtime and `sutram-link.exe` are unchanged. Built with
`tools/build_installer_linux.py` from an **empty** `--work` folder (the builder refuses a used one).

**R152 (v314):** the compiler (the FFI door, `--analysis-steps`), the engine and uninstaller (the desktop
collision) and the wizard (the checkbox label) changed; the runtime and `sutram-link.exe` are unchanged. Built
with `tools/build_installer_linux.py` from an empty `--work` folder.

**R153 (v314, rebuilt):** the engine and uninstaller only (shortcut ownership by the link's own bytes); the
compiler, runtime and `sutram-link.exe` are byte-unchanged. Built from an empty `--work` folder.

**R154 (v315):** the compiler (the tree limit's code, the fold guard), the engine and the uninstaller (PATH,
association and class records) changed; the runtime and `sutram-link.exe` are unchanged. Built from an empty
`--work` folder.

**R173 (v318):** the compiler changed (a `mala` declared in a `chakra`'s own body is made once); nothing else in
the payload but the documents. Built from an empty `--work` folder.

**R172 (v317):** the compiler changed (a `kosh` declared in a `chakra`'s own body is made once); nothing else in
the payload but the documents. Built from an empty `--work` folder.

**R163 (v316):** the compiler and `sutram-link.exe` (a file they read is never their output) changed; the engine,
the uninstaller, the wizard and the runtime are unchanged since R163's lock fix. Built from an empty `--work` folder.

## What `install-state.ini` records (R153-R155)

Every record is **what was done**, not a flag that something was done, and uninstall acts only on these:

| record | what it holds | what uninstall does with it |
|---|---|---|
| `OwnedShortcuts` | `<base64 path>\|<SHA-256 of the .lnk as written>` for each link this installer wrote | removes a link only if it is in the Start-menu `Sutram` folder or on the desktop, ends `.lnk`, and its bytes still have that hash. A record without a hash (before v315) is not ownership: the link is kept |
| `PathAdded` | the exact text of the one PATH entry this install added (empty if it added none - an equal entry was already there, and is the user's) | removes the first entry with that text and the one `;` that joined it; nothing else in PATH changes |
| `PathValueCreated` | `1` if the user's PATH value did not exist and this install made it | then removes the value too, if nothing else is left in it |
| `AssociationSet` | the value this installer set as `.sm`'s default (`Sutram.Source`), carried only while the default is still that | resets the default only if it still equals that |
| `AssociationBefore` | `absent` or `empty` - what the default was before it was set | puts that back: no default, or an empty one |
| `UninstallerSHA256` | the uninstaller's hash | an uninstaller that has changed is kept, and nothing is removed |

`PathOwned`, `DesktopOwned` and `AssociationOwned` are still written, derived from the records above. **Nothing
acts on them.** The `Sutram.Source` class is removed value by value (only values still equal to what the installer
wrote) and key by key (only keys left empty). Registry keys are opened, never remade: `New-Item -Force` on an
existing key deletes it, values and subkeys first (PowerShell's registry provider), and is used only for Sutram's
own `Uninstall\Sutram` key.

**The lock (R162).** Beside the installation folder, `<folder>.sutram-lock` is made by the installer or the
uninstaller with `CreateNew`, holds the line `Sutram installer lock`, is opened with no sharing, and is deleted when
it closes. Anything already at that path - empty, marked or not - is left exactly as it is and the
run stops, saying whether another installer holds it (R163, ChatGPT R225: R162 removed an empty or marked file as a
stale lock, but an empty file may be anyone's, and the name could change between the read and the delete). A lock
left by an installer that stopped is deleted by hand; the message says so.

