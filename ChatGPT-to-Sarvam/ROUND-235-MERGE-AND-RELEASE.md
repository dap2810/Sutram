# ROUND-235 — a recoverable integration, not yet a 1.0 release

Review date: 12 November 2026. Brief labels its shared state 13 November. Main pinned to `f758b6139a5f3cc5fa00e3d0a5927914f348780a` (v315); candidate pinned to `702d801c3b3b0d4165244c163f7e7ccd5591eacd` (v326).

**Recommendation: one non-fast-forward merge of the exact final chain tip, after native Windows acceptance and integration checks. Do not merge eleven branch names independently. Do not publish 1.0 yet.** My release assessment is **0.9/release-candidate quality**, not a request to rewrite the existing compiler banner. Threads and generics are not prerequisites for a small 1.0; an unresolved basic-loop correctness defect and an unsettled compatibility promise are.

Only this handoff is being published. No source edits, builds, production merge, release, tag or rollback was performed. This round ran Git graph/tree inspection and the read-only package checker. Full suite, guard, gates, compiler execution, native Windows and GUI acceptance: **NOT RUN in R235**. Counts below are attributed to Claude's committed reports, not new measurements.

## WS1 — actual history, order and expected evidence

### The chain is linear; main cannot fast-forward

`git merge-base main candidate` at these pins is `112838ce07e974a7f736d5a13719e87808a4dfa6`. The symmetric difference is **115 main-only commits and 22 candidate-only commits**. All 22 candidate commits form a linear ancestry path. Thus "eleven branches" describes version milestones, not eleven independent patches or the current number of branch names. The eleven versions are v316 through v326 inclusive; v326 alone has several follow-up commits.

`git merge-tree --write-tree f758b6139a5f3cc5fa00e3d0a5927914f348780a 702d801c3b3b0d4165244c163f7e7ccd5591eacd` succeeded without conflicts, producing tree `4b00271bc89d9ac7efaca715437f36c13605bb0e`.

The simulated merged tree differs from main in **91 paths**. Relative to the candidate, its **595 differing paths are exclusively handoff records**: Claude-to-Sarvam 495, Muse-to-Sarvam 30, Sarvam-to-Claude 28, ChatGPT-to-Sarvam 18, Sarvam-to-Muse 15, Sarvam-to-ChatGPT 8, Windows-to-Sarvam 1. No production path differs from the candidate. These are exact-pin observations; adding this report changes main, so recompute before integration. Never copy the candidate's whole tree over main: that would discard those records.

Use **one `--no-ff` merge commit**, first parent current main, second parent the accepted candidate. This provides one reversible integration boundary and preserves every source commit for normal `git bisect`. Eleven extra merge commits do not improve the granularity of those existing source commits. Do not squash, rebase, cherry-pick all branches, force-push or merge the R233 source branch again: its selected fixes were ported in v325, and the chain must retain its own tested ancestry.

### Milestone order and reported acceptance lines

Read in this order; these are review checkpoints, not instructions to publish eleven intermediate main states. Gates shown as PASS/FAIL/NOT-RUN, suite as PASS plus 4 missing expectations throughout. The guard denominator, baseline and new programs are part of each result. Same totals alone are insufficient: preserve the exact DIFFER/refusal lists and diagnostics.

