# Sutram v310 — verify the initializer fix, and close the acceptance list

**Copy this whole file to the Windows AI.**

**v310 is untested on Windows. Everything before it is verified. This round closes the gap.**

---

## 0. Where the project is

**v309 was verified end to end by you:** OOM 32/32 clean refusals, arithmetic 7/7 with the valid case still working, suite 322 PASS, installer clean 9.47 s / upgrade 21.20 s / interrupt-recover 8.65 s, a hand-edited file preserved with its exact bytes, 657/657 hashes, and **a Linux build and a Windows build producing 657 files plus manifest byte-identical.**

**v310 adds three things on top:**

| Change | What it does |
|---|---|
| **Module-level `vitti` initializers** | Now run both checks before generation. **On v309, `vitti leaked = make_kosh() + zero` held a descriptor address and `vitti g = make_kosh()` put a `kosh` in a module variable.** |
| **The expression walk's node budget** | Now refuses with `E_VAKYA_SEEMA` instead of passing. **Unreachable today — the AST heap caps at 43,690 nodes, the budget is 200,000.** |
| **The installer lock** | Taken before every installation-state read: registration, other installations, the state file, the pending record, the journal. |

**And two corrections from an independent reviewer that are being fixed now, so they may or may not be in the build you receive:**

- **The slice gate does not detect a newly added unchecked entry** — it counts calls in two named bodies.
- **The installer decides whether to delete the target by testing whether a file with a 12-hex-prefix name exists** — existence is not equality.

**If your build has a version string higher than v310, those two may already be fixed. Record the exact version you test.**

---

## 1. Task A — the module-level initializer, which was confirmed reachable

**On v309 these compiled:**

```sutram
prakriya make_kosh() {
    kosh k[1]
    kosh_kship(k, 7)
    nivartanam k
}
vitti g = make_kosh()
mukhya() { likha(g[0]) }
```

```sutram
prakriya make_kosh() {
    kosh k[1]
    kosh_kship(k, 7)
    nivartanam k
}
vitti zero = 0
vitti leaked = make_kosh() + zero
mukhya() { likha(leaked) }
```

**Expected on v310: both refused at compile time**, with `E_KOSH_GANIT` or `E_KOSH_DVARA`, exit non-zero, no executable produced.

**Record the exact message for each.**

### A1 — and a valid global must still work

```sutram
vitti counter = 7
mukhya() { likha(counter) }
```

**Expected: `7`.** **If this is now refused, the fix went too far — say so.**

### A2 — and the class question, checked rather than trusted

**Claude states: *"No other non-statement expression exists in the language (no constants, field defaults, default arguments, module-level kosh or mala — each a syntax error, measured)."***

**Please confirm three of those by trying them:**

```sutram
vitti a = 1
vitti b = 2
```
```sutram
rachana Point = { x: 1, y: 2 }
vitti p = Point
```
```sutram
prakriya f(vitti n = 5) { nivartanam n }
mukhya() { likha(f()) }
```

**Expected: a syntax error for each.** **If any compiles, then a non-statement expression does exist and the class is not closed.**

---

## 2. Task B — the expression budget

**The walk now refuses with `E_VAKYA_SEEMA` when its node budget runs out.** **Claude says it is unreachable — the AST heap caps at 43,690 nodes and the budget is 200,000.**

**So it cannot be triggered by a real program.** **Do not spend time trying.**

**But do this instead:** **build one deeply nested expression and confirm the compiler refuses rather than crashing or hanging.**

```sutram
mukhya() {
    likha((((((((((((((((((((((((((((((1)))))))))))))))))))))))))))))
}
```

**Expected: either it compiles, or it refuses with a message.** **A crash or a hang is a finding.**

**Add one nesting level at a time until something changes, and record where.**

---

## 3. Task C — the installer ownership checks, by name

**An independent reviewer named five ownership checks. Four can be tested from your side.**

### C1 — suffix preservation

**Interrupt an install partway. Look in the transaction folder beside the target for any `_superseded` directory.**

**Record: what is in it, and are the filenames suffixed with a hash prefix?**

**Expected: any file the installer replaced is preserved under a suffixed name, not deleted.**

### C2 — concurrency and fresh state

**Start two installer processes at the same time.**

