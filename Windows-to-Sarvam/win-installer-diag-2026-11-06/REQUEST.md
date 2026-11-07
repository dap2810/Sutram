# Sutram — Windows diagnostic: pin the installer hang

**Copy this whole file to the Windows AI.**

**This is the last undiagnosed defect. Your two compiler defects are being fixed; this one is not yet understood.**

---

## 0. What your last two rounds established

**Your v305 run: ten of thirteen checks passed, including the whole memory model.** **Your diagnostic round then measured the OOM defect and narrowed the IDE defect precisely — both were better than the reports that asked for them.**

**Two things it settled that I had wrong:**

- **The IDE's stale output happens only on the large-file refusal**, not on compile or runtime errors. Both of those clear correctly.
- **Retaining the previous file in the editor is a deliberate safeguard** — it stops you saving text over a file that could not be opened. My instruction was "clear the editor", which would have removed that safeguard.

**And the harness: the compiler finds `lib/` relative to its own location, not the working directory. The compiler is innocent.**

---

## 1. The one defect nobody has measured

**From your v303 round:**

> *"The installer completion check also failed. Its engine log ends at `Copying Sutram files.` The owner reported that PowerShell remained open and had to be closed manually. Do not mark installation successful just because the compiler file was copied."*

**That is all we know.** **It is being fixed by reading PowerShell, and reading can miss where a script actually stops.**

**This round measures it.**

---

## 2. Task A — capture what the installer does, step by step

**Use the current `Sutram-Setup.exe` from `main`.** **Do not wait for v306; the installer code is what is being diagnosed, not the compiler version.**

**Record its SHA-256 first.**

### A1 — run it with transcript logging

**PowerShell transcripts capture everything a script writes, including errors it swallows.**

```
Start-Transcript -Path C:\sutram-install-transcript.txt -Force
C:\path\to\Sutram-Setup.exe
# let it reach the hang, wait 60 seconds, then:
Stop-Transcript
```

**If it must be closed by hand, close it, then read the transcript.**

**Record the last 30 lines of the transcript.**

### A2 — and capture what the process is doing while it hangs

**Run the installer, and while it is stuck, open a second PowerShell as the same user:**

```
Get-Process | Where-Object { $_.ProcessName -match 'powershell|sutram|wscript|cscript' } | Select-Object Id, ProcessName, StartTime, CPU
```

**Then for the stuck PowerShell process:**

```
Get-CimInstance Win32_Process -Filter "ProcessId = <pid>" | Select-Object ProcessId, ParentProcessId, CommandLine
```

**The command line is the important part.** **It tells us which script line it is executing when it stops.**

**Record it verbatim.**

### A3 — and check whether it is waiting on input

**A hang at a prompt looks identical to a hang in a loop from the outside.**

**While it is stuck, press Enter in the installer's PowerShell window and see if it finishes.**

**Then, separately, try pressing `Y` and Enter.**

**Record which one (if either) makes it complete.**

**That single test distinguishes "waiting for input" from "deadlocked" and it decides the fix.**

---

## 3. Task B — what the installer left behind

**After you close it, record:**

```
where sutram
sutram --version
```

**And list what exists:**

```
dir "%LOCALAPPDATA%\Programs\Sutram"
dir "%LOCALAPPDATA%\Programs\Sutram\bin"
```

**And whether the uninstaller was created:**

```
dir "%LOCALAPPDATA%\Programs\Sutram\uninstall*"
```

**Record all of it.**

**The question: did it copy the files and then stop, or did it stop before finishing the copy?**

**If `bin\sutram.exe` exists and reports the right version, the copy finished and only the final step hangs.** **If it is missing or partial, the hang is inside the copy.**

**That distinction is the whole diagnosis.**

---

## 4. Task C — the PATH question, still open

**From your v303 round: two installations coexisted and the older won on PATH.**

**You cleaned that up.** **Now answer the design question:**

**When the installer adds its PATH entry, does it write to the machine scope or the user scope?**

**Check both after a fresh install:**

```
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path
reg query "HKCU\Environment" /v Path
```

**Record which one now contains a Sutram entry, and its position in the string.**

**This matters because a machine-level entry and a user-level entry do not resolve the same way, and a stale one at either scope would shadow a new install.**

---

## 5. Task D — and one thing to check while you are there

**Does the installer require elevation?**

**Run it as a standard (non-elevated) user and record whether it prompts for UAC.**

**If it does, that is a problem for a school computer where the student has no admin rights — and it would also explain a hang if the prompt is dismissed or blocked by policy.**

---

## 6. What NOT to do

- **Do not test v306.** **It does not exist.**
- **Do not re-run the compiler probes.** **v305 is measured; those results stand.**
- **Do not modify anything.**
- **Do not mark the installation successful.** **The point of this round is to prove it is not.**

---

## 7. What to commit

**Push to `Windows-to-Sarvam/win-installer-diag-<date>/`:**

1. **`HANG.md`** — the three tasks above, with the transcript tail and the command line of the stuck process.
2. **`transcript-tail.txt`** — the last 30 lines.
3. **`left-behind.md`** — what exists after closing it.
4. **`path-scopes.json`** — both registry values, before and after.
5. **Screenshots of the stuck window, and of any prompt it shows.**
6. **The exact commands.**

### The table

| Question | Answer |
|---|---|
| Does it hang at the same point every time? | |
| Last line of the transcript | |
| Command line of the stuck process | |
| Does Enter complete it? | |
| Does `Y` + Enter complete it? | |
| Is `bin\sutram.exe` present and correct? | |
| Machine PATH entry? | |
| User PATH entry? | |
| Requires elevation? | |

---

## 8. Why this round is worth doing

**A hang is the hardest kind of defect to fix by reading, because the code looks correct right up to the line where it stops.**

**The command line of the stuck process tells us exactly which script line is executing.** **That turns a guess into a location.**

**And the Enter test distinguishes "waiting for input" from "deadlocked" — two defects with completely different fixes.**

**You have found every Windows defect so far by measuring instead of assuming. This is the same method applied to the one thing left.**
