# Sutram v309 — verify the arithmetic fix, the OOM fix, and the deterministic payload

**Copy this whole file to the Windows AI.**

**Two of these were never verified on Windows, and one is a fix you have been waiting on since v306.**

---

## 0. What is outstanding, and why it is in this round

**Three things from earlier rounds are still unverified or unresolved. They are Tasks B, C and D below.**

| Outstanding | Since | Why it matters |
|---|---|---|
| **The OOM stack fix** | **v308** | **You measured the boundary on v307 — 448 sometimes, 480 and 512 always crashed. v308 changed how commit is reserved. Nobody has run it.** |
| **Deterministic payload bytes** | **v307** | **153 payload files differed between a Windows build and a Linux build because `.gitattributes` does not force LF for `*.md`. That is what made the installer look tampered-with to Acronis.** |
| **Recovery at worse moments** | **v307** | **You proved recovery works when killed after 17 files. Nobody has tried killing it before the first copy, or during the journal write.** |

**And Task A is new: v309 refuses a slice in arithmetic, and your own `wrapper-comparison/results.json` recorded the case that proves it was needed.**

---

## 1. Task A — the arithmetic refusal, which your own evidence prompted

**Your `win-v307-fixes-2026-11-06/wrapper-comparison/results.json` recorded this on v308: both `keep(k[0:1] + zero)` and `keep(k[0:1] ^ zero)` compiled, exited 0, and printed **7 then 99** after the `kosh` grew.**

**That was an outdated element read, and it was the last correctness defect in the language.**

**v309 refuses it.**

### A1 — the two programs that read the old element

**Run both again on v309.** **Expected: a compile-time refusal with `E_VIBHAG_ANKA` or `E_KOSH_GANIT`, exit non-zero, no output file.**

**If either still compiles and prints `7` then `99`, the fix did not work — say so plainly.**

### A2 — and the broader refusal

**Each of these should be refused:**

```sutram
mukhya() { kosh k[1]  kosh_kship(k, 7)  likha(k[0:1] + 0) }
```
```sutram
mukhya() { kosh k[1]  kosh_kship(k, 7)  yadi (k[0:1]) { likha(1) } }
```
```sutram
mukhya() { kosh k[1]  kosh_kship(k, 7)  likha(k[0:1]) }
```
```sutram
mukhya() { kosh k[1]  kosh_kship(k, 7)  vitti i = k[0:1]  likha(i) }
```

**Expected: all four refused.** **Record the exact message for each.**

**Note the third one — `likha(k[0:1])` directly.** **On v308 that printed an address. If it still does, say so: it is the simplest form of the defect and the one a student would meet first.**

### A3 — and that legitimate slice use still works

**`pankti_gan` takes a slice.** **Confirm it still does:**

```sutram
mukhya() {
    kosh k[1]
    kosh_kship(k, 1)
    kosh_kship(k, 2)
    kosh_kship(k, 3)
    likha(pankti_gan(k[0:2]))
}
```

**Expected: `2`.** **If this is now refused, the fix went too far — say so.**

---

## 2. Task B — the OOM stack fix, unverified since v308

**This is the one that matters most.** **You measured it on v307:**

```
448 MiB  -> clean, FD, FD
480 MiB  -> FD, FD, FD
512 MiB  -> FD, FD, FD
544 MiB  -> clean, clean, clean
```

**v308 reserves 64 KiB of commit at start and releases it before writing the message, so teardown always has room.**

**Claude's own limitation: *"Wine cannot impose a commit limit."*** **Only you can check this.**

### B1 — the same boundary, three runs each

```
448, 480, 512, 544, 576, 608, 640 MiB
```

**Expected at every failing limit: `Sutram truti: smritih na labdha`, exit 1, no `0xC00000FD`.**

### B2 — and the `mandapa` case, ten times

**Your `A3-mandapa.sm` at 64 MiB.** **On v307 it was 10 out of 10 `FD`.**

**Expected: 10 clean refusals.**

### B3 — and the page-touch control

**`A3-nirmmita-touch-pages.sm` at 64 MiB.** **Passed on v307; confirm it still does.**

### B4 — and the completeness check

**For every run, record whether stderr is exactly 32 bytes ending in LF.**

**A complete message plus exit 1 is a pass.** **A complete message plus `FD` is a failure — that is the exact distinction you established.**

---

## 3. Task C — the deterministic payload

**`.gitattributes` forces LF for `*.sm`, `*.smlib`, `*.asm`, `*.inc`, `*.lang`, `*.sandesh`, `*.sffi` — but not `*.md`.**

**153 payload files differed between builds because of it.**

**Claude is adding the rule. This task checks whether it worked.**

### C1 — build or obtain the payload from a Windows checkout

