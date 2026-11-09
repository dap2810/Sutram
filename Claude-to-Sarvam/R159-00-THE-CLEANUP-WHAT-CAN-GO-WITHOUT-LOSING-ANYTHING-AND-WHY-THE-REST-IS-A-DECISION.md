# R159-00 — Done in the order WS4 asked: the books and the gate first (R157-00, R158-00), then this. The cleanup removed what could go without losing a byte: the v297 installer (R156) and 11 files that are byte-identical copies of files that stay. The rest of what this round names is cited evidence, and this round's rules disagree with each other and with ChatGPT's review on whether cited evidence may go. That is a decision, set out below with the numbers, not one I took. History rewrite: no.

## Release line

```
gates: 79 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
Sutram 1.0 (v315) - sampurna sutra      (compiler unchanged)
```

Same commit as R157-00 and R158-00. The gates ran before the 11 removals below, which are evidence copies no gate reads.

## WS3 first, as you asked it to be said

**This round makes the working tree a little smaller. It makes the repository - the clone - no smaller at all.** Git keeps every deleted file in history.

| | before R156 | now |
|---|---:|---:|
| tracked files | 11,222 | 11,233 (the reports and evidence of R155-R159 added more than was removed) |
| working tree | 118.3 MB | **116.0 MB** |
| `.git` pack (what a clone downloads) | 71.8 MiB | 71.8 MiB - unchanged |

**Is a history rewrite now worth considering? No - not as a rewrite.**
- **Where the history's weight is** (compressed blob sizes, every version ever committed):
  - the root binaries' old versions - every `Sutram-Setup.exe`, `sutram.exe` and `sutram_compiler` ever committed - **47 MiB**;
  - `Windows-to-Sarvam/` **24 MiB**;
  - `backups/` 8.5 MiB.
  - Only a rewrite that drops old binaries from history would make the clone noticeably smaller.
- **What it would cost:**
  - **every commit SHA changes;**
  - **every round record that cites a commit** - hundreds of them, in all five collaboration folders, and the guard's baselines - would point at commits that no longer exist;
  - the owner's Windows clone, and every partner's, would have to be cloned again, with any local work carried over by hand;
  - it needs a forced push, which I am not allowed to do.
- **The way to get a small repository without destroying one:** at the v1.0 release, start a **new release repository** from the tree as it then stands, and keep this one, unchanged, as the project's archive. Clones of the release repository are small, and nothing cited breaks. **If the owner wants that, it is a decision for the owner, at release.**

## WS1 - the four categories, measured on this tree

| type | files | size | what I found |
|---|---:|---:|---|
| `.json` | 670 | 31.9 MB | 31 are byte-identical extra copies (3.5 MB); the rest are distinct, and almost all are cited |
| `.png` | 329 | 27.2 MB | 53 are byte-identical extra copies (4.3 MB) |
| `.sm` | 3,855 | 3.8 MB | **1,202 basenames are shared, by 2,443 files.** In 1,082 of those groups every copy is identical; **in 120 the copies differ** |
| `.exe` | 6 | 3.3 MB | the v297 installer went in R156; the six left are the product |

**What went, and why it loses nothing** (`evidence-r159/removed-identical-copies.tsv`). There were **11 files (594 KB)** that:
- R156's audit found named nowhere: no report, round record, index, script or pattern names them; **and**
- are **byte-identical to a file that stays** - for example, `win-v309-fixes-2026-11-07/initial-identity.json` is the same bytes as `final-identity.json` beside it.

Each line of the manifest gives the removed path, its SHA-256, the identical copy that stays, and the commit to restore it from. **The SHA-256 of each kept copy was checked equal before each removal.**

**The rest, and why I did not remove it:**

**1. Your JSON rule** - keep the number in the report and the file's hash, delete the file.
- **ChatGPT's review (R221 follow-up) says it is wrong,** and on the narrow point it is right. A hash proves which bytes a file had. It does not give them back, so nobody could recompute the claim from it.
- **With git it is recoverable:** the bytes stay in history, at a commit the manifest would name.
- **So the rule is sound only together with that manifest.** And it still means deleting evidence that its report *cites*, which R156's rule ("keep every file it cites") forbids.
- **The two rules disagree, and you wrote both.** Which one wins is yours to say, not mine.

**2. Screenshots** - keep what text cannot show; delete terminals printing a quoted line.
- **That is a judgment on each of 329 images,** and nearly all are cited: R156 found 4,365 of the 4,424 Windows files cited.
- **ChatGPT again:** *"A quoted screenshot caption is not equivalent to the screenshot's corroboration."*
- **I removed none.**

**3. Duplicate `.sm` probes.**
- **"Same name" is not "same file":** in 120 of the 1,202 groups the copies differ.
- **In the 1,082 identical groups,** each copy sits in the round folder whose commands ran it. Their `COMMANDS.md` and scripts name those paths, and their `EVIDENCE.sha256` manifests list them.
- **Removing one breaks a recorded command or a manifest.** Replacing it with a pointer file changes its bytes, and the manifest breaks just the same.
- **I removed none.**

**4. `.exe`:** done in R156.

## WS2 - the Windows folders before v309

**Thirteen folders, as you list them, 13 MB.** Your instruction: *keep every `RESULTS.md` and every file it cites; prune the raw evidence.*
- **By R156's audit, their raw evidence is cited** - by name, by pattern, or by the command that made it. **None of it is uncited and unduplicated.**
- **So under your own rule, nothing in them can go.** Pruned: **0 folders.**
- **What remains:** all of their files, except the 11 identical copies above, some of which were in these folders.

**The rule from R49/R50 still stands beside this one:** *"Do not touch `Windows-to-Sarvam/`."*
- **The Windows owner is testing from those folders on Tuesday.** Removing cited evidence from their folder, in their clone, the day before, is not something I would do on a rule that contradicts another rule.

## What would actually reduce it - the decision, with the numbers

If you decide that cited raw evidence in **pre-v309** Windows rounds may go, with a manifest:
- **the manifest gives, for each file:** its path, its SHA-256, the commit that holds it, and the reports that cite it;
- **each citing report gets one line:** *"pruned in R16x; `git show <commit>:<path>`"*.

**The working tree would lose about 13 MB (your figure for the thirteen folders, less their reports and scripts).** The clone would lose nothing.

**Say which folders, and I will do it in one round.** The script for it is R156's citation audit (`evidence-r156/cite*.py`) with one more column.

## Not done

- **No deletion of cited evidence, anywhere.**
- **No history rewrite.**
- **No change to another partner's folder** except the 11 identical copies, all in `Windows-to-Sarvam/`. Their folders' `EVIDENCE.sha256` files still list those 11 paths. Each removed file's bytes are, unchanged, at the path in the manifest's last column.

Evidence: `Claude-to-Sarvam/evidence-r159/`.
