# v307 native setup: clean install works; upgrade still triggers Acronis

6 November 2026, owner's Windows desktop, non-Administrator token. Candidate
hashes and commands: [COMMANDS.md](COMMANDS.md). Security settings were unchanged.

## Clean installation

All 662 files from the working v306 installation were preserved and hash-verified
in `%USERPROFILE%\AppData\Local\Programs\Sutram-before-v307-20261106`.
The canonical target was absent and its exact user-PATH entry removed for this
test. Other PATH entries and the machine PATH were preserved.

The v307 engine log records start at **22:39:04** and completion at **22:39:20**:
about **16 seconds**, at one-second log resolution. It copied all 657 payload
files. [clean-finish.png](clean-finish.png) shows native setup reporting success.
The first observer's JSON serialization problem delayed Finish observation;
therefore no precise GUI completion duration or child exit code is claimed.
The child was absent when the Finish screen was captured. The wizard remained
open on Finish and closed when Finish was clicked, with Launch IDE unchecked.
It did **not** close itself. See [clean-finish.json](clean-finish.json) and
[clean-engine.log](clean-engine.log).

[identity-clean.json](identity-clean.json) verifies **657/657 payload hashes**,
the pinned compiler, and a new `cmd.exe /d` using persisted machine+user PATH
from an unrelated working directory: exactly one canonical `sutram.exe`,
`Sutram 1.0 (v307) - sampurna sutra`, exit 0.

## Same-directory upgrade

The first attempt ended with an error dialog after the diagnostic observer hit
a log-sharing error. Its cause is unproven; it is retained separately as
`upgrade-observer-failed*` and is not used to establish the hang's cause.
The verified clean v307 backup was restored before retrying with a corrected
reader. See [COMMANDS.md](COMMANDS.md) for both diagnostic limitations.

The repeat's wizard PID is **31584**, PowerShell engine PID **43868**. The child
started at **22:47:25.2745802**. The last successfully observed engine line is:

```text
[2026-11-06 22:47:41] Copying 87/657: docs\sutram-keyword-words.html
```

At **22:47:41.040461**, Acronis Active Protection's `Create Delete Full Read`
heuristic flagged the PowerShell engine. At **22:47:41.041459**, its log explicitly
records both the engine and wizard as **suspended successfully**. The preceding
records name creation of `sutram-keyword-words.html.sutram-partial` and deletion
of `sutram-keyword-words.html`. These are vendor heuristic findings, not proof
that Sutram is malware.

The early snapshot independently records 28 suspended engine threads and five
suspended wizard threads; two other wizard threads show EventPairLow waits.
The UI stopped responding. [upgrade-stalled-dwm.png](upgrade-stalled-dwm.png)
is the existing native setup window, captured without resuming it. Its provenance
is in [dwm-screenshot.json](dwm-screenshot.json).

Raw vendor evidence, with source log paths, line numbers and surrounding context:
[security-upgrade-at-stall.json](security-upgrade-at-stall.json). Current phase
observations and thread states: [upgrade.json](upgrade.json).

The extracted engine matches the repository engine's text. It logs each filename
**before** copying, copies to a `.sutram-partial` sibling, deletes the old target
if present, then moves the sibling into place. The old mass-delete pass is gone;
the remaining per-file replacement still triggered protection on this machine.
The named file is not evidence of an intrinsic defect in that HTML file.

The observer ran **936.39 seconds** after Install, ending at **23:03:05.1254758**.
There was no Finish page, error dialog, child exit or timeout log. Both processes
remained alive and the pending manifest remained. Posting WM_CLOSE after the
observation did not close the suspended wizard. This verifies failure under
external suspension; it does not establish how the timer behaves in a runnable
wizard. The raw [upgrade-engine.log](upgrade-engine.log) ends at the same file 87
line. It was copied after the suspended writer's handles were closed.

[upgrade-defender.json](upgrade-defender.json) records no matching Defender
Operational events from this attempt's start through the query. That does not
mean that no security product intervened: the Acronis evidence positively
identifies the third-party intervention.

