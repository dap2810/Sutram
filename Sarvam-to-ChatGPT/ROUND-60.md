# Sutram — Round 60 handoff: Sarvam → ChatGPT

**Date:** 2026-10-14
**Base:** main `c7bd6435a11a` — includes your **R58** (constant folding, merged) and my **Windows IDLE work** (pushed this round).

## Why this round is yours

The standing split is: **Linux is mine, Windows is yours.** I have built the colourful IDLE
GUI and a working `Sutram-Setup.exe`, and I have verified everything I can *without a display* —
the source assembles, the PE is structurally valid, the payload is complete and hash-correct.

**What I cannot do is run it.** No Windows, no display. So "it builds and the headers are right"
is where my verification stops, and real Windows execution is where yours begins.

## Round 60 — ONE big task

**Take the Windows IDLE GUI + installer to a genuinely working, verified state on real Windows.**

### 1. Verify the fresh build actually renders (highest priority)
Build from main and run:
- `windows/gui/sutram_gui.asm` → `sutram-ide-gui.exe` (33.7 KB at my build)
- `windows/native-installer/sutram_setup.asm` → `Sutram-Setup.exe`

Then confirm, **with screenshots**:
- the **menu bar renders** (File / Edit / Shell / Debug / Options / Window / Help). It did not in
  an earlier build — I have since traced the code and believe it is correct (menu built before
  `CreateWindowExA`, handle passed as the 9th arg at `[rsp+72]`, APIs resolved through
  `user_table`), but **a screenshot is the only proof**.
- the **colourful tokeniser** shows: dark canvas, **orange** keywords, **teal** builtins,
  **green** strings, **purple** numbers, **grey** comments.
- the `>>>` shell accepts input and runs a program.

### 2. Fix whatever does not render
If the menu or any colour is wrong, fix it and say what the actual cause was. I have been wrong
about these binaries before; do not assume my diagnosis.

### 3. Prove the installer end-to-end on Windows
Run `Sutram-Setup.exe` and confirm: it installs **per-user, no UAC prompt**, the **"Sutram IDE"
Start Menu shortcut appears with the correct icon**, and the installed GUI launches.
Report the real wizard behaviour.

### 4. Icon check — this one matters to the user
The user reported a **wrong icon** (a blue/gold disc). The canonical icon is
`icons/sutram.ico` (teal disc, orange ring + S-curve, sha256 `b48aeb52…`). The GUI loads
`icons\sutram.ico` from disk with fallback `assets\sutram.ico`. Confirm the installed shortcut and
window show the **canonical thread icon**, and if any stale icon is still being picked up anywhere,
name the file.

### Evidence I will look for
- Screenshots of: the running GUI with menu bar + colours; the installer wizard; the installed
  shortcut icon.
- The exact commands you built with, and the resulting binary sizes.
- Anything that did **not** work, stated plainly. A verified partial beats a claim.

### Definition of done
- The GUI renders with menu + colours on real Windows, shown in a screenshot.
- The installer installs the language + IDLE and the shortcut has the correct icon.
- Handoff with screenshots, SHAs, and an honest list of what still does not work.

### Explicitly NOT this round
Do not change the compiler. Do not touch the lexer's *colour values* — those are user-approved.
Do not rewrite `lib/*.smlib`. Keep the pure-NASM / no-runtime / least-privilege fundamentals.

### Constraints (unchanged)
Pure NASM x86-64, one compiler source, native machine code, no runtime dependency, `.sm`,
Sanskrit keyword core, per-user install, no UAC, no registry writes beyond the user's own.
