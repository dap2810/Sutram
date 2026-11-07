# Sutram v307 — verify the four fixes, and settle the hang

**Copy this whole file to the Windows AI.**

**v307 fixes four things, and one of them is the hang you reproduced. This round checks whether the suspects were right.**

---

## 0. What v306 established, and what v307 changes

**Your v306 run passed: clean install in 8.05 s with no console, `657/657` payload hashes, the OOM refusal at 64/128/256/640 MiB, success at 768 and above, the page-touch refusal, **322 PASS** on the native suite, the IDE clearing its output, and the Save safeguard surviving.**

**Two failures remained, and your standard for them is now the project's standard:** ***"The message alone is insufficient to count a refusal as passing."***

| What you found | What v307 does |
|---|---|
| **`0xC00000FD` after the refusal message at 512 MiB, and `mandapa` at 64 MiB** | **Windows' memory handler registration was never checked — now it is** |
| **The same-directory upgrade stalls during copy** | **The mass delete is removed; the log names every file before copying it** |
| **An interrupted install traps the next run** | **The next run finishes it instead of refusing** |
| **The file the copy stopped on** | **Named — and nothing about it explains the stall** |

**And the hang has a suspect, unconfirmed:** ***"The owner's anti-ransomware driver, set off by the engine deleting 643 files and then writing 131 in four seconds."***

**Release line:** `gates: 72 PASS / 0 FAIL / 1 NOT-RUN` · `suite: PASS=327` · **installer payload v307, `--self-test` exit 0 under Wine.**

---

## 1. Task A — the OOM crash, which is the release blocker

**At 512 MiB and for `mandapa` at 64 MiB, the message appeared and then the process died with `STATUS_STACK_OVERFLOW`, 6 out of 6.**

**v307 registers the memory handler that was never checked.**

### A1 — the boundary, with repeats

**Run B3 at each limit, three times, and record exit code and whether the message was complete:**

```
448, 480, 512, 544, 576, 608, 640 MiB
```

**Expected at every failing limit: `Sutram truti: smritih na labdha`, exit 1, no `0xC00000FD`.**

**If 512 still fails and 544 passes, say so — the asymmetry was the clue and it would mean the cause is not the handler.**

### A2 — and the `mandapa` case

**Your `A3-mandapa.sm` at 64 MiB, ten times.**

**Record: crashes, clean refusals, and whether the message is always complete.**

### A3 — and the page-touch control

**Your `A3-nirmmita-touch-pages.sm` at 64 MiB.** **It passed on v306; confirm it still does.**

### A4 — and the completeness check, which is your own standard

**For every failing run, redirect stderr to a file and check it ends with a newline.**

**A complete message means the handler finished.** **A truncated one means it did not.** **Record which, at every limit.**

---

## 2. Task B — the hang, and whether the suspect was right

**v307 removes the mass delete.** **The suspect is an anti-ransomware driver reacting to 643 deletions followed by 131 rapid writes.**

**If the suspect is right, the same-directory upgrade should now complete.**

### B1 — the same-directory upgrade, which is the test

1. **Install v307 cleanly.** **Confirm it works.**
2. **Run `Sutram-Setup.exe` again into the same directory.**
3. **Let it run to completion, or for 15 minutes.**

**Record: does it complete?** **How long?** **Does the wizard close itself?**

**This is the exact path that stalled on v306.** **If it completes now, the suspect was right.**

### B2 — and the log, which should name every file

**v307 logs each file before copying it.**

**Record:**
- **does the log name files one at a time?**
- **what is the last line if it stalls?**
- **and does the log name the file *before* copying it, not after?**

**That last point matters: a log written after the copy cannot name a file the copy never finished.**

### B3 — and Defender, if the suspect is an anti-ransomware driver

**Record whether any Defender or third-party security event coincides with the install.**

```
Get-WinEvent -LogName "Microsoft-Windows-Windows Defender/Operational" -MaxEvents 20 |
  Select-Object TimeCreated, Id, Message
```

**If a controlled-folder-access or ransomware-block event appears at the same time, that confirms it and it should be written down.**

### B4 — and the interrupted install

**Interrupt an install deliberately, then run it again.**

