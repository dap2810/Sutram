# Sutram — ROUND-132: what a clean install should do, and what it does now

**Base:** main at v305 (`c7168137`). **Method:** read the installer source. I read
`windows/build-windows-setup.ps1` (the build, 7 lines), `windows/build-common.ps1` (build
helpers, 125 lines), `windows/native-installer/build-installer.ps1` (builds `Sutram-Setup.exe`),
`windows/native-installer/install-core.ps1` (the install-time engine, 25 KB, read in full),
`windows/native-installer/sutram_wizard.asm` (the wizard GUI, the parts that launch PowerShell
and wait), and `windows/sutram-installer.nsi` (retired — see below). I cannot run Windows here,
so I did not reproduce the hang or the PATH conflict; I report what the code does (and does not
do), and where the hang lives from the code plus the tester's log. The tester's observations
are quoted from the brief, not verified by me on Windows.

## The two blockers, as reported

1. **Two installations coexist and the older one wins on PATH.** A direct call to
   `AppData\Local\Programs\Sutram\bin\sutram.exe` prints `Sutram 1.0 (v303)` correctly. But a
   fresh `cmd.exe` resolving bare `sutram` gives `AppData\Local\Sutram\bin\sutram.exe` (older,
   wins) before `AppData\Local\Programs\Sutram\bin\sutram.exe` (v303), and prints `Sutram
   1.4.0`. So a student who installs this and opens a new terminal gets an old version.
2. **The installer does not complete.** Its engine log ends at `Copying Sutram files.` The owner
   reported that PowerShell remained open and had to be closed manually. The tester was honest
   about scope: main was already v305, the supplied v303 request was followed using an isolated
   worktree, and "these observations do not constitute testing of v305".

## WS1 — read the installer and tell me what it actually does

### Which files are which (the brief names three, but only one is the install-time engine)

- `windows/build-windows-setup.ps1` is the **build**, not the install. It runs, in order:
  `preflight-windows.ps1`, `build-windows-native.ps1`, `gui\build-gui.ps1`,
  `native-installer\build-installer.ps1`, then prints "Build complete. No installation or
  Windows integration was performed." It builds `Sutram-Setup.exe`; it installs nothing.
- `windows/build-common.ps1` is **build helpers only**: `Invoke-BoundedProcess` (runs a process
  with a 20 s timeout, throws on timeout/non-zero exit), `Assert-Pe64` (rejects a non-PE32+
  AMD64 exe, and a writable executable section), `Get-BuildTool` (throws if a build tool is
  missing — "No tools are installed automatically"), and the icon-resource emitters. It runs
  nothing at install time.
- `windows/sutram-installer.nsi` is **retired — do not use, do not ship**. Its header says so:
  it writes to HKLM (machine-wide registry) and needs administrator rights, while the
  project's hard constraint is a per-user install with no UAC prompt, so it cannot be shipped.
  It is superseded by `windows/native-installer/`. It is the **old** installer — and it is the
  one that wrote the old installation (see WS2). It is kept only as history.
- `windows/native-installer/build-installer.ps1` **builds** `Sutram-Setup.exe`: it stages a
  payload (`win\sutram.exe` → `bin\sutram.exe` and `win\sutram.exe`, `sutram-link.exe`,
  `sutram-ide-gui.exe`, icon, LICENSE, README, plus `lang`/`lib`/`examples`/`docs` folders,
  plus `lib`/`lang` under `bin/` and `win/`), writes a SHA-256 manifest for every staged file,
  zips it (`payload.zip`), embeds SHA-256 hashes of the payload, `install-core.ps1`,
  `uninstall-core.ps1`, and LICENSE into the wizard, assembles `sutram_wizard.asm` (pure NASM
  Win32 GUI) with `nasm` + `ld`, runs it with `--self-test` (embedded-hash self-test, must
  pass), and writes `Sutram-Setup.sha256`. It checks every payload input exists (throws
  "Missing payload input" if not) and every `.exe` is PE64 (throws if not).
- The **install-time engine** is two parts: the wizard (`Sutram-Setup.exe`,
  `sutram_wizard.asm`) and the script it runs (`install-core.ps1`, embedded in the wizard via
  `incbin`, extracted to a temp staging dir at install time). The wizard launches PowerShell
  (`powershell.exe -NoProfile -File <temp>\install-core.ps1 -PayloadZip … -InstallDir …
  -SetupExePath … -LogPath … [-AddPath] [-DesktopShortcut]`) via `CreateProcessW`, then waits
  for it. `install-core.ps1` does the actual installation (below).

