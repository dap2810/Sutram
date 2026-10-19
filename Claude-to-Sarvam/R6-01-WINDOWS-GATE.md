# R6-01 — WS1: `tools/accept-windows.ps1`, Windows as a gate

**Branch `claude/round-06`, commit `452aa523`.** Base: main `04aa7bb3` (v176). Three files:

| File | What it is |
|---|---|
| `tools/accept-windows.ps1` | The gate. One script; Windows PowerShell 5.1 or 7; ASCII. It writes `accept-windows.json` plus screenshots. |
| `tools/check_accept_windows_log.py` | **The half you run.** It reads a returned log on Linux and says whether it is Windows acceptance of *this* tree. |
| `tests/windows_accept/test_check_log.py` | 7 tests: what a log does and does not prove, and that the script is ASCII and names every required check. |

`TEST-ME.md` has a new section with the one command to run and what to send back.

## Read this first: what ran where

**Not one check in this round ran on Windows. I have no Windows here.** I ran the script under **Wine 9.0
on Linux** three times, against three builds. The logs are in `evidence-r6/`.

- **Wine has no UAC.** Every Wine process carries an administrator token. So the two least-privilege
  checks print **NOT-RUN** under Wine, and every check in a Wine log is labelled `"environment": "Wine"`.
- **The verdict line says so too:** `FAIL (Wine only - NOT Windows acceptance)`.
- **Your checker refuses a Wine log by design.**

