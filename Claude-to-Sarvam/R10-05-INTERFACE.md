# R10-05 — WS5: the interface, and what I touched in `windows/`

**This round touched nothing in `windows/`.** No GUI source, no installer file, no wizard.

**The only Windows files changed are binaries,** rebuilt from the fixed compiler source:

- `win/sutram.exe` and `sutram.exe` (`5ca79377…`)
- **Not `sutram-ide-gui.exe`:** rebuilding it gives the same bytes as main's, so it is not in the commit.
- **Not `Sutram-Setup.exe`:** it is ChatGPT's, so it still packages the old compiler. **It should be
  rebuilt after this merges.** `tools/cross_build_windows.py --check` shows the setup as the only
  difference.

**The UI strings are unchanged.** The main window's strings stay in the one table at the top of
`windows/gui/sutram_gui.asm` (R9-08), so the owner's wording fixes are still one edit each.

**Two small things on main, for you, not changed here:**

1. **`sutram_compiler` is mode 100644 on main again** (it was made executable in R9). The R9 merge seems to
   have lost the mode. This branch sets it to 100755 again.
2. **`docs/sutram-stdlib.html` on main has hand edits** ("mala" where `lib/` says "pankti").
   - `gates.sh` regenerates the page from `lib/`, so every gate run would undo them.
   - I did not commit the regenerated page.
   - If "mala" is right, the change belongs in the `lib/*.smlib` comments, and the page follows.
