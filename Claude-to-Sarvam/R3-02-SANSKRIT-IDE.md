# R3-02 — The Windows IDE: Sanskrit interface, editor keys, status line, `bhasha`, icon

Files: `windows/gui/sutram_gui.asm` (+1678/−…: pure NASM, no new DLLs beyond user32/gdi32 already
linked), `windows/gui/r67_gui_entry.asm`, `windows/gui/build-gui.ps1`, `windows/build-common.ps1`,
`tools/test_windows_gui.py`, the two GUI documents. Commits `a39d2f9` and `fdf409d`.
Screenshots: `evidence/r73/ide-native.png` (Latin program), `evidence/r73/ide-sanskrit.png`
(Devanagari program after `chal`), `evidence/r73/exe-icon.png` (icon extracted from the executable).

## 1. Every visible word is Sanskrit

Latin transliteration, the project's canonical form, and **the same tokens the Linux X11 IDE already
uses** (`ide/sutram_gui_linux.asm` slice 20) wherever one existed. New words are marked *new* and are
listed in R3-04 for confirmation.

| Where | Before | Now |
|---|---|---|
| title | `Sutram IDE` / `Sutram Shell 1.0` | `<patra> - Sutram sampadak`, `nava patra` when unnamed, ` *` while unsaved |
| menus | File · Shell · Help | `patra` · `sampad` · `chal` · `bhasha` *new* · `sahay` |
| patra | Open… Save Exit | `nava` *new* (Ctrl+N) · `khol...` (Ctrl+O) · `sanchay` (Ctrl+S) · `nava naam se sanchay...` *new* · `nishkas` |
| sampad | — | `punah` · `chhid` · `pratilip` · `sanyoj` · `sarvagrah` · `anwesh...` (Ctrl+F) · `agrim anwesh` *new* (F3) · `antar (4 sthan)` *new* (Tab) · `antar hatao` *new* (Shift+Tab) |
| chal | Run module · Clear shell | `chal` (F5) · `presh (kosh pankti)` *new* (Enter) · `phal_rikta` |
| bhasha | — | `swayam (lipi se pahchan)` *new* · `mool (Latin shabda)` *new* · `sanskrit  संस्कृतम्` |
| sahay | About Sutram | `kunji (shortcut)` *new* · `parichay` |
| buttons | Run Open Save Load example Send Clear shell | **unchanged, English** — the owner asked for the buttons to stay as they were; menus, status and messages carry the Sanskrit |
| status line *new* | — | `pankti N   stambh N   |   bhasha: …   |   akshara: N   |   sanchit / asanchit *` |
| messages | `[compiler failed]`, `[program exited abnormally]`, … | `[sankalan asaphal]`, `[karyakram asamanya roop se samapt]`, `[patra padhne/likhne me asaphal]`, `[prakriya 10 sekand se adhik; samapt ki gayi]`, … |
| questions | — | `patra parivartit hai. sanchay karein?` (Yes / No / Cancel) |
| file dialog | Sutram files / All files | `Sutram patra (*.sm)` / `sabhi patra (*.*)` |

Nothing in a string literal that the compiler reads was renamed (the standing `to` warning).

## 2. Typing Devanagari actually works now

The window class, message loop and subclasses were ANSI (`RegisterClassExA`, `GetMessageA`,
`DispatchMessageA`, `SetWindowLongPtrA`). With an ANSI loop, `TranslateMessage` produces code-page
`WM_CHAR`s, so a Hindi keyboard layout would have typed `?` into the editor and the shell line. The
class, loop and the three subclasses are now Unicode (`…W`); the test harness sets Devanagari with
`WM_SETTEXT`, so the typing path is covered by manual test 24 in `MANUAL-WINDOWS-GUI-TEST.md`, not by
automation. I did not type on a Hindi layout myself — **NOT-RUN**, please do.

## 3. Editor keys (the Tab request)

A Unicode subclass on the RichEdit (`editor_proc`):

- **Tab** → four spaces at the caret; with a multi-line selection, four spaces in front of every
  selected line (a selection ending at column 0 does not indent that last line).
- **Shift+Tab** → removes up to four leading spaces from each selected line; the caret or selection
  is put back where it was, minus what was removed.
- **Enter** → new line with the current line's indentation, **+4 after a line ending in `{`**.
- **`}`** typed on a whitespace-only line with ≥4 spaces → pulls that line back by four first.
- Tab and Enter characters are swallowed on `WM_CHAR` so no tab character ever enters the buffer.

The same operations are on the `sampad` menu (`antar`, `antar hatao`) for mouse users and for the
test harness, which cannot hold Shift.

## 4. Status line, title, unsaved-work guard, find

- `EN_SELCHANGE` from the RichEdit refreshes the status line; it stays quiet while the highlighter
  runs (the highlighter moves the selection once per token and restores it from `ch_start/ch_end`,
  which the status code must not touch — that was the one bug the harness caught during development).
- `akshara:` is the R67 grapheme-cluster count; `r67_gui_entry.asm` now writes it to the status line
  instead of overwriting the title.
