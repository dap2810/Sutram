# Sutram — Windows diagnostic round: pin the OOM boundary, and map the IDE's stale screen

**Copy this whole file to the Windows AI.**

**This is a diagnostic round. The two defects you found are being fixed. Your job is to give the fixer the numbers it needs to fix them once.**

---

## 0. What your v305 run established

**Ten of thirteen checks passed on native Windows, including everything memory-related:**

| Test | Result |
|---|---|
| Alias across 50,000 growths | `a0=99 k0=99` |
| 20,000 `kosh` objects | `sum=20000` |
| `parimana()` | `in=4096` |
| Budget | `E_PARIMITA` |
| `kosh` parameter grows | `gan=2` |
| `anka_akshar(66)` | `B` |
| IDE runs a program | `Namaste, Sutram!` |

**And two real defects:**

1. **The OOM path crashes** — `0xC0000005` under a 64, 128 or 256 MiB commit limit, instead of the Sanskrit refusal Linux gives.
2. **The IDE leaves a stale screen** — after refusing a large file, the editor still shows the previous file and the output pane still shows the previous program's output.

**And one thing that is not a defect: `79_ayojan_cwd` fails because the Windows harness runs the compiler from a different directory and cannot find `lib/`.** **The compiler is correct.**

---

## 1. Why this round exists

**A fixer who knows "it crashes under 256 MiB" will guess.** **A fixer who knows "it crashes below 512 MiB and refuses above" knows it is an allocation-size check, not a null-pointer check.**

**Both defects are being fixed blind right now.** **These measurements make the fix land once.**

---

## 2. Task A — pin the OOM boundary

**You already know:** 64, 128 and 256 MiB → access violation. **2048 MiB → succeeds.**

**Now find where it changes.**

### A1 — bisect the limit

**Run the same B3 executable under these commit limits, in order, and record exit code and output for each:**

```
384 MiB
512 MiB
640 MiB
768 MiB
1024 MiB
1536 MiB
```

**Stop at the first limit where it succeeds (exit 0).**

**The boundary tells us the size of the allocation the program makes before it fails.** **Record it.**

### A2 — and the same test with a smaller program

**Run this under the same limits:**

```sutram
mukhya() {
    kosh k[1]
    chakra i = 1 tak 2000000 {
        kosh_kship(k, i)
    }
    likha(kosh_gan(k))
}
```

**Two million elements is about 16 MB.** **Record: does it succeed under 64 MiB?** **If yes, the small case is fine and the defect only appears at scale.**

**If it *crashes* under 64 MiB, the defect is not about size at all and that is a much more serious finding.**

### A3 — and does it affect the other allocation paths?

**Test each of these under a 64 MiB commit limit:**

```sutram
mukhya() {
    vitti p = nirmmita(100000000)
    p[0] = 1
    likha(p[0])
}
```

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

**Record for each: refusal, crash, or success.**

**If `nirmmita` and `mandapa` both refuse correctly under the same limit and only `kosh` crashes, then the defect is in the `kosh` growth routine alone — and that is a one-function fix.**

**If all three crash, it is in the shared allocation path and it is one fix for all of them.**

**That distinction is the most valuable thing this round can produce.**

---

## 3. Task B — map the IDE's stale screen

**You found that after refusing a large file, the editor and output pane both still show the previous program.**

**Now find out how far that goes.**

### B1 — what happens on a compile error?

**1. Load `01_hello.sm` and Run it.** **Output appears.**
**2. Now open a file with a syntax error and Run it.**

**Record: does the output pane clear, or does the previous output stay with the error appended below?**

**If the previous output stays, the defect is not about file size — it is about every failure, and that is much broader.**

### B2 — what happens on a runtime error?

**1. Load and Run a program that prints something.**
**2. Then Run one that divides by zero.**

**Record: is the old output still there above the error?**

### B3 — what happens when you click another example after a refusal?

**1. Click `105_block_nesting_capacity` (refused).**
**2. Then click `02_arith.sm` and Run it.**

**Record: does the editor now show `02_arith.sm`, and does the output show its result or the old one?**

**This one matters: if the IDE recovers cleanly on the next click, the defect is a one-screen annoyance. If it stays confused, it is worse.**

### B4 — and take three screenshots

- **after a compile error**
- **after a runtime error**
- **after recovering by clicking a different example**

**The screenshots are worth more than the description.**

---

## 4. Task C — the harness path

**`79_ayojan_cwd` fails with `E_MODULE_MISSING: yoj patra aprapt: ganit` — it cannot find `lib/`.**

**Confirm the cause:** **run that example by hand from the repository root, and then from the harness's working directory.**

```
cd <repo root>
win\sutram.exe examples\79_ayojan_cwd.sm out.exe
```

**Then from wherever the harness ran it.**

**Record both results.** **If it compiles from the repo root and fails elsewhere, the harness is the only thing to fix and the compiler is innocent.**

---

## 5. What NOT to do

- **Do not test v306.** **It does not exist yet. This round is diagnostics on v305.**
- **Do not attempt the installer.** **It is being fixed.**
- **Do not modify the compiler, library, examples or goldens.**
- **Do not report the two known defects as new findings.** **They are known; this round measures them.**

---

## 6. What to commit

**Push to `Windows-to-Sarvam/win-diag-v305-<date>/`:**

1. **`OOM.md`** — the bisect table from Task A, with the boundary named.
2. **`IDE.md`** — the four IDE scenarios from Task B, with screenshots.
3. **`HARNESS.md`** — the two working-directory runs from Task C.
4. **Every `.sm` probe.**
5. **The exact commit limits and commands used.**

### The OOM table

| Commit limit | B3 exit | B3 output | 2M elements | `nirmmita` | `mandapa` |
|---:|---|---|---|---|---|
| 64 MiB | | | | | |
| 128 MiB | | | | | |
| 256 MiB | | | | | |
| 384 MiB | | | | | |
| 512 MiB | | | | | |
| 768 MiB | | | | | |
| 1024 MiB | | | | | |
| 2048 MiB | | | | | |

---

## 7. Why this round is worth doing

**The OOM defect is being fixed by reading code, and reading can miss the case that matters.** **Your boundary measurement tells the fixer whether it is checking a return value at all, or whether the check exists and tests the wrong thing.**

**And the IDE: if the stale screen happens on every failure rather than only on size, the fix is in a different place entirely.**

**Two measurements, and both change what gets built.**
