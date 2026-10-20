# R13-03 — WS3: the Linux IDEs' English

**There is no English left in either Linux IDE.** Everything below is romanised Sanskrit, in the same
words as the X11 GUI's existing menus (`chal`, `sanchay`, `khol`, `nishkas` …). The full diff is
`evidence-r13/linux-ide-strings.diff`.

## What changed

**The terminal IDE (`ide/sutram_ide.asm`):**

| Was | Now |
|---|---|
| ` Sutram IDE - the complete thread` | ` Sutram sampadak - sampurna sutra` |
| `Ctrl-R Run  Ctrl-S Save  Ctrl-Z Undo  Ctrl-L Load  Ctrl-E Examples  Ctrl-T Shell  Ctrl-Q Quit` | `Ctrl-R chal  Ctrl-S sanchay  Ctrl-Z punah  Ctrl-L khol  Ctrl-E udaharan  Ctrl-T samvad  Ctrl-Q nishkas` |
| ` Output` · ` [modified]` · ` Shell` | ` phal` · ` [asanchit]` · ` samvad` |
| `Enter Run  Ctrl-T Back to editor  Ctrl-Q Quit` | `Enter chal  Ctrl-T sampadakam prati  Ctrl-Q nishkas` |

**The X11 GUI (`ide/sutram_gui_linux.asm`):**

| Was | Now |
|---|---|
| `Sutram GUI: run (Ctrl-R)` | `Sutram sampadak: chalanam (Ctrl-R)` |
| `Sutram IDE: cannot open that file.` (shown in the window) | `Sutram sampadak: tat patram na udghatitam.` |
| `Sutram GUI: connected to X, window created.` | `Sutram sampadak: X-sevakena sambaddham, gavakshah rachitah.` |
| `Sutram GUI: cannot reach an X server (no DISPLAY).` | `Sutram sampadak: X-sevakah na praptah (DISPLAY nasti).` |
| `Sutram GUI: handshake failed.` | `Sutram sampadak: X-sambandhah viphalah.` |
| About: `… deshiya yantra-code, na koi runtime.` | `… deshiya yantra-bhasha, na kopi bahya-ashrayah.` |

**Two X11 tests read these lines, and are updated:** `test_x11_open.py` (the open-failure text) and
`test_x11_protocol.py` (the connection line).

**Both IDE binaries are rebuilt and committed.**

## What remains

1. **Neither Linux IDE follows the pack.**
   - Both still show romanised Sanskrit only.
   - The terminal IDE still runs the compiler without `--lang`.
   - **The X11 GUI cannot draw Indic script at all** (raw X11, 8-bit `ImageText8`), as R12-02 said.
2. **Kept as they are, because they are not words:**
   - the key names `Ctrl-R`, `Enter`
   - `DISPLAY` (the environment variable)
   - `X` (the protocol's name)
   - `NASM`
3. **Not part of this workstream, but the same rule, in the Windows IDE:**
   - **The menus, buttons and the two Help dialogs are English** (`File`, `Run`, `Load example`, `About
     Sutram`: "Sanskrit-keyword language -> x86-64 machine code"). That was the owner's R5 decision.
   - **Two labels are in Hindi grammar:** `sankalan / chalan ka phal`, `udaharan (do baar click)`.
   - **"No English when the project is not" contradicts the R5 decision.** Please ask the owner whether
     R5 still stands.
   - **If it does not, the cost:**
     - the 52 menu, button, dialog and label strings in the one table at the top of `windows/gui/sutram_gui.asm` (some are pack names or already romanised; I did not sort them)
     - the IDE checks in `tools/test_windows_gui.py`
     - part of a round
