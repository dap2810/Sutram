# v309 installation and interrupted recovery (Task D)

The native v309 installer completed the upgrade and both interruption retries. The edited file was preserved by an explicit refusal. **The late retry still copies all 657 payload files into staging**, so the requested shortcut for an already-published payload is not demonstrated.

| Attempt | Observation | Result |
| --- | --- | --- |
| Initial upgrade | Finish in 21.23 s; engine 0; closes after Finish | PASS |
| D1 before first copy | Stopped 0.347 s after Install; engine age 0.334 s; 0 payload files; no pending record or transaction | Boundary caught |
| D1 retry | Finish in 24.33 s; engine 0; no pending record/transaction | PASS |
| D2 after last file | Stopped at 18.82 s; 657 files present and 657 `PUBLISHED` journal records; pending record still present | Boundary caught |
| D2 retry | Finish in 21.25 s; engine 0; 657 staging START/DONE pairs, 0 Already staged, 0 replacement PUBLISH log entries | Recovery PASS; repeats staging |
| D3 partway | Stopped at 13.96 s; 57 payload files; appended one line to `docs/BUILDING.md` | Edit recorded |
| D3 retry | Engine 1; error dialog and explicit preserved-file log; edited bytes unchanged | Preservation PASS; observer acknowledgement error disclosed below |

These are observed timings, not performance guarantees. The native suite/OOM run overlapped early recovery work; timing differences cannot be assigned to installer changes.

## D1: previous-attempt handling

The first engine was stopped before it produced a pending record or transaction. The retry therefore has **no previous-attempt notice**; it starts normally and completes. See [stop](d1-stop.json), [retry](d1-retry.json), [retry log](d1-retry-engine.log) and [Finish screenshot](d1-retry-finish.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*.

## D2: distinguishes installed files from staging copies

The stop was caught after the last payload publication, before the pending record was cleared. The saved journal ends with `PUBLISHED` for `win\sutram.exe`; the log had just reached `Writing the payload manifest.` This proves the requested last-file/pending-record boundary, **not interruption inside a partially written journal record**.

The retry logs both prior journal and pending-record notices: `A previous installation stopped part-way ... this run finishes it.` It then recopies **657/657** files into the transaction staging folder. It does not reuse any already-staged entry. There are no per-file replacement `PUBLISH` entries on retry.

The no-replacement interpretation is supported by the pinned installer source: when the target hash matches the new payload hash, the publish loop discards the staged copy, journals `PUBLISHED`, and continues without replacing the target (`windows/native-installer/install-core.ps1`, lines 570-575). Thus it recognises matching installed content **after repeating extraction/staging**, not by immediately finalising the existing publication. No claim is made that all physical disk writes were independently traced.

Evidence: [stop](d2-stop.json), [stop log](d2-stop-engine.log), [stop journal](d2-stop-journal.txt), [retry](d2-retry.json), [retry log](d2-retry-engine.log), [D2 capture](d2-retry-finish.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*, [derived counts](recovery-summary.json). The D2 capture contains only the title bar, so it does not prove the rendered Finish page. D2 completion is supported by the observed Finish control, successful Finish click/exit and engine completion log; the initial and D1 captures show the full Finish page.

## D3: the owner's edited bytes survive

Appended exactly `\nV309 OWNER-EDIT RECOVERY PROBE: preserve this line.\n` to `docs/BUILDING.md`. The retry refuses before replacing it; the GUI reports that setup did not complete and points to the log. The log gives the specific reason and recovery instructions:

```text
[2026-11-07 10:14:54] Not this installer's file (preserved): %USERPROFILE%\AppData\Local\Programs\Sutram\docs\BUILDING.md
[2026-11-07 10:14:54] ERROR: 1 file(s) in the installation folder are not what this installer wrote (changed since installation, or not Sutram's), so it will not replace them: %USERPROFILE%\AppData\Local\Programs\Sutram\docs\BUILDING.md. Nothing was changed. Move those files elsewhere, or move the whole folder aside (for example to %USERPROFILE%\AppData\Local\Programs\Sutram-recovery-20261107-101454), then run this installer again.
```

| Evidence | SHA-256 |
| --- | --- |
| Original | `0f75f06bac0f014b9fb6b790bf97b0dce2699c19730fdc3dfb4db616ca1d4135` |
| Edited before retry | `ecf1de53b67cb8cdfc1550aaabb17cba074173b32fa3a356102574aa31c9bcd9` |
| Post-retry inventory before restore | `ecf1de53b67cb8cdfc1550aaabb17cba074173b32fa3a356102574aa31c9bcd9` |
| Preserved file, independently read after restore | `ecf1de53b67cb8cdfc1550aaabb17cba074173b32fa3a356102574aa31c9bcd9` |

The complete edited folder and transaction remain at:

```text
%USERPROFILE%\AppData\Local\Programs\Sutram-v309-d3-failed-20261107-101454
%USERPROFILE%\AppData\Local\Programs\Sutram-v309-d3-failed-20261107-101454.transaction
```

Sources: [original](d3-original-BUILDING.md), [edited](d3-edited-BUILDING.md), [result](d3-edit-result.json), [retry log](d3-retry-engine.log), [error screenshot](d3-retry-error.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*, [preservation/restore inventory](restore-d3-failed.json).

## Observer errors and final state

Two observer failures are retained rather than counted as product defects:

1. The first wizard observation tried Next before control 2002 existed. It closed the wizard before starting an engine. [Record](initial-observer-error.json). The helper was corrected to wait for the control; the actual upgrade then completed ([Finish](initial-finish.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*).
2. After capturing the D3 error dialog, synchronous `BM_CLICK` acknowledgement returned `SendMessageTimeout failed for message 0xF5`. The engine had exited 1 and the wizard also exited; the controller recorded `OBSERVER_ERROR`, preserved the interrupted folder, and restored the independently verified working v309 backup. This is why [d3-retry.json](d3-retry.json) is not labelled a clean observer pass. [Controller error](recovery-controller-error.txt). D3 preservation was then established read-only by comparing the original edit, post-retry inventory and preserved bytes; no install was repeated to hide this error.

The canonical installation is again **v309**, **657/657 hashes** match, one fresh-shell path resolves, and no pending file/transaction remains ([final identity](final-identity.json), [handoff-time identity](handoff-identity.json)). All 15 recorded wizard/engine processes are closed and no installer lock remains ([process check](final-processes.json)). No process was left waiting for the owner to close it.

Only handles belonging to the recorded test wizard/child were stopped. Logs/journals were copied after termination, with shared read access; live engine logs were not opened. No antivirus exclusion, service change or resumption of security-suspended processes was attempted. Successful finite runs do not establish that security-product suspensions can never recur. There was no v309 IDE acceptance test in this round.
