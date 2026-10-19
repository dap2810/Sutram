# R4-02 — WS2: the IDE buttons and the installer's own text in Sanskrit

**Commit `83af6270` on `claude/round-04`.** All screenshots were taken **under Wine 9 on Linux (Xvfb), not
on Windows.** They show layout and text. They are not Windows acceptance.

## 1. IDE buttons — `windows/gui/sutram_gui.asm`

| id | before | after | where the word comes from |
|---|---|---|---|
| 101 | `Run` | `chal` | X11 IDE menu `chal`; the Windows IDE's own run menu (R3) |
| 102 | `Open` | `khol` | X11 IDE menu `khol` |
| 103 | `Save` | `sanchay` | X11 IDE menu `sanchay` |
| 104 | `Load example` | `udaharan khol` | `udaharan` = example (R3 menu); `khol` as above |
| 105 | `Send` | `presh` | R3 word, still awaiting confirmation (R3-04 §2) |
| 106 | `Clear shell` | `phal_rikta` | X11 IDE menu `phal_rikta` |

`tools/test_windows_gui.py:143` checks these exact labels. It is a Windows-only test (`ctypes.windll`), so
it is **NOT-RUN here.** `MANUAL-WINDOWS-GUI-TEST.md`, `README-WINDOWS-GUI.md` and `TEST-ME.md` now use the
new names.

**Before / after (Wine):** `evidence-r4/screens/ide-before.png`, `ide-after.png`.
`ide-after-run-hello.png` shows `chal` working: "Namaste, Sutram!".

### A GUI defect found while taking the screenshots — fixed (my scope)

The IDE reported the wrong stage when something failed:

- **In the editor,** a *compile* error ended with "program ended abnormally".
- **In the shell,** a *runtime* error ended with "compile failed".

`compile_run` now records which stage failed (file 3, compile 1, run 2). The editor's `.printed` path and the
shell's `.error` path both print the message for that stage. Verified under Wine:

- compile error → `[sankalan asaphal]` (`ide-fix-compile-error.png`)
- out-of-bounds run → `[karyakram asamanya roop se samapt]` (`ide-fix-runtime-error.png`)

## 2. Installer text — `windows/native-installer/sutram_wizard.asm`

**49 strings, every one the user reads.** The full before/after table is below.

The wizard's `u16` macro widens ASCII bytes only, so every string is **romanised**, the same register as the
compiler messages. Devanagari would need a UTF-16 string macro, which is a change to ChatGPT's wizard
mechanics. I did not make it.

**Unchanged, on purpose:**

- window class names, the font name, the command-line arguments, environment variable names, file names
  and the PowerShell command lines