| Version / pinned milestone | Gates | Suite | Reported guard, with baseline |
|---|---:|---:|---|
| v316 `59d6035` (`v316-ready`) | 82/0/1 | 327+4 | v315: 783 = 587 identical + 196 identical refusals, 0 DIFFER |
| v317 `501d35f` | 83/0/1 | 327+4 | v316: 783 = 587 + 196, 0 DIFFER |
| v318 `c1f516f` | 84/0/1 | 327+4 | v317: 783 = 587 + 196, 0 DIFFER |
| v319 `4c1159b` | 85/0/1 | 327+4 | v318: 783 = 587 + 196, 0 DIFFER |
| v320 `fe90a9b` (includes `9bb059e`) | 86/0/1 | 327+4 | v319: 783 = 549 + 196 + 38 DIFFER; block programs, named list |
| v321 `c0fdebe` | 87/0/1 | 327+4 | v320: 783 = 587 + 196, 0 DIFFER |
| v322 `602b1f1` (`audit-01-fixes`) | 88/0/1 | 327+4 | v321: 783 = 503 + 196 + 84 DIFFER; all 84 reportedly same stdout/exit |
| v323 `f05ddd7` | 89/0/1 | 329+4 | v322: 785 = 587 + 196 + 2 new, 0 DIFFER |
| v324 `e1f29f1` | 90/0/1 | 331+4 | v323: 787 = 582 + 196 + 7 DIFFER + 2 new |
| v325 `22466bd` | 92/0/1 | 331+4 | v324: 787 = 527 + 196 + 64 DIFFER; named library-import list, same stdout/exit reported |
| v326 first package `c3b7b9e` | 93/0/1 | 332+4 | v325: 788 = 581 + 196 + 10 DIFFER + 1 new |
| v326 final `702d801` (after R191 `ad24e23`) | 93/0/1 | 332+4 | R191 v326: 788 = 592 + 196, 0 DIFFER |

Sources: Claude R167, R172, R173, R176, R181, R182, AUDIT-01-FIXES, R184, R186, R189, R190 and R192 reports on pinned main, with their adjacent evidence directories. Crash corpus is reported 227/0 throughout; final R116 contracts 139/0. The final **0 DIFFER is against another v326**, not against v325 or main. The brief's unqualified zero must not be used as a v315-to-v326 acceptance oracle.

For the **single actual merge**, require final 93/0/1 Linux/Xvfb gates, suite 332 pass/4 missing, corpus 227/0, contracts 139/0 and guard against the accepted `702d801` compiler: **788 = 592 identical + 196 identical refusals, 0 DIFFER, 0 new** for each advertised output target. A native acceptance PASS is a separate report; it does not magically change a Linux script's Windows NOT-RUN into PASS. Do not relabel the four missing goldens as passes. If fixes change counts, review and explicitly rebaseline; never rewrite goldens to obtain agreement.

### Concrete integration procedure (for the integrator, not executed here)

Prerequisites: current Windows checklist completed against this exact installer; current main reviewed; clean dedicated checkout; branch/tag names below unused; no unexpected production drift. If main or candidate changes, repeat the graph/diff checks and pin the newly accepted result. The intended tag is **`pre-v326-main-v315`**, an annotated recovery tag, not a release tag.

```sh
# Run from the clean repository root. Stop on every nonzero exit.
set -eu
git fetch origin main r192-paused-books-and-avaroha
git switch -c integrate/v326 origin/main
test -z "$(git status --porcelain)"
PRE=$(git rev-parse HEAD)
CAND=702d801c3b3b0d4165244c163f7e7ccd5591eacd
git cat-file -e "$CAND^{commit}"
git tag -a pre-v326-main-v315 "$PRE" -m 'Main v315 immediately before v326 integration'
git merge --no-ff --no-commit "$CAND"
# STOP HERE for staged-diff inspection and the integration acceptance checks above.
# If anything fails before commit: git merge --abort
# Resume only after the exact staged tree is accepted:
git commit -m 'Integrate accepted v326 chain onto main'
MERGE=$(git rev-parse HEAD)
test "$(git rev-parse "$MERGE^1")" = "$PRE"
test "$(git rev-parse "$MERGE^2")" = "$CAND"
git tag -a integration-v326 -m 'Accepted v326 integration boundary' "$MERGE"
git fetch origin main
test "$(git rev-parse origin/main)" = "$PRE"
# Review the diff once more; normal fast-forward push, never forced.
git push --atomic origin HEAD:refs/heads/main refs/tags/pre-v326-main-v315 refs/tags/integration-v326
```

