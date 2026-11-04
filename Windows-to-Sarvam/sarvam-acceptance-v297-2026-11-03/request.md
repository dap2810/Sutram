# Sutram — Windows acceptance test

**Give this file to an AI agent on a Windows machine. It contains every test to run, the exact expected result, and what to report back.**

---

## 0. What this is

**Sutram is a programming language with Sanskrit keywords.** It compiles to native machine code with no runtime, no garbage collector, and no dependency on C or Python.

- **Repository:** `https://github.com/dap2810/Sutram`
- **Expected version:** `Sutram 1.0 (v297) - sampurna sutra`
- **Test machine:** Windows (any modern version)
- **Time needed:** about 40 minutes

**The purpose of this run is to confirm the compiler, installer and IDE work on Windows the way they do on Linux.** **Linux is tested continuously; Windows is not, and has never been tested by an automated run.**

---

## 1. Known issues before you start

**Read these first so you do not report a known problem as a new one.**

| Issue | Status |
|---|---|
| **The installer's payload may be `v243`** while the repo root installer is `v297`. | **Known.** Test 2 confirms whether this is still true. If `sutram --version` says v243, that is the known payload problem, not a new bug. |
| **The linker still prints `Sutram Error`** while the compiler prints `Sutram truti`. | **Known and deliberate.** A link failure saying `Sutram Error` is expected. |
| **`patra_asti` is withdrawn** pending an OS query the compiler does not have. | **Known.** |
| **`sankhya_bindu` is withdrawn** and refuses with `E_PRATYAHRITA`. | **Known.** |
| **The IDE is a work in progress.** | **Known.** Report what you see, including if it is rough. |

---

## 2. Setup

**Choose one of two routes.**

### Route A — install from the repo (tests the installer)

1. Clone or download `https://github.com/dap2810/Sutram` (branch `main`).
2. Run `Sutram-Setup.exe` from the repository root.
3. Open a **new** Command Prompt (not the one you installed from).

### Route B — use the prebuilt compiler directly (skips the installer)

1. Clone the repository.
2. `cd` into it.
3. Use `sutram.exe` from the repository root directly.

**If you use Route B, tests 1, 3 and 4 cannot be run — mark them "not run" and continue.**

---

## 3. The tests

**For each test: run it, compare against the expected result, and record pass / fail / unexpected.**

**Where a test gives a program, write it to a file exactly as shown, including indentation. Sutram uses indentation, not braces, for blocks.**

---

### Test 1 — installer runs

**Run:** `Sutram-Setup.exe`

**Expected:** installs without an error dialog.

**Record:** ✅ / ❌ / ⚠️ plus any dialog text.

---

### Test 2 — compiler version after install

**Run:** `sutram --version`

**Expected:** `Sutram 1.0 (v297) - sampurna sutra`

**If it prints `v243`,** record ⚠️ and note it — that is the known payload issue.

**Record:** the exact output string.

---

### Test 3 — compiler is on PATH

**Run:** open a new Command Prompt, then `sutram --version` again.

**Expected:** the same version string as test 2.

**Record:** ✅ / ❌.

---

### Test 4 — uninstall

**Run:** uninstall Sutram from Settings → Apps.

**Expected:** removes cleanly. Afterwards `sutram --version` should fail with "not recognised".

**Record:** ✅ / ❌. **Reinstall afterwards if you need it for the remaining tests.**

---

### Test 5 — hello world

**Write `hello.sm`:**

```sutram
mukhya() {
    likha("namaste")
}
```

**Run:** `sutram hello.sm hello.exe`
**Then:** `hello.exe`

**Expected:** `namaste`

**Record:** ✅ / ❌ plus actual output.

---

### Test 6 — compile a missing file

**Run:** `sutram does_not_exist.sm out.exe`

**Expected:** a Sanskrit error message, not a crash or a silent success.

**Record:** the exact message.

---

### Test 7 — string equality and inequality

**Write `str1.sm`:**

