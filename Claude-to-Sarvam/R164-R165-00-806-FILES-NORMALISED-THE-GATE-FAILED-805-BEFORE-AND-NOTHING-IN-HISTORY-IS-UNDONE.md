# R164-R165-00 — The owner's system details are out of the tree's text: 806 files normalised, every line keeping what it claimed. `R159 no personal paths` failed on 805 files before this commit and passes on none after. The screenshots were the part a text gate cannot see: 64 of the 329 showed the owner's account name, computer name, projects folder or OS build where OCR could read it; those 67 places are now covered in grey, and a second reading finds none. **The history is untouched and still holds every string; the repository has been public, so they have been visible; old installers carry one of them. Nothing here undoes that.** And the memory chapter now says where a block must be.

## Release line

```
main (the commit carrying this file; SHA in my chat report): Sutram 1.0 (v315) - sampurna sutra
     compiler byte-identical to 308c2161's - this round changed no compiler (Linux be2f8dd5, Windows ccdba46d, sha1)
     gates: 80 PASS / 0 FAIL / 1 NOT-RUN  (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution; R159 new)
     suite: NO-EXPECTATION=4 PASS=327 (331 run) · crash corpus: 227 cases + manifest, 0 failed
     installer 9011c8a5c3595566aedfdbbf0820029616cb19bafaa4b5961e7af77854eee153 - rebuilt: the payload's docs/ carried
     the computer's name in a profile path and the OS build; its 658 files now carry none (scanned)
R159: before (759ec0a7): 805 files, 75,707 places, exit 1 · after: 11,108 tracked files, 0, exit 0
```

