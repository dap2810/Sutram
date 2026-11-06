# Sutram v303 — Windows release-candidate verification

**Copy this whole file to the Windows AI. This is the release candidate run.**

---

## 0. What changed since your last round

**You tested v297. Four versions have landed since, and every one matters:**

| Version | What changed |
|---|---|
| **v298** | `anka_akshar` and `vartani_sandhi` fixed — the two defects you found |
| **v299** | Windows memory merged: `parimana()` returns real bytes, `mandapa parimita` enforces, the `kosh` alias holds |
| **v300** | The Windows 1 GiB commit fixed — it was the arena, not the reservation |
| **v301** | The `kosh_vars` type tracking fixed — 8 defect instances (3 segfaults, 5 silent over-reads) closed |
| **v302** | **The descriptor built.** `kosh` is a 24-byte header that never moves; growth moves elements and every name sees it |
| **v303** | **Three descriptor defects found by reading, fixed** — one SIGSEGV, one silent memory overwrite, one wrong `parimana()`. The installer now carries the compiler |

**Linux: 68 gates, 0 failing. Suite 327. The one NOT-RUN gate is Windows execution — which is this round.**

---

## 1. What this round is for

**Linux passes everything. The installer carries v303. Nobody has run v303 on Windows.**

**Your job: install it, run it, and say whether it works.**

**This is the last gate.**

---

## 2. Priority 1 — install and verify the version

**1. Build or download the installer from `main`.**
**2. Run `Sutram-Setup.exe`.**
**3. Open a NEW Command Prompt.**
**4. Run `sutram --version`.**

**Expected: `Sutram 1.0 (v303) - sampurna sutra`**

**This is the check that has failed for weeks** — the payload used to be v243 while the source was v300+. **If it says v303, the release blocker is closed.**

**Record: the exact version string, and the SHA-256 of the installed binary.**

---

## 3. Priority 2 — the memory model, which is new since your last run

**This is the biggest change since v297 and the most likely place for a Windows-specific defect.**

### Test M1 — the alias follows growth

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

**Expected: `a0=99 k0=99`** — one object, two names, growth invisible.

**On v297 this would have printed `a0=41`.**

### Test M2 — many collections

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

**On v297 the 16th `kosh` would have segfaulted.**

### Test M3 — out of memory is a message

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

**Not a crash. Not a hang. If it hangs, kill it after 30 seconds and record a hang.**

### Test M4 — reporting

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

**Expected: `start=0`, `in=` a non-zero number, `after=0`.**

### Test M5 — the budget

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

---

## 4. Priority 3 — the two defects you found, confirmed fixed

**These were your findings. Confirm they are closed on Windows.**

### Test D1 — `anka_akshar`

```sutram
mukhya() {
    vitti c = anka_akshar(66)
    shabda(c)
}
```

**Expected: `B`** (was `P` on v297)

**Also: `anka_akshar(97)` must give `a`.**

### Test D2 — `vartani_sandhi`

```sutram
mukhya() {
    vitti s = "ab"
    vitti t = "cd"
    vitti u = vartani_sandhi(s, t)
    shabda(u)
    likha("orig: ", s)
}
```

**Expected: either `abcd` with `orig: ab`, or a refusal with `E_VARTANI_STHIRA`.**

**Not a crash. On v297 this was an access violation.**

---

## 5. Priority 4 — the full native suite

**Run the suite the way you ran it before and report the counts.**

**Your last run was 312 PASS / 0 FAIL on the v297 branch.**

**Expected now: the same or better, with the new descriptor tests included.**

**Record: the exact counts, and any test name that fails.**

---

## 6. Priority 5 — the IDE

**Launch the IDE and run a program through it.**

**And check the known defect: open a file larger than about 64 KiB.**

**What should happen: the IDE refuses it AND clears the previous output.**

**What did happen on v297: it refused the file but left the PREVIOUS program's output on screen — so a student sees output that is not theirs.**

**Record: does it still do that?** **If yes, that is a real usability defect and it needs fixing before students use this.**

---

## 7. What to commit

**Push to `Windows-to-Sarvam/win-v303-<date>/`:**

1. **`RESULTS.md`** — the table below, filled in.
2. **Every `.sm` probe you wrote.**
3. **The exact version string and the SHA-256 of the installed binary.**
4. **The full native suite counts.**
5. **A screenshot of the IDE.**
6. **The exact commands you ran.**

### The table

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| Installer runs | no error | | |
| `sutram --version` | v303 | | |
| M1 alias across growth | `a0=99 k0=99` | | |
| M2 20,000 koshes | `sum=20000` | | |
| M3 out of memory | Sanskrit message, exit 1 | | |
| M4 `parimana()` | non-zero inside block | | |
| M5 budget | `E_PARIMITA` | | |
| D1 `anka_akshar(66)` | `B` | | |
| D2 `vartani_sandhi` | `abcd` or refusal | | |
| Native suite | same or better than 312/0 | | |
| IDE runs a program | output appears | | |
| IDE 64 KiB file | refuses AND clears output | | |

---

## 8. Rules

- **Report what actually happened.** **A failed test recorded is worth more than a pass claimed.**
- **If something hangs, kill it after 30 seconds and record a hang.**
- **Do not modify the compiler, library, examples or goldens.** **Report only.**
- **If the version string is not v303, stop and report it** — that is the release blocker and nothing else matters until it is known.
- **Take a screenshot of the IDE.** **It is the one thing nobody has ever seen working end to end.**

---

## 9. Why this round matters

**This is the release candidate.** **Linux passes 68 gates with zero failures. The installer carries the current compiler. The memory model survived two independent attacks and three defects found by reading.**

**The one thing nobody can check from Linux is whether it works on the machine a student will actually use.**

**That is what this round is.**