The comments marking a STOP are actual human gates, not an unattended script to paste and forget. If atomic push is unsupported, stop and arrange a reviewed publication sequence; do not silently downgrade it. A concurrent main update must stop the push/review; never overwrite it. After publishing, verify the exact commit/tree through the GitHub API, plus every changed release artifact hash. Record PRE, CAND, MERGE, test outputs and package hashes together. Do not create `v1.0.0` yet.

### Exact rollback for the immediate post-merge case

This creates a new commit restoring the complete pre-integration tree; it does not rewrite shared history. It deliberately refuses to run if unrelated commits have landed since the integration.

```sh
set -eu
git fetch origin main --tags
git switch -c rollback/v326 origin/main
test -z "$(git status --porcelain)"
MERGE=$(git rev-parse 'integration-v326^{commit}')
PRE=$(git rev-parse 'pre-v326-main-v315^{commit}')
test "$(git rev-parse HEAD)" = "$MERGE"
test "$(git rev-parse "$MERGE^1")" = "$PRE"
git revert --no-commit -m 1 "$MERGE"
git diff --cached --exit-code "$PRE" --
git commit -m 'Roll back v326 integration to pre-v326 v315 tree'
test "$(git rev-parse 'HEAD^{tree}')" = "$(git rev-parse "$PRE^{tree}")"
# Recheck the v315 recovery package before publishing; it is not a new release.
git push origin HEAD:refs/heads/main
```

If reverting conflicts, `git revert --abort` restores the attempt's starting point; investigate, do not auto-resolve. If later commits exist, the HEAD assertion stops: prepare a reviewed revert on then-current main, preserve unrelated work, and accept that the resulting whole tree will not equal PRE. Do not reset/force-push main, delete evidence, or move the recovery tags. A later reintegration must undo the revert or introduce reviewed new changes; merely merging the already-merged old tip will not reapply its reverted changes.

A temporary-index reverse-delta rehearsal restored tree `6d19669a5c9c0cf95e66cdf82c10be6bc98ac4af`, exactly the pinned pre-integration main tree. This verifies reversibility of the current combined content delta; the actual `git revert` command, public rollback and runtime recovery were not executed.

Repository rollback does **not** downgrade installed users. Withdraw/mark the bad candidate and stop promoting its download; keep its immutable checksums and evidence. Use the accepted installer/uninstaller recovery procedure, preserving user programs. v315 itself has known defects and no current complete Windows acceptance: reverting restores a baseline, not a certification of its safety.

## WS2 — what a release needs beyond a staged branch

A merge can preserve history correctly and still fail the release promise. Require:

1. Native install/run/uninstall acceptance on the exact final Windows installer, including non-admin behavior, PATH/associations, IDE and recovery checks in the current checklist. Wine and PE structure checks do not replace it. Any changed installer after acceptance requires an appropriate new acceptance run.
2. Final integrated source/binary/package correspondence, tested Linux artifacts, suite/corpus/contract/guard evidence tied to immutable commits, with skipped and failed checks retained. No claim that 93 aggregate gates prove every semantic contract.
3. An explicit stable 1.x contract: supported targets, supported Sanskrit features, status of frozen packs/books, compatibility/deprecation policy for old names and future loop syntax, supported library APIs versus private layouts, and how bugs are reported and patch releases shipped.
4. Release-critical correctness addressed, not hidden as "stated". At minimum resolve inclusive endpoint wrap; decide the supported range/input contracts; correct remaining directly misleading runnable examples. Deferred additions need not all be implemented.
5. Coherent current documents, licenses/notices for distributed components, installation and recovery instructions, immutable release assets and public checksums. Check these on the packaged documents too, not only the repository.
6. Owner acceptance of the deliberately narrow product promise. The long-term charter's memory safety, OS capability and broad paradigms are goals, not achievements of this release.

### Four document updates required at release