### `install-core.ps1`, step by step (in order), with checks and failure behaviour

Params (all mandatory): `$PayloadZip`, `$InstallDir`, `$SetupExePath`, `$LogPath`; switches
`$AddPath`, `$DesktopShortcut`, `$VerifyOnly`. `$ErrorActionPreference='Stop'`,
`Set-StrictMode -Version 2.0`. Every `throw` goes to the `catch` block, which logs
`ERROR: <message>` and exits 1. On success it exits 0. There is no `Read-Host`, no `Pause`, no
`-Wait`, and no unbounded loop in this file (verified by grep, not just by reading — see the
hang section below).

1. **Log header + preconditions.** Writes "Sutram Setup Log", logs "Starting installation."
   Checks: 64-bit OS (else throw), 64-bit PowerShell process (else throw), `$PayloadZip` exists
   (else throw), `$SetupExePath` exists (else throw).
2. **InstallDir validation.** `GetFullPath`, trim trailing `\`, `Assert-NoReparsePath` (refuses
   any reparse point / symlink on the path, walking up to the root — throws if found). Must be
   under `$env:LOCALAPPDATA\Programs` (per-user only — throws "Sutram is a per-user install and
   must stay under: …" if not). Length ≤ 220 (else throw). Not a UNC path (`\\`, else throw).
   No shell metacharacters (`%&|<>^!`, else throw). If `$AddPath`, no `;` in the path (else
   throw). Not a drive root (else throw). Not equal to `WINDIR`, `SystemRoot`, `ProgramFiles`,
   `ProgramFiles(x86)`, or `USERPROFILE` (else throw "Unsafe installation folder").
3. **Existing installation — YES, it does look, but only for the NEW scheme.** It reads
   `HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram`. If registered AND
   `InstallLocation` exists AND it is a **different** dir than the requested `$InstallDir` AND
   that dir has a valid Sutram marker (`.sutram-install` containing exactly "Sutram Windows
   installation"), it throws: "Sutram is already installed at: {registeredDir}. Uninstall that
   copy first, or choose the same installation folder." If the registered dir is the **same**
   as `$InstallDir`, it proceeds (upgrade in place). If the registry key does not exist, or the
   registered dir has no marker, it does **not** throw — it proceeds. **It does NOT look for
   the old installation** (`AppData\Local\Sutram`, from the retired NSIS installer): that one
   used HKLM (not HKCU), a different folder (not under `LOCALAPPDATA\Programs`), and no
   `.sutram-install` marker — so the new installer's check does not see it. That is why two
   installations coexist (see WS2).
4. **Folder / marker / ownership checks.** Reads `.sutram-install` marker + `install-state.ini`
   (`Read-State`, key=value). If `$InstallDir` exists and has any file but **no** valid Sutram
   marker, it throws "The selected folder is not empty and is not an existing Sutram
   installation". Checks `HKCU:\Software\Classes\Sutram.Source\shell\open\command` — if it
   exists and differs from the wanted command (`sutram-ide-gui.exe "%1"`), it throws "A
   conflicting Sutram.Source registration exists." If the marker exists (existing install), it
   requires ownership metadata to be complete (`payload.manifest.sha256` exists AND
   `install-state.ini` has `UninstallerSHA256`, else throw "Existing installation ownership
   metadata is incomplete"), and if the old uninstaller exists and its SHA-256 differs from
   the recorded one, it throws "The existing uninstaller has been modified; refusing to
   overwrite it."
5. **Stage + verify payload.** Creates `$env:TEMP\Sutram-Payload-<guid>`, logs "Extracting
   embedded payload.", `Expand-Archive` (payload.zip → stage), `Verify-Payload` (every manifest
   line must be `64-hex *relpath`, no duplicates, no unsafe paths (must stay under the stage
   root), every file must exist and its SHA-256 must match, and **no unmanifested file may
   exist** — any mismatch throws). Checks the payload contains `bin\sutram.exe`,
   `sutram-ide-gui.exe`, and `win\sutram.exe` (throws if any is missing). Runs pre-install
   self-tests: `Invoke-SutramSelfTest` on the staged `bin\sutram.exe` with `--version` and
   `--help` (each bounded to 8000 ms — if it does not exit in 8 s, it is killed, waited on for
   2 s more, then it throws "Native compiler timed out … installation aborted"; it must exit 0
   AND print non-empty stdout, else it throws). If `$VerifyOnly`, it logs "VERIFY ONLY PASS …
   installation not performed." and exits 0 (no install).
6. **Upgrade safety.** If a previous manifest exists in `$InstallDir`, it reads it, and for
   each file in the new stage, if the target already exists in `$InstallDir` and is **not** in
   the previous manifest **or** its hash differs from the previous manifest's hash, it throws
   "Upgrade would overwrite a user file; preserve it elsewhere first." (It refuses to overwrite
   user-modified files on upgrade.) For each file in the stage, it asserts no reparse point on
   the target path.
7. **Remove old payload, copy new files.** Creates `$InstallDir`, and if a previous manifest
   exists, logs "Removing files owned by the previous Sutram payload." and calls
   `Remove-ManifestFiles` (removes files owned by the previous payload, per manifest SHA-256;
   **preserves** user-modified files — hash mismatch → logs "Preserved user-modified package
   file" and skips deletion; removes empty dirs, deepest first). Then logs **"Copying Sutram
   files."** and `Copy-Item` (stage `*` → `$InstallDir`, Recurse, Force), then `Copy-Item`
   (`$SetupExePath` → `$InstallDir\Sutram-Uninstall.exe`, Force), then writes the marker file
   (`.sutram-install`, "Sutram Windows installation").
8. **Post-install self-test.** Runs `Invoke-SutramSelfTest` on the **installed**
   `bin\sutram.exe` with `--version` (bounded 8 s, must exit 0 + non-empty stdout, else throw).
9. **PATH — user only (see WS2).** If `$AddPath`, logs "Ensuring Sutram is present in the
   current user PATH." and calls `Set-UserPathEntry` (`$InstallDir\bin`, `$true`) — which writes
   to `HKCU\Environment` (user PATH, never machine), normalises entries (trim, expand env vars,
   trim trailing `\`), adds the entry only if not already present, checks the new PATH is ≤
   32760 chars (else throw "The user PATH would become too long"), and broadcasts the change
   (`SendMessageTimeout`, WM_SETTINGCHANGE, 5000 ms timeout). It owns the entry only if this
   installer created it now or already owned it from a previous Sutram install; a pre-existing
   manual PATH entry remains user-owned and will not be removed by uninstall. If **not**
   `$AddPath` but previously owned, it removes the entry. Otherwise no PATH change.
10. **Shortcuts.** Creates `StartMenu\Programs\Sutram`, and shortcuts: "Sutram IDE.lnk" →
    `sutram-ide-gui.exe`, "Sutram Terminal.lnk" → `cmd.exe /K "set PATH=<binDir>;%PATH% &&
    sutram --version"`, "Sutram Documentation.lnk" → the English book (if it exists),
    "Uninstall Sutram.lnk" → `Sutram-Uninstall.exe --uninstall`. `New-Shortcut` (via
    `WScript.Shell` COM) **preserves** a pre-existing user shortcut: if the shortcut path
    already exists and is not in `oldState['OwnedShortcuts']`, it logs "Preserved pre-existing
    user shortcut" and returns without overwriting. Desktop: if `$DesktopShortcut`, creates
    `Desktop\Sutram IDE.lnk` (unless a pre-existing user desktop shortcut exists and was not
    owned, in which case it preserves it and logs); if not `$DesktopShortcut` but previously
    owned, it removes it.