**How to interrupt cleanly:** **start the install, wait until the log shows several files copied, then end the wizard process.**

```
Stop-Process -Name "Sutram*" -Force
```

**Then run `Sutram-Setup.exe` again.**

**Expected: it recognises the partial install and finishes it, rather than refusing behind a "user file" guard.**

**Record: does it complete?** **What does it say about the partial install?**

**This is the trap that locked the owner out on v303. If it is fixed, that is a real release condition met.**

---

## 3. Task C — the slice, which was a real memory-safety defect

**ChatGPT traced a function-value slice path and Claude reproduced it on v306 — a lost write and a SIGSEGV.** **It is closed in v307.**

### C1 — the four probes

**Run each and record the outcome:**

**C1a — the cell store:**
```sutram
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    vitti obstacle = nirmmita(16)
    mala box[1]
    box[0] = k[0:1]
    kosh_kship(k, 8)
    likha(box[0])
}
```

**C1b — the untyped parameter:** **a slice passed to a `prakriya` whose parameter is untyped, which grows the source.**

**C1c — the untyped return:** **a `prakriya` returning a slice as an untyped result, then the source grows.**

**C1d — the function value:** **a slice passed to a `prakriya` called through a variable.**

**Expected: each is refused at compile time, or produces the correct value.** **A stale read or a crash is a failure.**

**And note: on v306, C1d lost a write and segfaulted.** **If any of these still does, say which.**

---

## 4. Task D — the suite and the identity

**Run the native suite as before.** **Expected: 322 PASS, no FAIL, no COMPILE_FAIL.**

**And confirm in a new shell:**

```
where sutram
sutram --version
```

**Expected: one canonical path, `Sutram 1.0 (v307) - sampurna sutra`.**

---

## 5. What NOT to do

- **Do not report the v306 passes again.** **They stand.**
- **Do not modify the compiler, library, examples, goldens or installer.**
- **Do not claim release acceptance.** **That is a separate verdict.**
- **Do not install a debugger unless one is already present.**
- **If the upgrade completes now, say so plainly — that would confirm the suspect.**

---

## 6. What to commit

**Push to `Windows-to-Sarvam/win-v307-<date>/`:**

1. **`OOM.md`** — the A1 boundary table with 3 runs each, A2's ten `mandapa` runs, and A4's completeness answer at every limit.
2. **`UPGRADE.md`** — B1's outcome, B2's log tail, B3's Defender query, B4's interrupted-install recovery.
3. **`SLICE.md`** — the four C1 probes and their outcomes.
4. **`engine.log`** from both the clean install and the upgrade.
5. **Every probe and command.**
6. **Screenshots of the completed upgrade, if it completes.**

### The tables

**OOM:**

| Limit | Run 1 | Run 2 | Run 3 | Message complete? |
|---:|---|---|---|---|
| 448 MiB | | | | |
| 480 MiB | | | | |
| 512 MiB | | | | |
| 544 MiB | | | | |
| 576 MiB | | | | |
| 608 MiB | | | | |
| 640 MiB | | | | |

**Upgrade and recovery:**

| Question | Answer |
|---|---|
| Does the same-directory upgrade complete now? | |
| How long, and does the wizard close itself? | |
| Does the log name each file before copying? | |
| Last log line if it stalls | |
| Any Defender or security event at the same time? | |
| Does an interrupted install complete on retry? | |

**Slice:**

| Probe | Expected | Actual |
|---|---|---|
| C1a cell store | refusal or correct value | |
| C1b untyped parameter | refusal or correct value | |
| C1c untyped return | refusal or correct value | |
| C1d function value | refusal or correct value | |

---

## 7. Why this round settles the release

**Three of the five release conditions depend on measurements only you can take:**

- **the OOM refusal must not crash after printing**
- **an interrupted install must be recoverable**
- **the candidate must be accepted exactly as built**

**And the hang — the one thing nobody could explain for four rounds — has a suspect and a fix.** **If the same-directory upgrade completes now, that suspect was right, and the most persistent defect in this project closes on evidence rather than on an argument.**

**Your standard is the project's standard now: the message alone does not count.** **Apply it to all three.**
