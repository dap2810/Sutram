# R130-00 — The installer now refuses while another Sutram is installed, names it, and with Add to PATH finishes only when a new terminal runs this compiler and prints this version. The engine runs with no console window, non-interactive, logs every step, and the wizard stops it after 15 minutes instead of waiting forever. I did not find the hang's cause from the source; I removed every candidate I could name, and the new log will show where it stops if it happens again. Shipped in v306 with R131.

## Release line

```
gates: 69 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v306) - sampurna sutra
```

- **Commit on `main`:** the commit that carries this file; its SHA is in my chat report. Base: `30be5ac` (v305).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer:** `PASS payload v306 = compiler v306`, `Sutram-Setup.sha256` = `e6006caf2bacebf378b9d3b8cd4527d63c1de6ac2e96efa630e5c268ff852e5f`, `--self-test` exit 0 under Wine. Gate `R130 installer engine`: 16 checks, 0 failed.
- **The guard** (v305 → v306, 737 programs) is in R131-00: Linux ELF 584 identical / 153 refused / 0 DIFFER; PE 584 DIFFER (the Windows runtime changed), all 584 run old and new under Wine: the same output and exit.

**Not done, said plainly:**
- **No PowerShell ran here.** There is none in this container and the download of one was refused. `install-core.ps1` was changed by reading; its brackets balance; the gate checks it statically. The wizard was built and its `--self-test` runs under Wine, but the install itself has **NOT RUN**.
- **The hang's cause is not established** (WS1 below).
- **The Windows round (WS4) is the owner's:** `tests/windows/test_installer_e2e.py --i-understand-this-installs`, then the v306 round.

## WS1 - why the completion step did not run

**I read the engine as v303-v305 shipped it (`windows/native-installer/install-core.ps1`).** The answers to your four candidates:

| candidate | in the engine? |
|---|---|
| a `Read-Host` or any prompt | **no** - none anywhere |
| a job not waited on | **no** - no `Start-Job`; the one child process (the self-test) waits 8 s, then kills |
| an error swallowed by `-ErrorAction SilentlyContinue` | **no, not here** - the four uses are a registry read, a folder listing and two cleanups; `$ErrorActionPreference = 'Stop'` turns any other error into the `ERROR:` log line, and the log had none |
| a call that never returns | **only the copy itself is left** |

**Where it stopped, exactly.** After `Copying Sutram files.` the next thing that logs is the self-test, which logs `Native self-test start: post-install --version` *before* it starts anything. That line is missing. So the engine stopped inside these three lines and nowhere else:

```powershell
Copy-Item -Path (Join-Path $stage '*') -Destination $InstallDir -Recurse -Force
Copy-Item -LiteralPath $SetupExePath -Destination (Join-Path $InstallDir 'Sutram-Uninstall.exe') -Force
[IO.File]::WriteAllText($marker, ...)
```

**The version check is not part of it.** The post-install `--version` runs `bin\sutram.exe` by its full path, so it would have printed v303; the hang came before it. **The hang and the wrong version are two defects** (WS2 is the second).

**Why a copy of 658 files would not return: I cannot tell from the source.** What I know of the environment, from the wizard:
- **The wizard started PowerShell with a visible console window** (`CreateProcessW` with no creation flags) and **waited on it with `INFINITE`.** That is why PowerShell "remained open and had to be closed by hand": nothing would ever close it.
- **A visible console can stop a process:** a click in a Windows console window starts QuickEdit selection, and the next write to that console blocks until the selection ends; anything PowerShell writes there - a progress record, a warning - then waits. I could not check which writes Windows PowerShell 5.1's `Copy-Item` makes. **This fits the report, but it is a hypothesis; nothing here confirms it.** An antivirus scan of each new `.exe` would make the copy slow, not endless.

**What v306 changes** (`install-core.ps1`, `sutram_wizard.asm`):
1. **No console:** the engine starts with `CREATE_NO_WINDOW` and `-NoProfile -NonInteractive -ExecutionPolicy Bypass`. The uninstaller gets the same flags.
2. **Nothing can prompt:** `$ProgressPreference = 'SilentlyContinue'`, `$ConfirmPreference = 'None'`.
3. **The copy logs:** `Copy-StagedFiles` copies file by file with `[IO.File]::Copy` (no progress records), logs every 100 files and the count at the end; the uninstaller copy and the marker log too; so do the shortcut and registry steps. ~~If it stops again, the last log line names the file.~~ **Correction (R132): it does not** - the last line names the last hundredth file, not the one the copy stopped in. Logging each file before it is copied is proposed in R132-00.
4. **The wizard cannot wait forever:** `WaitForSingleObject` waits 15 minutes (`ENGINE_WAIT_MS`); then it ends the engine (`TerminateProcess`), the install is reported failed, and the log is shown. A slow machine copies the payload (658 files, 5.4 MB) in well under a minute, so 15 minutes is a hang, not a slow disk.
5. **Completion is checked, not assumed:** the engine still ends with `Installation complete: <folder>` only after the post-install self-test, and with Add to PATH, only after the WS2 check.

## WS2 - two installations: detect and refuse, as you said