11. **File associations + uninstall registry.** `HKCU:\Software\Classes\Sutram.Source`
    (command = `sutram-ide-gui.exe "%1"`, DefaultIcon = `assets\sutram.ico`),
    `HKCU:\Software\Classes\.sm` (default = `Sutram.Source` if not already set, else preserves
    the existing default; adds `OpenWithProgids\Sutram.Source`). If the `.sm` command already
    exists and differs, it throws (checked again here, as in step 4). Writes the uninstall key
    (`HKCU:\…\Uninstall\Sutram`): DisplayName `Sutram`, **DisplayVersion `0.1.0`**,
    Publisher `Sutram Project`, InstallLocation, DisplayIcon, UninstallString
    (`Sutram-Uninstall.exe --uninstall`), NoModify=1, NoRepair=1. **Note: `DisplayVersion` is
    hardcoded to `0.1.0` (line 399), and `install-state.ini` also says `Version=0.1.0` (line
    412) — not the actual release version (v305 / 1.0). That is a real (minor) defect: the
    installed version metadata is wrong/stale (a student checking Programs & Features would see
    0.1.0, not 1.0/v305). It does not cause the hang or the PATH conflict, but it should be
    fixed (the version should come from the build, not be hardcoded).**
12. **State + finish.** Writes `install-state.ini` (`Version=0.1.0`, `OwnedShortcuts`,
    `PathOwned`, `DesktopOwned`, `AssociationOwned`, `UninstallerSHA256`). Logs
    **"Installation complete: <InstallDir>"**, copies the log to
    `$InstallDir\install.log`, appends `InstallLogSHA256` to `install-state.ini`. The `finally`
    block removes the stage dir (`$env:TEMP\Sutram-Payload-<guid>`, Recurse, Force,
    SilentlyContinue — but only if the stage path is under `$env:TEMP\Sutram-Payload-`, else it
    throws "Unsafe stage cleanup path"). Then `exit 0`.