**The gate becomes a gate when the owner runs it once on Windows.** Rebuild the tree with
`windows\BUILD-WINDOWS-SETUP.cmd`, then:

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools\accept-windows.ps1
```

Run it from a normal, **not administrator**, window. Send back the `build\windows\accept-*` folder. Then on
your side:

```
python3 tools/check_accept_windows_log.py <folder>/accept-windows.json
```

The checker prints **ACCEPTED** only when all of these hold:

- the run was on Windows
- the run was not elevated
- every required check is PASS
- every binary hash in the log matches this tree

## What the log contains (your four requirements)

1. **The SHA-256 of each binary it tests.** The log carries an `artefacts[]` list:
   - `Sutram-Setup.exe`, plus a cross-check against `Sutram-Setup.sha256`
   - the repository `win\sutram.exe`, `sutram.exe` and `sutram-ide-gui.exe`
   - **after install, the installed copies:** `bin\sutram.exe`, `win\sutram.exe`, the IDE and
     `Sutram-Uninstall.exe`, so the installed payload can be tied to the build
   - the SHA-256 of the script itself
   - the git commit, read from `.git` when no git is installed
2. **The Windows version and build, and elevation.**
   - `windows_product`, `windows_display_version`, `windows_build`, `windows_ubr` (from the registry)
   - `TokenElevation` and `TokenElevationType` of the script's own process, plus Administrators-role
     membership
   - the same token fields **of the setup process it started**, and whether `consent.exe` (the UAC prompt)
     appeared during the install
3. **Per-check PASS / FAIL / NOT-RUN as JSON.** A check that cannot be automated is written as NOT-RUN with
   the reason. Nothing is left out silently.
4. **The exact command and raw output** for every check, plus `detail`, `environment` and `time`.

## The checks

| id | How it runs | Required |
|---|---|---|
| `runner-not-elevated` | the token of the script's own process | yes |
| `setup-hash-file` | `Sutram-Setup.exe` against `Sutram-Setup.sha256` | advisory |
| `setup-self-test` | `Sutram-Setup.exe --self-test` (embedded SHA-256) | yes |
| `install-no-elevation-prompt` | the setup is started with no RunAs verb; its process token is not elevated; no `consent.exe` appeared | yes |
| `install-wizard` | **BM_CLICK on the wizard it started:** Next, I accept, Next, Next, Install, then Finish with "Launch" unchecked. It logs whether Next was disabled before accepting, the default folder, the PATH and desktop boxes, and copies `install.log`. | yes |
| `install-footprint` | the installed files, 3 Start Menu shortcuts, the HKCU uninstall and class keys, the user PATH entry | yes |
| `devanagari-cli` | the installed `bin\sutram.exe --lang sanskrit 218_sanskrit_devanagari.sm`, run; it must print `योगः = 15` | yes |
| `ide-launches` | the installed IDE from its own folder; a `SutramNativeGUIWindow` within 15 s; pid, title, token | yes |
| `ide-menus-english` | `GetMenu` / `GetMenuStringW`: the top level must be exactly `File Edit Shell Language Help`, and all 21 items must be present | yes |
| `ide-buttons-english` | `WM_GETTEXT` on controls 101–106 and 208: `Run Open Save "Load example" Send "Clear shell"`, `Find:` | yes |
| `devanagari-ide` | editor = the 218 program; Language > Auto; Shell > Run module; the output must contain `योगः = 15` | yes |
| `tab-indent` | real `WM_KEYDOWN`+`WM_CHAR` VK_TAB to the editor: at a line end, and on a two-line selection | yes |
| `shift-tab-dedent` | Edit > Dedent, the command Shift+Tab is bound to. **With `-Keyboard`, also a real `SendInput` Shift+Tab.** | yes |
| `shift-tab-keyboard` | **NOT-RUN without `-Keyboard`:** real keys need the IDE in the foreground, so the person must not touch the mouse or keyboard | advisory |
| `unsaved-guard` | edit, then File > New; the question box must appear; Cancel must keep the text | yes |
| `uninstall-removes-install` | the installed `Sutram-Uninstall.exe --uninstall`, the Start Menu target. It waits for `uninstall.log`, then checks every footprint item is gone. | yes |
| `uninstall-folder-gone` | the install folder itself | advisory |
| `temp-staging-cleaned` | new `%TEMP%\STM*.tmp` folders. This is the known defect from R4-03 §3. | advisory |

**What it will not do:**

- **It refuses to install over an existing Sutram.** All install checks become NOT-RUN, with the
  existing folder named (tested: `evidence-r6`, run 11 in the harness notes).
- It never elevates and never touches HKLM.
- It sends window messages only to processes it started.
- Its screenshots are of its own windows only (`PrintWindow`), never the desktop.

## The three Wine runs (environment: Wine 9.0, PowerShell 7.2.24, Linux Xvfb)

All three logs carry script SHA-256 `d290257c…`, the committed script.

| Run | What was tested | Verdict | Required PASS / FAIL / NOT-RUN |
|---|---|---|---|
| **A** `A-main-committed` | **The binaries committed on main**: `Sutram-Setup.exe de52bab0…`, `sutram.exe a534a693…`, `sutram-ide-gui.exe 89fbde50…`. The checker confirms they **MATCH this tree**. | FAIL (Wine) | 5 / 4 / 5 |
| **B** `B-fresh-build` | **v176 source, freshly cross-built** the way `build-installer.ps1` does it | FAIL (Wine) | 9 / 1 / 5 |
| **C** `C-harness-build` | B, with **two lines changed in the install and uninstall scripts so Wine can run them** (`HARNESS-ONLY.diff`). **This is not a Sutram build;** it exists only to exercise the gate's install-to-uninstall path. Run with `-Keyboard`. | PARTIAL (Wine) | **12 / 0 / 3** |

**Run A tells you something you should know.** The Windows binaries committed on main are the **ROUND-03
build**. They predate R4's undefined-name error, R5's English labels and R5's colouring.

- The gate fails the committed IDE on its `anwesh:` find label and its Sanskrit unsaved-file question.
- Its `devanagari-ide` fails because **main commits no `win\sutram.exe`**, which the IDE needs beside it.
  The R3 IDE then reports the failure as "ended abnormally", the wrong-stage bug that R4 fixed.

Rebuilding is the first step on Windows. **I recommend that a v176 Windows build is committed only together
with its `accept-windows.json`.**

**Runs B and A fail `install-wizard` under Wine, and only because of Wine:**

- `install-core.ps1` sets `IconLocation = '…\sutram.ico'` without `,0`.
- Windows accepts that; Wine's `WScript.Shell` returns `E_FAIL`. Run C adds `,0` and installs.
- The same goes for uninstall: Wine returns a null `TargetPath` for an existing `.lnk`, and
  `uninstall-core.ps1:146` calls `.StartsWith` on it.

Neither is a Windows defect. **Both would be a one-line hardening for ChatGPT, if wanted.**

**Run C proves the gate's own machinery under Wine:**

- the wizard driving, the done-page detection and the footprint
- the IDE checks, including real `SendInput` Shift+Tab
- the unsaved-file box found and answered
- the uninstall wait and the removal checks

**It does not prove Windows behaviour.**

## Two defects of ChatGPT's that the Wine runs showed (reported, not fixed)

1. **A failed install leaves a half-install that cannot be retried.** After the run-B failure:
   - the install folder held `LICENSE.txt README.md Sutram-Uninstall.exe assets bin …`
   - the user PATH held its `bin` entry
   - there was no uninstall registration
   - the next install was refused: `ERROR: Existing installation ownership metadata is incomplete.`
     (`evidence-r6`, harness notes, run 9)

   `install-core.ps1` has no rollback. The trigger here was Wine's, but **any failure after "Copying Sutram
   files" on Windows ends the same way.** The user must delete the folder and edit PATH by hand.
2. **Uninstall reports nothing on success.** The uninstaller starts PowerShell and exits at once, so it
   can remove its own file, and `msg_uninst_done` is never shown. The only sign that it finished is
   `uninstall.log` in `%TEMP%`. The gate waits for that log. A person gets no confirmation.

## Commands and output

```
$ /tmp/pwsh/pwsh -c '[Parser]::ParseFile("tools/accept-windows.ps1",…)'      → PARSE OK
$ Add-Type of the C# helper (pwsh 7.4, Linux)                                  → COMPILED (23 public methods)
$ python3 -m unittest discover -s tests/windows_accept                         → Ran 7 tests … OK
$ wine64 powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\accept-windows.ps1 [-Keyboard]
    → evidence-r6/{A,B,C}/accept-windows.json, console.txt, screenshots, install.log / uninstall.log
