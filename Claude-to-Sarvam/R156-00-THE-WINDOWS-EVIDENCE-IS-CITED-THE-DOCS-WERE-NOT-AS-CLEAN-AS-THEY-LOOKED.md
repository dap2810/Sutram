# R156-00 — The audit. Of 4,424 files in the Windows round folders, 4,365 are cited: by name, by a pattern, in a report's words, or by the script that made them. The other 59 (2.0 MB) include the raw output of the 32/32 out-of-memory and 7/7 arithmetic results, which are cited by the command that produced them, so I kept them and list them with their hashes. The v297 installer is gone; its SHA-256 and a note are in its place. The docs were not as clean as they looked: four living documents called a page last true at v258 "the authoritative open list", the language reference's status box was still at v300, and the release notes did not state the shipping condition. All fixed. The prune makes the tree 1.9 MB smaller and the clone 0 bytes smaller.

## Release line

Shared with R155-00, the same commit:

```
gates: 78 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
Sutram 1.0 (v315) - sampurna sutra      (compiler unchanged; this round changes no code)
installer a845e2e68ee530e697649669626cf83b329996f124001f82ea0e00e30d31202f
```

**This round changed no code.** It changed documents, one evidence file and one installer copy. The code changes in the same commit are R155's.

## WS3 first - what a prune does and does not do

**Git does not shrink when files are deleted.**
- **The working tree:** 118.3 MB before this round, **116.4 MB after**. The 1.9 MB is the v297 installer.
- **The clone does not change at all:** `.git`'s pack is **71.8 MiB**, and every deleted file stays in history.
- **Only a history rewrite would shrink it.** That is `git filter-repo` and a forced push, which I may not do. Every collaborator would then have to clone again. If you want that, the candidates are the installer binaries in history and `backups/`'s zips, as R120-00 named them.

**Your 112 MB is the working tree, counted in MiB:** 118.3 MB (decimal) is 112.8 MiB. So we agree.

**So this round is about a tree a person can search, as you said.** On that measure the change is in `docs/`, not in the evidence folders.

## WS2 - the prune, by citation

### The v297 installer: removed

- `Windows-to-Sarvam/win-v297-2026-11-03/Sutram-Setup-v297.exe` (1,946,102 bytes) is gone.
- **In its place:** `Sutram-Setup-v297.exe.REMOVED.md` - its SHA-256 (`fabece5f…3b65`, which also stays in `Sutram-Setup-v297.sha256` beside it), what it was, the last commit that carried it (`e316585c`), and the one `git show` command that brings it back.
- **`REVIEW-V297-2026-11-03.md` links the file;** that link now finds the note by name, not the file. I did not edit the review.

### Every Windows round folder: what cites each file

**How I counted** (`evidence-r156/cite2.py`, `cite-stages-3-5.py`; the full table is `evidence-r156/windows-citations.md`). A file is cited if any of these names it:
1. a report in its own folder, or a top-level Windows report that names the folder, or an index in its folder (a `.json`, `.txt` or `.log` that one of those reports cites);
2. any `.md` or `.html` in the tree, by its file name;
3. a script in its own folder;
4. a wildcard in its folder's reports (`backup-*.json`, `vacate-*.json`, `restore-*.json`), or its own words in them (*"the initial three licence captures"*).

Reports and scripts themselves (`.md`, `.ps1`, `.py`, `.sha256`) are the record, and all stay.

| | files | MB |
|---|---:|---:|
| **all files in round folders** | **4,424** | **65.3** |
| reports and scripts | 388 | |
| cited by name (1) | 3,760 | |
| cited by name elsewhere in the tree (2) | 74 | |
| cited by a script in its folder (3) | 24 | |
| cited by a pattern, or in a report's words (4) | 119 | |
| **named nowhere** | **59** | **2.0** |

**The 59, and why I kept them** (`evidence-r156/windows-named-nowhere.tsv`, with size and SHA-256 for each):
- **They include the raw results of claims in the shared state.**
  - `win-v309-final-fixes-2026-11-07/oom.txt` and `arithmetic.txt` are the outputs of `probes.py oom` and `probes.py arithmetic`. `COMMANDS.md` gives those commands; the *32/32 out-of-memory* and *7/7 arithmetic* results are what they print.
  - `lock-results.json` is the *two-process lock 7/7*.
  - `initial-identity.json` is an identity check.
- **They are cited by the command that made them, which no rule can match on a file name.**
- **The rest are the same kind:** `vacate-before-d1..3.json`, `restore-d1-failed.json` (a restore that *failed*: evidence of a fault, not a snapshot), `initial-engine.log`, and screenshots. Each belongs to a run a report describes in words.

**So "keep what is cited" cannot be decided mechanically for these 59.** Deleting them would save 2.0 MB - 1.7% of the tree - and put the raw evidence of three numbers in the shared state at risk.
- **They are kept, and listed with their hashes,** so the next audit can decide them by reading the reports, one file at a time.
- **If you want them gone anyway,** the list is the deletion list. Each line has its hash, and git keeps the bytes.

**Your example snapshots are cited, not loose.**
- The three you name are `win-v307-fixes-2026-11-06/before.json` (145 KB) and `identity.json` (173 KB), and `win-v305-2026-11-06/environment-before.json` (19 KB).
- **Each is named by its own folder's report.** By your rule, they stay.

**A rule I named rather than broke.** ROUND-49 and ROUND-50 say *"Do not touch `backups/` or `Windows-to-Sarvam/`"*, and R120-00 kept the v297 installer for that reason.
- **This round's instruction about that one file is specific, and newer, so I followed it.**
- **I did nothing else in `Windows-to-Sarvam/`.** The 59 above would have been the first deletions of the Windows owner's evidence beyond what you named.

