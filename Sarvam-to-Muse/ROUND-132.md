# Sutram — ROUND-132: what a clean install should do, and what it does now

**Base:** main at v305 · **Deliver into:** `Muse-to-Sarvam/`

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

## WS1 - read the installer and tell me what it actually does
**`windows/build-windows-setup.ps1`, `windows/build-common.ps1`, and whatever engine runs at install time.**

**For each step: what does it do, does it check anything, and what happens on failure?**

**Specifically:**
- **does it look for an existing installation?**
- **does it write a PATH entry, and where - machine or user?**
- **what is the LAST thing it does before it should exit?**
- **and is there any `Read-Host`, `Pause`, `-Wait`, or unbounded loop in the path?**

**That last question is where a hang lives.**

## WS2 - and the PATH question, which is the one a student hits
**Two installations, the older wins.** **Which PATH entry does the installer write - machine, user, or both?** **And does an older entry take precedence because it is earlier in the list?**

**Report the order.** **A student typing `sutram` gets whichever comes first, and nothing tells them.**

## WS3 - and the check that should exist
**Write the test that would have caught both defects: a clean-shell check that the installer completes AND that `sutram --version` resolves to the installed version.**

**Not the code - the description of what it must do.** **Claude builds it.**