After observation, cleanup validated executable/command, PID and creation time,
then stopped only engine 43868 and wizard 31584. The 663-file partial tree was
preserved at `%USERPROFILE%\AppData\Local\Programs\Sutram-v307-upgrade-partial-20261106`.
All **662 restored files** matched the verified v307 backup; user/machine PATH
were unchanged and the CLI returned v307 with exit 0. See
[restore-upgrade.json](restore-upgrade.json).

## Deliberate interruption and recovery

**PASS in the final test.** The first retry was affected by a live-log-reader
confound and is retained under [reader-interference](reader-interference).
A local fixture proved that even a fully shared reader can prevent PowerShell
5.1 `Add-Content` from opening its log for writing. The engine uses that command
with stop-on-error. See [log-reader-check.json](log-reader-check.json) and the
full limitations in [COMMANDS.md](COMMANDS.md). The initial failure is not used
to claim a recovery defect independent of that interference.

After preserving that attempt and restoring the verified backup, the final
test began with an absent canonical folder. It interrupted only wizard **16540**
and engine **18272** after seeing **15 complete payload filenames**, at 10.85 s.
The observer did not open the live engine log. After both processes exited,
the log ended at `Copying 19/657: bin\lang\odia.lang`; the partial tree contained
20 files including `payload.pending.sha256`. The differing trigger/log counts
reflect copying that continued between the directory snapshot and termination.
See [interrupt.json](interrupt.json), [interrupt-engine.log](interrupt-engine.log)
and the retained [pending manifest](interrupted-payload.pending.sha256).

The retry into that same partial folder logged at **23:09:38**:

```text
A previous installation stopped part-way (it left %USERPROFILE%\AppData\Local\Programs\Sutram\payload.pending.sha256); this run finishes it.
```

It copied all **657 files**, recorded installation complete at **23:09:52**, and
reached the native Finish page after **16.57 s**. Engine PID **26632** exited
**0**. Wizard PID **40300** stayed on Finish until the observer unchecked Launch
IDE and clicked Finish; it then exited. It did not close itself. Evidence:
[recovery.json](recovery.json), [recovery-engine.log](recovery-engine.log),
[recovery-finish.png](recovery-finish.png). The screenshot was visually inspected.

The full-window [Defender query](defender.json), from the first clean install
through final verification, found only informational health events **1150/1151**,
not a blocking/ransomware event. The relevant Acronis logs record the upgrade's
two suspensions and no matching suspension for the final interruption/recovery
PIDs in the examined files; [security-log-excerpts.json](security-log-excerpts.json)
records scope and source hashes. Absence within these logs is not a universal
claim about all possible security activity.

## Final machine state

**Working v307 is installed at the canonical location.**
[identity.json](identity.json) verifies **657/657 payload hashes**, the pinned
compiler, and exactly one canonical path in a fresh shell.
[final-state.json](final-state.json) records 662 total installed files,
DisplayVersion **1.0.307**, no pending manifest, no `.sutram-partial` files,
CLI exit 0, and **none of the 14 test-owned wizard/engine processes still running**.
The working installation is the successful retry's result, not a post-retry
backup restoration. Original v306/v307 backups and failed partial trees remain
preserved. No protection setting was changed.

| Requested question | Result |
| --- | --- |
| Same-directory upgrade completes? | No; both processes externally suspended by Acronis |
| Duration / closes itself? | No result through 936.39 s; suspended wizard did not close |
| Each file logged before copying? | Yes; extracted engine text and native logs checked |
| Last line at stall? | File 87/657, `docs\sutram-keyword-words.html` |
| Security event? | Acronis explicitly suspends both processes; Defender only health events in the full window |
| Interrupted installation recovers? | Yes, final test reaches Finish in 16.57 s, engine exit 0, manifest verifies |

This is a measured recovery pass and an observed upgrade failure under this
diagnostic workflow. No additional same-directory upgrade without a live log
reader was run. The direct Acronis suspension records remain decisive for the
observed freeze; the reader-interference finding is a separate limitation and
logging issue. No general release acceptance is claimed.
