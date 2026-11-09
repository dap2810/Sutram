# Sutram — Windows round: clean up, test v305 directly, then re-test the installer

**Copy this whole file to the Windows AI.**

---

## 0. What your last run found, and why it was the right call

**You stopped at the version check because the brief told you to.** **That was correct.**

**You found two defects no Linux test could catch:**

1. **Two installations coexist and the older one wins on PATH** — a fresh `cmd.exe` resolving bare `sutram` gives `Sutram 1.4.0` from `AppData\Local\Sutram\`, not v303 from `AppData\Local\Programs\Sutram\`.
2. **The installer does not complete** — its log ends at `Copying Sutram files.` and PowerShell has to be closed by hand.

**And you said plainly: *"These observations do not constitute testing of v305."*** **That sentence is why the rest of your report can be trusted.**

**The installer is being fixed. This round does three things that do not wait for it.**

---

## 1. What has changed since you tested v303

| Version | Change |
|---|---|
| **v304** | A `kosh` parameter now grows and the caller sees it — the descriptor makes propagation possible. A slice of the same `kosh` is refused. |
| **v305** | The omitted-upper-bound slice retained the old endpoint — fixed. |

**Release candidate state on Linux:** **68 gates, 0 failing. Suite 327. Installer payload v305 with a matching SHA-256 and `--self-test` exit 0 under Wine.**

**The one gate that has never passed is Windows execution. That is still this round.**

---

## 2. Part A — clean up, so the next test means something

**Do this first, because a test run on a machine with two installations proves nothing.**

### A1 — document what is there now

```
where sutram
sutram --version
echo %PATH%
```

**Record the full PATH string, and every `sutram.exe` it finds, with the version each one reports.**

**Also record which of those paths is machine-level and which is user-level:**

```
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path
reg query "HKCU\Environment" /v Path
```

**This tells us why the older one wins — it is either earlier in the list, or machine-level while the new one is user-level.**

### A2 — remove the old installation

**Remove `%USERPROFILE%\AppData\Local\Sutram\` — the v1.4.0 one.**

**Use its own uninstaller if it has one.** **If not, delete the folder and remove its PATH entry by hand.**

**Record what you did.**

### A3 — confirm only one remains

```
where sutram
sutram --version
```

**Expected: exactly one path.** **If two remain, stop and report.**

**Do not install v305 yet.** **Part B tests it without installing.**

---

## 3. Part B — test v305 directly, without the installer

**This is the part that gets us a real answer today.** **The installer is broken; the compiler is not.**

**Take `win/sutram.exe` from the repository at `main` and use it directly.** **No installation, no PATH, no wizard.**

**Record its SHA-256 and its `--version` output first.**

### The tests

**Run each, and record the exact output.**

### B1 — the alias across growth

```sutram
mukhya() {
    kosh k[1]
    kosh_kship(k, 41)
    vitti a = k
    chakra i = 1 tak 50000 {
        kosh_kship(k, i)
    }
    k[0] = 99
    likha("a0=", a[0], " k0=", k[0])
}
```

**Expected: `a0=99 k0=99`**

**On v297 this printed `a0=41`.**

### B2 — many collections

```sutram
mukhya() {
    vitti s = 0
    chakra i = 1 tak 20000 {
        kosh k[1]
        kosh_kship(k, 1)
        s = s + k[0]
    }
    likha("sum=", s)
}
```

**Expected: `sum=20000`**

**On v297 the 16th `kosh` segfaulted.**

### B3 — out of memory is a message

```sutram
mukhya() {
    kosh k[1]
    chakra i = 1 tak 100000000 {
        kosh_kship(k, i)
    }
    likha(kosh_gan(k))
}
```

**Expected: a Sanskrit error beginning `Sutram truti: kosh vardhayitum smritih na labdha`, exit 1.**

**If it hangs, kill it after 60 seconds and record a hang.**

### B4 — reporting

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

**Expected: `start=0`, `in=4096`, `after=0`**

### B5 — the budget

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

**Expected: refused with `E_PARIMITA`, exit 1.**

### B6 — a `kosh` parameter grows (new in v304)

```sutram
prakriya badha(kosh k) {
    kosh_kship(k, 99)
    nivartanam 0
}