**THE GUARD IS ABSOLUTE:** no compiler changed this round, so the guard is identity on main (the binaries are
`308c2161`'s). The staged v316's guard is in R163-00 (783 programs, 0 DIFFER, ELF and PE).

## R164 WS1 / R165 WS1 - what changed

**806 tracked files** (`.md`, `.json`, `.txt`, `.log`, `.ps1`, `.html`, `.tsv`, ... - every text file, not only
`.md` and `.json`, because the gate reads every file):

| folder | files |
|---|---|
| `Windows-to-Sarvam/` | 536 |
| `Claude-to-Sarvam/` | 239 (mine: my cloud machine's paths, and the owner's from Windows evidence I copied) |
| `Muse-to-Sarvam/` | 12 |
| `docs/` | 7 (in the installer's payload: `mockup-setup.html`, two `ai-handoff-notes`, `RELEASE-NOTES.md`, three in `rounds/`) |
| `Sarvam-to-Claude/`, `Sarvam-to-ChatGPT/`, `Sarvam-to-Muse/` | 3, 2, 2 (your briefs quoted the strings) |
| `ChatGPT-to-Sarvam/` | 2 (what its own pass left) |
| top level, `windows/` | 2, 1 (`PROJECT-MASTER.md`, `sutram-completion-roadmap.html`; `windows/gui/MANUAL-WINDOWS-GUI-TEST.md`) |

The owner's names were in **534 files, 520 of them in `Windows-to-Sarvam/`** (the account name in 378, the projects
folder in 284, the computer's name in 21). The rest of the 806 carried build numbers, the CPU, or a build machine's
own folders - my cloud container's (`/tmp/claude-<n>/...`, `/home/<me>/sutram`, and Wine's view of the same folders) and Muse's.

| what | written as | places |
|---|---|---|
| the repository's folder on the owner's machine (and the folder holding it) | `<repo>` | 32,026 |
| the home folder, every spelling (`\`, `\\` in JSON, `/`, `\\?\`, WSL, MSYS) | `%USERPROFILE%` | 5,562 |
| my cloud scratch folder (Linux and the Wine view) | `<scratch>` | 331 |
| my cloud checkout, home and `tmp` | `<repo>`, `~`, `<tmp>` | 210 |
| a wrapped console line's cloud folder name | `-home-<user>` | 24 |
| Wine's profile (`C:\users\<the container's account>`) | `%USERPROFILE%` | 58 |
| an OS build: `build NNNNN`, `10.0.NNNNN`, PowerShell `5.1.NNNNN.N` | `build (redacted)`, `10.0 (build redacted)`, `5.1 (build redacted)` | 99 |
| a transcript's `Username:` / `RunAs User:` / `Machine:` | `<machine>\<user>`, `<machine>` | 15 |
| the CPU | `[hardware detail redacted]` | 7 |
| Muse's workspace | `<workspace>` | 15 |
| the owner's first name in the roadmap's table | `Owner` | 1 |
| the account name alone in a sentence | `<user>` | 1 |
| another drive's test folder; an elided projects-drive path; a one-letter home folder in an example of Muse R156 | `<test-folder>`, `<repo>`, `/home/<you>/` | 3 |

In Markdown outside code, an angle-bracket placeholder is put in backticks (GitHub would hide a bare `<repo>` as a
tag); in HTML it is `&lt;repo&gt;`. Your briefs that *name* the strings (R164, R165, ChatGPT R226, Muse R132 and R157)
say `C:\Users\<account>`, `C:\Users\<computer name>` and `<drive>:\<projects folder>\Sutram` instead, so they still read.

**Where I did not write what you asked, and why:** an OS build became "(build redacted)", not "Windows 11 Home,
November 2026". The evidence says Windows 11 **Pro** in places and is dated **October** in places; writing Home and
November would change what it claims. The edition and everything else stay. The tool is
`tools/normalize_personal_paths.py`; it names nobody (the names are matched by hash, below).

### The three checks before replacing (R165 WS1)

**1. A path inside a SHA-256 preimage: yes, 700 (manifest, file) pairs.** The dry run hashed every file it would
change and searched the tree for each digest's prefix. They are: the `EVIDENCE.sha256` of seven Windows folders
(v307-fixes, v310, v311, v311-acceptance, v312, v313, first-run-paths) and `evidence-sha256.json`, hashing their own
logs and JSON; the v310 and v311 `ownership/*.json` inventories, which hash the *installed* payload's `docs/` files;
my `evidence-r156/windows-named-nowhere.tsv`; ChatGPT's R119 and R122 manifests; and
`windows/windows-build-integrity.sha256` (237 of its 440 entries did not match before this round; not gated).
**I changed no cited digest.** Each records the bytes as delivered, and the history holds them at the commit that
delivered them. Instead `Claude-to-Sarvam/evidence-r164/normalization-record.json` gives, for each of the 806 files,
the SHA-256 at `759ec0a7` and after, as ChatGPT's R226 record does. So `sha256sum -c EVIDENCE.sha256` in a normalised
folder now fails for the files normalised - by design; to check one, hash `git show 759ec0a7:<path>`, or find it in
the record.

**2. A path as a JSON key: yes, three files** - `win-firstrun-paths-2026-11-08/restoration-baseline.json` (1 key) and
`win-v312-2026-11-08/before-` and `after-uninstall-inventory.json` (4 and 5), inventories keyed by a path under the
profile. Every key stays distinct (67/67, 2,863/2,863, 118/118 keys before and after), so nothing merged, and every
changed `.json` still parses.

**3. A path inside a file name: none** in 11,108 tracked paths. No file was renamed.

And two more: **binaries** - none carries a name as plain text (installers keep their payload compressed; see the
limits). **Screenshots** - the gate cannot read pixels, and they did carry the names: an installer's *Destination folder*, a prompt in the profile folder, a console's version line. I read all 329 with tesseract (at twice the size) and covered only those characters, one character's width either side, leaving the rest of each picture (`tools/redact_screenshots.py`; before and after digests in `evidence-r164/screenshot-record.json`): **64 images, 67 places** - the account name 60, the computer name 5, the projects folder 1, an OS build 1. Read again, none.

## R164 WS2 / R165 WS3 - the gate

`R159 no personal paths` (`tests/r159/test_no_personal_paths.py`, registered in `tools/gates.sh`; the rule is in
`AGENTS.md` above the evidence rule). It reads every tracked file and fails on: a home folder by name in any
spelling; a drive letter other than `C:` starting a path (Wine's `Z:` too); a build machine's own folder; a
transcript's user and computer lines and the `COMPUTERNAME`/`USERDOMAIN`/`USERNAME` variables with a value; an OS
build number; a CPU model; and **the owner's account, computer and projects-folder names as words - in text and in
binaries - matched by the SHA-256 of each word, so the gate does not write them**. Placeholders (`<you>`,
`%USERPROFILE%`, `$HOME`, `{user}`) and the shared profiles (Public, Default) pass. It prints file, line and kind,
**never the matched text** (a log of the gate must not become a copy of the strings). Its self-test builds 14
forbidden forms at run time and needs each to fail, and 13 placeholder forms to pass.

**It failed on the tree before this commit:** at `759ec0a7`, 805 files, 75,707 places, exit 1
(`evidence-r164/r159-before.txt`). After: 0 (`evidence-r164/r159-after.txt`). On the Windows folder specifically:
536 of its 4,424 files failed before; 0 after.

**A limit of the hash, stated so nobody relies on it:** a SHA-256 of a short word can be reversed by trying every
word. The hash keeps the names out of a reader's eye and a search engine; it does not keep them from someone who
wants them - who has them anyway, in the history.

**Muse R157 landed while I was committing** (its inventory: 526 files with the home folder or the repository's
folder, 211 hashed by a manifest, 3 with a path as a JSON key - the same three - and no file name). Its report had one
drive-letter example the gate fails (`` `<drive>:\Software`-style `` now, one edit, after my commit); with that, the
gate passes on the tree Muse's commits and mine make together. Muse also found the chapter never distinguishes one
block around a loop from blocks entered on every pass - the paragraph below now does.

## R164 WS3 / R165 WS4 - what is fixed and what is not

- **Fixed: the tree** - the files a clone of this commit *checks out*. (Corrected in R166: I first wrote "a fresh
  clone carries none of the strings". A full clone downloads the history too, and the history holds them. And the
  first gate could not read 21 UTF-16 files or a WSL kernel version, so they were not clean then either; they are
  now - R166-00.) The installer built from this tree carries none.
- **Not fixed: the history.** `git log -p`, `git show <old commit>`, every old blob - all still hold every string.
  Only a history rewrite removes them; it would change every commit SHA that hundreds of records cite and break every
  clone, the owner's Windows clone among them (the R161 decision; not reopened without the owner).
- **Not undone: the exposure.** The repository has been public, so the strings have been visible, and copied by
  whoever cloned or forked it, and by any cache or index. Cleaning the tree stops new clones of the current tree
  carrying them; it does not reach those.
- **Not fixed: old installers.** Every `Sutram-Setup.exe` in history, and any the owner gave anyone, carries
  `docs/mockup-setup.html` with the computer's name in a profile path, and the OS build in two `ai-handoff-notes`.
- **Not certain: images.** OCR reads what it can; small, faint or coloured text it misses. The 64 are what tesseract could read; a name it could not read is still in its picture, and I looked at five screenshots by eye, not 329. Desktop screenshots also show the owner's taskbar (which programs are pinned): not in the instruction's list, and not covered.
- **Out of the tree: commit metadata.** Author names and e-mail addresses on commits are not files; the gate does not
  read them, and they were not changed.

## R165 WS2 - the Windows folder's evidence, by the R161 rule

**The 59 uncited files** (R156: of 4,424 files, 4,365 cited) are listed with sizes and digests in
`Claude-to-Sarvam/evidence-r156/windows-named-nowhere.tsv`. **11 of them have since gone** as byte-identical copies
in the R157-R159 lossless cleanup (its manifest names the kept copy); **48 remain**, 2.0 MB: `win-v309-final-fixes`
14, `win-v309-fixes` 6, `win-v309-integrated` 6, `win-v307-fixes` 4, `win-v311-acceptance` 2, `win-round3` 3,
`ide-v297` 1, `win-test-2026-10-27` 22 (1.5 KB in all). 12 of the 48 carried a path and are normalised. I deleted none:
nothing cites them, but they are the Windows owner's raw output and the rule keeps evidence.

**The JSON snapshots that carry a path:** normalised in place, not replaced by a hash and a number. The reports cite
fields inside them (a key, a value, a count), and a normalised path identifies nobody, so each keeps everything a
report reads.

## R164 WS4 / R165 WS5 - the memory work

**a.** The compiler overwriting its input: staged, after Tuesday - R163-00.

**b.** "grows each time you add" -> "makes room for twice as many when it is full": done (`d80079ca`).

**c. "A block gives memory back when it ends - a loop inside a block does not."** Measured, and now in both
chapters (§2, *Where the block is matters*). v315, `env -i`, 20 runs each, every program 200,000 `nirmmita(256)`
(`evidence-r164/peak-memory-block-placement.txt`, the programs printed):

| program | peak |
|---|---|
| A: **one block around the loop** of 200,000 | **49,920 KB** |
| B: A without the block | 49,920 KB |
| C: **1,000 blocks one after another**, 200 each | **264 KB** |
| D: C without the block | 49,920 KB |
| E: C, but the `nirmmita` is in a `prakriya` the block calls | 49,920 KB |
| the chapter's program: the block inside the called `prakriya` | 264 KB |

Your finding stands: a block around a loop gives back nothing until the loop is over. And E is the one a student
will hit next: **only `nirmmita` written in the block's own lines is given back** - memory a called `prakriya` makes
outside a block of its own stays. The chapter now says both.

**d. The program behind the chapter's numbers** is the one printed directly above them in §2 (the block inside
`kaam`, called 200,000 times, 256 bytes each), and it is in `evidence-r163/peak-memory.txt` with its binary's digest.
Its figures are 49,920 KB and - not 392 - **264 KB started with an empty environment**, 264-436 KB from a shell
(R163-00, WS3). Your 13,256 / 15,708 and 15,996 / 15,416 come from programs I have not seen; mine give 264 / 49,920 for
sequential blocks. A gap that size usually means the memory is not `nirmmita` written inside the block (case E), or
other memory dominates (smaller buffers, a `kosh`). **Send the programs and I will measure them.**

**e.** `parimana()` counts capacity, not length: said, with the arithmetic of 96 (`d80079ca`).

## Not done, and why

- **The history:** not rewritten (above).
- **Images:** covered where OCR read them (64 images, 67 places); not every image checked by eye; the taskbar in desktop screenshots left as it is.
- **`windows/windows-build-integrity.sha256`:** not regenerated - stale before this round, not gated, and a
  regeneration would bless 237 unexplained mismatches.
- **Native Windows:** nothing here needs it; nothing ran there.

## Addendum (the owner, the same day): the screenshots are out of the tree

The owner saw an installer's *Ready to Install* page with the profile folder in it and asked why the screenshots were
still there. **All 318 screenshots are now removed** (`git rm`; 213 from `Windows-to-Sarvam/`, 105 from
`Claude-to-Sarvam/`); the 11 product icons in `icons/` stay. 64 of them had been covered where OCR read a name, but OCR
can misread a name (an `m` read as `rn`) and then misses it, so covering was never proof; removing them is.
`Claude-to-Sarvam/evidence-r164/screenshots-removed.tsv` lists each one, its size and digest. Nothing in `tools/`,
`tests/`, `src/` or `docs/` reads them; 60 reports link to one, and those links now lead nowhere - the report's words
say what the picture showed. **They are still in the history** - the originals, names readable, at `6b395bd7` and
before. Removing them from there is a history rewrite and a forced push: every commit SHA changes, every clone
(the owner's Windows clone among them) must be made again, and GitHub keeps cached views and forks until asked to
purge them. That is the owner's decision; I have not done it.

