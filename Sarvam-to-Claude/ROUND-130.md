# Sutram — ROUND-130: the installer hangs, and two installations fight over PATH.

**Base:** main at v305 · **Deliver into:** `Claude-to-Sarvam/`

## The Windows release-candidate run STOPPED. Two installation blockers.

**The tester followed the brief and stopped when the version check failed. Memory probes, native suite and IDE checks were NOT RUN.**

**1. TWO INSTALLATIONS COEXIST AND THE OLDER ONE WINS ON PATH.**
A direct call to `AppData\Local\Programs\Sutram\bin\sutram.exe` prints `Sutram 1.0 (v303) - sampurna sutra` correctly. But a fresh `cmd.exe` resolving bare `sutram` gives:
```
C:\Users\dmech\AppData\Local\Sutram\bin\sutram.exe        <- OLDER, wins
C:\Users\dmech\AppData\Local\Programs\Sutram\bin\sutram.exe  <- v303
Sutram 1.4.0
```
So a student who installs this and opens a new terminal gets an old version.

**2. THE INSTALLER DOES NOT COMPLETE.**
*"Its engine log ends at `Copying Sutram files.` The owner reported that PowerShell remained open and had to be closed manually. Do not mark installation successful just because the compiler file was copied."*

**And the tester was honest about scope: *"Main was already v305 at fetched commit... the supplied v303 request was followed using an isolated worktree. These observations do not constitute testing of v305."***

## WS1 - the installer must finish. This is the release blocker.
**PowerShell hangs at `Copying Sutram files.` and has to be closed by hand.**

**Two questions:**
1. **Why does the completion step not run?** **Read the installer engine - is the last step a PowerShell call that never returns, a `Read-Host`, a job that is not waited on, or an error swallowed by `-ErrorAction SilentlyContinue`?**
2. **Is the version check part of the completion step?** **If so, the hang and the wrong version may be the same defect.**

**Fix it so the installer runs to completion and closes.** **Then the completion check can actually verify something.**

## WS2 - and two installations must not coexist
**An older `AppData\Local\Sutram\` and the new `AppData\Local\Programs\Sutram\` both exist, and the OLDER one wins on PATH.**

**Pick one of these and build it:**
- **the installer detects an existing installation and removes or upgrades it**
- **the installer refuses to install while an old one is present, and says where it is**
- **the installer writes a PATH entry that takes precedence**

**My view: detect and refuse is the honest one.** **Silently leaving two installations is what caused this, and a student cannot know which one they are running.**

**But say which you would do and why.**

## WS3 - and one thing to check in the repo
**Is there a test that would have caught this?** **A gate that checks the installer completes, or that PATH resolves to the new install?**

**If not, that is the reason this reached a release candidate.** **A gate that installs and runs `sutram --version` in a clean shell would have caught both defects.**

## WS4 - and v305 is still untested on Windows
**The tester ran v303 as the brief asked, and said plainly it does not cover v305.**

**So after these fixes: v306, installer rebuilt, and the Windows round re-run against it.**