mukhya() {
    kosh k[1]
    kosh_kship(k, 1)
    badha(k)
    likha("gan=", kosh_gan(k))
}
```

**Expected: `gan=2`** — the caller sees the growth.

**If it refuses, record the exact message.** **A refusal here is safe but it means the feature did not reach Windows.**

### B7 — a slice, then growth (the v305 fix)

```sutram
mukhya() {
    kosh k[1]
    kosh_kship(k, 10)
    kosh_kship(k, 20)
    kosh_kship(k, 30)
    vitti s = k[1 tak]
    kosh_kship(k, 40)
    kosh_kship(k, 50)
    likha("slice_gan=", kosh_gan(s))
}
```

**Expected: either a refusal, or a slice length that is correct.** **A slice that silently keeps the old endpoint is the v305 defect.**

**Record what it prints. If it crashes, that is the v303 S1 defect and it matters most.**

### B8 — the two builtins you found

```sutram
mukhya() {
    vitti c = anka_akshar(66)
    shabda(c)
}
```

**Expected: `B`**

### B9 — the full native suite

**Run the suite the way you ran it before.** **Your last full run was 312 PASS / 0 FAIL.**

**Record the counts and any failing test name.**

---

## 4. Part C — the IDE

**Launch the IDE from the current build and run one program through it.**

**Then check the known defect: open a file larger than about 64 KiB.**

**What should happen: the IDE refuses it AND clears the previous output.**

**What happened on v297: it refused the file but left the PREVIOUS program's output on screen — so a student sees output that is not theirs.**

**Record: does it still do that?**

**Take a screenshot.**

---

## 5. What NOT to do

- **Do not install v305 through the wizard.** **It is being fixed.** **Part B deliberately avoids it.**
- **Do not modify the compiler, library, examples or goldens.**
- **Do not report a known issue as new.** **Known: the linker still says `Sutram Error`; `patra_asti` and `sankhya_bindu` are withdrawn; the IDE 64 KiB limit is documented but unfixed.**
- **Do not claim v305 is release-accepted.** **This is a compiler test, not an installer acceptance.**

---

## 6. What to commit

**Push to `Windows-to-Sarvam/win-v305-<date>/`:**

1. **`RESULTS.md`** — the table below, filled in.
2. **`ENVIRONMENT.md`** — the PATH audit from Part A, before and after cleanup.
3. **Every `.sm` probe you wrote.**
4. **The SHA-256 and `--version` output of the compiler you tested.**
5. **The suite counts.**
6. **A screenshot of the IDE.**
7. **The exact commands you ran.**

### The table

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A1 PATH audit | recorded | | |
| A2 old install removed | one remains | | |
| B1 alias across growth | `a0=99 k0=99` | | |
| B2 20,000 koshes | `sum=20000` | | |
| B3 out of memory | message, exit 1 | | |
| B4 `parimana()` | `in=4096` | | |
| B5 budget | `E_PARIMITA` | | |
| B6 parameter grows | `gan=2` | | |
| B7 slice then growth | refusal or correct length | | |
| B8 `anka_akshar(66)` | `B` | | |
| B9 native suite | same or better than 312/0 | | |
| C IDE runs a program | output appears | | |
| C IDE 64 KiB file | refuses AND clears output | | |

---

## 7. When the fixed installer arrives

**A later round will bring v306 with a fixed installer.** **That round will ask you to:**

- **install it into a clean environment**
- **confirm `sutram --version` in a NEW shell resolves to the new version**
- **confirm the installer exits on its own, with no PowerShell left open**
- **and confirm no second installation exists afterwards**

**Do not attempt that until you are told the installer is fixed.**

---

## 8. Why this round is split this way

**The installer is broken and the compiler is not.** **Testing them separately means the compiler results arrive today instead of waiting for the installer fix.**

**And cleaning up the duplicate installation first means the next installer test actually proves something.** **Right now a green result would be meaningless, because a student typing `sutram` still gets v1.4.0.**
