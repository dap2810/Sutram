# Sutram — ROUND-159: the cleanup, measured. Do it.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**The owner has asked for the repository to be reduced.** **This round is the cleanup, with the numbers measured on the current tree.**

---

## What the tree contains

**112 MB, 11,215 files.**

| Type | Files | Size |
|---|---|---|
| **`.json`** | **676** | **30.9 MB** |
| **`.png`** | **330** | **26.0 MB** |
| **`.md`** | **1,569** | **11.3 MB** |
| `.exe` | 7 | 5.0 MB |
| `.log` | 133 | 3.9 MB |
| `.sm` | **3,855** | 3.6 MB |
| `.asm` | 27 | 1.3 MB |

**And `Windows-to-Sarvam` is 67 MB - 60% of the repository.**

---

## WS1 - the four categories to cut, in order of size

### 1. JSON - 30.9 MB across 676 files
**These are machine snapshots and test-case dumps.** **The biggest:**

```
0.8 MB  win-v311-2026-11-07/nesting/results.json
0.8 MB  win-v310-2026-11-07/nesting/results.json
0.6 MB  Claude-to-Sarvam/evidence-r15/proofs/lib-mutant-score.json
0.6 MB  ChatGPT-to-Sarvam/ROUND-184-ENGLISH-INVENTORY.json
0.3 MB  win-v306-2026-11-06/a4-after.json
0.3 MB  win-v306-2026-11-06/before.json
0.3 MB  win-repair-2026-11-06/after.json
0.3 MB  win-v311-2026-11-07/native-cases.json
```

**The rule: if a `RESULTS.md` cites a claim that depends on a number in the JSON, keep the number - as a line in the markdown - and keep the file's SHA-256. The file itself is not needed to verify the claim.**

**A hash plus the number in the report is as verifiable as the 0.8 MB file.**

### 2. PNG - 26 MB across 330 files
**Every screenshot is evidence of something a text description already says.** **"The IDE printed Namaste, Sutram!" is the evidence; the screenshot is corroboration.**

**Keep:** **the screenshots that show something text cannot - the IDE's appearance, the licence page's rendering, the first-run desktop.**
**Delete:** **the ones that show a terminal printing a line the report already quotes.**

**If a `RESULTS.md` links a screenshot, either keep it or replace the link with a line saying the image was pruned and what it showed.**

### 3. `.sm` - 3,855 files, 1,202 duplicate basenames
**1,202 files share a name with another file elsewhere.** **The examples are the canonical copy; a probe copied into three round folders is three copies.**

**Keep one canonical copy of each probe.** **If a round needs its own version because it changed, keep both and say why.**

### 4. `.exe` - 7 files, 5 MB
**`Sutram-Setup.exe` at the root is the package.** **`win-v297-2026-11-03/Sutram-Setup-v297.exe` is a six-version-old copy that cannot be verified against anything current - delete it and record its hash.**

**`sutram.exe`, `win/sutram.exe`, `sutram-link.exe`, `sutram-ide-gui.exe`, `sutram-coff2smo.exe` are the product - keep them.**

---

## WS2 - and the superseded Windows rounds
**Thirteen Windows round folders predate v309 and total 13 MB:**

```
win-v29*, win-v30[0-8]*, win-round*, win-diag-2026-10*,
win-ffi*, win-linker*, win-run*, win-test-2026-10*
```

**These are rounds about versions six or more behind.** **Their conclusions are in the record and their `RESULTS.md` files are cited by later rounds.**

**Keep every `RESULTS.md` and every file it cites.** **Prune the raw evidence - the JSON, the screenshots, the logs - and replace each with a hash line.**

**And say in the report how many folders were pruned and what remained.**

---

## WS3 - and the honest statement
**Git does not shrink when files are deleted.** **The clone stays 112 MB unless history is rewritten, and that is destructive.**

**So this round reduces the working tree, not the clone.** **The gain is a repository a person can search: 11,215 files where 60% are machine snapshots from one platform.**

**State that plainly in the report.** **Do not claim the repository got smaller.**

**Unless: is a history rewrite now worth considering?** **Answer yes or no, and say what it would cost.** **The owner has a clone on Windows and is working from it, so the answer matters.**

---

## WS4 - and the docs, which come first
**ROUND-157 and ROUND-158 are still the priority: the memory chapter in English and Sanskrit, and the doc-currency gate.**

**If both rounds are done, this one follows.** **If they are not, do them first and say so.**

**A clean repository with a book that does not teach the memory model is a tidy empty room.**
