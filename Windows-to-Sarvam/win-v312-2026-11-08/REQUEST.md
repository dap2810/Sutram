# Sutram v312 — verify the four first-contact fixes

**Copy this whole file to the Windows AI.**

**Three of these four are things a user sees before they run a single program. One of them is the first screen they ever look at.**

---

## 0. What v312 changes, and why each one came from your last run

**Your v311 acceptance run found three defects and one thing you could not test. All four are addressed.**

| Your finding | What v312 does |
|---|---|
| **The licence page visibly corrupts the dash and joins lines** | **`license_to_utf16` widened UTF-8 byte by byte — U+2014 EM DASH became three characters, and bare LF does not break lines in an EDIT control. It now decodes UTF-8 and writes CR LF.** |
| **PowerShell appeared near the end of uninstall and closed itself** | **removed** |
| **An empty `.sm\OpenWithProgids` registry key survived uninstall** | **removed** |
| **The walk budget could not be reached, so its refusal path was untested** | **now 65,536 visits. A 20,000-term statement refuses with `E_VAKYA_SEEMA`; 10,000 terms compile.** |

**And one thing your run reported that v312 addresses but nobody has confirmed:** ***"every Sanskrit line showed as noise"*** on the licence page.

**The encoding fix should make Sanskrit render. **No one has looked at the result.** **That is Task A.**

---

## 1. Task A — the licence page, which is the first thing a user sees

**This is the most important task in this round.** **Everything else a student can work around; a broken first screen is the impression they keep.**

### A1 — capture the licence page as text

**Run the installer to the licence page and stop.** **Do not proceed past it until you have captured it.**

**Take a full screenshot.** **Then, if the page has a scrollbar, capture the top, the middle and the bottom.**

### A2 — and answer four specific questions

**Looking at the captured page:**

1. **Is the em dash (—) a single character, or three characters?**
2. **Are the lines broken, or run together into paragraphs?**
3. **Is any Sanskrit text present, and does it render as Devanagari rather than noise?**
4. **Is any text truncated at the right edge, or cut off mid-word?**

**Answer each one plainly.** **"The dashes are correct now" and "the Sanskrit still shows as noise" are both useful; "looks fine" is not.**

### A3 — and if Sanskrit still fails, capture it

**If the Sanskrit lines still show as noise or boxes, take a close screenshot of one line and record:**
- **the font the control appears to be using, if visible**
- **whether the characters are replacement glyphs (boxes), or wrong letters, or missing entirely**

**Those three are different defects with different fixes.**

---

## 2. Task B — the uninstall, which left two traces

### B1 — watch the whole uninstall

**Uninstall through Settings → Apps.** **Watch the entire process, from clicking Uninstall to the last window closing.**

**Record:**
- **did any console window appear at any point?**
- **did any PowerShell window appear?**
- **how long did it take?**
- **what was the last thing you saw?**

**On v311, PowerShell appeared near the end and closed itself.** **If it appears again, note exactly when — before the progress bar finishes, after it, or during cleanup.**

### B2 — and check what is left behind

**After the uninstall completes:**

```
dir "%LOCALAPPDATA%\Programs"
reg query "HKCU\Software\Classes\.sm" /s
reg query "HKCU\Environment" /v Path
where sutram
```

**Record every one.**

**On v311 an empty `.sm\OpenWithProgids` key survived.** **Expected now: the key is gone.**

**And check the rest:** **is the PATH entry removed? does anything still resolve? are shortcuts gone?**

### B3 — and the strict criterion

**List every file and every registry key that survives uninstall.**

**A strict uninstall leaves nothing.** **If something survives, name it exactly — the path or the key, and whether it has values or is empty.**

---

## 3. Task C — the walk budget, which is now reachable

**v312 lowered the budget from 200,000 visits to 65,536, and the claim is:**

- **a 20,000-term statement is refused with `E_VAKYA_SEEMA`, exit 1, no output**
- **a 10,000-term statement compiles**
- **and the message names the number**

**This was measured on Linux.** **It needs a native check because a different compiler build could behave differently.**

### C1 — build the two programs

**A 10,000-term expression.** **Something like a long sum:**

```sutram
mukhya() {
    likha(1 + 1 + 1 + ... )   // 10,000 terms
}
```

**Generate it with a script rather than typing it.** **Record the exact term count.**

**Expected: compiles, exit 0.**

### C2 — and a 20,000-term expression

**Expected: refused with `E_VAKYA_SEEMA`, exit 1, and the message names the number.**

**Record the exact message.**

### C3 — and if either behaves differently from the claim

**Say so.** **A budget that refuses at 10,000 on Windows but compiles on Linux would mean the walk counts differently per platform, which would be a real finding.**

---

## 4. Task D — identity and the suite

**After reinstalling v312, in a new shell:**

```
where sutram
sutram --version
```

**Expected: one canonical path, `Sutram 1.0 (v312) - sampurna sutra`.**

**Then run the native suite.** **Expected: 322 PASS, no FAIL, no COMPILE_FAIL, no TIMEOUT.**

**And record the elapsed time.** **Your v309 run took 18.6 seconds.** **v312 changed the walk budget, which affects compile time on large statements — if the suite is materially slower, say so.**

---

## 5. What NOT to do

- **Do not report the v311 passes again.** **They stand.**
- **Do not claim release acceptance.** **That verdict belongs to the release review.**
- **Do not proceed past the licence page until you have captured it.** **It is the whole point of Task A.**
- **Do not delete anything during the uninstall test.** **Uninstall is the test.**
- **If `sutram --version` is not v312 after install, stop and report that first.**

---

## 6. What to commit

**Push to `Windows-to-Sarvam/win-v312-<date>/`:**

1. **`LICENCE.md`** — the screenshots and the four answers from A2.
2. **`UNINSTALL.md`** — B1's timeline, B2's leftovers, B3's strict list.
3. **`BUDGET.md`** — C1 and C2, with the exact term counts and messages.
4. **`RESULTS.md`** — the table below.
5. **The exact version string, compiler SHA-256 and setup SHA-256.**
6. **Every generated probe and the script that generated it.**

### The table

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A2.1 — em dash is one character | one | | |
| A2.2 — lines are broken, not joined | broken | | |
| A2.3 — Sanskrit renders as Devanagari | renders | | |
| A2.4 — no text truncated at the edge | none | | |
| B1 — no console or PowerShell window | none | | |
| B2 — `.sm\OpenWithProgids` gone | gone | | |
| B2 — PATH entry removed | removed | | |
| B3 — nothing survives uninstall | nothing | | |
| C1 — 10,000 terms compile | exit 0 | | |
| C2 — 20,000 terms refused | `E_VAKYA_SEEMA` | | |
| D — identity | v312, one path | | |
| D — suite | 322 PASS, no FAIL | | |
| D — suite elapsed time | compare to 18.6 s | | |

---

## 7. Why this round matters

**Every previous round tested whether the language works.** **This one tests whether the product does.**

**A student who installs this sees the licence page first.** **On v311 it had mangled dashes, joined lines and unreadable Sanskrit.** **If it still does, everything after it is undermined — a language that teaches in Sanskrit, with a first screen full of noise.**

**And the uninstall test is the one nobody enjoys and everybody notices.** **Two traces left behind is not a failure of the language, but it is the difference between a product and a prototype.**

**Your standard has held throughout: a message followed by a crash is not a refusal, and a file that exists is not a file that matches.** **This round adds one more: "looks fine" is not a finding.**
