# Exact execution commands

Working directory: `E:\Github_Projects\Sutram`. Scripts and `.sm` probes are
retained on branch `codex/windows-v305-2026-11-06`, in this evidence folder.
Full per-process argument arrays and CWDs are in the JSON logs; commands used no
execution-policy bypass or Windows administrator elevation.

```powershell
git status --short --branch
git fetch origin
git log -5 origin/main --oneline
git diff --name-only HEAD origin/main
powershell -NoProfile -File Windows-to-Sarvam/win-v305-2026-11-06/environment.ps1 -Phase Before
powershell -NoProfile -File Windows-to-Sarvam/win-v305-2026-11-06/cleanup.ps1
powershell -NoProfile -File Windows-to-Sarvam/win-v305-2026-11-06/cleanup-finish.ps1
powershell -NoProfile -File Windows-to-Sarvam/win-v305-2026-11-06/environment.ps1 -Phase After
python Windows-to-Sarvam/win-v305-2026-11-06/verify.py identity
python Windows-to-Sarvam/win-v305-2026-11-06/verify.py probes
python Windows-to-Sarvam/win-v305-2026-11-06/verify.py suite
powershell -NoProfile -File Windows-to-Sarvam/win-v305-2026-11-06/ide.ps1
python Windows-to-Sarvam/win-v305-2026-11-06/followups.py
python Windows-to-Sarvam/win-v305-2026-11-06/oom_limit.py
python Windows-to-Sarvam/win-v305-2026-11-06/oom_limit.py B2 128
python Windows-to-Sarvam/win-v305-2026-11-06/oom_limit.py B3 64
python Windows-to-Sarvam/win-v305-2026-11-06/oom_limit.py B3 256
python Windows-to-Sarvam/win-v305-2026-11-06/oom_limit.py B3 2048
python Windows-to-Sarvam/win-v305-2026-11-06/environment_report.py
powershell -NoProfile -File Windows-to-Sarvam/win-v305-2026-11-06/restore-unrelated-path.ps1
powershell -NoProfile -File Windows-to-Sarvam/win-v305-2026-11-06/environment.ps1 -Phase After
python Windows-to-Sarvam/win-v305-2026-11-06/environment_report.py
```

The first `git fetch origin` was sandbox-denied for `.git/FETCH_HEAD`; the same
command succeeded with sandbox approval. Cleanup and native GUI execution also
used sandbox approval because they operate outside the workspace or launch a GUI.

`environment.ps1` reconstructed PATH from machine and user registry values before
launching fresh `cmd.exe /d /c` processes for `where sutram`, `sutram --version`,
and `echo %PATH%`. It also ran:

```text
reg.exe query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path
reg.exe query "HKCU\Environment" /v Path
```

It invoked each returned `sutram.exe --version` by its absolute path and recorded
its SHA-256. Output was pipe-captured, not an interactive terminal screenshot.

`cleanup.ps1` verified the old folder's resolved absolute path, absence of reparse
points, and expected compiler hash, then ran:

```text
"C:\Users\dmech\AppData\Local\Sutram\uninstall.exe" /uninstall
```

It confirmed only the owned uninstaller's removal and completion dialogs. The
uninstaller exited 0 but left `uninstall.exe`, so the first cleanup script
reported FAIL rather than claiming completion. After inspecting that the folder
contained only the expected uninstaller, `cleanup-finish.ps1` verified its hash,
removed that file and the now-empty directory using literal paths (no recursive
delete), and removed the exact stale old-install entry from the user PATH.

The first environment report generation stopped on an assertion: an unrelated
Codex bin entry was also missing after uninstall/cleanup. The original after
record was copied to `environment-after-uninstaller.json`. The restoration script
verified that no intervening PATH change had occurred and restored only that
missing entry to its original first position. The after-audit and report generation
were then repeated. The final check requires exact equality with the original
user PATH minus the old Sutram entry, not merely that the new compiler resolves.

`verify.py probes` compiled B1-B8 exactly as supplied, followed by separately
named corrected/supplemental cases. Each successful compilation was executed
natively. The 30-second timeout was extended to 60 seconds for B3. The probe and
suite commands ran concurrently; their output directories were disjoint.

`verify.py suite` ran the repository harness in memory with only
`out=ROOT/'build/windows/acceptance'` changed to
`build/windows-v305-2026-11-06/suite`. The original harness file was not edited.
The original hash and override are in `suite-harness.json`; the suite's own
compile/run commands are in `native-cases.json`. No failed case was removed.

`ide.ps1` launched `E:\Github_Projects\Sutram\sutram-ide-gui.exe` with the project
root as CWD in a visible window. It selected examples through their list control,
sent the actual Run menu command, read the output, and captured only that window
using PrintWindow. Both PNGs were visually inspected. An initial metadata field
used equality to describe retention of the previous output; it was corrected to
substring containment, with equality retained separately as
`entire_output_unchanged`. Captured text and images were not altered.

`followups.py` retained the unsuccessful native `--fail-alloc 3` attempt, ran the
R204 S1 rejection probe, and reran only the import-failing suite case with the
original project CWD and with an isolated complete portable layout. The latter
copies compiler/library bytes without modifying them; `bundle-manifest.json`
records hashes.

`oom_limit.py` ran the existing B3 executable in a Windows Job Object with
`JOB_OBJECT_LIMIT_PROCESS_MEMORY` and `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`.
CreateProcess used `CREATE_SUSPENDED`; successful assignment preceded ResumeThread.
Its default run was B3 with 128 MiB (`oom-limit.json`). The runner was then
parameterized for the four named control runs, with separate result files.
Its exit code indicates the runner completed; test outcomes are the captured
child exit codes, not the Python exit code. All five child runs completed within
their timeout.

Read-side follow-up inspected `win/winrt_blob.asm:234-279`,
`src/sutram_compiler.asm:2767`, `src/sutram_compiler.asm:3880-3908`,
and the existing descriptor tests to explain observations. No patch was made.