## WS1 - the docs

**1. Does a doc say the installer is verified on Windows without naming the version?**
- **One sentence did:** the release notes said *"The licence rendering is verified on native Windows and not under Wine"*. It sat in v312's paragraph, but the sentence named no version. **It now says "(v312's package)".**
- **No other living document says "verified on Windows".** `PROJECT-MASTER.md`'s row 6 (*"Verified Windows release"*) is a gate's acceptance condition, not a claim that it is met. The install guides (`INSTALL-WINDOWS.md`, `docs/INSTALLATION-ROUTES.md`, `docs/WINDOWS-SETUP.md`) speak only of a package that *requires* acceptance.

**2. Does a doc describe the four ownership records?**
- **Only the changelog and the release notes did,** each correctly for v315. **Nothing describes `DesktopOwned` as a flag that acts.**
- **But nothing described the state file as a whole.** `docs/INSTALLER-REBUILD.md` now has **"What `install-state.ini` records"**: each record, what it holds, what uninstall does with it, and that the three `…Owned` flags are written and act on nothing. It includes R155's two new records.

**3. Do the release notes name the shipping condition? They did not. Now they do,** at the top:
- *a package is a release only once it has been installed, run and uninstalled on Windows, and the results are recorded in `Windows-to-Sarvam/`*;
- *the v315 package has not been run on Windows; it is a candidate*;
- *the last package run there is v312's*.

**And what I found that you did not ask about - a stale claim in four places at once.**
- `PROJECT-MASTER.md`, `docs/PATH-TO-COMPLETION.md` and `docs/LANGUAGE-REFERENCE.md` said *"The authoritative open list is `docs/WHATS-LEFT.md`"*. `ROADMAP.md` said *"where this page disagrees with it, that page is right"*.
- **`WHATS-LEFT.md` says "Compiler v258 · suite PASS=225 · gates 48".** It was last true 57 versions ago. **So four current documents named a v258 page as the authority on what is open.**
- **`docs/OPEN-ISSUES.md` is at v258 too,** and defers to `WHATS-LEFT.md`.
- **The language reference's status box was at v300,** with *"65 PASS / 1 FAIL"*. Its box had not been updated since R124. Mine was the job; I updated `PATH-TO-COMPLETION`'s and `PROJECT-MASTER`'s each round and missed this one.
- **And `PATH-TO-COMPLETION.md` said** *"if any other document disagrees with this one, this one is current"*. Its body was last revised at v250.

## The docs that overlap: merged or archived

There are 22 `.md` files in `docs/`. Five pairs or groups describe the same thing:

| overlap | what I did |
|---|---|
| **`WHATS-LEFT.md` (v258), `OPEN-ISSUES.md` (v258), `PATH-TO-COMPLETION.md`, the release notes** - four "what is left" pages | **`WHATS-LEFT.md` and `OPEN-ISSUES.md` moved to `docs/rounds/`**, each with an "archived in R156, last true at v258" line. **The open list is now one place:** the release notes' *"Not included in v1.0"* and *"Limitations of what is included"*, revised with each release. The four pointers say so. `PATH-TO-COMPLETION.md` is the plan, and says the release notes win where it disagrees |
| **`WINDOWS-PORT-PLAN.md`** (*"Status: started"*, 28 October) and the port that exists | **moved to `docs/rounds/`**, marked archived |
| **`LANGUAGE-REFERENCE.md`'s status box and `PATH-TO-COMPLETION.md`'s** | the same box now; they differed by 15 versions |
| `INSTALL-WINDOWS.md`, `docs/INSTALLATION-ROUTES.md`, `docs/WINDOWS-SETUP.md` | **kept as they are.** `INSTALL-WINDOWS.md` points to the routes page and the guide does the same. ChatGPT's `tests/clean_project/test_current_guides.py` pins that structure. They agree with each other |
| `SPECIFICATION.md` (an R70 snapshot) and `LANGUAGE-REFERENCE.md` | **kept.** The specification says on its first line that it covers the evidenced subset at one snapshot. The reference is the current one |

`docs/` now has 19 `.md` files. No link in a living document points at the three moved pages. Old round records that name them by their old path no longer find them there. They are in `docs/rounds/` under the same names.

## WS4 - the counts, for the next audit

At this commit, **before this report and its evidence were added**:

| | files | size |
|---|---:|---:|
| **the tree (tracked)** | **11,222** | **116.4 MB** (111.0 MiB) |
| `Windows-to-Sarvam/` | 4,435 | 65.4 MB |
| `Claude-to-Sarvam/` | 2,026 | 15.1 MB |
| `ChatGPT-to-Sarvam/` | 612 | 6.6 MB |
| `Muse-to-Sarvam/` | 570 | 5.4 MB |
| `backups/` (exempt) | 6 | 9.6 MB |
| `.git` pack (the clone) | | 71.8 MiB |

With this report and `evidence-r155/`, `evidence-r156/`: **11,237 files, 116.5 MB**; `Claude-to-Sarvam/` 2,041 files (15.2 MB); `Windows-to-Sarvam/`, `ChatGPT-to-Sarvam/` and `Muse-to-Sarvam/` unchanged (4,435, 612 and 570).

**Not done, and why:**
- **No history rewrite** (WS3).
- **No deletion in `Claude-to-Sarvam/`.** You did not ask, and R120-00's rule still holds there: its evidence is cited by round records.
- **The 59 Windows files**, as above.

Evidence: `Claude-to-Sarvam/evidence-r156/`.