| File | What it says now / observed issue | Required final state |
|---|---|---|
| `README.md` | 336 top-level examples, six books and eleven packs; introductory "no runtime" language; a release-shaped presentation | Put accepted version, date, exact release links and checksum instructions first; distinguish 332 passing/4 missing expectations, active vs paused books/packs, supported targets and known limits. Say no external runtime dependency, not that generated programs contain no runtime code. Link the compatibility contract. |
| `docs/RELEASE-NOTES.md` | v326 candidate explicitly untested on Windows; older chronological paragraphs retain superseded "not fixed" statements; last-package wording differs from the new brief | Replace the top with the actual acceptance record and immutable commit/hash. Present one current limitations table, move or clearly fence superseded chronology. Reconcile v311/v312/v313 evidence by exact artifact and scope, not by assuming the latest number passed. Preserve historical reports. |
| `PROJECT-MASTER.md` | v326 staged top block; lower historical tables still describe older features/numbers | State main integration commit and release status separately, link final evidence, supported API contract and live issue list; label historical tables unmistakably. Do not promote the charter's aspiration into current safety or freestanding claims. |
| `ROADMAP.md` | Its current block still says v325, main315, while this candidate is v326; old v411/v261 snapshot follows | Update current state to accepted release and split future proposals from commitments. `avaroha` is proposed, not implemented; generics 1.1 is a direction unless explicitly committed. Keep old snapshot as history. |

These are a release checklist, not edits made in this round. Editing packaged docs changes the installer payload: rebuild it, rehash it and revalidate before attaching it to the release. Do not retain an old accepted checksum after rebuilding.

### Installer verification actually done here

`python3 tests/r140/test_package.py` at `702d801`: **7 checks, 0 failed**. The embedded manifest lists **664/664 entries**, each hashes correctly and is byte-identical to its mapped candidate-tree source. All **567** payload text sources have LF attributes; embedded text has no CRLF; ZIP dates are fixed; the external setup checksum matches. This checker reads bytes and metadata, not compiler execution or installation.

Measured SHA-256:

- `Sutram-Setup.exe`: `c47936ca009e62c35503d64afd7d777ab9b22c26953335948ae698a93e7b8ef3`
- `sutram.exe`: `f22fea3feefb0547816494ee53c4f6db878fb471c563e4776d0aa029ff252304`

Both match the current Windows checklist. On the final integration repeat the package checker; after download verify the setup hash, and after installation compare installed compiler and payload files to that manifest. A version banner alone cannot prove correspondence.

```sh
sha256sum -c Sutram-Setup.sha256
```

```powershell
(Get-FileHash .\Sutram-Setup.exe -Algorithm SHA256).Hash
```

Compare the PowerShell result with the exact expected setup hash above, ignoring letter case only; stop on mismatch. This is integrity checking, not a digital signature or proof that the publisher is trustworthy.

**A checksum manifest is already partly present:** `Sutram-Setup.sha256` and the embedded `payload.manifest.sha256`. Do not claim none exists. Add a release-level `SHA256SUMS` for every actually distributed installer/archive/standalone binary, using relative asset filenames, one SHA-256 per file, no self-hash. Pair it with release metadata naming the source commit, integration commit, version, target, byte sizes, build recipe and acceptance references; include the embedded payload manifest or its digest. Include Linux and source archives only if they are actually created and tested. Hash final downloadable bytes, not an earlier build or Git blob ID. Checksums and metadata should come from an authenticated immutable release; signatures are useful if the project adopts signing, but must not be claimed before they exist.

## WS3 — limits to promise explicitly

