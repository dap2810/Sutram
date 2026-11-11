# R188-00 — The documents are current at v325, and the gate proves it. **But finding B is not true: the changelog entries for v316 to v324 exist. Each was written in the commit that made its version, on the branch chain.** Main's changelog stops at v315 because main *is* v315. **Finding A is true:** `docs/WHATS-LEFT.md` did not exist, and it is live again. **`R158` passed on main with A true, and that was a gap: it never checked that a path a document names exists.** It does now. Run on main, the new check fails on exactly one line, `ROADMAP.md` citing `docs/WHATS-LEFT.md`.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
staged r189-audit-fixes 22466bda   Sutram 1.0 (v325) - sampurna sutra     (this round and R189 are one branch)
     crash corpus: 227 cases + manifest, 0 failed · suite: NO-EXPECTATION=4 PASS=331
     gates: 92 PASS / 0 FAIL / 1 NOT-RUN  (Linux, Xvfb; NOT-RUN = Windows execution; evidence-r189/gates-v325.txt)
     the guard: in R189-00 (64 DIFFER, every one from R189's library fixes; the documents changed no program)
```

Sanskrit only; no pack touched; `backups/` untouched.

**Why one branch with R189, and why not "no compiler change".** R189 arrived with this round and fixes two
library functions; documents that describe the tip have to describe those fixes. So the two rounds are one
version, v325. **The compiler's code is v324's - only its version string and comments changed.** The library
changed; that is R189's, and its guard is there.

## 1. Your audit, checked

### A. `docs/WHATS-LEFT.md` does not exist - TRUE

It was archived in R156 as `docs/rounds/WHATS-LEFT.md`, last true at v258, with a first line sending the reader
to the release notes. **Eight briefs have named `docs/WHATS-LEFT.md` since** (counted). And `ROADMAP.md` on main
still cites it.

**Fixed:** a live `docs/WHATS-LEFT.md` at the path the briefs name. The archived copy's first line now says
**HISTORY - not the live list** and links to the live one. **Not deleted** - R156's record cites it.

### B. "The CHANGELOG stops at v315; nine staged versions are in no document" - NOT TRUE

```
main:                docs/CHANGELOG.md newest entry   v315
r186-grahan-and-files (v324):                          v324, v323, v322, v321, v320, v319, v318, v317, v316, v315
r189-audit-fixes (v325):                               v325, v324, ...
```

**Every one of the nine has its entry, with the round, the change, the gate and the guard - on the branch that
carries the version.** `R158`'s changelog check requires it, and it passed at every one of those versions.
**Main's changelog is right for main.** If I wrote v316 to v324 into main's changelog today, main would describe
nine versions its compiler is not, and the merge would conflict with the real entries.

**What is true in B: nobody reading main can see the week's work.** That is the cost of an unmerged chain, and
its fix is the Windows run, not a document.

### C. Run `R158` and report - and which check should have caught A and B

| | `R158` | `R159` |
|---|---|---|
| main, as it stands | **25 checks, 0 failed** | 11,368 files, 0 |
| the v324 tip | **25 checks, 0 failed** | 10,890 files, 0 |
| main, with v325's `R158` | **27 checks, 1 failed** - `ROADMAP.md: cites docs/WHATS-LEFT.md, which is not in the tree` | - |
| v325 | **27 checks, 0 failed** | 10,897 files, 0 |

**For B, no check should have fired, and none did.** The changelog check compares the changelog with the
compiler *of the same tree*. Main: v315 and v315.

**For A, the gate had a gap, and here it is exactly.** `R158` has ten checks. The one that reads what a document
cites, `symbols`, verifies two things only: names of the form `r123_label`, and `E_` codes. **It never checked
that a path exists.** So `ROADMAP.md` could name a file that had been moved away, for two days, and pass.

**And a second gap that a check cannot close:** the eight citations that misled partners were in the briefs
(`Sarvam-to-*/`). `R158` reads the twenty "current" documents and deliberately not the round folders, which are
history. **A brief that names a moved file is not something the tree's gate can see.**

**Closed: check 11, `paths`.** Every repository path a current document cites (`docs/...`, `tests/...`,
`tools/...`, `lib/...`, `examples/...`, `src/...`, `windows/...`, `lang/...`, `win/...`) must be a tracked file
or folder, or the start of one (`examples/276` is `examples/276_*.sm`). It has a self-test that rejects a
missing file. **Two citations are allowed by name, each with its reason written beside it:** `lib/lang` (prose
for two folders) and `lib/fileio.smlib` (named as deleted, on purpose).

## 2. WS1 - what was brought current

| | what was wrong | now |
|---|---|---|
| **1. `docs/WHATS-LEFT.md`** | absent | live: the one thing before a release; the nine-item plan; five decisions waiting for the owner; open defects, worst first; the audit's open rows by ID; what is out of 1.0 on purpose |
| **2. CHANGELOG** | (see B) | v325's entry added; v316-v324 were there |
| **3. RELEASE-NOTES** | named v324 | names v325, with what v325 closes and does not |
| **4. PATH-TO-COMPLETION** | status at v324; it does not list memory as open | status at v325 |
| **5. ROADMAP** | **its status block is from compiler v261 and says "there is no `munmap` anywhere - nothing ever returns memory"** | a current status above it; the old block marked as history, with its two false sentences named. **Kept, because it is labelled the owner's** |
| **5. PROJECT-MASTER** | status at v324 | status at v325 |
| **6. README** | 222 examples; 305 functions; "three comment-only modules" that no longer exist; a baseline of 225 passing cases; **"Memory is released only on Linux. In a Windows program a `mandapa` block works, but releases nothing"**; no word about reading input | 335 and 16; 310 in 24; the status at v325; **a section "Reading input"** with `vartani_grahan`, `grahan`, `nivesha_anta` and files; the Windows sentence removed |
| **7. the three reference errors** | `likh8` / `pad8` as bits; `likh8c` / `pad8c` as the terminal; the braces section | all three corrected - and the braces section was worse than stale (R189-00, WS3) |

**The nine-item plan, as it stands - and it is not "all closed except generics".** Items 1, 3, 4, 5, 6, 8 and 9
are closed. **Item 7, generics, is 1.1. And item 2 - one Windows run, then merge - is open, and it is the one
everything else waits on.** `docs/WHATS-LEFT.md` puts it first.

**The README's Windows sentence was false before this chain.** Measured under Wine: 200,000 passes of
`nirmmita(256)` inside a `mandapa`, as a Windows executable, end with `parimana()` 0; without the block,
51,200,000. **The same on v315.** (Wine is not Windows.)

## 3. WS2 - the books against v324's behaviour

- **The memory chapter does not say what you feared.** It already says, since R181, that from v320 a block's
  memory is cleared as the block ends.
- **One passage was incomplete, and is fixed in both books.** "A `mala` made inside a block - never given back
  ... 200,000 calls ... end holding 51,200,000 bytes." **For calls that is still true on v325 (measured). For a
  loop it is not:** the same 200,000 passes written as a `chakra` around the block hold **256 bytes** on v325
  and 51,200,000 on v315 - v319 makes a `mala` in a loop once. One sentence added to each book.
- **Both books teach `vartani_grahan`** - 12 mentions, in the input section, with the read-to-the-end loop
  (R184, R186). A student can find it.
- **Two sentences in the English book were damaged by an old rename** and are repaired: "the full operator
  **sangrah**" (set) and "PATH is the **suchi** of folders" (list). See section 4.
- **The Sanskrit sentences are mine and unread by anyone who would catch an error in them.**
- **All 46 complete programs in the two books run** (`R158`, on v325).

## 4. WS3 - the cleanup: named, nothing deleted

**Where the 11,368 files and 88 MB are** (tracked files on main):

| | files | MB |
|---|---:|---:|
| `Windows-to-Sarvam/` | 4,219 | 37.4 |
| `Claude-to-Sarvam/` | 2,432 | 14.0 |
| `backups/` | 6 | 9.1 |
| `ChatGPT-to-Sarvam/` | 636 | 7.0 |
| `Muse-to-Sarvam/` | 419 | 6.3 |
| root (the compilers and the installer) | 26 | 3.4 |
| `docs/` | 119 | 2.3 |
| `tests/` | 2,185 | 1.2 |
| everything else | 1,326 | 7.3 |

**Seventy-four of every hundred megabytes are the partners' evidence, and that stays by the rule.** The
documents are 2.3 MB. **Cleaning `docs/` will not make the project smaller; it will make it truer.**

### 4.1 Superseded in `docs/` - and shipped to every student

**Every file below is inside the installer.** A student who installs Sutram gets them.

| file | what it is | why it is superseded |
|---|---|---|
| `docs/sutram-benchmark-report.html` | "Benchmark Report - vs C, C++, Rust, Java, Python, Node.js, Go" | **an older comparison that leads with "160x faster than Python" and "23x smaller than C -O2".** R185 measured the same languages: Sutram loses a hot loop to optimised C by 4 to 17 times. **This page tells a student the opposite of what was measured** |
| `docs/sutram-performance.html` | "Codegen Performance Analysis" | names no version; last changed 28 October; same subject as R185 |
| `docs/sutram-project-status.html` | "Project Status" | says compiler v246 |
| `docs/sutram-scorecard.html` | "progress scorecard" | says v298: suite 315, 305 functions |
| `docs/sutram-roadmap.html` | "Roadmap" | `ROADMAP.md` says it is the one roadmap (R95) |
| `docs/sutram-audit.html` | "Project Audit" | last changed 28 October; three audits since |
| `docs/sutram-stdlib-reference.html` | "Standard Library Reference" | beside `docs/sutram-stdlib.html`, which is the one 15 files link to |
| `docs/_newchapter_en.html` | a draft of the book's "What is new" chapter | **27 of its 31 sentences are in the English book word for word**; nothing links to it |
| `docs/mockup-setup.html` | a mock-up of the installer's window | the installer exists |
| `docs/sutram-book.html`, `-2.html`, `-3.html` | three pages saying "this edition was superseded" | the same page three times, one word apart |

`sutram-project-status.html` and `sutram-scorecard.html` are read by `tools/doc_counts_gate.py` and
`tools/check_version_strings.py`, so removing them means changing those tools.

### 4.2 At the root, and belonging elsewhere

| file | what it is | where it belongs |
|---|---|---|
| `sutram-completion-roadmap.html`, `sutram-progress-report.html` | two more status pages (the second says v146) | `docs/rounds/`, with the other history - only the changelog archive mentions them |
| `created_default.txt`, `created_private.txt` | **two empty files** | they are what `tests/r52_check/dvaram_default.sm` creates when it runs; a test's output committed at the root. A test folder, or not tracked |
| `LANGUAGE-PRIORITY.md` | "read this before any round" | arguably `docs/`; three documents link to it at the root, so moving it means three edits |

`README.md`, `PROJECT-MASTER.md`, `ROADMAP.md`, `AGENTS.md`, `INSTALL-WINDOWS.md` and `LICENSE.txt` are where a
reader looks for them. The compilers and the installer at the root are the build's layout, not documents.

### 4.3 What could go without losing a record

1. **The ten files of 4.1** - each is a snapshot of a state the changelog and the rounds record better. **The
   benchmark report first: it is the only one that is wrong in a way that misleads.**
2. **The two empty files** of 4.2.
3. **`docs/_newchapter_en.html`** - a draft whose text is in the book.

**What I would not touch:** `docs/rounds/` (39 files), `docs/reports/` (20), `docs/decisions/` (7) - records.
**And not the duplicates:** 1,359 file contents appear more than once, 3,074 extra copies - **almost all are
one-byte `.exit` goldens and empty output streams.** They are evidence of runs, they weigh nothing, and R161
decided evidence stays.

### 4.4 Found while looking: an old rename went through English prose and CSS

R111 renamed builtins to Sanskrit. **Somewhere the words "set" and "list" were replaced with `sangrah` and
`suchi` in text that was not code:**

- **`AGENTS.md`: "Do not sangrah up background watching"** - the project's own instructions. **Not changed: it
  is the shared instruction file, and not mine to edit unasked.**
- `docs/LIBRARY-BOUNDARY.md` and `docs/sutram-design-parameters.html`: "a sangrah of socket builtins".
- **CSS in four pages: `ul { suchi-style: none }`** - the property is `list-style`; a browser ignores the
  broken one, so those lists show their bullets (`sutram-benchmark-report.html`, the three book-edition pages).
- The English book, two sentences - **fixed** (section 3).

Nine places in prose and four in CSS (counted by pattern; there may be others the pattern does not match).

## 5. WS4 - the proof

1. **`R158`: 25 / 0 before (main and the v324 tip), 27 / 0 after.** The two new checks are `paths` and its
   self-test.
2. **`R159`: 0 before, 0 after.**
3. **The guard.** Documents change no compiled program, and they did not. **The guard reads 64 DIFFER, not 0 -
   all 64 from R189's two library fixes, every one bringing in `ganit` or `brihat`, every one printing what it
   printed.** With the library as it was, the same tree is byte-identical: ChatGPT's own record of the
   non-library changes is 587 identical, 196 refused, 0 DIFFER.

## Not done, and why

- **Nothing deleted, nothing moved** - you said to name it. The list is section 4.
- **`AGENTS.md`'s damaged sentence is not changed.**
- **The four frozen books are not checked** - Gujarati, Hindi, Tamil, Telugu.
- **The rest of the reference is not audited by me** - the audit's open Tier 2 and Tier 3 rows are listed by ID
  in `docs/WHATS-LEFT.md`.
- **Main is not changed.** Everything is on `r189-audit-fixes`, behind the same Windows run.