- the product names `Sutram IDE` and `Sutram Terminal` (Start Menu entries made by ChatGPT's script)
- `PATH`, `%TEMP%`, `Start Menu`, `Windows PowerShell`, `install.log`
- **the licence text.** It is `LICENSE.txt`, embedded as-is.

**One layout fix was needed for the translation.** The side-panel footer was drawn with a fixed length of
12, `len("SUTRAM SETUP")`, so `SUTRAM STHAPANA` came out as `SUTRAM STHAP`. It is now drawn NUL-terminated
(`mov r8d, -1`). This is a text-length fix inside the string change, not a behaviour change. I also shortened
the licence intro to one line so it is not clipped above the licence box.

**Before / after (Wine):**

- `wizard-welcome-before.png` / `wizard-welcome-after.png`
- the other pages after: `wizard-license-after.png`, `wizard-dir-after.png`, `wizard-comp-after.png`,
  `wizard-ready-after.png`

The `sthapana` button fits but has almost no margin.

| key | before | after |
|---|---|---|
| wiz_title / msg_title | Sutram Setup | Sutram sthapana |
| btn_back / btn_next | < Back / Next > | < purva / agrim > |
| btn_install / btn_finish / btn_cancel / btn_browse | Install / Finish / Cancel / Browse... | sthapana / samapt / nirast / chayan... |
| t_welcome | Welcome to Sutram Setup | Sutram sthapana me svagat |
| t_license | License Agreement | anugyapti anubandh |
| t_dir | Choose Install Location | sthapana sthan |
| t_comp | Select Components | ghatak chayan |
| t_ready | Ready to Install | sthapana ke liye sajja |
| t_prog | Installing Sutram | Sutram ki sthapana |
| t_done | Completing the Sutram Setup Wizard | Sutram sthapana purna |
| b_welcome | This wizard will install Sutram, the Sanskrit-keyword programming language, on your computer. | yah sahayak aapke sanganak par Sutram sthapit karega - Sanskrit kunjishabd vali programming bhasha. |
| b_welcome2 | Sutram installs for the current Windows user only. No administrator rights are needed, and nothing is written outside your own account. | Sutram keval vartaman Windows upayokta ke liye sthapit hota hai. prashasak adhikar avashyak nahi, aur aapke khate ke bahar kuchh nahi likha jata. |
| b_welcome3 | Click Next to continue. | aage badhne ke liye agrim dabaiye. |
| b_lichead | Please read the following license agreement. You must accept the terms to continue. | anubandh padhiye. aage badhne ke liye svikar avashyak hai. |
| b_accept / b_decline | I &accept / I do &not accept the terms of the license agreement | anugyapti anubandh ki shartein &svikar / &asvikar |
| b_dirlabel | &Install location: | sthapana &sthan: |
| b_dirnote | Setup will install Sutram in the folder below. The installer needs write access to this folder. | Sutram neeche ke folder me sthapit hoga. is folder me likhne ka adhikar avashyak hai. |
| b_complbl | Select the components to install: | sthapana ke ghatak chuniye: |
| b_ckpath | &Add Sutram to my user PATH (recommended) | Sutram ko mere upayokta PATH me &jodiye (anushansit) |
| b_ckdesk | Create a &desktop shortcut (Sutram Terminal) | &desktop par shortcut (Sutram Terminal) |
| b_compnote | The compiler, standard library, language packs, examples and books are always installed. Start Menu shortcuts are always created. | sankalak, manak pustakalaya, bhasha pak, udaharan aur pustakein sada sthapit hote hain. Start Menu shortcut sada bante hain. |
| b_ready / b_ready2 | Setup is ready to install Sutram on your computer. / Click Install to begin the installation. | Sutram aapke sanganak par sthapana ke liye sajja hai. / aarambh ke liye sthapana dabaiye. |
| b_proging | Please wait while Sutram is installed... | kripaya pratiksha kijiye, Sutram sthapit ho raha hai... |
| b_donemsg / b_donemsg2 | Sutram has been installed successfully. / You will find Sutram IDE and Sutram Terminal in your Start Menu. | Sutram safaltapurvak sthapit ho gaya. / Sutram IDE aur Sutram Terminal aapke Start Menu me milenge. |
| b_cklaunch | &Launch Sutram IDE | Sutram IDE &aarambh |
| st_extract / st_script / st_final | Extracting package files... / Running setup script (this can take a minute)... / Finalizing installation... | pak ke patra nikale ja rahe hain... / sthapana script chal raha hai (ek minat lag sakta hai)... / sthapana purna ho rahi hai... |
| sum_dir / sum_path_y,n / sum_desk_y,n | Destination folder: / Add to user PATH: yes,no / Desktop shortcut: yes,no | lakshya folder: / upayokta PATH me jodna: haan,nahi / desktop shortcut: haan,nahi |
| msg_failed | Sutram setup did not complete. Check the install log in %TEMP% (unique STM folder) for details. | Sutram sthapana purna nahi hui. vivaran ke liye %TEMP% (STM folder) me install.log dekhiye. |
| msg_nopower | Sutram setup could not start Windows PowerShell. | Sutram sthapana Windows PowerShell aarambh nahi kar saki. |
| msg_nodir | Please choose an install location first. | kripaya pahle sthapana sthan chuniye. |
| msg_fb_ask | Install Sutram for the current user with default options? | Sutram ko vartaman upayokta ke liye mool vikalpon se sthapit karein? |
| msg_uninst_done / _failed | Sutram was removed from this user account. / Sutram could not be fully removed. | Sutram is upayokta khate se hata diya gaya. / Sutram poori tarah hataya nahi ja saka. |
| brow_title | Select the folder to install Sutram in | Sutram ke sthapana folder ka chayan |
| side_footer | SUTRAM SETUP | SUTRAM STHAPANA |

## Two things you should know before accepting the words

1. **`docs/sutram-vocabulary.html` is the frozen vocabulary for the language.** Its keywords and library
   names contain almost none of these UI words. I checked: of the 37 words above, only `agrim`, `phal`,
   `manak`, `bhasha` and `patra` occur there.
   - The six button words come from the X11 IDE, which is already merged.
   - The installer words are **new** and need your confirmation (R4-04 §2).
   - The full sentences are closer to **Hindi grammar in romanisation** (`ho raha hai`, `kijiye`) than to
     Sanskrit. That is the register the merged compiler messages already use (`Sanket: is sthan par shabd aur
     vyakaran dekho`), so I matched it. If you want a stricter Sanskrit register, say so and I will redo the
     table.
2. **`agrim` is a keyword (`continue`), and the wizard uses it for "Next".** This is the same kind of
   collision as `prakriya` in R3-04 §2. It is harmless in a button, but it is your call.

## Commands

```
nasm -f win64 -I./ windows/gui/{r67_gui_entry,r66_indic_clusters,r67_cluster_count}.asm   # each → .obj
x86_64-w64-mingw32-ld -mi386pep --subsystem windows --entry=_start -o gui.exe *.obj \
    -L/usr/x86_64-w64-mingw32/lib -lkernel32 -lshell32 -luser32 -lgdi32            → GUI_LINK_OK
nasm -f win64 -I<stage>/ -I./ windows/native-installer/sutram_wizard.asm -o w.obj
x86_64-w64-mingw32-ld -mi386pep --subsystem windows --entry=_start -o wizard.exe w.obj -lkernel32 -lbcrypt
DISPLAY=:99 WINEPREFIX=… wine64 wizard.exe ; import -window root … ; xdotool mousemove X Y click 1
```

The wizard staging folder held a 160-byte placeholder `payload.zip` and generated `embedded_hashes.inc`.
That is enough to render the pages; it is **not** a real payload.

## Not done / not verified

- **NOT-RUN on Windows.** No native rendering, no DPI scaling, no screen reader, no Windows `test_windows_gui.py`.
- **The icon resource was not built.** `-dR73_ICON` needs `r73_icon.inc`, which PowerShell's
  `Write-IconResourceInclude` generates, so the Wine builds have no icon resource. The sidebar logo still shows
  in the wizard because it is drawn.
- **Devanagari renders as boxes under Wine** in the sidebar, in both the before and the after builds. This is a
  font problem in my Wine prefix, not a wizard change. On Windows R3 showed it rendering.
- **No Devanagari strings in the wizard.** The `u16` macro handles ASCII only.
- **Seen in the IDE, not changed:**
  - A diagnostic in the IDE names the temp file (`STGxxxx.tmp:8:25`), not the example's name.
  - A REPL error names `.sutram_repl.sm`.
  - Both are true but unhelpful to a beginner. The fix is to pass the display name to the compiler, which
    would need a compiler flag. I did not add one.