**I built detect and refuse.**
- **Before it stages anything,** the engine looks for another `sutram.exe` where a new terminal could find it: every folder on the machine PATH and the user PATH (as the registry has them now, not as the installer's own process inherited them), and the legacy `%LOCALAPPDATA%\Sutram\bin\` and `%LOCALAPPDATA%\Sutram\`. Its own `bin\` (a re-install or upgrade of the same folder) does not count.
- **If one is found it stops:** `Another Sutram is already installed: <path>. A new terminal could run that one instead of this. Uninstall it (Settings > Apps > Sutram, or its own uninstaller), or delete that folder and remove it from PATH, then run this installer again.` Nothing is copied. A PATH folder with no `sutram.exe` in it does not count.
- **With Add to PATH, after writing PATH,** it asks a fresh `cmd.exe` - PATH rebuilt from the registry, working folder `%TEMP%`, 8 s limit - which `sutram.exe` comes first and what `sutram --version` prints. **Unless that is this folder's `bin\sutram.exe` and this version, the install fails** with both shown. This is the check that would have caught v303: it asks the question a student's new terminal asks.

**Why not the other two:**
- **Removing or upgrading the old one:** the old `AppData\Local\Sutram` is not this installer's. It has no manifest of ours; a student may have their programs in it. Deleting what we did not install is the wrong default, and "upgrading" it means guessing its layout.
- **A PATH entry that takes precedence:** on the owner's machine both entries are in the **user** PATH (ChatGPT's diagnostic, `9ae1b12`, corrects the earlier reading), so putting ours first there would have worked on that machine. But Windows puts the machine PATH before the user PATH, so an old machine-wide install would still win without administrator rights; and either way two compilers stay installed, with the order deciding which one a student gets - the defect, made permanent and harder to see.
- **Refusing is the one that leaves one compiler,** and says where the other is.

## WS3 - was there a gate? No.

- **Nothing in the tree installed.** The installer gates (`R93`, `check_installer_version`) are static: they read the payload's version, hashes and files. They passed v303, correctly - the payload *was* v303. **Neither defect is in the payload;** both are in what happens on a machine.
- **Now there are two:**
  - **`R130 installer engine`** (Linux, in `tools/gates.sh`, 16 checks): the wizard's flags, no window, a bounded wait with terminate, the engine's preferences, no prompt anywhere, the per-file copy, the other-Sutram refusal before staging (and the legacy folder), the fresh-terminal check and version comparison, the completion log, and that `Sutram-Setup.exe` embeds this tree's engine and uninstaller. **Run on v305's wizard, engine and `Sutram-Setup.exe` (copies from `30be5ac`), it fails 12 of 16;** the 4 it passes are true of v305 too (no prompt in the engine, the completion line, the exe embeds its own scripts). On v306: 0 failed. Both runs are in the evidence.
  - **`tests/windows/test_installer_e2e.py`** (Windows only; changes this user's install, so it needs `--i-understand-this-installs`): runs the engine the wizard runs, with `-AddPath`, checks it exits 0 within 15 minutes and logs completion, then a new `cmd.exe` with PATH from the registry: `where sutram` must list the installed `bin\sutram.exe` first and `sutram --version` must print the tree's version; then it uninstalls and checks PATH. **That is the gate you described. It is NOT RUN here; it is in the gate list's Windows NOT-RUN.**

## What landed on `main` while I worked (ChatGPT, native Windows, read before this was sent)

- **`9ae1b12`, the diagnostic:** on the owner's machine as it was, the v305 installer did not hang - it refused before copying, both times, because the installed `bin\sutram-link.exe` did not match the previous install's manifest (`Upgrade would overwrite a user file`). **The copy-stage hang was not reproduced.** It also found:
  - **the wizard shows 90 % ("finalizing") as soon as the engine exits, before it looks at the exit code** (`sutram_wizard.asm` near the `WaitForSingleObject`), so a nearly full bar is not evidence of success. The failure dialog is still shown. **Not changed in v306** - a display order, not a wrong result; next round if you want it.
  - the registered DisplayVersion is still `0.1.0`. **Not changed in v306.**
- **`870acb3`, the repair (owner-authorized):** the 137 files moved to `Programs\Sutram-recovery-20261106-205221`, then the unchanged v305 installer ran into the empty folder: **it finished in about 15 s, closed normally, 657 of 657 files match, and bare `sutram` from a new terminal is v305.**
- **What this means for R130:** the hang has now been seen once (v303, by the owner) and not again (v305, twice refused, once complete). **Its cause is still not established** - I say so above and do not claim the v306 changes fixed it. They make it impossible to wait forever, and make the log say where it stopped.
- **On that machine now:** `%LOCALAPPDATA%\Sutram\bin` is still in the user PATH, ahead of `Programs\Sutram\bin`, but bare `sutram` resolves to the new install, so there is no `sutram.exe` in it. **v306's check does not refuse for that;** it would if a `sutram.exe` were there again. The machine has v305 installed, so `test_installer_e2e.py` will refuse (it needs a machine with no Sutram) - run the v306 wizard over it as an upgrade instead, then a new terminal: `where sutram` and `sutram --version`.

## WS4 - v306

v306 carries this and R131. The installer is rebuilt (above). **The Windows round on v306 is the owner's** - in this order: `test_installer_e2e.py`, then the wizard by hand (it should refuse while `AppData\Local\Sutram` is on PATH, naming it), then the R131 probes and the native suite.

Evidence: `Claude-to-Sarvam/evidence-r130-r131/`.
