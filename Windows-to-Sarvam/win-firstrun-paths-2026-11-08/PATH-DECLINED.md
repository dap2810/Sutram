# PATH declined

## A1 — installation

The actual checkbox is `&Add Sutram to my user PATH (recommended)` (`&` is the Windows access-key marker).
It was checked by default. We cleared it, selected the desktop option for C, and confirmed the Ready page
said `Add to user PATH: no` and `Desktop shortcut: yes`.
Setup reached Finish in **27.799 seconds**, its engine exited 0, and the wizard closed.
This timing is one observation, not a benchmark comparison.

The previous installation's canonical PATH entries were removed only after recording them; the old
installation, shortcuts and registry keys were moved aside. This was a fresh target directory on the
existing account, not a new Windows profile. User PATH was unchanged by this install and contained no
Sutram entry. A fresh ordinary `cmd /d /c "sutram --version"` returned exit 1:

```text
'sutram' is not recognized as an internal or external command,
operable program or batch file.
```

Evidence: [defaults](install-options-default.png), [selected options](install-options-selected.png),
[Ready](install-ready.png), [raw wizard record](install.json), [identity and clean-shell check](identity.json).

## A2 — actual Start-menu terminal

Opened the installer-created `Start Menu\Programs\Sutram\Sutram Terminal.lnk` through Windows shell execution.
This launches the actual installed shortcut; it was not a reconstructed command.
It targets `cmd.exe` with these recorded arguments:

```text
/K "set "PATH=C:\Users\dmech\AppData\Local\Programs\Sutram\bin;%PATH%" && sutram --version"
```

The terminal immediately displays the version, then a command prompt. Typing `sutram --version` displays:

```text
Sutram 1.0 (v312) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

`where sutram` reports only `C:\Users\dmech\AppData\Local\Programs\Sutram\bin\sutram.exe`.
The shortcut prepends its own compiler folder to the terminal's process PATH; the user's persistent PATH
remains unchanged. It provides a working prompt and version banner, but no compile-command tutorial in that banner.

Evidence: [startup](terminal-startup.png), [typed command](terminal-version.png),
[raw version](terminal-version.txt), [stderr](terminal-stderr.txt), [where](terminal-where.txt),
[terminal process PATH](terminal-path.txt), [launch/commands record](terminal.json).

## A3 — recovery without reinstalling

Both the Start-menu terminal and full-path execution of `bin\sutram.exe --version` work without reinstalling.
The [Finish page](install-finish.png) says “You will find Sutram IDE and Sutram Terminal in your Start Menu.”
It gives no additional instruction specific to declining PATH.
The installed README points to `docs/WINDOWS-SETUP.md`; the English book is accessible through its Start-menu
shortcut. Its §17.6, “Understanding PATH,” explicitly says to type the full path or run from the containing
folder when PATH is absent. Its troubleshooting table likewise mentions the full path.
The installed book is therefore a discoverable recovery explanation, in addition to the working terminal shortcut.
See [documentation result](DOCS.md) and the exact [book excerpt](book-path-excerpt.html).
