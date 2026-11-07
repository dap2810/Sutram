# Follow-up commands and scope

Working directory: `E:\Github_Projects\Sutram`, normal Windows user token.

**Publication note:** upstream commit `60ce554d` introduced v307 after these
measurements. It was integrated while publishing this evidence-only commit.
The installed/restored product and every execution in this report are still
**v306**. No v307 compiler or installer was executed in this round. Reproduce the
installer experiment from the pinned v306 source `da349daf` with these diagnostic
files; the setup hash guard deliberately rejects the newer executable on main.

```powershell
git fetch origin
git merge --ff-only origin/main
python Windows-to-Sarvam/win-v306-followup-2026-11-06/oom.py
& .\Windows-to-Sarvam\win-v306-followup-2026-11-06\inventory.ps1
& .\Windows-to-Sarvam\win-v306-followup-2026-11-06\run.ps1
& .\Windows-to-Sarvam\win-v306-followup-2026-11-06\upgrade.ps1 -ExistingWizardPid 42236
```

The fetched source was `da349daf`; changes since the previous report were
documentation-only. The OOM script compiles two copied probes using the installed
compiler and executes 21 B3 runs plus ten mandapa runs. `job_runner.py` is the
unchanged runner from the prior rounds. JSON records each exact compiler and
program argv and working directory. Generated executables stay under `build/`.

The first `run.ps1` invocation verified a 662-file backup, opened the wizard,
then its observer attempted to click Next before that control existed. It
stopped **before installation began**. The original observer and its result are
archived as `upgrade-initial-observer.ps1` and `navigation-attempt.json`.
The corrected observer waits for each control and resumed that same welcome
window. There was one actual same-directory upgrade attempt, not two installations.

The observer records the real child command line, process state, engine-log
progress and any completion/error dialog. It captures stall evidence after
30 seconds without log progress, and leaves the installer processes untouched
through a 935-second observation. `openfiles /query /fo table` is read-only;
local tracking was disabled and the remote-query section returned access denied.
No tracking, security or machine-policy setting was changed.

Additional read-only evidence collection:

```powershell
python Windows-to-Sarvam/win-v306-followup-2026-11-06/security-log-read.py
& .\Windows-to-Sarvam\win-v306-followup-2026-11-06\capture.ps1 -TargetProcess 42236 -Mode Screen
& .\Windows-to-Sarvam\win-v306-followup-2026-11-06\capture-dwm.ps1
& .\Windows-to-Sarvam\win-v306-followup-2026-11-06\after-deadline.ps1
& .\Windows-to-Sarvam\win-v306-followup-2026-11-06\restore.ps1
```

The first window capture could not return while the source UI was suspended;
its helper was bounded and stopped, without touching the installer. Direct
screen captures were obscured by the terminal and are excluded from publication.
The accepted screenshot is the existing window's DWM thumbnail rendered into
a short-lived preview and captured with `PrintWindow`; it was visually inspected.
This captures the suspended window without sending installer input or resuming
its threads. Implementation references:
[DwmRegisterThumbnail](https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/nf-dwmapi-dwmregisterthumbnail),
[DWM_THUMBNAIL_PROPERTIES](https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ns-dwmapi-dwm_thumbnail_properties).

`security-log-read.py` saves narrowly selected Acronis log excerpts around the
two runs' verified process suspension records, with source paths and line numbers.
It does not copy unrelated application activity into the published evidence.

After the completed timeout observation, `restore.ps1` validates the test-owned
PIDs and creation times, stops only those remaining installer processes, preserves
the partial tree and restores the verified pre-test backup. Its separate result
is restoration verification, not a repeated clean-install acceptance test.

The installation/GUI operations required approved tool access outside the
workspace. The installer rejects an elevated Administrator token. No debugger
was installed, no original example or product code was changed, and no GitHub
Actions run was launched.

The file-access check selected the eight highest CreationTime entries from
`stall.json`, then opened each with `FileMode.Open`, `FileAccess.Read`, and
`FileShare.ReadWrite -bor FileShare.Delete`, closing it immediately. The candidate
file and its preserved counterpart were compared with `Get-FileHash -LiteralPath`.
Defender was queried with `Get-WinEvent -FilterHashtable` against
`Microsoft-Windows-Windows Defender/Operational`, from the observer start to the
query/end time. Full query errors and timestamps are saved in the JSON evidence.

`streams/*.stderr` is marked `-text` in the local `.gitattributes` so a Windows
checkout cannot turn the measured final LF into CRLF. Staged Git blobs were
compared against the recorded raw hex. Original Windows error transcripts retain
their trailing whitespace; the ordinary diff check flags only those captured
transcript lines. The final whitespace check used command-local
`core.whitespace=-blank-at-eol,-blank-at-eof` without altering repository settings.