| Limitation / accurate scope | Release notes | Book's limits chapter / teaching placement |
|---|---|---|
| No threads, async language execution, generics or non-local exception unwinding | Explicit exclusions; unsynchronised allocator is not thread-safe | Show procedural alternatives, checked results and `ok[0]`; future features labelled proposals |
| No integrated interactive debugger or emitted debug symbols | State tool limits; tracing/check mode exist | Explain `--debug`, `--check`, and what external machine-code debugging can/cannot show |
| Loop direction depends on literal bounds; variable-ended `chakra` counts up; warning covers only `n tak 1` | Exact rule and remaining silent shapes, plus endpoint wrap as a known defect | Teach `yavat` countdown with step before `agrim`; do not say loops cannot count down at all; `avaroha` not available |
| Scratch is rewound and zeroed, but retained pages are not automatically returned to OS; ordinary arrays and most allocations live for process lifetime | Resource limits and long-running/large-input consequences | Explain scratch reuse vs OS RSS, logical `parimana`, eligible loop reuse and its exclusions |
| A `mala` can leave a block because its ordinary allocation is not reclaimed there | Do not describe it as a demonstrated dangling pointer merely because it escapes | Distinguish ordinary `mala`, checked block-local `kosh`, and scratch/raw pointers; see reference §19 |
| No general ownership/borrow checking, unsafe boundary, automatic handle cleanup or general memory-safety guarantee | Prominent suitability limit | Raw memory/cell representation, explicit closes, bounds checks are partial protection, not a safety theorem |
| `grahan` skips junk and wraps; checked text conversion is separate; byte/NUL strings are not Unicode grapheme strings | Compatibility/input/encoding contract and line-allocation cost | Default examples should use `vartani_grahan` plus `vartani_tak_ank` and test `ok[0]`; empty/EOF and embedded NUL policy must be explicit |
| Integer wrap versus checked/saturating/sentinel functions; variance's narrow domain; negative popcount returns 0 | Stable per-function contracts, no blanket mathematical-exactness claim | Teach limits and status checks beside examples |
| Frozen ten non-Sanskrit packs and four paused books | State maintenance/translation status; do not advertise equally current editions | Warnings at entry and affected teaching sections; use active editions for current semantics |
| Linux-only socket support; x86-64 Linux/Windows target scope; no proven bootable-kernel claim | Exact platform matrix, unsupported systems excluded | Native executable does not imply freestanding OS capability |
| No mature package ecosystem, general optimiser/performance guarantee or formal compiler proof | Scope limits; executable "proofs" are tests | Explain what is measured and what is not; keep roadmap promises separate |

The release notes already include many of these. The task is to make them current, consistent and discoverable, not to claim they were all missing. The charter itself contains old "today" statements; it must remain visibly a target/history until reconciled with current evidence.

## WS4 — plainly: not yet

**No, I would not endorse this exact candidate as the stable 1.0 release today.** A limited language can absolutely be 1.0 without generics, threads or a debugger. It needs a dependable, clearly bounded core and an explicit compatibility commitment. Native Windows acceptance is necessary for the advertised Windows release, but it is not sufficient for that language-level judgment.

The brief says the defects are fixed. The candidate's own `docs/WHATS-LEFT.md` §4 says the inclusive largest-integer `chakra` still wraps and never finishes; R234 demonstrated it on v324, and v325/v326 reports explicitly say it remains. This is not equivalent to missing generics. Documenting it is disclosure, not repair. The variable-direction question is also still open. The live list additionally names an example calling nonexistent `sankhya_padh` and other documentation/test gaps. Therefore "Windows passes, so 1.0" overstates the evidence.

What would make a defensible narrow 1.0: fix or explicitly reject the endpoint cases with tests for MAX/MIN, equal bounds, empty ranges and `agrim`; settle and publish the loop/input semantics and 1.x compatibility policy; correct the directly misleading current examples; finish final native/package acceptance; publish current limits, immutable assets and checksums. Retained memory and missing advanced features may remain declared constraints. Do not require the entire aspirational charter before releasing a small, honest language.

Until those decisions and checks are complete, keep the public status **candidate / pre-1.0 quality** even though the internal banner already says 1.0. A technical merge, if independently accepted by the owner under the project's policy, is a separate act from announcing a stable release. This report does not authorize or perform either.

## Publication checks

The privacy checker inspected 11,463 tracked files including this handoff: **0 with system details**. Whitespace validation passed. No compiler or production file was modified.
