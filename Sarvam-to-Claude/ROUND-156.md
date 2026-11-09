# Sutram — ROUND-156: the repository has doubled. Audit and prune.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**This is an audit round. It changes no code.** **Everything below was measured on the current tree.**

---

## The finding

**The repository is 112 MB and 11,215 files.** **At the last audit it was 53 MB and 7,141.** **It has more than doubled.**

| Directory | Now | Then |
|---|---|---|
| **`Windows-to-Sarvam/`** | **67 MB** | 12 MB |
| `Claude-to-Sarvam/` | 17 MB | 15 MB |
| `ChatGPT-to-Sarvam/` | 6.5 MB | 6 MB |
| `Muse-to-Sarvam/` | 5.4 MB | 4.5 MB |
| `tests/` | 2.7 MB | 2.4 MB |
| `docs/` | 2.4 MB | 2.3 MB |
| `src/` | 1.6 MB | 1.5 MB |

**The Windows folder is 60% of the repository and it grew by 55 MB in a week.**

**The largest round folders:**

```
8.3 MB  win-v311-2026-11-07
7.9 MB  ide-v297-2026-11-03
7.8 MB  win-v310-2026-11-07
6.2 MB  win-v309-final-fixes-2026-11-07
4.7 MB  win-v311-acceptance-2026-11-07
4.1 MB  win-v309-fixes-2026-11-07
3.8 MB  win-v312-2026-11-08
3.5 MB  win-v309-2026-11-07
```

**And two installer copies: `Sutram-Setup.exe` at the root (1.9 MB) and `win-v297-2026-11-03/Sutram-Setup-v297.exe` (1.9 MB).** **The second is a v297 artifact, six versions old.**

---

## WS1 - and the docs are cleaner than I expected
**I checked for the stale claims I expected to find, and did not find them:**

- **no "the slice class is closed" claim without its argument**
- **no `r157`**
- **no stale "87 checks"**

**So the docs are in better shape than the code was.** **But check three things I did not:**

1. **Does any doc say the installer is verified on Windows without naming the version?** **If it says "verified" and the version is v312 while main is v315, that is a stale claim.**
2. **Does any doc describe the four ownership records?** **They changed twice in two days.** **If the docs still describe `DesktopOwned` as a flag, they are wrong.**
3. **And the release notes: do they name the shipping condition - that a package must be installed and run on Windows before it is a release?**

## WS2 - and the prune, with a rule
**The rule from the last audit holds: keep every round record, and delete only what is not cited.**

**But this time there is a clearer case. Two things:**

**1. The v297 installer copy.** **A six-version-old artifact inside an evidence folder.** **It is not the shipped package and it cannot be verified against anything current. Remove it, or replace it with its SHA-256 and a note.**

**2. Raw environment snapshots.** **`environment-before.json` at 19 KB, `before.json` at 145 KB, `identity.json` at 173 KB - these are machine states, not evidence of a defect.** **If a round's claim does not depend on the full snapshot, the snapshot is not needed to verify the claim.**

**So: for each Windows round folder, what does its `RESULTS.md` actually cite?** **Keep what is cited, and for what is not, keep a hash and a one-line description rather than the file.**

**A hash plus a description is as verifiable as the file for most purposes, and it is a thousand times smaller.**

## WS3 - and the honest note
**Git does not shrink when files are deleted.** **The clone will stay 112 MB unless history is rewritten, and that is destructive.**

**So this round is not about size.** **It is about a repository a person can search.** **11,215 files where 60% are machine snapshots from one platform is a repository where finding the language is hard.**

**Say so in the round's report, so the record is honest about what the prune does and does not achieve.**

## WS4 - and the counts
**After pruning, report: total files, total size, and the count in each of the four collaboration folders.** **So the next audit has a baseline.**

## And one thing to check while you are in there
**`docs/` has 22 files, 36 rounds and 7 decisions.** **Are any of the 22 superseded by another?** **Two documents that describe the same thing differently is worse than one.**

**Name any pair that overlap, and merge or delete.**
