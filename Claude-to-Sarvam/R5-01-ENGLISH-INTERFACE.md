# R5-01 — The owner's instruction: the interface labels in English

**Branch `claude/round-05`, draft PR. Base: main `c504e3c6` (v173).**

| Commit | What it does |
|---|---|
| `70b02e8f` | IDE labels |
| `a1340416` | IDE colouring (separate, so it can be taken or dropped on its own) |
| `79928d90` | Installer strings |

**Every screenshot in this round was taken under Wine 9.0 on Linux (Xvfb), not on Windows.** They show the
words and the layout. They are not Windows acceptance.

## 1. What the 13 October build used, and what I matched

I read the 13 Oct build from history: `c7bd6435`, the last change before the R3 merge, and its parents
`c6d9f8d2` and `1d136bef`. Its menu bar was **IDLE-style**:

```
m_file 'File'   m_edit 'Edit'   m_shell 'Shell'   m_debug 'Debug'   m_opts 'Options'   m_window 'Window'   m_help 'Help'
i_open 'Open...'   i_save 'Save'   i_exit 'Exit'   i_run 'Run module'   i_clear 'Clear shell'   i_about 'About Sutram'
label_run 'Run'  label_open 'Open'  label_save 'Save'  label_example 'Load example'  label_send 'Send'  label_clear 'Clear shell'
```

`Edit`, `Debug`, `Options` and `Window` were **empty** in that build. The 18 Oct IDE has five real menus.

**What I used:**

- **Where the 13 Oct build had a word, I used its word.**
- **Where it had none, I used the standard Windows word.**
- **The run menu is `Shell`, not `Run`.** That is the 13 Oct word, and that menu holds Run module, Send and
  Clear shell, as it did on 13 Oct. If the owner prefers `Run`, it is a one-word change.