- `is_modified` is set on the first real `EN_CHANGE` (not during load, new, or startup), cleared on
  load/save/new; the title shows ` *`; `nava`, `khol` and closing the window ask first; Yes saves
  (asking for a name if there is none), No discards, Cancel keeps the window.
- `anwesh:` box in the toolbar; Ctrl+F focuses it; Enter or F3 finds forward from the caret with
  `EM_FINDTEXTEXW`, wraps once, selects the match and returns focus to the editor; a miss writes
  `anwesh: nahi mila` in the status line.
- Buttons act only on `BN_CLICKED`. Before, any notification with a button id (a focus change)
  ran the handler — the same defect the wizard still has (R3-03 §1).

## 5. `bhasha`: running a Devanagari program through the pack

The compiler needs `--lang <pack>`; nothing in the IDE passed it, so a Devanagari program could not
run from the IDE at all. Now `compose_compile` builds
`"<compiler>" [ --lang sanskrit] "<source>" "<binary>"` according to the `bhasha` menu:

| choice | behaviour |
|---|---|
| `swayam` (default) | any UTF-16 unit in U+0900–U+097F in the editor text (or an `E0 A4/A5 xx` sequence in the shell's replayed UTF-8 source) selects `--lang sanskrit`; otherwise no pack. Status shows `swayam (sanskrit)` after such a run. |
| `mool` | never a pack — the Latin core only |
| `sanskrit` | always `--lang sanskrit` |

`lang/sanskrit.lang` is now loaded with the other ten packs, so Devanagari **Sanskrit** keywords colour
as keywords (before, only the ten other scripts did). The radio state lives in `lang_mode`; the pack
name and the flag string are data (`lang_flag_w`), so each further pack is: one menu line, one name,
one detection range (or none: an explicit choice needs no detection). The owner asked for Sanskrit
first; **the other ten packs are not wired**, deliberately.

Verified (harness checks `devanagari-swayam`, `devanagari-mool-fails`, `devanagari-sanskrit`): the
shipped `examples/218_sanskrit_devanagari.sm` prints `योगः = 15` under `swayam` and `sanskrit`, and
under `mool` the compiler reports `Sutram Error: undefined function: लिख` — the pack really is the
difference.

## 6. The icon (the owner's question, twice)

`sutram-ide-gui.exe` had no icon resource: the window icon was loaded from `icons/sutram.ico` at run
time, Explorer and the taskbar showed the generic executable icon, and the Setup window's title bar
showed the generic icon too. `windows/build-common.ps1` now has `Write-IconResourceInclude`, which
reads the `.ico` header and emits a NASM `.rsrc` section: one `RT_GROUP_ICON` (id 1) naming the eight
images, eight `RT_ICON` entries each an `incbin` slice of the icon file, RVAs via `wrt ..imagebase`.
GNU ld places the section and fills the PE resource data directory; `Assert-PeResourceDirectory`
fails the build if it did not. The GUI's class `hIcon`/`hIconSm` and the wizard's come from
`LoadImageW(hInstance, 1, …)`; the old file-path load remains as a fallback.
`ExtractIconExW(…, -1)` reports one icon group in each executable (`icon-resource` check);
`evidence/r73/exe-icon.png` is the 32×32 image Windows extracts from the IDE.

The owner then pointed at the big logo in the Setup wizard's sidebar: that one was never an icon —
`paint_sidebar` drew an orange ring and a Bézier "thread" with GDI, which is why it never matched.
It now calls `DrawIconEx` with the 96-px rendering of the same resource (the hand-drawn version
remains only as the fallback for a resource-less build). `evidence/r73/installer-sidebar.png`.

## 7. Dark canvas

`WM_CTLCOLORSTATIC/EDIT/LISTBOX` return one dark brush (`COL_BG`), so the gutter (grey digits),
the examples list, the shell line, the find box and the status line match the editor and output
pane. Buttons keep the system theme.

## 8. What was tested, and what was not

| | How | Result |
|---|---|---|
| 30 native checks | `tools/test_windows_gui.py` against the freshly built exe: window, argv open, run, Unicode set-text, menu run, layout, render, 7 token colours, compiler error, **button labels, status line, title, Tab, Enter, `}`, menu unindent, block indent, Devanagari via swayam / mool / sanskrit, status pack, find, icon resource** | **30 / 30**, `evidence/r73/gui-smoke.json` |
| static contracts | `tests/gui` (28), incl. the export-name/slot test every new `API` call must satisfy | OK |
| installed copy | Start-Menu shortcut → title, buttons, Devanagari run, close question (No) | PASS, `R3-01 §5` |
| typing with an Indic layout / IME, Save-As round trip of a Devanagari file name, resize, long files, Shift+Tab by keyboard | manual list 20–28 in `MANUAL-WINDOWS-GUI-TEST.md` | **NOT-RUN** by me |
| other ten packs from the `bhasha` menu | — | **not implemented** this round |