### What is the LAST thing it does before it should exit?

In `install-core.ps1`: log "Installation complete: <InstallDir>", copy the log to
`install.log`, append `InstallLogSHA256` to `install-state.ini`, remove the stage dir
(`finally`), then `exit 0`. In the wizard: after PowerShell exits 0, remove the temp staging
dir (`%TEMP%\STM*.tmp`, its three files, the log, then the folder — on a failure it stays, so
the failure can be examined), report success, exit. **The tester's log ends at "Copying Sutram
files." (step 7), which is before the post-install self-test (step 8), PATH (step 9),
shortcuts (step 10), associations/registry (step 11), state (step 12), and "Installation
complete". So it stopped after the copy started but before any of those — most likely in
`Copy-Item` itself (see the hang section below).**

### Is there any `Read-Host`, `Pause`, `-Wait`, or unbounded loop in the path? — that is where a hang lives

**No `Read-Host`, no `Pause`, no `-Wait`, and no unbounded loop in `install-core.ps1`, in the
wizard, or in the build scripts (verified by grep).** The only unbounded wait is in the wizard,
`sutram_wizard.asm:1145-1146`:

```
mov  edx, INFINITE
API  WaitForSingleObject
```

That is in the install path (after `CreateProcessW` launches PowerShell with `install-core.ps1`,
around lines 1125–1146): the wizard builds the PowerShell command line (with the `-AddPath` /
`-DesktopShortcut` flags from the GUI checkboxes), calls `CreateProcessW`, posts progress (60%),
then **waits with `WaitForSingleObject(..., INFINITE)` — unbounded, no timeout, no cancel** —
then posts progress (90%), gets the exit code, and fails if it is non-zero. The other
`CreateProcessW` sites in the wizard (lines 1288, 2412) close their handles immediately without
waiting (they launch the IDE/shell after install, not the install itself). The
`install-core.ps1` comment even names it: "No unbounded compiler preflights: a broken native
compiler must not freeze the Windows wizard forever inside `WaitForSingleObject(INFINITE)`."
— so the wizard's unbounded wait is a known hazard, and the self-tests are bounded (8 s) to
avoid triggering it. But the **copy** is not bounded, and there is no progress logging during
it: if `Copy-Item` is slow or stuck, the wizard sits at 60% forever, PowerShell remains open,
and the owner has to close it manually — exactly what was reported.

So the hang is **not** a prompt waiting for input (there is no prompt to answer). It is the
wizard waiting forever for a PowerShell that has not exited. And the log stopping at "Copying
Sutram files." points at the stall being in (or just after) the copy: the next log line would
be "Native self-test start: post-install --version" (if it reached the self-test) or "Ensuring
Sutram is present in the current user PATH." (if it reached PATH) — neither appears, so it
stopped between "Copying Sutram files." and the self-test start, i.e. in `Copy-Item` (the
payload copy), the `Sutram-Uninstall.exe` copy, or the marker write (the marker write is a
single `WriteAllText`, fast, so it is almost certainly `Copy-Item`). `Copy-Item` has no timeout
and no progress logging: the payload (docs — six HTML books, examples — ~300 files, lib — 24
modules, lang — ten packs, plus `bin/`/`win/` binaries, total on the order of 10–20 MB in
hundreds of files) could be slow on a slow disk or with antivirus scanning each file, and the
tester/owner may have interpreted "slow" as "hung" and closed PowerShell manually before it
finished — or a single file could be locked/stuck. I cannot distinguish "slow copy that was
interrupted" from "stuck copy" from the log alone (the log does not say how long they waited,
and there is no progress line during the copy), and I cannot run Windows here to reproduce it.
What the code establishes is: (a) there is no prompt, so it is not waiting for input; (b) the
wizard waits unbounded, so any stall in PowerShell (slow or stuck) looks like a hang with no
timeout and no cancel; (c) the stall is in/just after the copy, before the self-test. The fix
(for Claude) is: add a timeout (or a cancel) to the wizard's wait, and/or log progress during
`Copy-Item` (so the log shows it is still copying, not stuck), and/or check for a locked file
before copying. My job here is to report it, not to fix it — and to write the test that would
have caught it (WS3).