| R73 / R4 (Sanskrit) | R5 (English) | Source of the word |
|---|---|---|
| `patra` / `sampad` / `chal` / `bhasha` / `sahay` | **File / Edit / Shell / Language / Help** | 13 Oct (`Language` is new: 13 Oct had no such menu) |
| `nava` · `khol...` · `sanchay` · `nava naam se sanchay...` · `nishkas` | New · **Open...** · **Save** · Save As... · **Exit** | bold = 13 Oct |
| `punah` · `chhid` · `pratilip` · `sanyoj` · `sarvagrah` | Undo · Cut · Copy · Paste · Select All | standard |
| `anwesh...` · `agrim anwesh` · `antar (4 sthan)` · `antar hatao` | Find... · Find Next · Indent (4 spaces) · Dedent | standard |
| `chal` · `presh (kosh pankti)` · `phal_rikta` | **Run module** · Send (shell line) · **Clear shell** | bold = 13 Oct |
| `swayam (lipi se pahchan)` · `mool (Latin shabda)` · `sanskrit  संस्कृत` | Auto (detect script) · Core (Latin keywords) · `sanskrit  संस्कृत` | the pack's name stays: it is what `--lang` takes |
| `kunji (shortcut)` · `parichay` | Shortcut keys · **About Sutram** | bold = 13 Oct |
| buttons `chal khol sanchay "udaharan khol" presh phal_rikta` | **Run Open Save "Load example" Send "Clear shell"** | 13 Oct = 18 Oct, exactly. This reverts my R4 change. |
| `anwesh:` (the find box's label in the toolbar) | Find: | standard |

**Text that names a control changed with it,** so nothing on screen points at a word that is gone:

- the two Help dialogs (the shortcut list and About)
- the unsaved-file question: `The file has changed. Save it?`
- `Untitled` in the title (was `nava patra`)
- two output messages:
  - `Ready. Run (F5) compiles and runs the program in the editor.`
  - `[shell history is full; use Clear shell]`

**Kept as asked:**

- the dark theme, line numbers, Devanagari colouring and the icon
- Tab / Shift+Tab, Enter auto-indent, `}` dedent, and the status line
- the `bhasha` menu's behaviour: **Language > Auto** detects Devanagari and runs the compiler with
  `--lang sanskrit`

Screenshots:

- **`evidence-r5/screens/ide-r5-main.png`**: the main window
- **`ide-r5-menus.png`**: all five menus open
- before, for comparison: `evidence-r4/screens/ide-after.png` (R4, Sanskrit) and `ide-before.png`
  (18 Oct, English buttons, Sanskrit menus)

### Left in Sanskrit, deliberately — please confirm

The instruction named **menus, buttons and installer**. These are neither, so I left them as they are:

- **The status line:** `pankti 1   stambh 1   |   bhasha: swayam   |   akshara: 41   |   sanchit`.
  `tools/test_windows_gui.py` checks these words, and the brief says "keep the status line".
- **The output-pane messages from the IDE:** `[sankalan asaphal]`, `[karyakram asamanya roop se samapt]`,
  `[patra padhne/likhne me asaphal]`, the timeout and size-limit messages.
- **The window title** `Sutram sampadak`. It is how the owner named this build.
- **The compiler's own diagnostics.** They are the compiler's, not the IDE's.

If "the whole interface in English" includes these, it is one more short commit. Say the word.

## 2. Installer — 49 strings back to English

`windows/native-installer/sutram_wizard.asm`: the 49 `u16` strings are now **byte-for-byte the pre-R4
text**. They were taken from `60d2e4ce`, the last commit before R4. The diff against main is exactly those 49
lines; `git diff … | grep -v u16` gives nothing else. **Nothing else in `windows/native-installer/` was
touched.**

R4's footer length fix is kept. It was already on main, and the brief says not to touch the installer
beyond strings; the fix draws `SUTRAM SETUP` exactly as before.

Screenshots: `evidence-r5/screens/wizard-r5-pages.png` (welcome, licence, location, components, ready)
and `wizard-r5-license.png`. I stopped at Ready and pressed Cancel; nothing was installed.

**Two things the English text brings back, for you to know (not changed, because they are not strings):**

- **The licence intro is clipped under Wine.** `Please read the following license agreement. You must accept
  the terms to continue.` needs two lines and the label has room for one: `wizard-r5-license.png`. This
  is why R4 had shortened it. On Windows, with Segoe UI, it may fit; I cannot check.
- **The licence mojibake is unchanged** (`Sutram âThe Complete Thread`), as R4-03 §2 reported. It is
  ChatGPT's.

## 3. The owner's question: the file-list panel

**It was not removed. It is in the 18 Oct build, and it shows in every Wine screenshot I have taken**
(`ide-r5-main.png`: `01_hello.sm`, `02_arith.sm`, … on the right).

The code:

- `sutram_gui.asm:1528` creates it: the `LISTBOX` `ID_LIST`, the same control as 13 Oct.
- `layout_controls` places it to the right of the editor at every window size, 280 px wide.
- `fill_examples` fills it from `examples\*.sm`.
- The IDE sets its working directory to its own folder at start (`SetCurrentDirectoryW`), so the installed
  copy finds `examples\` too.
- Double-click, or **Load example**, opens the selected file.

**What I cannot see is the owner's screenshot.** Three things would make the panel look absent, and none of
them is a removal:

1. The IDE started from a folder with no `examples\`. The list is then an **empty** dark box, easy to miss
   against the dark theme.
2. A screenshot cropped to the editor.
3. A different executable, e.g. an older `sutram-ide-gui.exe` left in another folder.

**Ask:** if the owner can send that screenshot, or say how the IDE was started, I can say which one it is.

## 4. Something the owner should know (not acted on)

The brief invites this. **English labels are a reasonable call for a Windows tool.** They match the OS's own
dialogs (Open, Save, Yes/No/Cancel are English anyway), and the 13 Oct build is what users have seen.

**One consequence worth knowing:** the IDE is now English while every message it shows from the compiler is
Sanskrit, e.g. `Sutram Error [E_UNDEFINED_NAME]: agyat naam 'totl'` / `Sanket: …`.

- A user who reads only English gets English menus and Sanskrit diagnostics.
- A user who reads no English gets the opposite of what they need.

This does not argue against the change. It is a reason to decide the diagnostics language (R5-03 §3)
**together with** the interface, so the two do not drift apart again.

## 5. A defect found while checking the look — fixed, separate commit `a1340416`

**The editor did not colour most of the current keywords.**

- `kw_words` / `bi_words` in `sutram_gui.asm` still held the **pre-v157** names (`pratiyati ayojan
  anyatha nishkriya … char_at char_code set_char`).
- So `vitti`, `chakra`, `prati`, `tak`, `anya`, `agrim`, `yoj` and every renamed builtin (`kosh_push`,
  `akshar` …) were drawn as plain text.
- `ide-colour-before-fix.png` shows it: `prakriya`, `mukhya` and `yadi` are orange; `vitti`, `chakra`,
  `prati`, `tak`, `anya` and `agrim` are white.

**The fix.** Both tables are now exactly the compiler's own `kw_*` (28) and `bn_*` (45) strings. The new
`tests/gui/test_win_gui_colour_tables.py` keeps them equal: 3 FAIL on v173, 3 PASS now.

**The look is unchanged:** same colours, same classes. The words that should have been coloured now are
(`ide-colour-after-fix.png`). This is the same kind of defect R3 fixed in the X11 GUI. It is in its own commit
because the brief said not to change the look; drop it if you read it that way.

## Commands

```
nasm -f win64 -I./ windows/gui/{r67_gui_entry,r66_indic_clusters,r67_cluster_count}.asm
x86_64-w64-mingw32-ld -mi386pep --subsystem windows --entry=_start -o gui.exe *.obj -L/usr/x86_64-w64-mingw32/lib -lkernel32 -lshell32 -luser32 -lgdi32
nasm -f win64 -I<stage>/ -I./ windows/native-installer/sutram_wizard.asm -o w.obj
x86_64-w64-mingw32-ld -mi386pep --subsystem windows --entry=_start -o wizard.exe w.obj -lkernel32 -lbcrypt
DISPLAY=:99 WINEPREFIX=… wine64 gui.exe        # then xdotool clicks, ImageMagick `import`
```

## Not verified

- **NOT-RUN on Windows.** No native rendering, DPI or Segoe UI metrics.
- **`tools/test_windows_gui.py` is NOT-RUN.** It is Windows-only. I updated its `button-labels` check to
  the English words.
- **The icon resource was not built under Wine,** as in R4: `-dR73_ICON` needs the PowerShell-generated
  include.
- **Devanagari renders as boxes in my Wine prefix** (font), in the menus and the wizard sidebar, before
  and after alike.
