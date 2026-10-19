# R9-08 — WS8: keeping the interface cheap to change, and what I touched in `windows/`

## What changed in `windows/`

| Path | Change | Commit |
|---|---|---|
| `windows/gui/sutram_gui.asm` | font faces, eleven-pack Language menu, typing mode, output colour, the string table | `6f63fe36`, `7583e8d0` |
| `windows/gui/r9_translit.asm` | **new:** the transliteration engine | `6f63fe36` |
| `windows/gui/r9_translit_data.inc` | **new, generated** by `tools/translit.py --write-inc`; do not hand-edit | `6f63fe36` |
| `windows/gui/MANUAL-WINDOWS-GUI-TEST.md` | items 29–31, for the owner's test | `6f63fe36` |
| `windows/native-installer/check-script-fonts.ps1` | **new;** an offer to ChatGPT, called by nothing | `afe0431c` |
| `win/sutram.exe`, `sutram.exe`, `sutram-ide-gui.exe` | rebuilt from this source (`tools/cross_build_windows.py`) | `a5c72c44`, `7583e8d0` |

**Not touched:**

- `windows/native-installer/install-core.ps1`, `uninstall-core.ps1`, `sutram_setup.asm`,
  `sutram_wizard.asm`, `build-installer.ps1`
- **`Sutram-Setup.exe` and `Sutram-Setup.sha256`.** All the installer files are ChatGPT's, and its R77
  rebuilds the setup.
- **Merge note:** the setup must be rebuilt *after* this branch merges, or it will package the old
  compiler and IDE.

## One table per window

**The main window:**

- **Every word it shows is now in one place**, at the top of `sutram_gui.asm`.
  - The UTF-16 strings come first: menus, the status line, the About and Keys dialogs, the language
    names and the new typing-mode strings.
  - Directly after them come the ANSI strings: buttons and output-pane messages.
- **Before:** the ANSI half sat between the import tables, 200 lines away. One unused string
  (`delivery_about_text`) has been removed.
- **So a wording change is one edit in one block.**

**Other windows:**

- The open and save dialogs are the system's.
- The installer wizard is ChatGPT's, and its strings are in `sutram_wizard.asm`.

**For the owner's fixes:**

- **To add a language:**
  - a `lang/<pack>.lang` file
  - one menu item and one name string in the table
  - one entry in `PACKS` in `tools/translit.py`, then `--write-inc`
- **To change a phonetic rule:** edit `TOKENS` or `FALLBACK` in `tools/translit.py`, regenerate, and run
  `tests/translit/test_translit.py`.
