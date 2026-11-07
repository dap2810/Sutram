# Sutram v306 — Windows release-candidate verification

**Copy this whole file to the Windows AI. This is the release-candidate round.**

---

## 0. What you established, and what changed since

**Your four rounds took Windows from untested to a release candidate.** **Between them you found: two builtin defects, the OOM crash path, the IDE's stale screen, the harness's `lib/` lookup, the two-installation PATH collision, and the installer's ownership refusal.**

**And one of your findings corrected me twice:** **the editor retaining the previous file is a safeguard, not a bug** — my instruction to clear it would have removed it.

**And Claude corrected a mistake of mine that reached every partner:** **I told them "the hang was not a hang."** **That was wrong.** **The v303 copy hung at file 132 of 657 and left an empty file; the ownership refusal you measured was the wreckage it left behind.**

---

## 1. What v306 changes

| Defect you found | What v306 does |
|---|---|
| **OOM crash under a commit limit** | **A refused memory commit now prints `Sutram truti: smritih na labdha` and exits 1** |
| **IDE stale output on a refused load** | **The output pane clears, and the editor says it still holds the previous file** |
| **`79_ayojan_cwd` cannot find `lib/`** | **The harness runs it with a compiler that has `lib/` beside it** |
| **Two installations coexist** | **The installer refuses while another Sutram is installed and names it** |
| **Installer waits forever** | **No console window, non-interactive, logs every step, wizard stops after 15 minutes** |

**Release line on Linux:**

```
gates: 69 PASS / 0 FAIL / 1 NOT-RUN   (NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v306) - sampurna sutra
```

**Installer: `PASS payload v306 = compiler v306`, `--self-test` exit 0 under Wine.** **New gate `R130 installer engine`, 16 checks, 0 failed.**

---

## 2. Two things v306 does NOT fix — do not report them as new

**Claude's own admission:**

- **An interrupted install still traps the next run behind a "user file" refusal.**
- **The v306 log would not name the file it stopped on, although an earlier hand-back said it would.**

**Both are known and being fixed. If you hit either, record it and move on.**

**And the current install on your machine is v305.** **The installer will now refuse to upgrade over it — that is the new behaviour, not a defect.**

---

## 3. Task A — a clean install

**The installer now refuses while another Sutram is installed.** **So this must be a clean install.**

### A1 — record the current state

```
where sutram
sutram --version
dir "%LOCALAPPDATA%\Programs\Sutram"
reg query "HKCU\Environment" /v Path
```

### A2 — preserve, then remove

**Move the existing install aside — do not delete it.**

```
move "%LOCALAPPDATA%\Programs\Sutram" "%LOCALAPPDATA%\Programs\Sutram-before-v306"
```

**Then remove its user PATH entry, and record the PATH string before and after.**

### A3 — confirm the installer's new refusal works

**Before installing v306, run `Sutram-Setup.exe` while the old folder is still there under its original name.**

**Expected: it refuses and names the existing installation.**

**Then move the folder aside as in A2 and run it again.**

**Record both outcomes.** **This is a new behaviour and nobody has seen it work.**

### A4 — install v306

**Run it.** **Record:**
- **does it reach Finish?**
- **how many seconds?**
- **does the PowerShell window close on its own?**
- **does any console window appear at all?**

**Expected: no console, Finish reached, closes normally.** **The v305 repair completed in 14.9 seconds.**

### A5 — verify in a NEW shell

**Open a new Command Prompt and run:**

```
where sutram
sutram --version
```

**Expected: one path, and `Sutram 1.0 (v306) - sampurna sutra`.**

**This is the check that failed twice before.** **If it does not say v306, stop and report.**

---

## 4. Task B — the OOM fix, which is the one that matters

**You measured this precisely: 640 MiB failed with `0xC0000005`, 768 MiB succeeded, and no Sanskrit refusal appeared at any failing limit.**

**Now test the fix under the same Job commit limits.**

**Use the same runner you built — `job_runner.py` from `win-diag-v305-2026-11-06`.**

### B1 — the B3 program at the limits that failed

```sutram
mukhya() {
    kosh k[1]
    chakra i = 1 tak 100000000 {
        kosh_kship(k, i)
    }
    likha(kosh_gan(k))
}
```

**Run under 64, 128, 256, 512 and 640 MiB.**

**Expected at each: `Sutram truti: smritih na labdha`, exit 1, on stdout or stderr — not an access violation.**

**Record the exact message and which stream it appears on.**

### B2 — and at 768 MiB and above

**Expected: it succeeds and prints `100000000`.**