## WS2 — and the PATH question, which is the one a student hits

**Which PATH entry does the installer write — machine, user, or both? User only.** It writes
to `HKCU\Environment` (the current-user PATH), via `Set-UserPathEntry` in `install-core.ps1`,
and only the `bin` dir (`$InstallDir\bin`, i.e. `AppData\Local\Programs\Sutram\bin`), and only
if `-AddPath` was passed (the wizard passes it from the GUI checkbox). It **never** writes to
the machine PATH (`HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment`), and it
never reads, removes, or checks the machine PATH. The retired NSIS installer (the old one)
wrote to the **machine** PATH (`EnVar::SetHKLM`, `EnVar::AddValue "Path" "$INSTDIR\bin"`,
`EnVar::Update` in `sutram-installer.nsi`), which is why the old installation has a machine
PATH entry.

**Does an older entry take precedence because it is earlier in the list? Yes.** On Windows,
when a command is resolved, the **system (machine) PATH is searched before the user PATH** —
a process's PATH is constructed as (machine PATH) + (user PATH), in that order. So the older
machine entry (`%USERPROFILE%\AppData\Local\Sutram\bin\sutram.exe`, from the retired NSIS
installer) is searched before the newer user entry
(`%USERPROFILE%\AppData\Local\Programs\Sutram\bin`, from the new installer), so the older
version wins, and a student typing `sutram` in a fresh `cmd.exe` gets `Sutram 1.4.0` (the old
one), not v303/v305 (the new one). The installer writes only to user PATH, so it **cannot**
fix the old machine entry: it does not even look at it, and removing a machine PATH entry
would require administrator rights, which a per-user installer (no UAC prompt, by design) does
not have. The order, as the student experiences it, is:

1. `%USERPROFILE%\AppData\Local\Sutram\bin` — **older, machine PATH, wins** (from the retired
   NSIS installer; the new installer does not see it, does not remove it, and cannot remove it
   without admin rights).
2. `%USERPROFILE%\AppData\Local\Programs\Sutram\bin` — **newer, user PATH, loses** (from the
   new installer; it is added correctly, but it is searched after the machine PATH).

Nothing tells the student this. The fix (for Claude/owner) is for the installer to **detect**
the old machine PATH entry (and the old installation) and warn the user — or refuse to proceed
until the old copy is uninstalled — rather than silently installing a second copy that loses on
PATH. (Removing the machine entry itself needs admin/UAC, so the installer should tell the
user to uninstall the old copy first, or offer to do it with elevation — it should not silently
leave two installations fighting over PATH.) The existing-install check (WS1, step 3) should
also be extended to look for the old installation (old path, old HKLM registry, old machine
PATH entry), not just for the new-scheme HKCU registration — otherwise it will keep missing
the old copy, as it did here.

## WS3 — and the check that should exist

The full test description is in `r132_clean_shell_test.md` (delivered with this round, for
Claude to build). In short: **a clean-shell check that the installer completes AND that
`sutram --version` in a fresh shell resolves to the installed version.** It must: start from a
machine with an old installation present (to catch the PATH conflict, not just a clean machine);
run the installer with a timeout (fail if it does not exit); assert it exits 0 and the log
reaches "Installation complete"; assert no `powershell.exe` or `Sutram-Setup.exe` lingers after
it exits; then open a **fresh** `cmd.exe` (a new process, so it picks up the new PATH) and run
bare `sutram --version` and `where sutram`, and assert the version matches the installed
version (v305) and the resolved path is the new install dir
(`AppData\Local\Programs\Sutram\bin\sutram.exe`), not the old one
(`AppData\Local\Sutram\bin`). It should also assert the uninstall entry's DisplayVersion is the
installed version (not the hardcoded `0.1.0` found in WS1). See the file for the full steps,
setup, assertions, and timeouts.

## NOT RUN

Windows execution (cannot run Windows here; the hang and PATH observations are the tester's,
not mine — I report what the code does, and where the hang lives from the code plus the log),
browser, implementation (reading only — no installer code changed by me), native-speaker
review, full suite (no tree changes; v305 suite numbers stand, not re-run here). Whether
`Copy-Item` was slow (and interrupted) or stuck (on a locked file) cannot be determined from
the log alone, and I did not reproduce it — the code establishes the mechanism (unbounded
wizard wait + no progress during the copy), not which of those two it was.