$ python3 tools/check_accept_windows_log.py evidence-r6/A-main-committed/accept-windows.json
    → binaries MATCH this tree; NOT ACCEPTED: under Wine; elevated; 4 FAIL; 5 NOT-RUN   (checker.txt)
```

**How Wine was made to run it** (`evidence-r6/*.sh`, `powershell_shim.c`):

- Wine's own `powershell.exe` is a stub that exits 0. Before this round's fix, that is why the R4
  wizard "succeeded" without installing anything.
- I put PowerShell 7.2 in `C:\pwsh72` and replaced the stub with a 20-line forwarder.
- The runs need a pseudo-terminal, because PowerShell fails without a console under Wine.

## Not verified, plainly

- **Windows, all of it.** Two things specifically:
  - **PowerShell 5.1 has not run this script.** I wrote it to the 5.1 subset and kept it ASCII; the C# is
    C# 5, which is what 5.1 compiles. It was parsed and compiled only by 7.x. **The owner's run is the
    first real test.**
  - The menu check has not run anywhere: Wine cannot read another process's menu. On Windows `GetMenu`
    across processes is standard.
- **UAC behaviour:** the token and `consent.exe` logic is untested, because Wine has no UAC.
- **Screen scaling, a real keyboard layout, a screen reader.**
- **`-Keyboard` on Windows.** SendInput needs the IDE in the foreground; Windows can refuse
  `SetForegroundWindow` to a background process, and the check would then FAIL rather than lie.
