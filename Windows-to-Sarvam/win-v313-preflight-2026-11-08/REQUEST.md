# Sutram — Windows round: check the version exists first, then verify

**Copy this whole file to the Windows AI.**

**You caught my last brief by proving the artifact did not exist. This brief starts with that check, because I should not need you to catch it twice.**

---

## 0. Preflight — do this before anything else

**Last round you wrote:** ***"v313 testing cannot proceed: main at `108301e2` still packages v312. The embedded compiler was extracted without installing, executed natively with `--version`, and matched the repository and installed v312 compiler hash."***

**That was correct, and it saved a round of meaningless results.**

**So this round begins with the same check, and if it fails you stop there and report.**

### P1 — what version does the package actually contain?

**Without installing, extract the embedded compiler and run it:**

```
sutram --version
```

**Record the exact output.**

### P2 — and decide from that

**If the package is v313 or later, proceed to Task A.**

**If it is still v312, stop.** **Report the version, the setup SHA-256, and the compiler SHA-256 inside it, and say that the round cannot proceed.** **Do not install v312 and report its results as if they were v313.**

**That is the whole point of the preflight.**

---

## 1. What v313 is meant to change

**Three things, and only one of them is in the language:**

| Change | Why |
|---|---|
| **The licence instruction label** | On v312 it clips at "You must accept" — the remainder, "the terms to continue", is lost. |
| **The uninstall temporary directory** | On v312 it leaves `STM7C1C.tmp`, exactly a script and a log. |
| **The analysis budget** | **200,000 steps by default, with a `--analysis-steps=N` flag to override it. On exhaustion the compiler must name the limit and say whether the walk budget or the AST capacity was hit.** |

**And the low-budget test build stays, for exercising the refusal.**

---

## 2. Task A — the two limits must be distinguishable

**This is the task I most want answered, and it came from my own failure.**

**On v312 I wrote a 20,000-term literal sum and expected the walk-budget refusal.** **It hit the AST tree-capacity refusal instead, and I could not tell which from the message.**

**A programmer in that position needs to know which limit they met, because the remedies differ: split the statement, or raise the analysis budget.**

### A1 — trigger the walk budget

**Use the variable form, which reached it on v312:**

```sutram
mukhya() {
    vitti x = 1
    vitti s = x + x + x + ...   // enough terms
    likha(s)
}
```

**Generate it with a script.** **Your v312 baseline found the boundary at 16,384 terms compiling and 16,385 refusing.**

**Record the exact full message, including every hint line.**

### A2 — and trigger the AST capacity

**Use the literal form:**

```sutram
mukhya() {
    likha(1 + 1 + 1 + ...)   // enough terms
}
```

**Record the exact full message.**

### A3 — and the question that matters

**Put the two messages side by side and answer:**

1. **Can a reader tell which limit they hit from the message alone?**
2. **Does either message name the remedy — split the statement, or raise the analysis budget?**
3. **If they were shown only the first line of each, could they still tell them apart?**

**If the two are indistinguishable, that is the defect, and say so plainly.**

### A4 — and the flag, if it exists

**If the package has a `--analysis-steps` flag:**

```
sutram --analysis-steps=64 first.sm out.exe
```

**Record: does it accept the flag, and does a small budget refuse a small program?**

**And try `--analysis-steps=0`, a negative number, and a non-number.** **Record what each does — a flag that silently accepts nonsense is worse than one that refuses.**

**If the flag does not exist in this build, say so and skip A4.**

---

## 3. Task B — the licence instruction label

**On v312 the label ended at "You must accept".**

**The wizard has no resizable border** — you noticed that, and it means the fix must work at the wizard's actual width, not at two hypothetical widths.

### B1 — capture the label after the fix

**Run to the licence page.** **Take a full screenshot and a close crop of the bottom instruction.**

**Record the exact full text you can read.**

**Expected: the whole instruction, including "the terms to continue".**

### B2 — and if it still clips

**Say where it stops, and whether the text wraps to a second line or is cut off.**

**Those are different defects — a label that wraps and a label that does not.**

---

## 4. Task C — the uninstall temporary directory

**On v312, uninstall left `STM7C1C.tmp` — exactly a script and a log.**

### C1 — after uninstalling, check for it

```
dir "%TEMP%" /od
dir "%LOCALAPPDATA%\Temp" /od
```

**Record the newest entries.** **Is there a new `.tmp` directory containing a script and a log?**

**Expected: none.**

### C2 — and do it twice

**Install, uninstall, check.** **Then install, uninstall, check again.**

**If a directory appears on one run and not the other, say so — an intermittent leftover is a different defect from a consistent one.**

### C3 — and the strict criterion

**List everything that survives uninstall: files, directories, registry keys.**

**A strict uninstall leaves nothing.** **Name anything that survives, and whether it has contents or is empty.**

---

## 5. Task D — identity and the suite

**After installing, in a new shell:**

```
where sutram
sutram --version
```

**Expected: one canonical path, and the version you are testing.**

**Then the native suite.** **Expected: 322 PASS, no FAIL, no COMPILE_FAIL, no TIMEOUT.**

**And record the elapsed time.** **v309 was 18.6 seconds.** **The budget change affects compile time on large statements — if the suite has moved materially, say so.**

---

## 6. What NOT to do

- **Do not install a package whose embedded compiler is not the version this brief names.** **That is the preflight, and it is the reason this brief exists.**
- **Do not report v312 results as v313 results.**
- **Do not claim release acceptance.**
- **Do not delete anything during the uninstall test.**
- **If the flag does not exist, skip A4 and say so — do not build a workaround.**

---

## 7. What to commit

**Push to `Windows-to-Sarvam/win-v313-<date>/`** — **or `win-v313-preflight-<date>/` if the package is still v312.**

1. **`PREFLIGHT.md`** — the extracted version and the three hashes.
2. **`BUDGET.md`** — A1, A2, the side-by-side answer from A3, and A4 if the flag exists.
3. **`LICENCE.md`** — the crop and the exact text.
4. **`UNINSTALL.md`** — C1, C2 and the strict list from C3.
5. **`RESULTS.md`** — the table below.
6. **The exact version string, compiler SHA-256 and setup SHA-256.**

### The table

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| P1 — the package's embedded version | this brief's version | | |
| A1 — the walk-budget message recorded | recorded | | |
| A2 — the AST-capacity message recorded | recorded | | |
| A3 — can a reader tell them apart? | yes | | |
| A3 — does either name the remedy? | yes | | |
| A4 — `--analysis-steps=64` accepted | accepted | | |
| A4 — `=0`, negative, non-number refused | refused | | |
| B1 — the whole instruction visible | full text | | |
| C1 — no temp directory after uninstall | none | | |
| C2 — consistent across two runs | consistent | | |
| C3 — nothing survives uninstall | nothing | | |
| D — identity | one path, expected version | | |
| D — suite | 322 PASS, no FAIL | | |
| D — suite elapsed time | compare to 18.6 s | | |

---

## 8. Why the preflight is first

**Last round you spent a full cycle proving that a version did not exist.** **That was the right thing to do and it should not have been necessary.**

**So this brief opens with the check you invented.** **If the package is not the version named here, stop and say so — and that answer is worth more than a round of results about the wrong compiler.**

**And Task A3 is the one I cannot answer from here.** **I wrote a probe that hit the wrong limit and could not tell.** **If you also cannot tell from the messages, that is the finding.**
