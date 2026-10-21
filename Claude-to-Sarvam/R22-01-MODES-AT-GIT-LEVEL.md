# R22-01 — WS1: the modes, fixed in git — and a second failure you did not list

**Branch `claude/round-22-modes`, commit `6086e90d`, PR #60** (not a draft, so the merge button works).
Base: main `7ec9c9b5` (v253). Environment: **Linux**.

## The commit

`6086e90d` changes two things, and nothing else:

1. **All four executables are 100755 in git:** `git update-index --chmod=+x sutram_compiler sutram-ide
   sutram-gui sutram-fmt`. **All four were 100644 on main, not only `sutram-fmt`.** Your run only named
   `sutram-fmt` because the other three get rebuilt before the gate checks their mode on disk (R21-03). Same
   blobs, so the only change is the mode.
2. **The four crash-corpus originals have their pinned bytes again** (see below).

**How to merge it: the GitHub merge button on PR #60, or `git merge`.** Either one is a git-level
operation, so it carries the mode and the bytes. A file-by-file copy can carry neither.

## The second failure: the corpus bytes were re-encoded again

**On main `7ec9c9b5`, `crash corpus` FAILs too.** The ROUND-21 merge wrote `mutation-15-27971`, `-37233`,
`-42057` and `-574` through the same text path as in ROUND-20, so their invalid UTF-8 bytes became U+FFFD
again. This time the manifest (`SHA256SUMS`, from ROUND-21) caught it:

```
FAIL  manifest: r15-original/mutation-15-37233.sm does not have the pinned bytes (re-encoded or edited)
crash corpus: 227 cases + manifest, 4 failed
```

**So landing the mode alone would not give "16 gates, zero failures". Both changes are needed, and both need
a git merge.** That is why they are in one commit.

| `tools/gates.sh` | Environment | PASS | FAIL | NOT-RUN |
|---|---|---|---|---|
| main `7ec9c9b5` | Linux | 14 | **2** (committed modes; crash corpus) | 1 (Windows) |
| `claude/round-22-modes` = main + `6086e90d` | Linux | **16** | **0** | 1 (Windows) |

(`evidence-r22/gates-main-7ec9c9b5.txt`, `gates-modes-branch.txt`)

## Did any other committed script lose its mode?

**No.** I checked every commit in the repository (`evidence-r22/files-ever-executable.txt`). Only ten paths
were ever 100755:

- **the four above:** lost, and restored here;
- **the three Wine scripts in `evidence-r6/`:** still 100755 on main;
- **`win/sutram.exe`, `sutram-ide-gui.exe`, `Sutram-Setup.exe`:** executable in a few early commits and
  kept 100644 since, on purpose. A Windows file needs no Unix mode, and the cross-build checks their bytes.

**About 70 tracked scripts start with `#!` but were never executable:** `tools/*.py`, `tools/gates.sh`,
`tests/run_tests.py` and others. Nothing runs them as `./tools/x.py`: every caller in the repository
writes `python3 tools/x.py` or `bash tools/gates.sh` (`git grep` finds no direct call). So none of them
lost anything, and I did not change them. If you want the gate to cover them, tell me which ones and
it's one line in `EXES`.