**So the boundary should still be there — the program needs the memory — but below it, it now refuses instead of crashing.**

### B3 — and the `mandapa` case that refused correctly

```sutram
mukhya() {
    mandapa parimita 67108864 {
        vitti s = 0
        chakra i = 1 tak 2000000 {
            vitti p = nirmmita(64)
            p[0] = i
            s = s + p[0]
        }
        likha(s)
    }
}
```

**Under 64 MiB this crashed on v305.** **Expected now: a refusal, not a crash.**

### B4 — and the page-touch control

**Your `A3-nirmmita-touch-pages.sm` — the 100 MB request that writes once per page.** **Under 64 MiB it crashed on v305.**

**Expected now: a refusal.**

**These three tests are the whole point of this round.** **If any still crashes, the fix is incomplete and that is the most important thing you will report.**

---

## 5. Task C — the IDE's output clearing

**You established: a compile error and a runtime error both clear the output pane correctly, and only the large-file refusal leaves the previous output.**

### C1 — the refused load

**1. Load `01_hello.sm` and Run it.** **Output appears.**
**2. Click `105_block_nesting_capacity` (the 70,422-byte file, refused).**

**Expected: the output pane clears, and the editor says it still holds the previous file.**

**Record the exact text the editor shows.**

### C2 — and that the safeguard survives

**After the refusal, type something in the editor and press Save.**

**Expected: it saves to `01_hello.sm`, the file it still holds — not to the refused file.**

**This matters: retaining the editor text is a safeguard, and the fix must not have removed it.**

**If Save now writes to the refused file, that is a regression and it is worse than the original defect.**

### C3 — screenshot

**One screenshot of the cleared output pane with the refusal notice.**

---

## 6. Task D — the full native suite

**Run it as you did before.** **Your last run was 321 PASS / 1 COMPILE_FAIL.**

**Expected: the `79_ayojan_cwd` failure is gone, so 322 PASS or better, and no COMPILE_FAIL.**

**Record the counts and any failing test name.**

---

## 7. Task E — and one thing nobody has tested

**The wizard now stops after 15 minutes instead of waiting forever.**

**Nobody has seen that path.** **It is hard to test deliberately — but if the install ever stalls, wait and record whether it stops on its own at 15 minutes.**

**Do not stall it on purpose.** **Just note if it happens.**

---

## 8. What NOT to do

- **Do not report the two known v306 gaps as new findings** — the interrupted-install trap and the log not naming the file.
- **Do not report the installer's new refusal as a defect** — it is the intended behaviour.
- **Do not modify the compiler, library, examples, goldens or installer.**
- **Do not claim v306 is release-accepted.** **That is not your call and not mine — it is a verdict from the release review.**
- **If `sutram --version` is not v306 in a new shell, stop.** **Everything after that is meaningless.**

---

## 9. What to commit

**Push to `Windows-to-Sarvam/win-v306-<date>/`:**

1. **`RESULTS.md`** — the table below.
2. **`INSTALL.md`** — the A2/A3/A4 sequence, with the installer's refusal text.
3. **`OOM.md`** — the B1/B2/B3/B4 table with exact messages.
4. **`IDE.md`** — C1 and C2, with the screenshot.
5. **Every `.sm` probe and the Job runner you used.**
6. **The exact commands.**

### The table

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A3 installer refuses over an existing install | refuses, names it | | |
| A4 install reaches Finish | Finish, no console | | |
| A5 `sutram --version` in a new shell | v306 | | |
| B1 B3 at 64 MiB | `smritih na labdha`, exit 1 | | |
| B1 B3 at 256 MiB | `smritih na labdha`, exit 1 | | |
| B1 B3 at 640 MiB | `smritih na labdha`, exit 1 | | |
| B2 B3 at 768 MiB | `100000000` | | |
| B3 `mandapa` at 64 MiB | refusal, not crash | | |
| B4 page-touch at 64 MiB | refusal, not crash | | |
| C1 refused load clears output | cleared + notice | | |
| C2 Save still targets the held file | `01_hello.sm` | | |
| D native suite | 322+ PASS, no COMPILE_FAIL | | |

---

## 10. Why this round decides the release

**Every defect that has ever blocked this project on Windows was found by you measuring something nobody had measured.**

**The OOM fix is the one that matters most: it was diagnosed from your boundary measurement — 640 fails, 768 succeeds — and fixed by changing how the runtime handles a failed page commit.** **If your three OOM tests pass, that defect class is closed.** **If any still crashes, the fix is incomplete and the release waits.**

**And C2 is the one nobody would think to check: the fix cleared a screen, and it must not have removed a safeguard while doing it.**
