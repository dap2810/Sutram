# Sutram v311 — the release acceptance run

**Copy this whole file to the Windows AI.**

**Every defect found so far is fixed and verified. This round is the one that would accompany a release.**

---

## 0. Where this stands

**You have verified every fix on native Windows, including two the Linux side could not test at all.** **The data-loss path you reproduced on v310 is fixed in v311: the installer now compares the full SHA-256 and keeps both copies when they differ.**

**The remaining release conditions are closed on the evidence you supplied:**

| Condition | Your evidence |
|---|---|
| The global initializer refused | `E_KOSH_DVARA` and `E_KOSH_GANIT`, exit 1, no executable |
| The scalar global still works | `7` |
| Nesting refuses rather than crashing | 0–1022 compile, 1023 refuses cleanly |
| Superseded files preserved | full hash match in the suffixed backup |
| Concurrency safe | 1 proceeds, 0 refuses, 657 matching hashes |
| A live edit survives | the exact edit survives |
| Unequal backup refuses | both copies named and preserved |
| Payload integrity | 657/657, embedded compiler equals the tested one, uninstaller hash equals setup |

**This round does the three things nobody has done: a fresh-machine acceptance, the IDE on v311, and the timeout that has never been observed.**

---

## 1. Task A — a fresh-machine acceptance

**The point is to install as a stranger would, with no history on the machine.**

**Do not skip the removal step. A machine that already has Sutram does not test a first install.**

### A1 — record the starting state

```
where sutram
sutram --version
dir "%LOCALAPPDATA%\Programs"
reg query "HKCU\Environment" /v Path
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path
```

**Record all of it.** **If a Sutram installation exists, preserve it as you have before — do not delete anything.**

### A2 — remove every trace, and confirm removal

**Move the install folder aside, remove any Sutram entry from the user PATH, and confirm:**

```
where sutram
```

**Expected: `INFO: Could not find files...`** **If anything resolves, stop and say what.**

### A3 — install as a first-time user would

**Run `Sutram-Setup.exe` and take the default options.** **Record:**
- **does it show a licence or welcome page?** **What does it say?**
- **what options are pre-selected?**
- **how long to Finish?**
- **does any console window appear at any point?**
- **does the wizard close itself?**

### A4 — the first thing a new user does

**Open a **new** Command Prompt and run:**

```
sutram --version
```

**Expected: `Sutram 1.0 (v311) - sampurna sutra`**

**Then write a file by hand in Notepad:**

```
mukhya() {
    likha("namaste")
}
```

**Save as `first.sm`, then:**

```
sutram first.sm first.exe
first.exe
```

**Expected: `namaste`**

**This is the whole point of the round: a person with no history on the machine gets a working program.**

### A5 — and the uninstaller

**Uninstall through Settings → Apps.** **Record:**
- **does it remove cleanly?**
- **does `sutram` stop resolving?**
- **does it leave anything behind in `%LOCALAPPDATA%\Programs`, in the PATH, or in the registry?**

**Then reinstall, because the rest of this round needs it.**

---

## 2. Task B — the IDE on v311

**The IDE was last verified on v305/v306.** **Nobody has run it on v311, and the compiler has changed four times since.**

### B1 — launch and run

**Launch the IDE from the Start Menu shortcut.** **Load `01_hello.sm`, press Run.**

**Expected: `Namaste, Sutram!` in the output pane.**

**Take a screenshot.**

### B2 — and a program that is refused

**Open a file with a deliberate syntax error and press Run.**

**Expected: a Sanskrit diagnostic with a line number, and the old output cleared.**

**Take a screenshot.**

### B3 — and the arithmetic refusal, through the IDE

**This is the v311 fix, and nobody has seen it in the GUI.**

```sutram
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    likha(k[0:1] + 0)
}
```

**Expected: a compile-time refusal in the IDE, not a number.**

**Record the exact message and take a screenshot.**

**This matters: the fix was verified from the command line. If the IDE swallows the diagnostic or shows the old output, a student never sees it.**

### B4 — and the large-file refusal

**Open a file over 64 KiB.** **Expected: refused, output cleared, and the editor says it still holds the previous file.**

**Take a screenshot.**

---

## 3. Task C — the timeout that has never been observed

**v306 added a 15-minute stop so the wizard cannot wait forever.** **Nobody has watched it fire, and Claude noted it cannot fire if the thread that waits is itself suspended.**

**Do not stall an install deliberately.** **But if an install ever stalls during this round, let it run the full 15 minutes and record:**
- **does it stop on its own?**
- **at what time?**
- **what does it log?**
- **is the wizard left open or closed?**

**If no install stalls, say so plainly — that is the expected outcome and it is not a failure to skip this.**

---

## 4. Task D — the suite, and one number to compare

**Run the native suite.** **Expected: 322 PASS, no FAIL, no COMPILE_FAIL, no TIMEOUT.**

**And record the elapsed time.** **Your v309 run took 18.6 seconds.** **If v311 is materially slower, say so — the expression check now runs inside `gen_expr` and a compile-time cost is possible.**

**That is the one performance question nobody has asked, and it is worth a number.**

---

## 5. What NOT to do

- **Do not report the v309 or v310 passes again.** **They stand.**
- **Do not modify the compiler, library, examples, goldens or installer.**
- **Do not claim release acceptance.** **That verdict belongs to the release review, not to this run.**
- **Do not delete anything during the fresh-machine test.** **Preserve and move aside, as you have been doing.**
- **If `sutram --version` is not v311 after install, stop and report that first.**

---

## 6. What to commit

**Push to `Windows-to-Sarvam/win-v311-acceptance-<date>/`:**

1. **`FRESH-INSTALL.md`** — A1 to A5, with the exact screens and messages.
2. **`IDE.md`** — B1 to B4, with four screenshots.
3. **`TIMEOUT.md`** — what happened, or that nothing stalled.
4. **`SUITE.md`** — the counts and the elapsed time.
5. **The exact version string, compiler SHA-256 and setup SHA-256.**
6. **Screenshots of the welcome page, the Finish page, and the first program running.**

### The table

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A2 — no `sutram` resolves after removal | not found | | |
| A3 — install to Finish | Finish, no console | | |
| A4 — `sutram --version` in a new shell | v311 | | |
| A4 — first program compiled and run | `namaste` | | |
| A5 — uninstall clean, nothing left behind | clean | | |
| B1 — IDE runs `01_hello.sm` | `Namaste, Sutram!` | | |
| B2 — IDE shows a syntax error, output cleared | diagnostic, cleared | | |
| B3 — **IDE refuses `k[0:1] + 0`** | refusal | | |
| B4 — IDE refuses a 64 KiB file, output cleared | refused, cleared | | |
| C — timeout observed, or nothing stalled | either | | |
| D — suite | 322 PASS, no FAIL | | |
| D — suite elapsed time | compare to 18.6 s | | |

---

## 7. Why this round is the one that counts

**Every previous round tested a fix.** **This one tests the thing a student actually experiences: take a machine with no history, install it, write a program, run it.**

**And two things have never been checked:**

**The IDE on v311** — the arithmetic refusal is the newest and most important fix, and if the IDE does not show the diagnostic, a student never learns why their program was rejected.

**The compile-time cost of the new check** — it now runs inside `gen_expr`, on every expression. **A suite that was 18.6 seconds and is now 40 would be a real regression, and nobody has measured it.**

**You have found every defect on this platform by measuring the thing nobody had measured. These are the last two.**