**Expected: one proceeds and the other refuses with a message naming the lock. Neither corrupts the other's state.**

**Record the exact messages from both.**

### C3 — an edit during publication

**This is the case that matters most.**

**1. Start an install.**
**2. While it is copying, edit a file already written into the target — add a line to a `.md` file.**
**3. Let the install finish.**
**4. Check whether your edit survived.**

**Expected: either your edit survives, or the installer reports that it overwrote a changed file.**

**If your edit vanishes silently, that is the defect the reviewer described and it is a data-loss path.**

### C4 — superseded equality

**The reviewer's finding: the installer deletes the target when a file with a matching 12-hex-prefix name exists, and existence is not proof of identical bytes.**

**You cannot easily create two files sharing a 12-hex prefix.**

**What you *can* do: after an interrupted install, check whether any file was deleted from the target that still exists nowhere else.**

**Compare the target folder before and after a retry, and record every file that disappeared.**

**If a file disappears and is not in the transaction folder, say so — that is the data-loss path.**

---

## 4. Task D — identity and the suite

**In a new shell:**

```
where sutram
sutram --version
```

**Expected: one canonical path, and the version you are testing.** **Record it exactly.**

**Then run the native suite.** **Your last run was 322 PASS, no failures.**

**Expected: 322 or better, no FAIL, no COMPILE_FAIL, no TIMEOUT.**

---

## 5. Task E — and the arithmetic refusal, once more

**v310's slice gate is now 64 checks, up from 59.** **Your v309 run passed 7 of 7.**

**Re-run the two original add/XOR cases:**

```sutram
prakriya keep(x) { nivartanam x }
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    vitti zero = 0
    vitti kept = keep(k[0:1] + zero)
    kosh_kship(k, 8)
    likha(kept)
}
```

**Expected: refused.** **And the length control `pankti_gan(k[0:2])` must still return `2`.**

---

## 6. What NOT to do

- **Do not report the v309 passes again.** **They stand and they are in the record.**
- **Do not spend time trying to exhaust the expression budget.** **It is unreachable by design and the margin is stated.**
- **Do not modify the compiler, library, examples, goldens or installer.**
- **Do not claim release acceptance.** **That is a separate verdict.**
- **If `sutram --version` is not the version you expect, stop and report it first.**

---

## 7. What to commit

**Push to `Windows-to-Sarvam/win-v310-<date>/`:**

1. **`INITIALIZER.md`** — A, A1 and A2, with the exact message for each.
2. **`BUDGET.md`** — where nesting stops compiling or starts refusing.
3. **`OWNERSHIP.md`** — C1 to C4, including every file that disappeared across a retry.
4. **`ARITHMETIC.md`** — Task E.
5. **`RESULTS.md`** — the table below.
6. **The exact version string, the compiler SHA-256 and the setup SHA-256.**
7. **Every probe and command.**

### The table

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A — `vitti g = make_kosh()` | refusal | | |
| A — `vitti leaked = make_kosh() + zero` | refusal | | |
| A1 — `vitti counter = 7` | `7` | | |
| A2 — `vitti b = 2` after `vitti a = 1` | syntax error | | |
| A2 — record literal | syntax error | | |
| A2 — default argument | syntax error | | |
| B — deep nesting | compiles or refuses, never crashes | | |
| C1 — suffixed files preserved | present | | |
| C2 — two processes at once | one refuses, no corruption | | |
| C3 — edit during publication | survives or is reported | | |
| C4 — any file deleted with no copy | none | | |
| D — identity | one path, expected version | | |
| D — suite | 322+ PASS, no FAIL | | |
| E — add/XOR refused | refusal | | |
| E — `pankti_gan(k[0:2])` | `2` | | |

---

## 8. Why this round matters

**Three of the reviewer's remaining acceptance items can only be closed from your machine: the native run of the initializer fix, the concurrency case, and the edit-during-publication case.**

**And C4 is the one I would most want answered.** **The installer deletes a target file based on a filename match, not a byte comparison. If a file ever disappears without a copy in the transaction folder, that is data loss — and it would be the first data-loss path found in this whole project.**

**Your standard holds: a message followed by a crash is not a refusal, and a file that exists is not a file that matches.**
