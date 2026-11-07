# Clean-shell installer test — description (for Claude to build)

**Purpose:** catch both R132 defects — (1) the installer does not complete (hangs, PowerShell
remains open, log ends at "Copying Sutram files."), and (2) two installations coexist and the
older one wins on PATH (a student typing `sutram` gets an old version). This is a description,
not code. Claude builds it.

## Setup (before the test runs)

1. **Start from a machine with an OLD installation present** (not just a clean machine — a
   clean machine would not catch defect 2). Install the old version first (the retired NSIS
   installer, or a manual copy) so that `AppData\Local\Sutram\bin\sutram.exe` exists and is on
   the **machine** PATH (as in the R132 report). Record its version (`sutram --version` in a
   fresh shell before the test — it should be the old version, e.g. `Sutram 1.4.0`).
2. Record the version under test (the new installer, e.g. v305) and its expected install dir
   (`AppData\Local\Programs\Sutram\bin\sutram.exe`).
3. Ensure no `Sutram-Setup.exe` or installer `powershell.exe` is already running (so a
   lingering process from a previous run is not mistaken for this run's).

## Run

4. Run the installer (`Sutram-Setup.exe`, the new per-user installer) **with a timeout** (e.g.
   120 seconds — long enough for a normal install on a slow disk, short enough to catch a hang).
   Accept the defaults in the wizard (including "Add to PATH" if that is the default, or check
   it explicitly — the test must state which it used, because PATH is only written if `-AddPath`
   is passed). Do **not** close PowerShell manually during the run (that would mask the hang).
5. **Fail the test if the installer does not exit within the timeout** (this catches defect 1
   — the hang). Record how long it took, and whether `powershell.exe` (the installer's
   PowerShell) and `Sutram-Setup.exe` (the wizard) are still running after the timeout (they
   should not be — if either lingers, the test fails, even if the installer window closed).
6. Assert the installer **exits 0**. Assert the engine log (the installer's log file, in
   `%TEMP%` and/or `$InstallDir\install.log`) contains **"Installation complete:"** (not just
   "Copying Sutram files." — the log must reach the end, not stop at the copy). If the log ends
   at "Copying Sutram files." (as in R132), the test fails, and the log is kept as evidence.
7. Assert the installed `bin\sutram.exe` exists at the expected new path
   (`AppData\Local\Programs\Sutram\bin\sutram.exe`), and that a direct call to it prints the
   installed version (e.g. `Sutram 1.0 (v305)`).

## Clean-shell check (the PATH part — defect 2)

8. Open a **fresh** `cmd.exe` (a new process, started after the installer exits — so it picks
   up the new PATH; do **not** reuse a shell that was open before the install, because it would
   have the old PATH).
9. In that fresh shell, run bare `sutram --version` (no path — resolve it via PATH, as a
   student would). **Assert it prints the installed version** (e.g. `Sutram 1.0 (v305)`), not
   the old version (e.g. `Sutram 1.4.0`). If it prints the old version, the test fails (defect
   2 — the older installation wins on PATH).
10. In the same fresh shell, run `where sutram` (which lists every `sutram.exe` on PATH, in
    resolution order). **Assert the first line is the new install dir**
    (`AppData\Local\Programs\Sutram\bin\sutram.exe`), not the old one
    (`AppData\Local\Sutram\bin\sutram.exe`). If the old path is first (or only), the test
    fails. Record the full `where` output as evidence (it shows the order, which is the defect).
11. Assert the uninstall entry (Programs & Features / `HKCU:\…\Uninstall\Sutram`) shows
    **DisplayVersion = the installed version** (e.g. `1.0` / `v305`), not the hardcoded `0.1.0`
    found in R132 WS1. (This is a separate minor defect, but the same test should catch it,
    because it is the same "what version is installed?" question a student asks.)

## Also assert (to catch the hang's side effects)

12. After the installer exits, assert **no `powershell.exe` from the installer is still
    running** (the owner's report was that PowerShell remained open and had to be closed
    manually — a lingering PowerShell after the installer exits is a failure, even if the
    installer window closed). Assert **no `Sutram-Setup.exe` is still running** either.
13. Assert the install dir contains `install.log` (the installer copies its log there on
    success), and that `install.log` also contains "Installation complete:".

## What it must NOT do

- It must **not** mark installation successful just because the compiler file was copied (the
  R132 brief is explicit about this — copying `sutram.exe` is step 7 of 12, not the end; the
  test must check the log reaches "Installation complete" and the installer exits 0, not just
  that the file exists).
- It must **not** reuse a shell that was open before the install (that shell would have the old
  PATH, so `sutram --version` in it would give the old version even if the install was correct
  — a false failure; or, if the shell had the new PATH manually set, a false pass). Always a
  fresh shell, started after the installer exits.
- It must **not** run on a clean machine only (a clean machine has no old installation, so
  defect 2 would not appear — the test would pass even though the PATH conflict is still there
  for any student who has the old version). It must run with the old installation present (step
  1), and ideally also on a clean machine (as a second case, to check the install works from
  scratch).

## Expected outcome

- **Pass:** installer exits 0 within the timeout, log reaches "Installation complete", no
  lingering PowerShell/wizard, fresh-shell `sutram --version` prints the installed version,
  `where sutram` lists the new install dir first, DisplayVersion is the installed version.
- **Fail (defect 1):** installer does not exit within the timeout, or log ends at "Copying
  Sutram files.", or PowerShell/wizard lingers after it exits.
- **Fail (defect 2):** fresh-shell `sutram --version` prints the old version, or `where
  sutram` lists the old path first.
- **Fail (minor):** DisplayVersion is `0.1.0` (or any version other than the installed one).
