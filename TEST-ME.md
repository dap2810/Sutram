# TEST-ME — the Windows ROUND-03 test build (2026-10-18)

A short acceptance script for the Sanskrit IDE on Windows. Written by Claude for the owner; kept here so
the same steps can be repeated on any machine.

## Steps

1. **Double-click `Sutram-Setup.exe`** — as a **normal user**. **No administrator prompt should appear.**
2. **Start Menu → Sutram → Sutram IDE.**
3. **Load example → `218_sanskrit_devanagari.sm` → F5 (Run).**
   Expect: **`योगः = 15`** in Devanagari, and **`bhasha: swayam (sanskrit)`** in the status line.
4. Try **Tab / Shift+Tab**, **Enter after `{`**, typing **`}`** on a blank indented line, and **Ctrl+F**.
5. **Help → Shortcut keys** shows all keys. Close with unsaved edits → a **Yes / No / Cancel** question.

**Uninstall:** Start Menu → Sutram → Uninstall Sutram, or Settings → Apps.

## Automated: one command, one log (ROUND-06)

The steps above are also a script that prints a machine-readable log. From the folder that holds
`Sutram-Setup.exe`, in a **normal (not administrator) PowerShell window**:

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools\accept-windows.ps1
```

**What it does:**

- installs for the current user, launches the installed IDE, compiles `218` and runs the IDE checks
- closes the IDE and uninstalls
- refuses to run over an existing Sutram installation

**What it writes:** `build\windows\accept-<time>\accept-windows.json` and screenshots. **Send that folder back.**

**Checking a returned log, on any machine:**

```
python3 tools/check_accept_windows_log.py <folder>/accept-windows.json
```

It says whether the log is Windows acceptance of the tree it is run in: same binaries (SHA-256),
Windows (not Wine), not elevated, every required check PASS.

**Rebuild first** (`windows\BUILD-WINDOWS-SETUP.cmd`). The committed `Sutram-Setup.exe` and
`sutram-ide-gui.exe` are the ROUND-03 build, so the script will correctly fail them on the English-labels
checks.

## Note

`sutram-ide-gui.exe` run on its own needs `win\sutram.exe`, `lang\`, `lib\` and `examples\` beside it.
**Use the installer.**

## What was verified here, and what was not

**Verified on this side (Linux, from the merged tree):** the three binaries are **byte-identical to the
ROUND-03 delivery** (same SHA-256), all three are valid **PE32+ x86-64**, and
`examples/218_sanskrit_devanagari.sm` **compiles through the `sanskrit` pack and prints `योगः = 15`** —
matching step 3.

**NOT verified here:** anything that needs Windows to run — the installer, the GUI, the key handling and
the uninstall. **This side cannot execute Windows.** Claude's evidence for those is in
`Claude-to-Sarvam/R3-*` (screenshots, `gui-smoke.json`, install and uninstall logs) and the steps above are
for the owner to repeat by hand.
