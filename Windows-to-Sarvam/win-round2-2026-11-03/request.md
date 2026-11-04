# Sutram — Windows round: verify, fix what is fixable, commit findings

**Copy this whole file to the Windows AI. It is self-contained.**

---

## 0. What has already happened

**You tested v297 on Windows and produced excellent evidence. Three AI partners have now read your `native-cases.json` in full and classified all eight failures.** **This round is: confirm their classification by running, fix the two real defects, and commit the findings.**

**The three-way diagnosis:**

| Cause | Tests | Verdict |
|---|---|---|
| **My test was wrong** | `220`, `29` | `220` omitted `--lang hindi`. `29` is a Linux raw-syscall example run with a Linux exit expectation. |
| **Documented Linux-only feature** | `288`, `303`, `317`, `318` | Memory reporting and the budget do not work on Windows, and the reference says so. **Confirm, do not "fix" the golden.** |
| **An old builtin defect that Windows exposed** | `322`, `323` | **`anka_akshar` and `vartani_sandhi` are wrong on Linux too. Linux hides it because the golden was recorded from the same broken behaviour.** |

**Your evidence found something Linux testing never would have.** **That is the headline of this round.**

---

## 1. Your tasks, in order

### Task A — re-run the two harness failures correctly

**`220_hindi_parse_error`** — the recorded command omitted `--lang hindi`.

```
sutram.exe --lang hindi examples\220_hindi_parse_error.sm out.exe
```

**Expected:** the Hindi pack message in Devanagari, exit 1.

**Record:** the exact stdout and stderr. **If it now matches the golden, `220` is closed as a test-harness error.**

**`29_nishkriya`** — this example emits a raw Linux `syscall` instruction (`mov eax,60`). **That instruction does not exist on Windows.**

**Confirm the example is Linux-specific by reading it.** **Then mark it target-specific and record that this is not a Sutram exit-code bug.**

**Do not attempt to make a Linux syscall work on Windows.**

---

### Task B — confirm the memory gap is real and bounded

**`317`, `318`, `303`, `288`.** **All four are memory features that the reference says are Linux-only.**

**Run these three programs and record the output exactly:**

**B1 — memory reporting:**
```sutram
mukhya() {
    likha("start=", parimana())
    mandapa {
        vitti p = nirmmita(4096)
        likha("in=", parimana())
    }
    likha("after=", parimana())
}
```

**Expected on Windows:** all three print `0`. **That is the confirmed defect.**

**B2 — the budget:**
```sutram
mukhya() {
    mandapa parimita 1048576 {
        vitti s = 0
        chakra i = 1 tak 20000 {
            vitti p = nirmmita(64)
            p[0] = i
            s = s + p[0]
        }
        likha(s)
    }
}
```

**Expected on Windows:** it runs to completion and prints a number, **instead of refusing with `E_PARIMITA`.**

**Record the exact output.**

**B3 — the `kosh` alias:**
```sutram
mukhya() {
    kosh k[1]
    kosh_push(k, 41)
    vitti a = k
    vitti obstacle = nirmmita(64)
    kosh_push(k, 42)
    k[0] = 99
    likha("a[0]=", a[0], " k[0]=", k[0])
}
```

**Expected on Windows:** `a[0]=41 k[0]=99` — **the alias diverges.** **On Linux it is `a[0]=99 k[0]=99`.**

**Record the exact output.**

**Then answer one question: is the reference honest about this?** **Search `docs/` for the memory section and check whether it says these are Linux-only.** **If it does, quote the line. If it does not, say so — because then the documentation is wrong, not the compiler.**

---

### Task C — the two real defects. Investigate, do not fix blind.

**`322` and `323` crash with exit `3221225477` = `0xC0000005`, an access violation.**

**The output shows:**
```
laghu 97 guru 65
�42          ← should be "B42"
             ← "abcd" is missing
```

**So `anka_akshar` and `vartani_sandhi` are implicated.**

**Claude's finding: *"two old builtin defects — `anka_akshar` and `vartani_sandhi` — that are wrong on Linux too, which Linux happens to hide."***

**Your task:**

1. **Read `examples/322_r111_new_names.sm` and find the lines that use `anka_akshar` and `vartani_sandhi`.**
2. **Write two minimal programs, one per function, and run them on Windows.**
3. **Then run the same two programs on the Linux binary if you have one — or report that you cannot.**
4. **Record: does each function return the wrong value, crash, or both?**
5. **Report what the function should return.**

**Do not fix the compiler.** **This is a diagnosis. The Linux side owns the fix because the defect is not Windows-specific.**

---

### Task D — commit everything

**Push to the repository under `Windows-to-Sarvam/`, in a new folder `win-round2-<date>/`:**

1. **`RESULTS.md`** — the table in section 2 below, filled in.
2. **Every program you wrote**, as `.sm` files.
3. **Every log and screenshot.**
4. **The exact command lines you ran.**

**Commit message:** something like `Windows round 2: harness re-runs, memory gap confirmed, two builtin defects located`

**Do not modify `src/`, `lib/`, `examples/`, `tests/` or any golden.** **Report only.**

---

## 2. The table to fill in

| Task | Test | Result | Exact output | Verdict |
|---|---|---|---|---|
| A | `220` with `--lang hindi` | | | harness error / real defect |
| A | `29` is Linux-only | | | confirmed / not confirmed |
| B | `317` `parimana` | | | all zeros / something else |
| B | `318` `parimana_moves` | | | |
| B | `303` `parimita` | | | refuses / does not refuse |
| B | `288` `kosh` alias | | | diverges / shared |
| B | reference says Linux-only? | | | quote the line |
| C | `anka_akshar` minimal | | | wrong value / crash / both |
| C | `vartani_sandhi` minimal | | | |

---

## 3. Rules

- **Do not change a golden to make a test pass.** **If a golden is wrong, say so in the report.**
- **Do not modify the compiler or the library.** **Diagnosis only.**
- **Do not attempt to port a Linux syscall to Windows.**
- **Report exactly what happened, not what should have happened.** **If you are unsure, paste the raw output and mark it uncertain — a human will judge.**
- **If you cannot do something, say "not done" and why.** **A gap named is worth more than a gap hidden.**

---

## 4. Why this matters

**The memory gap is the one confirmed Windows defect.** **A student on Windows gets a `parimana()` that always says zero and a `parimita` budget that never refuses.**

**That is a safety feature that does not work on the platform students use.** **Either it gets built for Windows, or the reference must say plainly that it is Linux-only — and right now nobody is sure which.**

**And the two builtin defects matter more, because they are not Windows-specific at all.** **Windows found them.** **Linux hides them behind a golden that was recorded from the same broken behaviour.**

**That is the most valuable thing your run produced, and it is why we test on more than one platform.**