```sutram
mukhya() {
    vitti s = "ab"
    likha("eq: ", s asti "ab")
    likha("ne: ", s nasti "cd")
}
```

**Expected:**
```
eq: 1
ne: 1
```

**Record:** ✅ / ❌ plus actual output.

**Note:** `asti` is the word for `==` and `nasti` is `!=`. **If this prints `eq: 0`, that is a serious regression — report it prominently.**

---

### Test 8 — string ordering

**Write `str2.sm`:**

```sutram
mukhya() {
    vitti s = "ab"
    likha("lt: ", s < "b")
    likha("gt: ", "b" < s)
}
```

**Expected:**
```
lt: 1
gt: 0
```

**Record:** ✅ / ❌ plus actual output.

---

### Test 9 — string concatenation

**Write `str3.sm`:**

```sutram
mukhya() {
    vitti u = "ab" + "cd"
    likha(u)
}
```

**Expected:** `abcd`

**Record:** ✅ / ❌ plus actual output.

---

### Test 10 — `likha` with three arguments

**Write `likha3.sm`:**

```sutram
mukhya() {
    vitti a = 5
    vitti b = 7
    likha(a, " ", b)
}
```

**Expected:** `5 7`

**Record:** ✅ / ❌ plus actual output.

---

### Test 11 — the new `kosh` names

**Write `kosh1.sm`:**

```sutram
mukhya() {
    kosh k[1]
    kosh_kship(k, 10)
    kosh_kship(k, 20)
    likha("gan=", kosh_gan(k))
    likha("hri=", kosh_hri(k))
    likha("rikt=", kosh_rikt(k))
}
```

**Expected:**
```
gan=2
hri=20
rikt=0
```

**Record:** ✅ / ❌ plus actual output.

---

### Test 12 — old `kosh` names still work

**Write `kosh2.sm`:**

```sutram
mukhya() {
    kosh k[1]
    kosh_push(k, 1)
    likha(kosh_len(k))
}
```

**Expected:** prints `1`, **and** prints a deprecation notice mentioning `kosh_kship`.

**Record:** stdout, and any text on stderr. **Separate the two — this test is about whether the notice goes to stderr rather than stdout.**

---

### Test 13 — division by zero

**Write `divzero.sm`:**

```sutram
mukhya() {
    vitti a = 5
    vitti b = 0
    likha(a / b)
}
```

**Expected:** an error beginning `Sutram truti [E_SHUNYA_BHAJAN]:`, in Sanskrit, with a line number. Exit code 1.

**Record:** the **exact full text** of the message, and the exit code.

**This test matters:** it exercises a long error message, which used to crash the compiler on literals of 127 bytes or more. **If the message is truncated, garbled, or the program crashes, report it prominently.**

---

### Test 14 — decimal loop bound

**Write `loopbound.sm`:**

```sutram
mukhya() {
    chakra i = 0 tak 3.0 {
        likha(i)
    }
}
```

**Expected:** refused with `E_CHAKRA_DASHAM`. **It must not hang and must not print numbers.**

**Record:** the message. **If it hangs for more than 5 seconds, kill it and record ❌ HANG — that is a serious defect.**

---

### Test 15 — integer overflow refusal

**Write `overflow.sm`:**

```sutram
yoj ganit
mukhya() {
    likha(dvigun(9223372036854775807))
}
```

**Expected:** `Sutram truti [E_ATIPRAVAH]: dvigun: ...` naming the valid range.

**Record:** the exact message.

---

### Test 16 — the same function on legitimate input

**Write `ok.sm`:**

```sutram
yoj ganit
mukhya() {
    likha(dvigun(5))
}
```

**Expected:** `10`

**Record:** ✅ / ❌.

---

### Test 17 — a different refusal code

**Write `abscase.sm`:**

```sutram
yoj ganit
mukhya() {
    likha(nirapeksh_mulya(-9223372036854775808))
}
```

**Expected:** `E_PHALA_SEEMA` — a **different** code from test 15.

**Record:** the exact message, and confirm the code differs from test 15.

---

### Test 18 — memory reporting

