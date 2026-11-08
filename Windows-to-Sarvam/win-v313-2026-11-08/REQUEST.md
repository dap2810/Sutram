# Sutram v313 — the two last first-contact findings

**Copy this whole file to the Windows AI.**

**Everything you verified on v312 passed. Two things remain, and both are things a user sees before running a program.**

---

## 0. What you established on v312

| Test | Result |
|---|---|
| Em dash | single U+2014, correct |
| Line breaks | CR LF, text matches the licence source exactly |
| **Sanskrit and Hindi** | **visibly render** |
| Uninstall window | none detected |
| Empty `.sm` key | gone, and the empty parent removed |
| PATH | baseline restored, `where sutram` exit 1 |
| Identity | one canonical path, v312, 657/657 hashes |
| Suite | 322 PASS, no failures |

**And you caught two things in your own run that matter:**

**1. The licence instruction label clips "the terms to continue."** The body wraps; the label does not.

**2. Uninstall leaves a new temporary directory with a script and a log.**

**And you flagged that my 20,000-term literal probe hit the AST tree-capacity refusal before the walk budget** — the variable and global forms behaved exactly as claimed. **That was my probe being wrong, and you said so precisely instead of passing it.**

---

## 1. Task A — the clipped instruction label

**The licence page's body wraps correctly. The instruction at the bottom does not, and loses "the terms to continue."**

### A1 — capture it precisely

**Run the installer to the licence page.** **Capture the whole page, and a close crop of the bottom instruction.**

**Record the exact text you can read, and where it stops.**

### A2 — and what the full text should be

**If you can read the licence source in the repository, record the full instruction line as it should appear.**

**Then state what is missing from the display.**

**A fix that wraps the label needs to know whether the full line fits at the current window width, or whether it needs two lines.**

### A3 — and after the fix, check it at two window sizes

**Once v313 is available: capture the licence page at the default window size, and again with the window narrowed.**

**Expected: the instruction is fully readable at both.**

**If it wraps at one size and clips at another, say which.**

---

## 2. Task B — the temporary directory left by uninstall

**On v312, uninstall left a new temporary directory containing a script and a log.**

### B1 — find it and identify it

**After uninstalling, check the usual temporary locations:**

```
dir "%TEMP%" /od
dir "%LOCALAPPDATA%\Temp" /od
```

**Record the newest entries and their contents.** **Name the directory and list every file in it.**

**Is it the installer's script and log, or something else?**

### B2 — and check whether it is the same on every uninstall

**Install, uninstall, and check again.** **Record whether the same directory name pattern appears.**

**If the name contains a random or timestamp component, say what the pattern is.**

### B3 — and after the fix, confirm removal

**Once v313 is available: install, uninstall, and confirm the temporary directory is gone.**

**And check that nothing else new appeared.**

---

## 3. Task C — the budget, and what a programmer sees

**The compiler refuses a statement with too many terms, using `E_VAKYA_SEEMA` and a number.**

**There is a disagreement between two reviewers about whether the limit should be 65,536 or 200,000.** **Whichever is chosen, the message has to be usable.**

### C1 — trigger it and read the whole message

**Build a statement with enough terms to be refused. The variable form worked on v312:**

```sutram
mukhya() {
    vitti x = 1
    vitti s = x + x + x + ...   // enough terms
    likha(s)
}
```

**Generate it with a script.** **Record the exact full message, including any hint line.**

### C2 — and answer one question about it

**If you were a programmer who had never seen this compiler, would that message tell you what to do?**

**Not whether it is accurate — whether it is actionable.** **If it names the limit but not the remedy, say so.**

**That answer decides how the fix should be written, and it is the kind of thing only a fresh reader can judge.**

### C3 — and the boundary

**Find the term count where it flips from compiling to refusing.** **Bisect if needed.**

**Record the number.** **It was measured on Linux as 8,200 to 16,400 terms; confirm or correct it.**

---

## 4. Task D — identity and the suite

**In a new shell after installing v313:**

```
where sutram
sutram --version
```

**Expected: one canonical path, `Sutram 1.0 (v313) - sampurna sutra`.**

**Then run the native suite.** **Expected: 322 PASS, no FAIL, no COMPILE_FAIL, no TIMEOUT.**

**And record the elapsed time.** **v309 was 18.6 seconds. If it has grown materially, say so — the expression check now runs on every statement.**

---

## 5. What NOT to do

- **Do not report the v312 passes again.** **They stand.**
- **Do not claim release acceptance.**
- **Do not delete anything during the uninstall test.**
- **Do not spend time on the 20,000-term literal.** **It hits the tree-capacity limit first and that is already understood.**
- **If `sutram --version` is not v313 after install, stop and report that first.**

---

## 6. What to commit

**Push to `Windows-to-Sarvam/win-v313-<date>/`:**

1. **`LICENCE.md`** — the crop, the missing text, and the two window sizes after the fix.
2. **`UNINSTALL.md`** — the temporary directory, its contents, its name pattern, and whether it is gone after the fix.
3. **`BUDGET.md`** — the full refusal message, your answer to "is it actionable", and the measured boundary.
4. **`RESULTS.md`** — the table below.
5. **The exact version string, compiler SHA-256 and setup SHA-256.**

### The table

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A1 — instruction label fully visible | full text | | |
| A3 — readable at default window size | readable | | |
| A3 — readable at a narrowed window | readable | | |
| B1 — temporary directory identified | named | | |
| B3 — gone after the fix | gone | | |
| C1 — full refusal message recorded | recorded | | |
| C2 — is the message actionable? | your judgement | | |
| C3 — the boundary term count | a number | | |
| D — identity | v313, one path | | |
| D — suite | 322 PASS, no FAIL | | |
| D — suite elapsed time | compare to 18.6 s | | |

---

## 7. Why these two matter more than they look

**A clipped instruction on the licence page means the first sentence a user is given is incomplete.** **It is a one-line fix and it is the first thing anyone reads.**

**And a temporary directory left behind after uninstall is the difference between a product and a prototype.** **Not because it is harmful, but because a user who checks will find it, and will wonder what else was left.**

**Both are small. Both are visible. Neither is a defect in the language.**

**And Task C2 is the one I cannot answer from here: whether the refusal message is *actionable* is a judgement only a fresh reader can make.**
