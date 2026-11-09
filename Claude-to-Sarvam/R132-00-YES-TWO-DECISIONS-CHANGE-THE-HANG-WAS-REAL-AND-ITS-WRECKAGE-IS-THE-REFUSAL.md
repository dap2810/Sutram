# R132-00 — Yes, two of my decisions change. The record is wrong on one point that matters: the "hang" was real. The owner's machine still shows exactly where the v303 copy stopped: in the middle of file 132 of 657, an empty file. The ownership refusal that ChatGPT measured is what that interrupted copy left behind; it does not replace the hang. And v306 handles that wreckage badly: its log would not name the file it stopped on (my R130 hand-back said it would - that was wrong), and an interrupted install still traps the next run behind a "user file" refusal. I have not changed the tree: v306 is under Windows test. I propose both fixes for the next round.

## Release line (unchanged this round)

```
gates: 69 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh at 94e5e2d, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v306) - sampurna sutra
```

- **Commit on `main`:** the commit that carries this file; its SHA is in my chat report.
- **`crash corpus: 227 cases + manifest, 0 failed`** (same run).
- **The guard: NOT RUN this round, because nothing it covers changed.** `git diff 94e5e2d HEAD -- src win lib lang windows tools tests` and the compiler, linker and setup binaries: empty. The v305 → v306 guard (R131-00) stands: ELF 0 DIFFER; PE 584 DIFFER, all the same output and exit under Wine.
- **No PowerShell and no native Windows here**, as before. What follows was read from ChatGPT's committed snapshot (`Windows-to-Sarvam/win-installer-diag-2026-11-06/before.json`) and checked against the payloads in git history.

## The answer: what changes, and why

### 1. The hang was real. The refusal is its wreckage. (A correction to the record, not just to my decisions.)

ROUND-132 says *"The reported 'hang' was not a hang"* and that the refusal explains it. **The evidence says otherwise.** ChatGPT's own diagnostic says so too: *"This identifies the current refusal. It does **not** identify the original v303 copy stall."* The order alone settles it:
- the refusal is raised **before** `Copying Sutram files.`;
- the original log **ended at** `Copying Sutram files.`;
- so the v303 run had already passed the guard.

**What the installed folder held before the repair** (137 files, each with its hash in ChatGPT's snapshot), compared with the payload inside the v303 `Sutram-Setup.exe` (`47c3791`):

| | files |
|---|---|
| byte-identical to the v303 payload | **131** |
| that match only the previous install's manifest (an older, Windows-built payload: 643 entries, a linker of its own) | **0** - the engine removed them first (`Removing files owned by the previous Sutram payload`) |
| the previous install's state (`payload.manifest.sha256`, `install-state.ini`, `.sutram-install`, `install.log`, `Sutram-Uninstall.exe`) | 5 |
| **`docs\rounds\PROJECT-OVERVIEW.md`: 0 bytes, written 2026-11-06 18:35:34.979** | **1** |

Copy-Item copies in name order. **The copy got this far:**
- every file of `assets\` and `bin\` (48 of 48), and `docs\` up to `docs\rounds\PLAN-TO-FINISH.md` (82 of 118);
- then it **created `docs\rounds\PROJECT-OVERVIEW.md` and never wrote a byte into it;**
- nothing after: `examples\`, `lang\`, `lib\`, `win\` and the root files have 0 of their files.

It is the only file with a timestamp from that evening; the others keep the payload's times. **That is the moment and the file where the copy stopped:** the 132nd file of 657, a 7.6 KB Markdown file, at 18:35:34. It did not fail - a failure throws, and the engine logs `ERROR:`. It stopped inside the copy until the owner closed PowerShell.

**Why the next runs refused.** The folder now held v303's `bin\sutram-link.exe` (`b6c722e9…` - the linker of every payload from v302 to v305), but still the **previous** install's manifest, which expects `84d653fb…` - a linker no commit in this repository has, so it was built on Windows. The v305 runs compared the two, and called our own half-copied linker "a user file". **The refusal is what the interrupted copy left.** The repair worked because it moved that state aside.

**Still unknown: why the copy blocked on that file.** It is not in the source. The candidates are what blocks a process inside a file copy: a filter driver (antivirus, a backup agent - Acronis filter drivers are on this machine's PATH), or a write to the visible console that QuickEdit had paused. **I cannot tell which from here.** It blocked on file 132 of 657 on one run; the v305 install after the repair copied all 657 in 15 s.

(A smaller correction: HANG.md says the installed `bin\sutram.exe` "prints v305". The snapshot's `where sutram` lists the repository's own `<repo>\sutram.exe` first. The installed file's hash is the v303 payload's, `4c05d5cb…`.)

### 2. Decision changed: the log must name the file it is copying. My R130 hand-back was wrong.

I wrote that v306's copy logs every 100 files and *"If it stops again, the last log line names the file."* **It does not:** a copy that stops at file 132 leaves `Copied 100 of 657 files; last: <file 100>`. **The fix:** log each file before it is copied (`Copying 132/657: docs\rounds\PROJECT-OVERVIEW.md`). That is 657 short lines, the same file that v306 already appends to. With the 15-minute stop, the log's last line is then the file the copy stopped in. **I have corrected the sentence in R130-00.**

### 3. Decision changed: an interrupted install must not trap the next one

v306 replaces an endless wait with a stop after 15 minutes. **A stop mid-copy leaves exactly the owner's state:**
- part new files;
- the old manifest;
- and the next run refuses with a message that blames the student (`a user file`).

**I made the wait bounded without making what it leaves recoverable.** That is the second decision that changes. **The fix I propose:**
- **Before** removing the old files, the engine writes the new payload's manifest beside the old one, as `payload.pending.sha256`, and deletes it only after `Installation complete`.
- **On the next run,** a file that matches the old manifest **or** the pending one is ours. With that, every one of the owner's 131 files would have been accepted: each matches the v303 payload, which was pending. Only a file matching neither is a user file.
- **The message names the case:** `A previous installation stopped part-way (log: ...). Run this installer again to finish it` when a pending manifest is present.
- **A Linux gate check for it,** and an e2e case: install, stop the engine mid-copy, install again.

**I have not built 2 or 3.** v306 is what the Windows round is testing; changing `Sutram-Setup.exe` now would make that run test the wrong file. **No compiler change is involved** - the payload stays v306. Say the word and it is one round: the engine, the gate checks, the installer rebuilt.

### What does not change

- **Detect and refuse another Sutram (R130 WS2):** unchanged. The picture confirms that two installations, and the PATH order between them, caused the wrong version.
- **The OOM message (R131 WS1):** unchanged.
  - The measurements (reserve succeeds, commit fails; 64-640 MiB crash, 768 MiB succeeds) are what I worked from.
  - The `mandapa` result fits: with a 64 MiB budget and a 64 MiB Job limit, Windows refuses the commit before the budget is reached. v306 then prints `smritih na labdha` and exits 1, where the budget would have said `E_PARIMITA`.
  - Making those agree needs the budget to know the OS limit, which a program cannot know in advance. I leave it, and say so in the release notes.
- **The IDE keeps the previous file (R131 WS2):** unchanged; I kept it for the same reason ROUND-132 gives.
- **`79_ayojan_cwd` (R131 WS3):** unchanged; the four runs are the same conclusion.
- **No release-notes change yet.** The installer limitation goes in with the fix, or now if you want it recorded before.

## Not done

- 2 and 3 are proposed, not built (above).
- The cause of the block on file 132 is not found.
- The guard was not re-run (nothing changed).
- Nothing ran on Windows.
