# Sutram — Windows round: diagnose eight failures

**You are working on a Windows machine. This is a diagnostic round, not a build round.**

**Read this whole file before running anything.**

---

## 0. What happened before you

**A Windows build already exists and was tested. The result was:**

```
{'FAIL': 8, 'NO_EXPECTATION': 3, 'PASS': 305, 'SKIP_SIDE_EFFECT_OR_INLINE_ASM': 3}
```

**Eight tests fail on Windows. They pass on Linux. That is the whole question.**

**The evidence is already in the repository:**

- `Windows-to-Sarvam/win-v297-2026-11-03/native-cases.json` — **267 KB, per-case results**
- `Windows-to-Sarvam/win-v297-2026-11-03/native-tests.log` — the summary
- `Windows-to-Sarvam/win-v297-2026-11-03/build-success.log` — the build
- `Windows-to-Sarvam/win-v297-2026-11-03/payload-check.log` — the installer verification
- `Sutram-Setup-v297.exe` — **1,946,102 bytes, SHA-256 `fabece5f0945c938a45f3c379fe5d7dd816647e23a6fe60d5f19aa00859f3b65`**

---

## 1. The eight failing tests

| Test | What it covers |
|---|---|
| `303_r103_parimita_refuses` | the memory budget refusal |
| `317_r107_parimana` | `parimana()` memory reporting |
| `318_r108_parimana_moves` | memory moving as allocations happen |
| `322_r111_new_names` | the new Sanskrit builtin names |
| `323_r111_old_names` | old names working as aliases |
| `288_r86_kosh_alias_moves` | the `kosh` alias |
| `29_nishkriya` | an older test |
| `220_hindi_parse_error` | a pack parse error |

**Five of the eight are this week's work.** **That is why this matters.**

---

## 2. Your job, in one sentence

**For each of the eight, determine which of these three it is:**

- **A COMPILER failure** — the compiler produced wrong code, crashed, or refused something it should accept on Windows.
- **An OUTPUT mismatch** — it compiled and ran, but printed something different from the golden.
- **A HARNESS assumption** — the test itself assumes Linux behaviour (exact memory numbers, exact paths, exact exit codes) and the language is fine.

**That distinction is the entire deliverable.** **Do not fix anything until you have classified all eight.**

---

## 3. How to classify each one

**For each failing test, do this:**

### Step 1 — find the test and its golden

**Tests live in `tests/`.** **Goldens are in `tests/expect/`.** **The test name maps to an example in `examples/`, for example `303_r103_parimita_refuses` → `examples/303_*.sm`.**

**Read both: the `.sm` program and the expected output.**

### Step 2 — read the actual result from `native-cases.json`

**Find the case by name. It should carry the actual stdout, stderr and exit code.**

**If the JSON does not have the detail, re-run the single test yourself (see section 4).**

### Step 3 — decide which of the three it is

**Ask these in order:**

1. **Did it compile at all?** If the compiler errored, it is a **compiler failure**.
2. **Did it run?** If it crashed or hung, it is a **compiler failure**.
3. **Did it produce output?** If it produced output but different from the golden, compare them line by line:
   - **If the difference is a number that depends on memory or the OS** → **harness assumption**.
   - **If the difference is text the compiler should have printed** → **compiler failure**.
4. **If the difference is only whitespace, line endings, or a path** → **harness assumption**.

### Step 4 — and for each, say what would fix it

**One line: "fix the compiler" or "fix the golden" or "make the test conditional on the platform".**

---

## 4. Re-running a single test

**From the repository root on Windows:**

```
sutram.exe examples\303_*.sm out.exe
out.exe
echo %ERRORLEVEL%
```

**Compare against the golden in `tests\expect\`.**

**For the pack test (`220_hindi_parse_error`):**

```
sutram.exe --lang hindi examples\220_*.sm out.exe
```

---

## 5. What I expect, and I may be wrong

**My guesses, so you can confirm or refute them:**

- **`317` and `318` (`parimana`)** — **likely harness.** **Memory accounting on Windows will not match Linux byte for byte.** **If the golden asserts an exact number, it is Linux-shaped.**
- **`303` (`parimita`)** — **the question is whether the golden asserts an exact allocation count.** **On Linux a 1 MB budget admits exactly 16,384 × 64-byte allocations.** **If Windows differs, the golden is Linux-shaped. If the refusal itself failed, that is a real defect.**
- **`322` and `323` (the renames)** — **these worry me most.** **A rename should not care about the platform.** **If it fails only on Windows, either the alias table is emitted differently for PE, or the golden compares message text that differs.**
- **`29_nishkriya` and `220_hindi_parse_error`** — **older tests. Were they ever run on Windows before?**

**Confirm or refute each of these with evidence.** **A guess refuted with evidence is worth more than a guess confirmed.**

---

## 6. What to push back to the repository

**When you are done, commit to the repository under `Windows-to-Sarvam/`:**

**A folder named `win-diag-<date>/` containing:**

1. **`DIAGNOSIS.md`** — the table below, filled in.
2. **Any log files you produced.**
3. **The exact command lines you ran.**

**The table:**

| Test | Class (compiler / output / harness) | Evidence | Fix |
|---|---|---|---|
| `303_r103_parimita_refuses` | | | |
| `317_r107_parimana` | | | |
| `318_r108_parimana_moves` | | | |
| `322_r111_new_names` | | | |
| `323_r111_old_names` | | | |
| `288_r86_kosh_alias_moves` | | | |
| `29_nishkriya` | | | |
| `220_hindi_parse_error` | | | |

**Plus one paragraph: which of the eight share a cause?** **If five share one bug, this is one fix, not five.**

---

## 7. Rules

- **Do not modify the compiler or the library.** **This is diagnosis.**
- **Do not change a golden to make a test pass.** **If a golden is wrong, say so in the report — do not quietly fix it.**
- **Do not report a known issue as new.** **Known: the linker still says `Sutram Error`; `patra_asti` and `sankhya_bindu` are withdrawn.**
- **If you cannot classify one, say "unclassified" and give the raw evidence.** **That is better than a wrong classification.**
- **Paste actual output, not summaries.** **A human will read this.**

---

## 8. Why this round is diagnosis only

**This project has 62 Linux gates and has never run an automated Windows gate.** **Eight failures appeared the first time it did.**

**If we fix them without knowing which are real, we will "fix" a test that was correct and leave a compiler defect in place.** **The classification is the work.**