**Write `mem1.sm`:**

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

**Expected:**
```
start=0
in=4096
after=0
```

**Record:** ✅ / ❌ plus actual output.

---

### Test 19 — memory budget refuses

**Write `mem2.sm`:**

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

**Expected:** refused with `E_PARIMITA`.

**Record:** the message.

---

### Test 20 — withdrawn function

**Write `withdrawn.sm`:**

```sutram
yoj sankhyiki
mukhya() {
    kosh a[2]
    likha(sankhya_bindu(a, a))
}
```

**Expected:** refused with `E_PRATYAHRITA`, and the message should name an alternative.

**Record:** the exact message. **If it compiles and runs, that is a serious defect — report it prominently.**

---

### Test 21 — Devanagari in output

**Write `deva.sm`:**

```sutram
mukhya() {
    likha("नमस्ते")
}
```

**Expected:** prints `नमस्ते` correctly.

**Record:** ✅ / ❌ plus a screenshot or a copy of what appeared. **If it prints boxes or question marks, record ⚠️ and note your console font.**

---

### Test 22 — the IDE opens

**Launch the IDE** from the Start Menu (or wherever the installer placed it).

**Expected:** a window opens.

**Record:** ✅ / ❌. **Take a screenshot.**

---

### Test 23 — the IDE compiles and runs

**In the IDE:** type the hello-world program from test 5 and run it.

**Expected:** output appears in the IDE.

**Record:** ✅ / ❌ plus a screenshot.

---

### Test 24 — the IDE shows an error in Sanskrit

**In the IDE:** type the division-by-zero program from test 13 and run it.

**Expected:** the Sanskrit error appears in the IDE, and Devanagari renders correctly.

**Record:** ✅ / ❌ plus a screenshot.

---

## 4. What to report back

**Return a table like this, one row per test:**

| Test | Result | Actual output / notes |
|---|---|---|
| 1 — installer | ✅ | |
| 2 — version | ⚠️ | `Sutram 1.0 (v243)` |
| … | … | |

**Plus:**

1. **The exact `sutram --version` string.**
2. **The exact text of any Sanskrit error message you saw** — copy it verbatim, do not paraphrase.
3. **Screenshots of the IDE** (tests 22–24). **These are the most valuable thing in the report, because nobody has seen the IDE.**
4. **Your Windows version and console** (CMD, PowerShell, or Windows Terminal).
5. **Anything that surprised you**, even if it passed. **Especially that.**

---

## 5. Rules for the tester

- **Do not modify the repository.** Read and run only.
- **Do not report a known issue from section 1 as a new finding.**
- **If a test hangs, kill it after 5 seconds and record it as a hang.** Do not wait.
- **Report exactly what happened, not what should have happened.** If the output looks wrong but you are unsure, record it as ⚠️ and paste it — a human will judge.
- **If a test cannot be run** (for example Route B skips the installer), mark it "not run" rather than guessing.

---

## 6. Why each test is here

**Short version, so you can judge the severity of a failure.**

| Group | What it protects |
|---|---|
| **Tests 1–4** | Whether a student can install this at all. **The installer's payload has been stale before.** |
| **Tests 5–6** | Whether the compiler runs on Windows at all. |
| **Tests 7–10** | **String operations were broken until recently** — `"ab" == "ab"` was false. These confirm the fix reaches Windows. |
| **Tests 11–12** | The Sanskrit renames, and that old programs still work. |
| **Test 13** | **A long error message used to crash the compiler** (literals of 127+ bytes, present since v244). This is the test for that. |
| **Test 14** | A decimal loop bound once ran 4.6 × 10¹⁸ times. It must refuse. |
| **Tests 15–17** | Library functions that used to return wrong numbers now refuse, with distinct codes for distinct causes. |
| **Tests 18–19** | Memory reporting and the budget refusal. |
| **Test 20** | A broken function is withdrawn, not silently wrong. |
| **Test 21** | Devanagari renders. |
| **Tests 22–24** | **The IDE has never been tested by an automated run.** |