**Record the SHA-256 of three text files as they exist in your Windows checkout:**

```
certutil -hashfile docs\LANGUAGE-REFERENCE.md SHA256
certutil -hashfile lang\sanskrit.lang SHA256
certutil -hashfile README.md SHA256
```

**Then compare against the manifest's recorded hash for each.**

**Expected: all three match.** **If any differ, the `.gitattributes` rule is incomplete — say which file and what the difference is.**

### C2 — and whether the file has CRLF

**A one-line PowerShell check:**

```powershell
(Get-Content -Raw docs\LANGUAGE-REFERENCE.md) -match "`r`n"
```

**Expected: `False` if the rule worked.** **`True` means the file still has CRLF on checkout.**

---

## 4. Task D — recovery at worse moments

**You proved recovery works when the install is killed after 17 files.** **Three moments nobody has tried:**

### D1 — kill it before the first file is copied

**Start the install and stop it within the first second.**

```
Stop-Process -Name "Sutram*" -Force
```

**Then run it again.** **Expected: it completes normally.** **Record what it says about the previous attempt.**

### D2 — kill it after the last file but before the record is cleared

**Harder to time. If the log shows the last file copied, stop it immediately.**

**Then run it again.** **Expected: it recognises completion rather than re-copying everything.** **Record whether it re-copies or recognises.**

**If you cannot time this, say so — it is not a failure to skip it.**

### D3 — and the safeguard question

**1. Start an install and interrupt it partway.**
**2. Before retrying, edit a file inside the target folder by hand — add a line to a `.md` file.**
**3. Then run the installer again.**

**Expected: your edited file is preserved, or you are told it will be overwritten.**

**If it is silently overwritten, that is a defect — an edited file is not the installer's file.**

---

## 5. Task E — identity and the suite

**In a new shell:**

```
where sutram
sutram --version
```

**Expected: one canonical path, `Sutram 1.0 (v309) - sampurna sutra`.**

**Then run the native suite.** **Your last run was 322 PASS, no FAIL.**

**Expected: 322 or better, no FAIL, no COMPILE_FAIL.**

---

## 6. What NOT to do

- **Do not report the v306 or v307 passes again.** **They stand.**
- **Do not report an Acronis suspension as a Sutram defect — but do record it, because if the payload is now deterministic it should not happen.**
- **Do not modify the compiler, library, examples, goldens or installer.**
- **Do not claim release acceptance.**
- **If `sutram --version` is not v309 in a new shell, stop and report that first.**

---

## 7. What to commit

**Push to `Windows-to-Sarvam/win-v309-<date>/`:**

1. **`ARITHMETIC.md`** — A1, A2 and A3, with the exact message for each.
2. **`OOM.md`** — the B1 table with three runs each, B2's ten runs, B4's completeness check.
3. **`PAYLOAD.md`** — C1's three hashes against the manifest, C2's CRLF check.
4. **`RECOVERY.md`** — D1, D2 and D3.
5. **Every probe and the exact commands.**

### The tables

**OOM:**

| Limit | Run 1 | Run 2 | Run 3 | stderr 32 bytes + LF? |
|---:|---|---|---|---|
| 448 MiB | | | | |
| 480 MiB | | | | |
| 512 MiB | | | | |
| 544 MiB | | | | |
| 576 MiB | | | | |
| 608 MiB | | | | |
| 640 MiB | | | | |

**Arithmetic:**

| Program | Expected | Actual | Pass? |
|---|---|---|---|
| `keep(k[0:1] + zero)` — the 7/99 case | refusal | | |
| `keep(k[0:1] ^ zero)` — the 7/99 case | refusal | | |
| `likha(k[0:1] + 0)` | refusal | | |
| `yadi (k[0:1])` | refusal | | |
| `likha(k[0:1])` | refusal | | |
| `vitti i = k[0:1]` | refusal | | |
| `pankti_gan(k[0:2])` | **`2`** — must still work | | |

**Payload and recovery:**

| Question | Answer |
|---|---|
| Three text-file hashes match the manifest? | |
| Any of them still CRLF on checkout? | |
| Killed before the first copy: does the retry complete? | |
| Killed after the last file: re-copies or recognises? | |
| Edited file after interruption: preserved or overwritten? | |

---

## 8. Why this round may close it

**Task B is the last unverified fix in the language.** **If the OOM boundary refuses cleanly at every limit, the memory model has no known defect on either platform.**

**Task C removes the trigger that caused four rounds of installer investigation — not by working around a security product, but by making the payload deterministic.**

**And Task A confirms the last correctness defect is refused, using the exact program your own run recorded.**

**Your standard holds: a message followed by a crash is not a refusal, and a pass that prints an address is not a pass.**
