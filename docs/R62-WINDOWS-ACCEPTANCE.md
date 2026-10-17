# Round 62 — Windows acceptance procedure (review branch)

**Scope:** Windows workstreams 1–3. This is an **unexecuted** standard-user, offline test harness. It does not certify native Windows execution, IDE colours, shell, GUI Run or the installer. Workstreams 4–5 remain **not implemented**.

## Run on a genuine Windows 10/11 desktop

Use a **normal non-elevated 64-bit PowerShell 5.1+** session. Clone/check out this review branch, install NASM + MinGW PE64 linker/compiler using the machine's existing approved build environment (never elevate or weaken protection for this test). From the repo root:

```powershell
powershell.exe -NoProfile -File .\tools\r62_windows_acceptance.ps1 -Stage Prepare
# If a real pre-R61 executable is available, re-run Prepare with:
#  -LegacyCompiler "C:\path\to\pre-r61\sutram.exe"
```

The Prepare stage calls `tools/r61_windows_compiler_diagnostics.ps1`, requiring `R61_PE_NORMAL_SIZE` and `R61_WINDOWS_COMPILE_EXECUTE_PASS` from **real** native Windows stdout, with the 64 KiB runaway-output guard and 12 s bounded processes. The optional legacy A/B prints `legacy-compile` elapsed time, exit, and observed output size; record those numbers, do not infer them. After success, it rebuilds `win/sutram.exe`, `sutram-ide-gui.exe`, and `windows/native-installer/output/Sutram-Setup-0.1.0-native-x64.exe` with the **current compiler** embedded; runs package `--self-test`; checks canonical `icons/sutram.ico` SHA; and saves `build-manifest.txt` to `%TEMP%\Sutram-R62-Windows-Acceptance`.

**Stop if Prepare fails.** Do not claim R61 fixed until the generated program really executes. With a passing Prepare, run the newly built setup EXE **interactively as standard user**, choose per-user `%LOCALAPPDATA%\Programs\Sutram`, complete the wizard, and note any failure text. No UAC should appear. If installation fails, retain `%TEMP%\Sutram-Setup-*\install.log`; report the actual `ERROR:` entry and do not infer a cause.

Then:

```powershell
powershell.exe -NoProfile -File .\tools\r62_windows_acceptance.ps1 -Stage Audit
```

Audit checks `HKCU\...\Uninstall\Sutram`, actual per-user install marker, real saved `install.log` and completion event, correct Start Menu `Sutram IDE.lnk` target and canonical ICO **byte hash**, byte equality of installed compiler with just-built compiler, bounded compilation of `R62_COLOUR_FIXTURE.sm`, actual generated PE stdout `R62_SHELL_AND_RUN_OK`, and creation of the installed GUI window. This is **not** an automated wizard-click test or evidence that visual colours/shell Run work.

## GUI screenshot and manual acceptance

In the installed GUI use **File > Open** to load `%TEMP%\Sutram-R62-Windows-Acceptance\R62_COLOUR_FIXTURE.sm`. Visually compare **orange keywords** (`mukhya`, `vitti`, `yadi`), **teal builtin** (`likha`), **green string**, **purple 123**, **grey # comment**. Check menus (File / Edit / Shell / Debug / Options / Window / Help), editor **Run** actual stdout, and `>>>` shell execution. If any fails, report the real symptom.

With that actual fixture visible, capture the desktop:

```powershell
powershell.exe -NoProfile -File .\tools\r62_windows_acceptance.ps1 -Stage Screenshot -CaptureGui
```

This produces `GUI_REVIEW_REQUIRED.png` beside the logs. **Someone must actually open and visually inspect it.** Capture install wizard and Start Menu shortcut icon separately; an ICO file's hash alone is not visual confirmation. Do not assume a GitHub runner has an interactive desktop.

## Preserved safety / limitations

- `windows/native-installer/install-core.ps1` restores R61's **bounded 8-second pre/post compiler self-tests** that were absent from `main`, and copies the successful installation log into `%LOCALAPPDATA%\Programs\Sutram\install.log`. Failure leaves the wizard's temporary log for diagnosis.
- `tools/r61_windows_compiler_diagnostics.ps1` is restored from the existing R61 draft branch with its original content. No assertion of fresh Windows results.
- `.github/workflows/r59-native.yml` removes an inherited `push` trigger; all repo workflows on **this branch** remain manual-only. No new workflows created, no CI runs launched, no notification flood.
- **No** compiler, language pack, approved golden, or GUI source code changed. No network calls, secrets, UAC elevation, HKLM writes or bypasses introduced.
- **Round 62 workstreams 4 and 5 remain open.** Push/pop and store/reload peephole need proven emission-site safety plus instruction counts and gates; automatic overflow traps need an opt-in compatibility story and actual native before/after evidence. Neither is claimed here.
