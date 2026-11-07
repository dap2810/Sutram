# Sutram v306 follow-up — two failures to pin, one timeout to watch

**Copy this whole file to the Windows AI.**

**Your v306 run was the best report of the project. Two failures, precisely measured, and one standard I want kept.**

---

## 0. What your run established

**Passed:**

| Test | Result |
|---|---|
| Clean install | **Finish after 8.05 s, no console, wizard closed itself** |
| New-shell identity | **`Sutram 1.0 (v306)`, 657/657 payload hashes match** |
| OOM at 64 / 128 / 256 MiB | **exact message on stderr, exit 1** |
| OOM at 640 MiB | **refusal, exit 1** |
| OOM at 768 / 1024 / 2048 MiB | **`100000000`, exit 0** |
| Page-touch at 64 MiB | **refusal, exit 1** |
| Native suite | **322 PASS, 3 NO-EXPECTATION, 6 skipped, no FAIL** |
| IDE refused load | **old output replaced by two notices** |
| IDE Save safeguard | **edited copy changed; refused file and all originals untouched** |

**And your standard is right, so it is now the project's standard:**

> ***"The message alone is insufficient to count a refusal as passing."***

**A program that says "out of memory" and then dies has narrated its crash, not refused.**

---

## 1. Failure one — `0xC00000FD` after the message

**At 512 MiB, and for `mandapa` at 64 MiB: the exact refusal appears, then `STATUS_STACK_OVERFLOW`.** **Reproduced 6/6.**

**The asymmetry is the clue:** 64, 128, 256 and 640 all pass; 512 fails.

**This round pins it.**

### A1 — map the boundary precisely

**Run B3 at these limits, 3 times each:**

```
448 MiB
480 MiB
512 MiB
544 MiB
576 MiB
608 MiB
640 MiB
```

**Record for each: exit code, whether the message appeared, and how many of the 3 runs failed.**

**If only 512 fails and 544 passes, the cause is something specific to that size — and that is a very different bug from a general one.**

### A2 — and capture where the stack went

**For a failing run, get the faulting thread's stack information.**

**If you have `procdump` or WinDbg available:**

```
procdump -e -ma -x <dir> <exe>
```

**Then record the exception code, the faulting address, and whether the stack trace shows repeated frames — repetition means recursion.**

**If no debugger is available, say so and skip this.** **Do not install one just for this.**

### A3 — and one question that may answer it without a debugger

**Does the failing run print the message to stderr and then crash, or crash before the message is flushed?**

**Run it with stderr redirected to a file, then check whether the file is complete and ends with a newline.**

**A message that is complete means the handler finished and something after it faulted.** **A truncated message means the fault happened inside the handler.**

**That distinction is worth more than a stack trace and costs one redirect.**

### A4 — and the `mandapa` case

**Run the `mandapa` probe at 64 MiB ten times.**

**Record: how many crash, how many refuse cleanly, and whether the message is always complete.**

**If it is intermittent, that changes the diagnosis entirely.**

---

## 2. Failure two — the same-directory upgrade

**Your finding: the installer permits a same-directory upgrade, and that path stalls during copy.**

**The owner's earlier interrupted copy stopped at file 132 of 657 — an empty file.**

**This round makes the stall diagnosable.**

### B1 — reproduce it deliberately, and catch it in the act

**Set up a same-directory upgrade:**

1. **Install v306 cleanly.** **Confirm it works.**
2. **Note the file count in the install directory.**
3. **Run `Sutram-Setup.exe` again, into the same directory.**
4. **Let it run until it stalls — or for 5 minutes, whichever comes first.**

**While it is stalled, capture:**

```
Get-Process | Where-Object { $_.ProcessName -match 'powershell|sutram' } | Select-Object Id, ProcessName, CPU, StartTime
Get-CimInstance Win32_Process -Filter "ProcessId = <pid>" | Select-Object CommandLine
```

**And the engine log from the install directory.**

### B2 — and check whether a file is locked

**While stalled, check what the process holds open.** **If `handle.exe` or `openfiles` is available:**

```
openfiles /query /fo table
```

**Or, in PowerShell, list files in the install directory whose `LastWriteTime` is within the last two minutes:**

```
Get-ChildItem "$env:LOCALAPPDATA\Programs\Sutram" -Recurse |
  Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-2) } |
  Select-Object FullName, Length, LastWriteTime
```

**The last file written is where it stopped.** **Record its name and size.**

**This is the measurement that would have found the hang on the first attempt.**

### B3 — and whether Defender is involved

**Your `a3-defender-events.json` suggests you already looked.** **Record whether any Defender event coincides with the stall.**

**If a file write is being scanned and blocked, that is the answer and it is a known class of installer problem.**

### B4 — and the 15-minute timeout

**Let one stalled run go the full 15 minutes without touching it.**

**Record: does it stop on its own?** **At what time?** **What does it log?**

**This has never been observed. It is the one behaviour v306 added that nobody has seen.**

---

## 3. What NOT to do

- **Do not report the clean-install results again.** **They passed; they stand.**
- **Do not modify the compiler, library, examples, goldens or installer.**
- **Do not claim release acceptance.** **That is a separate verdict.**
- **Do not install a debugger unless one is already present.** **A1, A3 and B2 answer most of it without one.**
- **If the upgrade does not stall this time, say so.** **An intermittent hang is a different finding and it matters.**

---

## 4. What to commit

**Push to `Windows-to-Sarvam/win-v306-followup-<date>/`:**

1. **`OOM.md`** — the A1 boundary table with 3 runs each, and A3's answer about message completeness.
2. **`UPGRADE.md`** — B1's capture, B2's last-file-written, B3's Defender check, B4's timeout result.
3. **`engine.log`** and any `procdump` output.
4. **Every probe and command.**
5. **Screenshots of the stalled wizard.**

### The OOM boundary table

| Limit | Run 1 | Run 2 | Run 3 | Message complete? |
|---:|---|---|---|---|
| 448 MiB | | | | |
| 480 MiB | | | | |
| 512 MiB | | | | |
| 544 MiB | | | | |
| 576 MiB | | | | |
| 608 MiB | | | | |
| 640 MiB | | | | |

### The upgrade table

| Question | Answer |
|---|---|
| Did the upgrade stall? | |
| Last file written, and its size | |
| File count at stall vs after a clean install | |
| Any Defender event at the same time? | |
| Did the 15-minute timeout fire? | |
| At what time, and what did it log? | |

---

## 5. Why this round is worth doing

**The OOM asymmetry — 512 fails, 640 passes — is unusual enough to identify the cause with one good measurement.** **A boundary table with repeats either shows a specific size or shows intermittency, and both answers are actionable.**

**And the upgrade stall is the last unexplained thing in this project.** **It stopped at file 132 once and nobody could say why.** **The last-file-written check answers it in one command.**

**You have found every Windows defect by measuring the thing nobody had measured. These are the last two.**
