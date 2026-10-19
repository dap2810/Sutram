# TEST-ME — the Windows ROUND-03 test build (2026-10-18)

A short acceptance script for the Sanskrit IDE on Windows. Written by Claude for the owner; kept here so
the same steps can be repeated on any machine.

## Steps

1. **Double-click `Sutram-Setup.exe`** — as a **normal user**. **No administrator prompt should appear.**
2. **Start Menu → Sutram → Sutram IDE.**
3. **Load example → `218_sanskrit_devanagari.sm` → F5 (Run).**
   Expect: **`योगः = 15`** in Devanagari, and **`bhasha: swayam (sanskrit)`** in the status line.
4. Try **Tab / Shift+Tab**, **Enter after `{`**, typing **`}`** on a blank indented line, and **Ctrl+F**.
5. **`sahay` → `kunji`** shows all keys. Close with unsaved edits → a **Yes / No / Cancel** question.

**Uninstall:** Start Menu → Sutram → Uninstall Sutram, or Settings → Apps.

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
